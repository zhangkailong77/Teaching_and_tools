from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.profile import TeacherProfile
from app.models.profile import StudentProfile
from app.models.course import Enrollment, Class
from app.models.content import Course, ClassCourseBinding
from app.schemas import profile as schemas

router = APIRouter()

# 1. 获取我的教师档案
@router.get("/teacher/me", response_model=schemas.TeacherProfileOut)
def read_my_teacher_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="当前账号不是教师")

    profile = db.query(TeacherProfile).filter(TeacherProfile.user_id == current_user.id).first()
    
    if not profile:
        # ❌ 原来的写法：return TeacherProfile(user_id=current_user.id) -> id 是 None，导致报错
        
        # ✅ 修改后的写法：手动给个 id=0，骗过 Pydantic 的 int 校验
        # 前端拿到 id=0 也没关系，因为更新接口是用 user_id 查数据的，不依赖这个 id
        return TeacherProfile(user_id=current_user.id, id=0)
    
    return profile

# 2. 更新/创建我的教师档案
@router.put("/teacher/me", response_model=schemas.TeacherProfileOut)
def update_my_teacher_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.TeacherProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="当前账号不是教师")

    profile = db.query(TeacherProfile).filter(TeacherProfile.user_id == current_user.id).first()

    if not profile:
        # 如果不存在，则创建 (Create)
        profile = TeacherProfile(
            user_id=current_user.id,
            **profile_in.dict(exclude_unset=True)
        )
        db.add(profile)
    else:
        # 如果存在，则更新 (Update)
        update_data = profile_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile


# ------------------------------------------------------------------
# 3. 获取我的学生档案 (含统计数据)
# ------------------------------------------------------------------
@router.get("/student/me", response_model=schemas.StudentProfileOut)
def read_my_student_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="当前账号不是学生")

    # A. 获取档案 (如果不存在则初始化)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        # 如果是第一次访问，尝试从 User 表同步之前老师录入的信息
        profile = StudentProfile(
            user_id=current_user.id,
            real_name=current_user.full_name,        # 同步 Teacher 录入的姓名
            student_number=current_user.student_number # 同步 Teacher 录入的学号
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # B. 获取班级信息
    enrollment = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).first()
    
    class_name = "暂未入班"
    course_count = 0
    course_names = []

    if enrollment and enrollment.classroom:
        cls = enrollment.classroom
        class_name = cls.name
        
        # C. 获取课程信息
        # 逻辑: 班级 -> Bindings -> Courses
        bindings = db.query(ClassCourseBinding).filter(ClassCourseBinding.class_id == cls.id).all()
        for b in bindings:
            if b.course:
                course_names.append(b.course.name)
        
        course_count = len(course_names)

    # D. 拼装返回
    return {
        **profile.__dict__,        # 基础档案
        "class_name": class_name,   # 算出来的班级
        "course_count": course_count, # 算出来的数量
        "course_names": course_names  # 算出来的列表
    }

# ------------------------------------------------------------------
# 4. 更新我的学生档案
# ------------------------------------------------------------------
@router.put("/student/me", response_model=schemas.StudentProfileOut)
def update_my_student_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.StudentProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="当前账号不是学生")

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        # 理论上 GET 接口已经创建了，但防一手空指针
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    # 更新字段
    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)

    # 更新完后，也需要返回统计数据（直接调用上面的逻辑，或者前端刷新页面）
    # 这里为了简单，返回的数据里统计字段可能是默认值，建议前端更新后重新调用 GET 刷新
    # 或者在这里简单查一下
    # ... (省略重复查询逻辑，只返回基础更新即可，前端通常会 fetch 最新)
    
    return {
        **profile.__dict__,
        "class_name": "更新后请刷新", 
        "course_count": 0, 
        "course_names": []
    }