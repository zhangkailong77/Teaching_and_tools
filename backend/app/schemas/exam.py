from pydantic import BaseModel
from typing import List, Optional, Any, Union
from datetime import datetime

# 选项的数据结构
class QuestionOption(BaseModel):
    label: str  # A, B, C, D
    text: str   # 选项内容

# 1. 创建/更新题目时的参数 (Request)
class QuestionCreate(BaseModel):
    type: str               # single, multiple, judge, blank, essay
    content: str            # 题干 HTML
    options: Optional[List[QuestionOption]] = [] # 选项列表
    answer: Any             # 答案 (可能是 str 或 list)
    analysis: Optional[str] = None
    difficulty: int = 1     # 1, 2, 3
    tags: List[str] = []    # 标签列表

# 2. 返回给前端的题目结构 (Response)
class QuestionOut(QuestionCreate):
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 3. 题目列表筛选参数
class QuestionFilter(BaseModel):
    type: Optional[str] = None
    difficulty: Optional[int] = None
    keyword: Optional[str] = None

# 4. 带有分页信息的题目列表返回 (新增)
class QuestionPagination(BaseModel):
    total: int
    items: List[QuestionOut]


# =======================
# 试卷相关 Schema
# =======================

# 1. 题目项 (用于手动组卷提交)
class ExamQuestionItem(BaseModel):
    question_id: int
    score: int = 2

# 2. 随机策略项
class RandomStrategyItem(BaseModel):
    type: str       # single/multiple...
    difficulty: int # 1/2/3
    tag: Optional[str] = None
    count: int      # 题数
    score: int      # 每题分值

# 3. 创建/更新试卷 Request
class ExamCreate(BaseModel):
    title: str
    mode: int = 1 # 1=手动, 2=随机
    
    # 手动模式必填：题目列表
    questions: List[ExamQuestionItem] = []
    
    # 随机模式必填：策略配置
    random_config: List[RandomStrategyItem] = []
    
    # 基础配置 (可选，也可以后续单独配置)
    duration: int = 60
    pass_score: int = 60
    total_score: int = 100

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    class_ids: List[int] = []

# 4. 发布配置 Request
class ExamPublish(BaseModel):
    class_ids: List[int]
    start_time: datetime
    end_time: datetime

# 5. 试卷列表 Response
class ExamListOut(BaseModel):
    id: int
    title: str
    status: int
    total_score: int
    duration: int
    question_count: int = 0 # 题目数量
    created_at: datetime
    class_names: List[str] = [] 
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 6. 试卷详情返回 (包含题目)
class ExamDetailOut(ExamListOut):
    mode: int
    duration: int
    pass_score: int
    total_score: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    class_ids: List[int] = []
    # 这里的题目需要包含原始题目信息，方便前端展示
    questions: List[Any] = [] 
    random_config: Optional[List[Any]] = []


# 7. 学生单题作答提交
class AnswerSubmit(BaseModel):
    question_id: int
    answer_content: Any # 可以是字符串或列表

# 8. 整卷提交 Request
class ExamSubmit(BaseModel):
    answers: List[AnswerSubmit]
    cheat_count: int = 0

# 9. 学生端考试列表项 Response
class StudentExamOut(BaseModel):
    id: int
    title: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: int
    total_score: int
    pass_score: int
    
    # 学生特有状态
    my_status: int = -1 # -1:未开始, 0:进行中, 1:已提交, 2:已批改
    my_score: Optional[int] = None
    
    class Config:
        from_attributes = True


# =======================
# 阅卷/成绩相关 Schemas
# =======================

# 10. 成绩看板-学生列表项
class ExamRecordListItem(BaseModel):
    id: int # record_id
    student_id: int
    student_name: str
    student_number: str
    class_name: str
    avatar: Optional[str] = None
    
    status: int          # 0进行中 1待批改 2已完成
    submit_time: Optional[datetime]
    
    objective_score: int # 客观题分
    subjective_score: int # 主观题分
    total_score: int     # 总分
    
    class Config:
        from_attributes = True

# 11. 阅卷详情-单题结构
class GradingQuestionDetail(BaseModel):
    question_id: int
    type: str
    content: str
    options: Optional[Any] = None
    
    # 关键数据
    student_answer: Any  # 学生填的
    standard_answer: Any # 标准答案 (给老师对照)
    full_score: int      # 该题满分 (来自试卷设置)
    
    # 批改状态
    earned_score: int    # 学生得分
    is_correct: Optional[bool] = None
    teacher_feedback: Optional[str] = None

# 12. 阅卷详情-完整试卷
class ExamRecordDetail(BaseModel):
    record_id: int
    student_name: str
    total_score: int
    objective_score: int
    questions: List[GradingQuestionDetail]

# 13. 提交评分 Request
class GradeItem(BaseModel):
    question_id: int
    score: int
    feedback: Optional[str] = None

class GradeSubmitRequest(BaseModel):
    items: List[GradeItem]


# 14. 题目库存查询请求
class QuestionCheckReq(BaseModel):
    type: str
    difficulty: int
    tag: Optional[str] = None # 知识点