from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, practice, course, profile, upload, content, homework, exam, announcement

api_router = APIRouter()

# 挂载认证路由 (登录/注册)，前缀 /auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 挂载用户路由 (个人信息)，前缀 /users
api_router.include_router(users.router, prefix="/users", tags=["users"])

# --- 2. 挂载实训路由 ---
api_router.include_router(practice.router, prefix="/practice", tags=["practice"])

# --- 2. 挂载课程/班级路由 ---
api_router.include_router(course.router, prefix="/classes", tags=["classes"])

# ✅ 挂载档案路由
api_router.include_router(profile.router, prefix="/profiles", tags=["profiles"])

# ✅ 挂载上传路由
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])

# ✅ 挂载内容资源路由
api_router.include_router(content.router, prefix="/content", tags=["content"])


# ✅ 挂载作业路由
api_router.include_router(homework.router, prefix="/homeworks", tags=["homeworks"])

# ✅ 新增考试路由
api_router.include_router(exam.router, prefix="/exam", tags=["exam"])

# ✅ 新增公告路由
api_router.include_router(announcement.router, prefix="/announcements", tags=["announcements"])
