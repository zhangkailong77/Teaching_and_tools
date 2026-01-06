from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
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
    task_count = Column(Integer, default=0)
    total_duration = Column(Integer, default=0)
    lesson_count = Column(Integer, default=0)
    course_type = Column(String(50), default="实训课程")
    chapters = relationship("CourseChapter", back_populates="course", order_by="CourseChapter.sort_order", cascade="all, delete-orphan")

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


# ------------------------------------------------------------------
# 4. 课程章节 (CourseChapter)
# ------------------------------------------------------------------
class CourseChapter(Base):
    __tablename__ = "course_chapters"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # 关联：所属课程
    course = relationship("Course", back_populates="chapters")
    
    # 关联：包含的课时 (自动按 sort_order 排序)
    lessons = relationship("CourseLesson", back_populates="chapter", order_by="CourseLesson.sort_order", cascade="all, delete-orphan")


# ------------------------------------------------------------------
# 5. 课时资源 (CourseLesson)
# ------------------------------------------------------------------
class CourseLesson(Base):
    __tablename__ = "course_lessons"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("course_chapters.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    resource_type = Column(String(20), nullable=False) # pdf, ppt, video
    file_url = Column(String(500), nullable=True)      # 文件路径
    
    duration = Column(String(50), nullable=True)       # 时长/页数
    is_free = Column(Boolean, default=False)           # 是否试看
    
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # 关联：所属章节
    chapter = relationship("CourseChapter", back_populates="lessons")


# 6. 学习进度表
class StudentLearningProgress(Base):
    __tablename__ = "student_learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("course_lessons.id"), nullable=False)
    
    status = Column(Integer, default=0) # 0:未开始, 1:进行中, 2:已完成
    last_position = Column(Integer, default=1) # 阅读到的页码
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())