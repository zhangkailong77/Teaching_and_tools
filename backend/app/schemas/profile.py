from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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


# =======================
# 学生档案 (Student Profile)
# =======================

# 1. 基础字段 (用于更新)
class StudentProfileBase(BaseModel):
    real_name: Optional[str] = None
    student_number: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    intro: Optional[str] = None

class StudentProfileUpdate(StudentProfileBase):
    pass

# 2. 返回字段 (包含统计数据)
class StudentProfileOut(StudentProfileBase):
    id: int
    user_id: int
    
    # ✅ 统计/关联数据 (数据库里没有，后端算出来的)
    class_name: Optional[str] = "暂未入班"
    course_count: int = 0
    course_names: List[str] = []

    class Config:
        from_attributes = True


# 1. 活跃度数据项
class ActivityData(BaseModel):
    date: str  # "01-15"
    count: int # 完成课时数

# 2. 公告简报
class NoticeSimple(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

# 3. 侧边栏聚合数据
class StudentSidebarData(BaseModel):
    # 学习力分析
    activity_chart: List[ActivityData]
    # 学习成就
    total_completed_lessons: int
    # 班级公告
    latest_notices: List[NoticeSimple]