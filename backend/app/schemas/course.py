from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

# --- 1. 班级相关 Schema ---

# 创建班级时的参数
class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    course_ids: List[int] = []

# 班级信息返回 (包含 ID 和 创建时间)
class ClassOut(ClassCreate):
    id: int
    teacher_id: int
    created_at: datetime
    # 统计信息 (可选，比如该班有多少人)
    student_count: Optional[int] = 0
    bound_course_names: List[str] = []  # 绑定的课程名称列表

    class Config:
        from_attributes = True

