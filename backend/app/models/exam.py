from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# ==========================================
# 1. 题库表 (Question)
# ==========================================
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 题型: single(单选), multiple(多选), judge(判断), blank(填空), essay(简答)
    type = Column(String(20), nullable=False, index=True)
    
    # 题干 (富文本)
    content = Column(Text, nullable=False)
    
    # 选项 (仅选择题使用) -> 存 JSON: [{"label":"A", "text":"..."}, {"label":"B", "text":"..."}]
    options = Column(JSON, nullable=True)
    
    # 标准答案 -> 单选存字符串 "A"，多选存数组 ["A","B"]，填空存关键词数组
    answer = Column(JSON, nullable=False)
    
    # 解析
    analysis = Column(Text, nullable=True)
    
    # 难度: 1=易, 2=中, 3=难
    difficulty = Column(Integer, default=1)
    
    # 标签/知识点 -> 存 JSON: ["第一章", "计算机基础"]
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    teacher = relationship("User", backref="questions")


# ==========================================
# 2. 试卷主表 (Exam)
# ==========================================
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 考试配置
    start_time = Column(DateTime, nullable=True) # 允许开始时间
    end_time = Column(DateTime, nullable=True)   # 截止时间
    duration = Column(Integer, default=60)       # 考试时长(分钟)
    pass_score = Column(Integer, default=60)     # 及格分
    total_score = Column(Integer, default=100)   # 总分 (由题目累加或随机生成指定)
    
    # 状态: 0=草稿, 1=已发布, 2=已结束
    status = Column(Integer, default=0)
    
    # 发布给哪些班级 (存班级ID数组: [1, 2])
    class_ids = Column(JSON, nullable=True)
    
    # 组卷模式: 1=手动, 2=随机
    mode = Column(Integer, default=1)
    
    # 随机组卷的策略配置 (仅 mode=2 时有效)
    # 格式: [{"type":"single", "count":10, "score":2, "tags":["物流"], "diff":1}, ...]
    random_config = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan") # 稍后定义

# ==========================================
# 3. 试卷-题目关联表 (ExamQuestion)
# ==========================================
class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # 该题目在本试卷中的分值 (覆盖题库默认分值)
    score = Column(Integer, default=2)
    
    # 题目排序 (手动组卷用)
    sort_order = Column(Integer, default=0)

    # 关联
    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question")


# ==========================================
# 4. 考试记录表 (ExamRecord)
# ==========================================
class ExamRecord(Base):
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间记录
    start_time = Column(DateTime, default=func.now()) # 开始答题时间
    submit_time = Column(DateTime, nullable=True)     # 交卷时间
    
    # 状态: 0=进行中, 1=已提交(待批改), 2=已批改(完成)
    status = Column(Integer, default=0)
    
    # 分数统计
    objective_score = Column(Integer, default=0) # 客观题得分(系统自动判分)
    subjective_score = Column(Integer, default=0) # 主观题得分(老师人工判分)
    total_score = Column(Integer, default=0)      # 总得分
    
    # 监考数据
    cheat_count = Column(Integer, default=0) # 切屏次数/作弊嫌疑记录
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    exam = relationship("Exam", backref="records")
    student = relationship("User", foreign_keys=[student_id])
    answers = relationship("ExamAnswer", back_populates="record", cascade="all, delete-orphan")

# ==========================================
# 5. 学生答题明细表 (ExamAnswer)
# ==========================================
class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("exam_records.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # 学生填写的答案 (单选:"A", 多选:["A","B"], 填空/简答: "文本内容")
    answer_content = Column(JSON, nullable=True)
    
    # 判分结果
    is_correct = Column(Boolean, nullable=True) # 是否正确 (主观题初始为None)
    score = Column(Integer, default=0)           # 该题实得分
    
    # 老师评价
    teacher_feedback = Column(Text, nullable=True)

    # 关联
    record = relationship("ExamRecord", back_populates="answers")
    question = relationship("Question")