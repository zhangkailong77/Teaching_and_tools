from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.course import Enrollment, Class
from app.core.security import get_password_hash, verify_password
from app.schemas import user as schemas

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


@router.post("/change-password")
def change_user_password(
    password_in: schemas.UserPasswordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 验证旧密码
    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码输入错误")
    
    # 2. 验证新密码强度 (简单示例：不能为空且长度不够)
    if len(password_in.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于6位")

    # 3. 更新密码
    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "密码修改成功，下次登录请使用新密码"}


# -----------------------------------------------------------
# [教师端] 重置学生密码
# -----------------------------------------------------------
@router.put("/{user_id}/reset-password")
def reset_password_by_teacher(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 权限校验
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    # 2. 查找目标用户
    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    # 3. 双重校验：确保操作对象是学生 (防止误重置其他老师密码)
    if student.role != "student":
        raise HTTPException(status_code=400, detail="只能重置学生账号的密码")

    # 4. 执行重置
    # 默认密码设为 123456
    student.hashed_password = get_password_hash("123456")
    db.add(student)
    db.commit()
    
    return {"message": f"学生 {student.full_name or student.username} 的密码已重置为 123456"}