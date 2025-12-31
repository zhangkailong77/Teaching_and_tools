from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# 1. 课程资源包 (Course)
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)       # 课程名称
    cover = Column(String(255), nullable=True)       # 封面图
    intro = Column(Text, nullable=True)              # 简介
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 创建者
    created_at = Column(DateTime, default=func.now())

    # 关联：创建者 (User)
    # 注意：这里使用字符串 "User" 是为了防止循环引用
    owner = relationship("User", back_populates="owned_courses")
    
    # 关联：绑定关系 (ClassCourseBinding)
    bindings = relationship("ClassCourseBinding", back_populates="course")


# 2. 班级-课程 绑定表 (ClassCourseBinding)
class ClassCourseBinding(Base):
    __tablename__ = "class_course_bindings"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    bound_at = Column(DateTime, default=func.now())

    # 关联：班级 (Class)
    classroom = relationship("Class", back_populates="course_bindings")
    
    # 关联：课程 (Course)
    course = relationship("Course", back_populates="bindings")


# 3. 教师购课权限表 (新增)
class TeacherCourseAccess(Base):
    __tablename__ = "teacher_course_access"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())