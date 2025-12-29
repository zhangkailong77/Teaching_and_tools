from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.api import deps
from app.core import security
from app.models.user import User
from app.models.course import Class, Enrollment
from app.models.content import Course, ClassCourseBinding
from app.schemas import course as schemas
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------
# 1. 获取我的班级列表 (老师端 Dashboard 用)
# ------------------------------------------------------------------
@router.get("/", response_model=List[schemas.ClassOut])
def read_my_classes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 如果是老师，只查自己创建的班级
    classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
    
    # (可选优化) 简单统计每个班有多少人
    # 这里为了演示简单，暂时不写复杂的 count 逻辑，直接返回
    return classes

# ------------------------------------------------------------------
# 2. 创建新班级
# ------------------------------------------------------------------
@router.post("/", response_model=schemas.ClassOut)
def create_class(
    *,
    db: Session = Depends(deps.get_db),
    class_in: schemas.ClassCreate,
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
# 3. 向班级添加学生 (核心需求)
# 逻辑：账号不存在则自动创建，存在则直接关联
# ------------------------------------------------------------------
@router.post("/{class_id}/students")
def add_student_to_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: int,
    student_in: schemas.StudentAdd,  # 这里现在包含了 full_name 和 student_number
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
@router.get("/my-students", response_model=List[schemas.StudentListOut])
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
@router.get("/stats", response_model=schemas.DashboardStats)
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
# 修改: 获取我的班级列表 (填充详细信息)
# ------------------------------------------------------------------
@router.get("/", response_model=List[schemas.ClassOut])
def read_my_classes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    print(f"\n========== [DEBUG] 开始查询班级列表: 用户 {current_user.username} ==========")
    
    # 1. 查询该老师的所有班级
    classes = db.query(Class).filter(Class.teacher_id == current_user.id).order_by(Class.created_at.desc()).all()
    
    if not classes:
        print("--- [DEBUG] 该老师名下没有班级 ---")
        return []

    results = []
    for cls in classes:
        # 2. 显式查询人数
        s_count = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()
        
        # 3. 显式查询绑定课程
        bindings = db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == cls.id).all()
        c_names = []
        for binding in bindings:
            course_obj = db.query(Course).filter(Course.id == binding.course_id).first()
            if course_obj:
                c_names.append(course_obj.name)
        
        # 打印每一行数据的查询结果，确保逻辑执行了
        logger.info(f"--- [DEBUG] 班级ID: {cls.id} | 名称: {cls.name}")
        logger.info(f"    --> 查到人数: {s_count}")
        logger.info(f"    --> 查到课程: {c_names}")

        # 4. 显式构造字典返回
        results.append({
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "teacher_id": cls.teacher_id,
            "cover_image": cls.cover_image,
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "created_at": cls.created_at,
            # 填入查询到的真实数据
            "student_count": s_count, 
            "bound_course_names": c_names
        })
    
    print("========== [DEBUG] 查询结束 ==========\n")
    return results