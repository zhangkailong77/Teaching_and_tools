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

# 新增 Dashboard 统计模型
class DashboardStats(BaseModel):
    total_students: int      # 去重后的学生总数
    total_classes: int       # 班级总数
    pending_homeworks: int   # 待批改作业 (暂时 Mock)


# --- 2. 添加学生相关 Schema ---

# 老师添加学生时，只需要传一个手机号
class StudentAdd(BaseModel):
    username: str        # 手机号 (必填，用于登录)
    full_name: str       # 真实姓名 (必填)
    student_number: str  # 学号 (必填)

# --- 3. 学生列表展示 Schema (用于前端表格) ---
class StudentListOut(BaseModel):
    id: int                  # 学生 User ID
    username: str            # 手机号
    full_name: Optional[str] # 真实姓名
    student_number: Optional[str] # 学号
    
    class_name: str          # 所属班级名称
    class_color: Optional[str] = "#00c9a7" # 前端展示用的颜色 (后端暂给默认值)
    
    joined_at: datetime      # 加入时间
    is_active: bool          # 状态
    
    # 进度暂时 Mock，因为还没有作业系统
    progress: int = 0       

    class Config:
        from_attributes = True