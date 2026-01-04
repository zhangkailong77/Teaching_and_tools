from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserResponse
from app.models.user import User
# ✅ 1. 引入班级和选课模型 (用于查询学生所属班级)
from app.models.course import Enrollment, Class

router = APIRouter()

# 获取当前登录用户的信息 (需要 Token)
@router.get("/me", response_model=UserResponse)
def read_user_me(
    db: Session = Depends(deps.get_db), # ✅ 2. 注入数据库会话
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # 3. 将 SQLAlchemy 对象转换为字典，方便我们手动添加数据库里没有的字段
    user_data = current_user.__dict__

    # 4. 特殊处理：如果是学生，查询他加入的班级
    if current_user.role == "student":
        # 查询 enrollments 表
        enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
        
        if enrollments:
            class_names = []
            for e in enrollments:
                # 通过 relationship 获取班级实体 (前提是 Enrollment 模型里定义了 classroom)
                # 如果没定义，可以用 db.query(Class).filter(Class.id == e.class_id).first()
                if e.classroom:
                    class_names.append(e.classroom.name)
            
            # 将班级列表拼接成字符串，例如 "25电商1班, 25实训3班"
            user_data['class_name_display'] = ", ".join(class_names)
        else:
            user_data['class_name_display'] = "暂未加入班级"
            
    elif current_user.role == "teacher":
        # 老师可以简单显示身份，或者去查 teacher_profiles 表获取职称
        user_data['class_name_display'] = "教师"

    return user_data