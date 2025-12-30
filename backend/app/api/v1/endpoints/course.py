from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.api import deps
from app.core import security
from app.models.user import User
from app.models.course import Class, Enrollment
from app.models.content import Course, ClassCourseBinding
from app.schemas import classroom as class_schemas
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------
# 1. 获取我的班级列表 (老师端 Dashboard 用)
# ------------------------------------------------------------------
@router.get("/", response_model=List[class_schemas.ClassOut])
def read_my_classes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 查询该老师的所有班级
    classes = db.query(Class).filter(Class.teacher_id == current_user.id).order_by(Class.start_date.desc()).all()
    
    # 2. 遍历班级，手动填充统计数据
    results = []
    for cls in classes:
        # --- A. 统计人数 ---
        # 查询 Enrollment 表，计算该 class_id 下有多少记录
        s_count = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()
        
        # --- B. 查询绑定课程名 ---
        # 1. 先查中间表 bindings
        bindings = db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == cls.id).all()
        # 2. 再查具体的课程名
        c_names = []
        c_ids = []
        for binding in bindings:
            course_obj = db.query(Course).filter(Course.id == binding.course_id).first()
            if course_obj:
                c_names.append(course_obj.name)
                c_ids.append(course_obj.id)
        
        # --- C. 拼装返回数据 ---
        # 我们不能直接返回 cls 对象了，因为 cls 对象里没有 student_count 属性
        # 我们需要构造一个字典，包含所有字段
        results.append({
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "teacher_id": cls.teacher_id,
            "cover_image": cls.cover_image,
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "created_at": cls.created_at,
            
            # ✅ 这里填入我们刚算出来的数据
            "student_count": s_count, 
            "bound_course_names": c_names,
            "bound_course_ids": c_ids
        })
        
    return results

# ------------------------------------------------------------------
# 创建新班级
# ------------------------------------------------------------------
@router.post("/", response_model=class_schemas.ClassOut)
def create_class(
    *,
    db: Session = Depends(deps.get_db),
    class_in: class_schemas.ClassCreate,
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以创建班级")

    if class_in.start_date and class_in.end_date:
        # 1. 确保两个时间都不为 None (Pydantic 已保证是 datetime 类型)
        
        # 2. 统一去除时区信息 (转为 naive time) 再比较，防止报错
        # replace(tzinfo=None) 是去除时区的标准做法
        start_naive = class_in.start_date.replace(tzinfo=None)
        end_naive = class_in.end_date.replace(tzinfo=None)
        
        if end_naive < start_naive:
            raise HTTPException(status_code=400, detail="结课时间不能早于开课时间")

    new_class = Class(
        name=class_in.name,
        description=class_in.description,
        teacher_id=current_user.id,
        cover_image=class_in.cover_image,
        start_date=class_in.start_date,
        end_date=class_in.end_date
    )
    db.add(new_class)
    db.flush()

    if class_in.course_ids:
        for cid in class_in.course_ids:
            binding = ClassCourseBinding(
                class_id=new_class.id,
                course_id=cid
            )
            db.add(binding)

    db.commit()
    db.refresh(new_class)
    return new_class


# ------------------------------------------------------------------
# 更新班级信息 (修改名称、时间、重新绑定课程)
# ------------------------------------------------------------------
@router.put("/{class_id}", response_model=class_schemas.ClassOut)
def update_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: int,
    class_in: class_schemas.ClassUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 查班级
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")
    if class_obj.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 2. 转换数据
    update_data = class_in.dict(exclude_unset=True)
    
    # 3. 处理课程绑定更新
    if "course_ids" in update_data:
        new_course_ids = update_data.pop("course_ids")
        if new_course_ids is not None:
            # 先清空旧绑定
            db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == class_id).delete()
            # 再加新绑定
            for cid in new_course_ids:
                db.add(ClassCourseBinding(class_id=class_id, course_id=cid))

    # 4. 更新基本字段
    for field, value in update_data.items():
        setattr(class_obj, field, value)

    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    # 5. 重新构造返回数据 (为了包含统计信息)
    # 简单调用一下查询逻辑补全字段
    s_count = db.query(Enrollment).filter(Enrollment.class_id == class_obj.id).count()
    bindings = db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == class_obj.id).all()
    c_names = []
    c_ids = []
    for binding in bindings:
        course = db.query(Course).filter(Course.id == binding.course_id).first()
        if course:
            c_names.append(course.name)
            c_ids.append(course.id)

    return {
        **class_obj.__dict__,
        "student_count": s_count,
        "bound_course_names": c_names,
        "bound_course_ids": c_ids
    }


