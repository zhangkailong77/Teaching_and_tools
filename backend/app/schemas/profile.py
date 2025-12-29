from pydantic import BaseModel
from typing import Optional

# 基础字段
class TeacherProfileBase(BaseModel):
    real_name: Optional[str] = None
    gender: Optional[str] = "保密"
    phone: Optional[str] = None
    school: Optional[str] = None
    college: Optional[str] = None
    title: Optional[str] = None
    intro: Optional[str] = None
    avatar: Optional[str] = None

# 更新时使用的 Schema (和 Base 一样，所有字段选填)
class TeacherProfileUpdate(TeacherProfileBase):
    pass

# 返回给前端的 Schema
class TeacherProfileOut(TeacherProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True