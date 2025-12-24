from sqlalchemy import Column, Integer, String, Boolean, DateTime
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