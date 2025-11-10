"""
栏目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Section(Base):
    """栏目模型 - 用于区分文章类型"""
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 该栏目是否需要关联平台 (如验证栏目需要，但百科、指南等不需要)
    requires_platform = Column(Boolean, default=False, nullable=False)
    
    # 显示顺序
    sort_order = Column(Integer, default=0)
    
    # 是否激活
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    articles = relationship("Article", back_populates="section")
    categories = relationship("Category", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Section(id={self.id}, name={self.name}, requires_platform={self.requires_platform})>"
