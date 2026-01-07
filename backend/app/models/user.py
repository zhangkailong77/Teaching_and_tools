from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    # 这里的字段必须对应前端的 UserInfo 需求，也要对应 MySQL 的列
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False) # 用户名
    hashed_password = Column(String(100), nullable=False)                  # 加密后的密码
    role = Column(String(20), default="student", nullable=False)           # 角色: student / teacher
    is_active = Column(Boolean, default=True)                              # 是否激活
    created_at = Column(DateTime, default=func.now())                      # 注册时自动写入当前数据库时间
    last_login = Column(DateTime, nullable=True)                           # 初始为空，登录时更新
    comfyui_port = Column(Integer, nullable=True, unique=True)             # ComfyUI 端口
    full_name = Column(String(50), nullable=True)      # 真实姓名
    student_number = Column(String(30), nullable=True) # 学号

    # 关联关系
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)
    teaching_classes = relationship("Class", back_populates="teacher")
    enrollments = relationship("Enrollment", back_populates="student")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    owned_courses = relationship("Course", back_populates="owner")
    submissions = relationship("StudentSubmission", back_populates="student")