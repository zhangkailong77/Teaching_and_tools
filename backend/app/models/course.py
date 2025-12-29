from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# 1. 班级表 (Classes)
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)       # 班级名称，如"ComfyUI 2025春季班"
    description = Column(Text, nullable=True)        # 班级描述
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 归属老师
    created_at = Column(DateTime, default=func.now()) # 创建时间
    cover_image = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # 关联关系
    teacher = relationship("User", back_populates="teaching_classes") # 关联到 User
    enrollments = relationship("Enrollment", back_populates="classroom") # 关联到 Enrollment
    course_bindings = relationship("ClassCourseBinding", back_populates="classroom")

# 2. 选课关联表 (Enrollments)
class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)   # 哪个班
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 哪个学生
    joined_at = Column(DateTime, default=func.now()) # 加入时间

    # 关联关系
    classroom = relationship("Class", back_populates="enrollments")
    student = relationship("User", back_populates="enrollments")