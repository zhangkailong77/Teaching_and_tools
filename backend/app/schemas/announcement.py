# backend/app/schemas/announcement.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 1. 创建公告请求体
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    type: str = "normal"      # urgent, normal, course, tip
    target_type: str = "class" # all, class
    class_ids: List[int] = [] # 如果 target_type=class，这里必填
    is_pinned: int = 0
    expires_at: Optional[datetime] = None

# 2. 公告列表响应体 (简略版)
class AnnouncementListOut(BaseModel):
    id: int
    title: str
    type: str
    is_pinned: int = 0
    created_at: datetime
    publisher_name: str
    
    # 统计信息
    read_count: int = 0
    total_count: int = 0
    
    # 学生端特有
    is_read: bool = False 

    content: str 

    class Config:
        from_attributes = True

# 3. 公告详情响应体
class AnnouncementDetail(AnnouncementListOut):
    content: str
    target_classes: List[str] = [] # 发布给了哪些班级