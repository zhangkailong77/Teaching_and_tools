from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# 基础属性 (前端传过来的通用数据)
class UserBase(BaseModel):
    username: str
    role: str = "student" # 默认为学生

# 注册时专用 (需要包含密码)
class UserCreate(UserBase):
    password: str

# 响应给前端的数据 (不包含密码)
class UserResponse(UserBase):
    id: int
    is_active: bool

    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    full_name: Optional[str] = None
    class_name_display: Optional[str] = None

    class Config:
        # Pydantic V2 写法，允许从 ORM 模型读取数据
        from_attributes = True