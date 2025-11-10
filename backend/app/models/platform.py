"""
交易平台模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Platform(Base):
    """交易平台模型"""
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    rating = Column(Float, default=0.0, nullable=False)  # 0-5 star
    rank = Column(Integer, nullable=True, index=True)  # 排名

    # 交易相关
    min_leverage = Column(Float, default=1.0, nullable=False)
    max_leverage = Column(Float, default=100.0, nullable=False)
    commission_rate = Column(Float, default=0.0, nullable=False)  # 0.001 = 0.1%
    is_regulated = Column(Boolean, default=False)

    # 链接和媒体
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)

    # 状态
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    articles = relationship("Article", back_populates="platform", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Platform(id={self.id}, name={self.name}, rank={self.rank})>"
