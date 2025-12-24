from typing import Any
from fastapi import APIRouter, Depends
from app.api import deps
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter()

# 获取当前登录用户的信息 (需要 Token)
@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return current_user