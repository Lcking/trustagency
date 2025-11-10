"""
管理员用户模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class AdminUser(Base):
    """管理员用户模型"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_superadmin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 关系
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    ai_tasks = relationship("AIGenerationTask", back_populates="creator", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username={self.username}, email={self.email})>"
