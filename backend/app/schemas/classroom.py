from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

# 基础字段
class ClassBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# 1. 创建班级 (Request)
class ClassCreate(ClassBase):
    name: str 
    course_ids: List[int] = [] # 创建时可绑定课程

# 2. 更新班级 (Request) - 用于编辑功能
class ClassUpdate(ClassBase):
    # 更新时，如果传了 course_ids，代表重置该班级的课程绑定
    course_ids: Optional[List[int]] = None

# 3. 班级信息返回 (Response)
class ClassOut(ClassBase):
    id: int
    name: str
    teacher_id: int
    created_at: datetime
    status: int = 0  # 0进行中 1已归档
    
    student_count: int = 0
    bound_course_names: List[str] = []
    # 返回已绑定的课程ID列表，方便前端回显
    bound_course_ids: List[int] = [] 
    bound_course_public_ids: List[str] = [] 
    bound_course_covers: List[Optional[str]] = [] 
    bound_course_progress: List[int] = [] 
    
    teacher_name: Optional[str] = "未设置"
    teacher_title: Optional[str] = "讲师"
    teacher_avatar: Optional[str] = None 

    teacher_intro: Optional[str] = None
    teacher_school: Optional[str] = None
    teacher_college: Optional[str] = None
    pending_count: int = 0

    class Config:
        from_attributes = True



# 通用图表数据项 { name: "班级A", value: 45, extra: [...] }
class ChartItem(BaseModel):
    name: str
    value: int
    extra: Optional[List[str]] = None # 用于存课程名列表等辅助信息


# 新增 Dashboard 统计模型
class DashboardStats(BaseModel):
    # 模块1: 学生概况
    total_students: int          # 去重后的总人数
    student_distribution: List[ChartItem] # 各班级人数分布

    # 模块3: 执教概况
    teaching_class_count: int    # 执教班级总数
    teaching_distribution: List[ChartItem] # 各班级绑定的课程数及名称

    # 模块4: 待办任务
    total_pending: int           # 总待办数
    task_distribution: Dict[str, int] # { "homework": 10, "exam": 5 }


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
    avatar: Optional[str] = None
    
    class_name: str          # 所属班级名称
    class_id: int
    class_color: Optional[str] = "#00c9a7" # 前端展示用的颜色 (后端暂给默认值)
    
    joined_at: datetime      # 加入时间
    is_active: bool          # 状态
    
    # 进度暂时 Mock，因为还没有作业系统
    progress: int = 0       

    class Config:
        from_attributes = True


# 2. 新增：更新学生信息的参数 (用于编辑弹窗)
class StudentUpdateFromTeacher(BaseModel):
    full_name: str
    student_number: str
    username: str  # 允许修改手机号
    class_id: int  # 允许转班


class ClassmateOut(BaseModel):
    name: str    # 显示真实姓名或昵称
    avatar: Optional[str] = None # 头像

    class Config:
        from_attributes = True


# ✅ 新增：日程表项
class ScheduleItem(BaseModel):
    id: int
    type: str       # 'exam' | 'homework'
    title: str
    time: datetime
    class_name: str
    status: str     # '进行中' | '即将截止'

    class Config:
        from_attributes = True