# backend/app/models/announcement.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# 公告主表
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    
    # 紧急/常规/课程/提示
    type = Column(String(20), default="normal") 
    
    # 发布范围: all(全部班级), class(指定班级)
    target_type = Column(String(20), default="class")
    
    is_pinned = Column(Boolean, default=False)
    publisher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    status = Column(Integer, default=1) # 1正常 0已删除

    # 关联
    publisher = relationship("User", backref="published_announcements")
    targets = relationship("AnnouncementTarget", back_populates="announcement", cascade="all, delete-orphan")
    reads = relationship("AnnouncementRead", back_populates="announcement", cascade="all, delete-orphan")


# 公告-班级关联表
class AnnouncementTarget(Base):
    __tablename__ = "announcement_targets"

    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    announcement = relationship("Announcement", back_populates="targets")
    classroom = relationship("Class")

# 阅读记录表
class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"

    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime, default=func.now())

    announcement = relationship("Announcement", back_populates="reads")
    student = relationship("User")