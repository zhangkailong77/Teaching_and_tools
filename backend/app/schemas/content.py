from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.utils.hash import encode_id

# 基础字段
class CourseBase(BaseModel):
    name: str
    cover: Optional[str] = None
    intro: Optional[str] = None
    task_count: int = 0
    total_duration: int = 0
    lesson_count: int = 0
    course_type: str = "实训课程"

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
    created_at: datetime
    public_id: Optional[str] = None

    is_locked: bool = False 

    class Config:
        from_attributes = True



# ✅ 新增：进度更新参数
class ProgressUpdate(BaseModel):
    lesson_id: int
    status: int      # 1 or 2
    last_position: int

# ✅ 新增：进度返回结构 (嵌套在 lesson 里)
class LessonProgress(BaseModel):
    status: int = 0      # 0/1/2
    last_position: int = 1



# =======================
# 作业模板 (Course Task) 相关
# =======================
class CourseTaskBase(BaseModel):
    title: str
    content: Optional[str] = None
    sort_order: int = 0

# 返回给前端的数据结构
class CourseTaskOut(CourseTaskBase):
    id: int
    course_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =======================
# 作业发布管理 (Task Publish)
# =======================

# 1. 单个班级的发布状态 (Response)
class ClassTaskStatus(BaseModel):
    class_id: int
    class_name: str
    deadline: Optional[datetime] = None
    is_published: bool = False # 是否已发布

# 2. 提交发布的配置项 (Request)
class TaskPublishConfig(BaseModel):
    class_id: int
    deadline: Optional[datetime] = None

# 3. 批量提交请求体
class TaskPublishRequest(BaseModel):
    configs: List[TaskPublishConfig]