# ------------------------------------------------------------------
# 向班级添加学生 (核心需求)
# 逻辑：账号不存在则自动创建，存在则直接关联
# ------------------------------------------------------------------
@router.post("/{class_id}/students")
def add_student_to_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: int,
    student_in: class_schemas.StudentAdd,  # 这里现在包含了 full_name 和 student_number
    current_user: User = Depends(deps.get_current_user),
):
    # A. 权限校验 (不变)
    class_obj = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_user.id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在或无权操作")

    # B. 查找学生账号是否存在
    student = db.query(User).filter(User.username == student_in.username).first()

    if not student:
        # --- 分支 1: 账号不存在 -> 自动注册 ---
        print(f"账号 {student_in.username} 不存在，正在自动创建...")
        hashed_password = security.get_password_hash("123456")
        student = User(
            username=student_in.username,
            hashed_password=hashed_password,
            role="student",
            is_active=True,
            # ✅ 新增：写入姓名和学号
            full_name=student_in.full_name,
            student_number=student_in.student_number
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    else:
        # --- 分支 2: 账号已存在 -> 更新信息 ---
        if student.role != "student":
            raise HTTPException(status_code=400, detail="该账号已存在，但不是学生账号")
        
        # ✅ 新增：既然老师手动输入了，我们就更新一下这个学生的资料
        student.full_name = student_in.full_name
        student.student_number = student_in.student_number
        db.add(student)
        db.commit()
        db.refresh(student)

    existing_enrollment = db.query(Enrollment).filter(Enrollment.student_id == student.id).first()
    
    if existing_enrollment:
        # 如果已经有记录了
        if existing_enrollment.class_id == class_id:
            return {"message": f"学生 {student.full_name} 已经在当前班级中"}
        else:
            # 查一下他所在的班级名字，提示友好一点
            old_class = db.query(Class).filter(Class.id == existing_enrollment.class_id).first()
            class_name = old_class.name if old_class else "其他班级"
            
            # 抛出 400 错误，阻止操作
            raise HTTPException(
                status_code=400, 
                detail=f"添加失败：该学生已属于【{class_name}】，一个学生只能加入一个班级。"
            )

    # D. 建立关联 (不变)
    enrollment = db.query(Enrollment).filter(
        Enrollment.class_id == class_id, 
        Enrollment.student_id == student.id
    ).first()

    if not enrollment:
        enrollment = Enrollment(class_id=class_id, student_id=student.id)
        db.add(enrollment)
        db.commit()
        return {"message": f"学生 {student.full_name} 添加成功"}
    else:
        return {"message": f"学生 {student.full_name} 已经在班级中"}


# ------------------------------------------------------------------
# 4. 获取老师名下的所有学生 (用于学生名单表格)
# ------------------------------------------------------------------
@router.get("/my-students", response_model=List[class_schemas.StudentListOut])
def read_my_students(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 逻辑：查询 Enrollments 表
    # 条件 1: 关联的 Class 的 teacher_id 必须是当前用户
    # 联表: Enrollment -> Class, Enrollment -> Student(User)
    
    results = db.query(Enrollment).join(Class).join(User, Enrollment.student_id == User.id)\
        .filter(Class.teacher_id == current_user.id)\
        .all()
    
    # 组装数据返回
    students_data = []
    for enrollment in results:
        student = enrollment.student
        classroom = enrollment.classroom
        
        students_data.append({
            "id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "student_number": student.student_number,
            "class_name": classroom.name,
            "joined_at": enrollment.joined_at,
            "is_active": student.is_active,
            "progress": 0 # 暂时为 0
        })
        
    return students_data

# ------------------------------------------------------------------
# 新增: 获取教师工作台统计数据
# ------------------------------------------------------------------
@router.get("/stats", response_model=class_schemas.DashboardStats)
def read_dashboard_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    # 1. 统计班级总数
    class_count = db.query(Class).filter(Class.teacher_id == current_user.id).count()

    # 2. 统计学生总数 (去重!)
    # SQL 逻辑: SELECT count(DISTINCT student_id) FROM enrollments JOIN classes ...
    student_count = db.query(func.count(distinct(Enrollment.student_id)))\
        .join(Class, Enrollment.class_id == Class.id)\
        .filter(Class.teacher_id == current_user.id)\
        .scalar()

    # 3. 待批改作业 (暂未开发，返回 0 或假数据)
    pending_homeworks = 12 # Mock 数据

    return {
        "total_students": student_count or 0,
        "total_classes": class_count or 0,
        "pending_homeworks": pending_homeworks
    }


# ------------------------------------------------------------------
# 6. 将学生移出班级
# ------------------------------------------------------------------
@router.delete("/{class_id}/students/{student_id}")
def remove_student_from_class(
    class_id: int,
    student_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 权限校验
    class_obj = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_user.id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")

    # 2. 删除关联记录
    enrollment = db.query(Enrollment).filter(
        Enrollment.class_id == class_id, 
        Enrollment.student_id == student_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="该学生不在本班级中")

    db.delete(enrollment)
    db.commit()
    return {"message": "移出成功"}