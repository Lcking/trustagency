"""
文章模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # 栏目和分类
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    tags = Column(String(500), nullable=True)  # 逗号分隔

    # 作者和平台
    author_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=True)  # 改为可选

    # 发布状态
    is_published = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False)

    # SEO
    seo_title = Column(String(80), nullable=True)
    meta_description = Column(String(160), nullable=True)
    meta_keywords = Column(String(500), nullable=True)

    # 统计
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # 关系
    author = relationship("AdminUser", back_populates="articles")
    section = relationship("Section", back_populates="articles")  # 新增
    category_obj = relationship("Category", back_populates="articles", foreign_keys=[category_id])
    platform = relationship("Platform", back_populates="articles")

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title}, author_id={self.author_id})>"

    # 便于接口序列化输出分类名称（优先使用外键关系名称，其次向后兼容的字符串字段）
    @property
    def category_name(self) -> str | None:
        """获取分类名称"""
        try:
            if self.category_obj and getattr(self.category_obj, 'name', None):
                return self.category_obj.name
        except Exception:
            pass
        return None
