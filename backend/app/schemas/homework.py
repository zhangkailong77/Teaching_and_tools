from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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
    course_cover: Optional[str] = None
    
    class Config:
        from_attributes = True


# =======================
# 教师端作业管理升级版
# =======================

# 1. 单个作业项 (Item)
class TeacherAssignmentItemV2(BaseModel):
    id: int
    title: str
    course_name: str
    deadline: Optional[datetime]
    stats: dict # {total, graded, submitted, unsubmitted}

# 2. 班级分组 (Group)
class ClassHomeworkGroup(BaseModel):
    class_id: int
    class_name: str
    pending_count: int # 该班级总待批改数
    assignments: List[TeacherAssignmentItemV2]

# 3. 统计看板增强版
class HomeworkStatsV2(BaseModel):
    pending_count: int
    # 饼图数据
    pie_data: dict # { submitted, graded, unsubmitted }
    # 排行榜数据
    rank_data: List[dict] # [{ class_name: "1班", rate: 85 }, ...]


# ✅ 新增：评分与批注提交模型
class GradeSubmission(BaseModel):
    score: int
    feedback: Optional[str] = None # 这是原来的“总评语”
    
    # --- 新增字段 ---
    annotated_content: Optional[str] = None # 存带有 <span> 的 HTML
    annotations: Optional[List[Dict[str, Any]]] = [] # 存 [{id:.., text:..}]