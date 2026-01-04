from pydantic import BaseModel
from typing import Optional, List

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