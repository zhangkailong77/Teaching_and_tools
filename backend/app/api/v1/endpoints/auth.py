from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

# 1. 登录接口 (获取 Token)
@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    role: str = Form(...) 
) -> Any:
    # 验证账号密码
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password"
        )

    # 如果数据库里的角色 (user.role) 和 前端选的角色 (role) 不一致
    if user.role != role:
        raise HTTPException(
            # ❌ 修改前：status_code=status.HTTP_401_UNAUTHORIZED
            # ✅ 修改后：改为 400，避免被前端拦截器误伤
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"登录失败: 该账号不是【{role}】账号，请切换角色。"
        )

    user.last_login = datetime.now() 
    db.add(user)  # 标记为更新
    db.commit()   # 提交到数据库
    
    # 生成 Token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = security.create_access_token(
        subject={"sub": user.username, "role": user.role, "id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 2. 注册接口
# @router.post("/register", response_model=UserResponse)
# def register_user(
#     *,
#     db: Session = Depends(deps.get_db),
#     user_in: UserCreate,
# ) -> Any:
#     user = db.query(User).filter(User.username == user_in.username).first()
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this username already exists.",
#         )
#     user = User(
#         username=user_in.username,
#         hashed_password=security.get_password_hash(user_in.password),
#         role=user_in.role,
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user