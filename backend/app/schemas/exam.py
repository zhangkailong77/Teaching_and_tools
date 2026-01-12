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