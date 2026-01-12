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