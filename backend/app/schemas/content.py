from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 基础字段
class CourseBase(BaseModel):
    name: str
    cover: Optional[str] = None
    intro: Optional[str] = None

# 1. 创建课程时的参数
class CourseCreate(CourseBase):
    pass

# 2. 更新课程时的参数 (所有字段都可选)
class CourseUpdate(BaseModel):
    name: Optional[str] = None
    cover: Optional[str] = None
    intro: Optional[str] = None

# 3. 返回给前端的数据
class CourseOut(CourseBase):
    id: int
    owner_id: int
    created_at: datetime

    is_locked: bool = False 

    class Config:
        from_attributes = True