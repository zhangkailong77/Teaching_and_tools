from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.base_class import Base


class SchoolConfig(Base):
    __tablename__ = "school_config"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(String(64), unique=True, nullable=False, index=True)
    school_name = Column(String(120), nullable=False)
    sso_enabled = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
