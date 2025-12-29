from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    real_name = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True) # '男' / '女'
    phone = Column(String(20), nullable=True)
    
    school = Column(String(100), nullable=True)  # 学校
    college = Column(String(100), nullable=True) # 学院
    title = Column(String(50), nullable=True)    # 职称
    intro = Column(Text, nullable=True)          # 简介
    
    avatar = Column(String(255), nullable=True)  # 头像
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 建立反向关联
    user = relationship("User", back_populates="teacher_profile")