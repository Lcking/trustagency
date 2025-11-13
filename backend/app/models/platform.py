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
    slug = Column(String(255), unique=True, index=True, nullable=False)
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

    # Bug001修复：平台详情页字段 - 平台介绍/特性/费用/开户步骤
    introduction = Column(Text, nullable=True)  # 平台介绍
    main_features = Column(Text, nullable=True)  # 主要特性（JSON格式）
    fee_structure = Column(Text, nullable=True)  # 费用结构详情（JSON格式）
    account_opening_link = Column(String(500), nullable=True)  # 开户链接
    
    # Bug005修复：卡片字段 - 安全评级
    safety_rating = Column(String(10), default='B', nullable=False)  # A/B/C/D等级
    founded_year = Column(Integer, nullable=True)  # 成立年份
    fee_rate = Column(Float, nullable=True)  # 费率（用于列表显示）
    
    # Bug002修复：推荐逻辑字段
    is_recommended = Column(Boolean, default=False, index=True)  # 是否推荐

    # ===== 新增：详情页面完整字段 =====
    # 为什么选择我们（Gamma Trader 风格）
    why_choose = Column(Text, nullable=True)  # JSON格式的"为什么选择xx平台"内容，包含4个主要优点
    
    # 交易条件和费用优势（Beta Margin 风格）
    trading_conditions = Column(Text, nullable=True)  # JSON: 交易条件列表 (最大杠杆、最低入金等)
    fee_advantages = Column(Text, nullable=True)    # JSON: 费用优势列表 (手续费、借款利息等)
    
    # 账户类型
    account_types = Column(Text, nullable=True)  # JSON: 账户类型详情 (基础、专业等)
    
    # 交易工具
    trading_tools = Column(Text, nullable=True)  # JSON: 交易工具列表
    
    # 开户步骤（模板化）
    opening_steps = Column(Text, nullable=True)  # JSON: 开户步骤 (注册、验证、入金等)
    
    # 安全与监管
    security_measures = Column(Text, nullable=True)  # JSON: 安全措施列表
    customer_support = Column(Text, nullable=True)   # JSON: 客户支持信息
    
    # 学习资源
    learning_resources = Column(Text, nullable=True)  # JSON: 学习资源链接和描述
    
    # 平台标签和分类
    platform_type = Column(String(50), nullable=True)  # 平台类型: "专业", "新手友好", "平衡", "高风险" 等
    platform_badges = Column(Text, nullable=True)      # JSON: 平台徽章 ["推荐平台", "新手友好", "零佣金"] 等

    # 状态
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    articles = relationship("Article", back_populates="platform", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Platform(id={self.id}, name={self.name}, rank={self.rank})>"
