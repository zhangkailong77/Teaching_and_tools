from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, practice

api_router = APIRouter()

# 挂载认证路由 (登录/注册)，前缀 /auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 挂载用户路由 (个人信息)，前缀 /users
api_router.include_router(users.router, prefix="/users", tags=["users"])

# --- 2. 挂载实训路由 ---
api_router.include_router(practice.router, prefix="/practice", tags=["practice"])