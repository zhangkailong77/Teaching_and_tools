from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.core import security
from app.models.user import User
from app.models.course import Class, Enrollment
from app.schemas import course as schemas

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

    new_class = Class(
        name=class_in.name,
        description=class_in.description,
        teacher_id=current_user.id
    )
    db.add(new_class)
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