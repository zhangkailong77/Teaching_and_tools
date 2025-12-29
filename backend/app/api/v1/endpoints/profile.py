from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.profile import TeacherProfile
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