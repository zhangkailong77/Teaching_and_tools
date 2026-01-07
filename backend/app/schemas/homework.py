from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 1. 提交作业的数据 (Request)
class SubmissionCreate(BaseModel):
    content: str  # 富文本内容
    # 如果有附件或图片，可以在 content 里存 URL，或者单独加字段

# 2. 作业状态简报 (嵌入章节列表用)
class LessonAssignmentInfo(BaseModel):
    assignment_id: Optional[int] = None # 具体的作业实例ID
    status: str = "none" # none(未发布), pending(待做), submitted(已交), graded(已批), expired(已截止)
    deadline: Optional[datetime] = None
    score: Optional[int] = None

# 3. 作业列表项 (给左侧“作业任务”菜单用)
class AssignmentCard(BaseModel):
    id: int               # assignment_id
    title: str            # 作业标题
    course_name: str      # 所属课程
    lesson_title: str     # 所属课时
    deadline: Optional[datetime]
    status: int           # 0:未交, 1:已交, 2:已批
    score: Optional[int]
    
    class Config:
        from_attributes = True