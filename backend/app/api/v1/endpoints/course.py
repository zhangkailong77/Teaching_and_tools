from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.utils.hash import encode_id 

from app.api import deps
from app.core import security
from app.models.user import User
from app.models.course import Class, Enrollment, ClassAssignment, StudentSubmission
from app.models.content import Course, ClassCourseBinding, CourseChapter, CourseLesson, StudentLearningProgress
from app.schemas import classroom as class_schemas
import logging
import pandas as pd
import io 
from datetime import datetime, timedelta
from app.models.exam import Exam

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
        c_public_ids = []

        for binding in bindings:
            course_obj = db.query(Course).filter(Course.id == binding.course_id).first()
            if course_obj:
                c_names.append(course_obj.name)
                c_ids.append(course_obj.id)
                c_public_ids.append(encode_id(course_obj.id))

        pending = db.query(StudentSubmission).join(ClassAssignment).filter(
            ClassAssignment.class_id == cls.id,
            StudentSubmission.status == 1
        ).count()
        
        # --- C. 拼装返回数据 ---
        results.append({
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "teacher_id": cls.teacher_id,
            "cover_image": cls.cover_image,
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "created_at": cls.created_at,
            
            "student_count": s_count, 
            "bound_course_names": c_names,
            "bound_course_ids": c_ids,
            "bound_course_public_ids": c_public_ids,
            "pending_count": pending
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
@router.get("/my-students", response_model=dict)
def read_my_students(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    class_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    
    # 1. 构建基础查询 (保持原本的联表逻辑)
    query = db.query(Enrollment).join(Class).join(User, Enrollment.student_id == User.id)\
        .filter(Class.teacher_id == current_user.id)

    if class_id:
        query = query.filter(Enrollment.class_id == class_id)

    if keyword:
        # 模糊搜索：姓名、学号、手机号
        query = query.filter(
            (User.full_name.like(f"%{keyword}%")) | 
            (User.student_number.like(f"%{keyword}%")) |
            (User.username.like(f"%{keyword}%"))
        )

    total = query.count()

    offset = (page - 1) * limit
    results = query.order_by(Enrollment.joined_at.desc()).offset(offset).limit(limit).all()
    
    # 组装数据返回
    students_data = []
    for enrollment in results:
        student = enrollment.student
        classroom = enrollment.classroom

        s_avatar = None
        if student.student_profile:
            s_avatar = student.student_profile.avatar

        # --- B. ✅ 核心新增：计算该学生在当前班级的总进度 ---
        progress_percent = 0
        bindings = db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == classroom.id).all()
        bound_course_ids = [b.course_id for b in bindings]
        
        if bound_course_ids:
            # 2. 计算分母：这些课程的总课时数
            total_lessons = db.query(CourseLesson).join(CourseChapter)\
                .filter(CourseChapter.course_id.in_(bound_course_ids))\
                .count()
            
            # 3. 计算分子：该学生在这些课程中已完成的课时数 (status=2)
            # 关联链: Progress -> Lesson -> Chapter
            finished_count = db.query(StudentLearningProgress)\
                .join(CourseLesson, StudentLearningProgress.lesson_id == CourseLesson.id)\
                .join(CourseChapter, CourseLesson.chapter_id == CourseChapter.id)\
                .filter(
                    StudentLearningProgress.student_id == student.id,
                    StudentLearningProgress.status == 2, # 已完成
                    CourseChapter.course_id.in_(bound_course_ids) # 必须是当前班级绑定的课程
                ).count()
            
            # 4. 计算百分比
            if total_lessons > 0:
                progress_percent = int((finished_count / total_lessons) * 100)
        
        students_data.append({
            "id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "student_number": student.student_number,
            "class_name": classroom.name,
            "class_id": classroom.id,
            "joined_at": enrollment.joined_at,
            "is_active": student.is_active,
            "progress": progress_percent,
            "avatar": s_avatar 
        })
        
    return {
        "total": total,
        "items": students_data
    }

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

    # 3. 待批改作业
    my_assignment_ids = db.query(ClassAssignment.id)\
        .join(Class, ClassAssignment.class_id == Class.id)\
        .filter(Class.teacher_id == current_user.id)\
        .all()
    
    # 提取为列表 [1, 2, 3]
    assign_id_list = [i[0] for i in my_assignment_ids]
    
    pending_homeworks = 0
    if assign_id_list:
        # 步骤 B: 查待批改数
        # status: 1 = 已提交(待批改), 2 = 已批改
        pending_homeworks = db.query(StudentSubmission).filter(
            StudentSubmission.assignment_id.in_(assign_id_list),
            StudentSubmission.status == 1 
        ).count()

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


# ------------------------------------------------------------------
# [教师端] 批量导入学生 (Excel)
# ------------------------------------------------------------------
@router.post("/{class_id}/students/batch")
def batch_import_students(
    class_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 权限校验
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")
    
    class_obj = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_user.id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在或无权操作")

    # 2. 读取 Excel 文件
    try:
        contents = file.file.read()
        # 使用 pandas 读取流
        df = pd.read_excel(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="文件格式错误，请上传标准的 .xlsx 文件")

    # 3. 字段映射 (Excel中文列名 -> 数据库字段)
    # 假设模板列名为：姓名, 手机号, 学号
    required_columns = ['姓名', '手机号', '学号']
    
    # 检查列名是否存在
    if not set(required_columns).issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Excel模板错误，必须包含列：{required_columns}")

    # 4. 循环处理
    success_count = 0
    errors = [] # 记录失败原因
    
    # 将 NaN 替换为空字符串，防止报错
    df = df.fillna("")

    for index, row in df.iterrows():
        row_num = index + 2 # Excel 从第2行开始是数据
        
        # 获取数据并清洗 (转为字符串并去空格)
        name = str(row['姓名']).strip()
        phone = str(row['手机号']).strip()
        student_no = str(row['学号']).strip()
        
        # 处理可能的 .0 (比如手机号被读成了浮点数 138xxx.0)
        if phone.endswith(".0"): phone = phone[:-2]
        if student_no.endswith(".0"): student_no = student_no[:-2]

        # 基础校验
        if not phone or not name:
            errors.append(f"第{row_num}行：姓名或手机号为空，已跳过")
            continue

        try:
            # --- 用户逻辑 ---
            student = db.query(User).filter(User.username == phone).first()
            
            if not student:
                # 不存在 -> 创建新用户
                hashed_password = security.get_password_hash("123456")
                student = User(
                    username=phone,
                    hashed_password=hashed_password,
                    role="student",
                    is_active=True,
                    full_name=name,
                    student_number=student_no
                )
                db.add(student)
                db.flush() # 拿到 ID
            else:
                # 已存在 -> 校验角色并更新信息
                if student.role != "student":
                    errors.append(f"第{row_num}行：手机号 {phone} 已注册为教师，无法添加")
                    continue
                # 更新姓名学号
                student.full_name = name
                student.student_number = student_no
                db.add(student)
                db.flush()

            # --- 绑定逻辑 ---
            # 检查是否已在当前班级
            existing_enroll = db.query(Enrollment).filter(
                Enrollment.student_id == student.id
            ).first()

            if existing_enroll:
                if existing_enroll.class_id == class_id:
                    # 已经在当前班，忽略，算作成功(或跳过)
                    success_count += 1
                else:
                    # 已经在别的班，报错
                    other_class = db.query(Class).filter(Class.id == existing_enroll.class_id).first()
                    c_name = other_class.name if other_class else "其他班级"
                    errors.append(f"第{row_num}行：{name} 已加入【{c_name}】，无法重复加入")
            else:
                # 未加入任何班 -> 绑定当前班
                new_enroll = Enrollment(class_id=class_id, student_id=student.id)
                db.add(new_enroll)
                success_count += 1
                
        except Exception as e:
            # 捕获单行错误，防止打断整个循环
            errors.append(f"第{row_num}行：处理异常 - {str(e)}")
            continue

    # 5. 统一提交事务
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="数据库提交失败")

    return {
        "total_processed": len(df),
        "success_count": success_count,
        "error_count": len(errors),
        "error_logs": errors
    }



# ------------------------------------------------------------------
# [教师端] 编辑学生信息 (含转班功能)
# ------------------------------------------------------------------
@router.put("/students/{student_id}")
def update_student_info(
    student_id: int,
    student_in: class_schemas.StudentUpdateFromTeacher,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 查找学生
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    # 2. 更新基础信息
    student.full_name = student_in.full_name
    student.student_number = student_in.student_number
    
    # 如果修改了手机号(username)，需要查重
    if student.username != student_in.username:
        exists = db.query(User).filter(User.username == student_in.username).first()
        if exists:
            raise HTTPException(status_code=400, detail="该手机号已被其他账号使用")
        student.username = student_in.username

    # 3. 处理转班逻辑 (如果传入的 class_id 变了)
    # 先找到该学生当前在老师名下的 Enrollment
    current_enrollment = db.query(Enrollment).join(Class).filter(
        Enrollment.student_id == student_id,
        Class.teacher_id == current_user.id
    ).first()

    if current_enrollment and current_enrollment.class_id != student_in.class_id:
        # 校验目标班级是否属于该老师
        target_class = db.query(Class).filter(Class.id == student_in.class_id, Class.teacher_id == current_user.id).first()
        if not target_class:
            raise HTTPException(status_code=403, detail="目标班级不存在或无权操作")
        
        # 修改关联
        current_enrollment.class_id = student_in.class_id

    db.add(student)
    if current_enrollment:
        db.add(current_enrollment)
        
    db.commit()
    return {"message": "修改成功"}




# ------------------------------------------------------------------
# 学生端] 获取我加入的班级及课程信息
# 接口地址: GET /api/v1/classes/my-enrolled-classes
# ------------------------------------------------------------------
@router.get("/my-enrolled-classes", response_model=List[class_schemas.ClassOut])
def read_student_classes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 身份校验：虽然老师也能调，但业务上主要是给学生的
    # if current_user.role != "student":
    #     return [] 
    
    # 2. 查询 Enrollment 表，找到该用户 ID 对应的所有选课记录
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    
    results = []
    
    for enrollment in enrollments:
        # 3. 通过外键关系直接获取班级对象
        cls = enrollment.classroom
        
        if not cls:
            continue

        real_student_count = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()

        t_name = "未知教师"
        t_title = "讲师"
        t_avatar = None

        t_intro = None
        t_school = None
        t_college = None

        if cls.teacher:
            # 优先从 profile 取
            if cls.teacher.teacher_profile:
                profile = cls.teacher.teacher_profile
                if profile.real_name:
                    t_name = profile.real_name
                if profile.title:
                    t_title = profile.title
                # ✅ 获取头像路径
                t_avatar = profile.avatar
                t_intro = profile.intro
                t_school = profile.school
                t_college = profile.college
            else:
                t_name = cls.teacher.username

        # 4. 查询该班级绑定的课程包 (为了获取课程名和封面)
        bindings = db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == cls.id).all()
        
        c_names = []
        c_ids = []
        c_public_ids = []
        c_covers = []
        c_progress = []
        
        # 逻辑：优先显示课程的封面，如果没绑课，才显示班级封面
        display_cover = cls.cover_image 
        
        for binding in bindings:
            course_obj = db.query(Course).filter(Course.id == binding.course_id).first()
            if course_obj:
                c_names.append(course_obj.name)
                c_ids.append(course_obj.id)
                c_public_ids.append(encode_id(course_obj.id))
                c_covers.append(course_obj.cover) 
                # 简单的封面逻辑：取第一个绑定的课程封面作为展示
                if not display_cover and course_obj.cover:
                    display_cover = course_obj.cover

                # ========== ✅ 计算进度核心逻辑 ==========
                # 1. 计算该课程的总课时数 (Course -> Chapter -> Lesson)
                total_lessons = db.query(CourseLesson).join(CourseChapter)\
                    .filter(CourseChapter.course_id == course_obj.id).count()
                
                # 2. 计算该学生已完成的课时数 (Status = 2)
                # 关联路径: StudentLearningProgress -> CourseLesson -> CourseChapter -> Course
                finished_count = db.query(StudentLearningProgress)\
                    .join(CourseLesson, StudentLearningProgress.lesson_id == CourseLesson.id)\
                    .join(CourseChapter, CourseLesson.chapter_id == CourseChapter.id)\
                    .filter(
                        CourseChapter.course_id == course_obj.id,
                        StudentLearningProgress.student_id == current_user.id,
                        StudentLearningProgress.status == 2 # 2代表已完成
                    ).count()
                
                # 3. 计算百分比
                if total_lessons > 0:
                    percent = int((finished_count / total_lessons) * 100)
                else:
                    percent = 0
                
                c_progress.append(percent)


        results.append({
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "teacher_id": cls.teacher_id,
            "cover_image": display_cover, 
            "start_date": cls.start_date,
            "end_date": cls.end_date,
            "created_at": cls.created_at,
            
            "student_count": real_student_count, 
            "bound_course_names": c_names,
            "bound_course_ids": c_ids,
            "bound_course_public_ids": c_public_ids,
            "bound_course_covers": c_covers,
            "bound_course_progress": c_progress,
            "teacher_name": t_name,
            "teacher_title": t_title,
            "teacher_avatar": t_avatar,
            "teacher_intro": t_intro,
            "teacher_school": t_school,
            "teacher_college": t_college
        })
        
    return results


# ------------------------------------------------------------------
# [学生端] 获取同班同学列表
# ------------------------------------------------------------------
@router.get("/{class_id}/classmates", response_model=List[class_schemas.ClassmateOut])
def read_classmates(
    class_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 安全校验：调用者必须是该班级的学生
    is_member = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.student_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="你不是该班级的成员，无法查看同学列表")

    # 2. 查询该班级的所有学生
    # 联表查询: Enrollment -> User
    enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
    
    results = []
    for enrollment in enrollments:
        student = enrollment.student
        
        # 构造数据显示名字
        display_name = student.full_name if student.full_name else student.username
        
        # 构造头像
        display_avatar = None
        if student.student_profile:
            display_avatar = student.student_profile.avatar

        # 数据对象
        item = {
            "name": display_name,
            "avatar": display_avatar 
        }

        # ✅ 核心修改：排序逻辑
        # 如果是当前登录用户，插入到列表最前面 (索引0)
        if student.id == current_user.id:
            # 可选：给自己的名字加个标记，比如 "张三 (我)"
            # item["name"] = f"{display_name} (我)" 
            results.insert(0, item)
        else:
            # 其他人追加到后面
            results.append(item)
        
    return results


# -----------------------------------------------------------
# 获取教师日程 (未来7天的考试和作业截止)
# -----------------------------------------------------------
@router.get("/schedule", response_model=List[class_schemas.ScheduleItem])
def read_teacher_schedule(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    now = datetime.now()
    future = now + timedelta(days=7) # 只看未来7天
    
    schedule_list = []

    # 1. 查即将开始或结束的考试
    exams = db.query(Exam).filter(
        Exam.teacher_id == current_user.id,
        Exam.start_time >= now, # 还没开始的
        # 或者正在进行但还没结束的也可以查，这里简单处理查未来的开始时间
        Exam.start_time <= future
    ).all()
    
    for e in exams:
        # 获取关联班级名(取第一个)
        c_name = "多班级"
        if e.class_ids:
            cls = db.query(Class).filter(Class.id == e.class_ids[0]).first()
            if cls: c_name = cls.name
            
        schedule_list.append({
            "id": e.id,
            "type": "exam",
            "title": e.title,
            "time": e.start_time,
            "class_name": c_name,
            "status": "即将开考"
        })

    # 2. 查即将截止的作业
    # 查找该老师发布的所有作业，且截止时间在未来7天内
    homeworks = db.query(ClassAssignment).join(Class).filter(
        Class.teacher_id == current_user.id,
        ClassAssignment.deadline >= now,
        ClassAssignment.deadline <= future
    ).all()

    for hw in homeworks:
        schedule_list.append({
            "id": hw.id,
            "type": "homework",
            "title": hw.title,
            "time": hw.deadline,
            "class_name": hw.classroom.name, # ClassAssignment 关联了 classroom
            "status": "即将截止"
        })

    # 3. 按时间排序 (最近的在前)
    schedule_list.sort(key=lambda x: x["time"])
    
    return schedule_list[:5] # 只返回最近5条