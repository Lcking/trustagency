"""
分类模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Category(Base):
    """分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    section = relationship("Section", back_populates="categories")
    articles = relationship("Article", back_populates="category_obj")

    # 索引
    __table_args__ = (
        Index("idx_category_section", "section_id"),
        Index("idx_category_active", "is_active"),
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, section_id={self.section_id})>"
