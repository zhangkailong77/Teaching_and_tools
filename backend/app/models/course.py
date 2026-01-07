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
    assignments = relationship("ClassAssignment", back_populates="classroom", cascade="all, delete-orphan")

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



# ==========================================
# 3. 班级作业实例 (ClassAssignment) - 动态任务
# ==========================================
class ClassAssignment(Base):
    __tablename__ = "class_assignments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    # 如果是引用课程模板创建的，这里存模板ID
    origin_task_id = Column(Integer, ForeignKey("course_tasks.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # 0:待发布, 1:进行中, 2:已截止
    status = Column(Integer, default=0) 
    created_at = Column(DateTime, default=func.now())

    # 关联
    classroom = relationship("Class", back_populates="assignments")
    
    # 关联：来源模板 (跨文件关联)
    origin_task = relationship("CourseTask", back_populates="class_assignments")
    
    # 关联：学生提交记录
    submissions = relationship("StudentSubmission", back_populates="assignment", cascade="all, delete-orphan")


# ==========================================
# 4. 学生提交记录 (StudentSubmission)
# ==========================================
class StudentSubmission(Base):
    __tablename__ = "student_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("class_assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=True) # 提交内容 (富文本HTML或图片URL)
    score = Column(Integer, nullable=True) # 分数
    feedback = Column(Text, nullable=True) # 评语
    
    # 0:已提交/未批改, 1:已批改, 2:被打回
    status = Column(Integer, default=0)
    
    submitted_at = Column(DateTime, default=func.now())
    graded_at = Column(DateTime, nullable=True)

    # 关联
    assignment = relationship("ClassAssignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")