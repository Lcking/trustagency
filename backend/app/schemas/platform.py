"""
平台 Schema (Pydantic 验证)
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== 详情页面的子字段Schema =====

class WhyChooseItem(BaseModel):
    """为什么选择该平台 - 单项"""
    icon: Optional[str] = None      # 图标 emoji 或 CSS class
    title: str                       # 标题: "教育优先", "安全优先" 等
    description: str                 # 描述


class TradingCondition(BaseModel):
    """交易条件项"""
    label: str                       # "最大杠杆", "最低入金" 等
    value: str                       # "1:50", "$2,000" 等


class FeeAdvantage(BaseModel):
    """费用优势项"""
    label: str                       # "交易手续费", "借款利息" 等
    value: str                       # "0.10-0.20%", "年 4-6%" 等


class AccountType(BaseModel):
    """账户类型"""
    name: str                        # "基础账户", "专业账户" 等
    description: Optional[str] = None
    suitable_for: Optional[str] = None  # "适合: 进阶初学者"
    features: Optional[List[str]] = None  # 特性列表
    leverage: Optional[str] = None   # "1:10 - 1:30"
    min_deposit: Optional[str] = None    # "$2,000"
    commission: Optional[str] = None     # "0.15%"
    cta_text: Optional[str] = None       # CTA按钮文字
    cta_link: Optional[str] = None       # CTA链接


class TradingTool(BaseModel):
    """交易工具项"""
    title: str                       # "高级图表工具"
    description: str                 # 描述


class OpeningStep(BaseModel):
    """开户步骤项"""
    step_number: int                 # 1, 2, 3
    title: str                       # "注册账户", "验证身份" 等
    description: str                 # 描述
    icon_color: Optional[str] = None # "primary", "info", "success" 等


class SecurityMeasure(BaseModel):
    """安全措施项"""
    text: str                        # "自律监管机制"


class CustomerSupportItem(BaseModel):
    """客户支持项"""
    type: str                        # "24/5 客户支持", "优先支持" 等
    description: Optional[str] = None


class LearningResource(BaseModel):
    """学习资源项"""
    title: str                       # "新手指南", "交易研讨会" 等
    description: Optional[str] = None
    link: Optional[str] = None


class PlatformBase(BaseModel):
    """平台基础 Schema"""
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = 0.0
    rank: Optional[int] = None
    min_leverage: float = 1.0
    max_leverage: float = 100.0
    commission_rate: float = 0.0
    is_regulated: bool = False
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_featured: bool = False
    # Bug001: 平台详情页字段
    introduction: Optional[str] = None
    main_features: Optional[str] = None
    fee_structure: Optional[str] = None
    account_opening_link: Optional[str] = None
    # Bug005: 卡片字段
    safety_rating: str = "B"
    founded_year: Optional[int] = None
    fee_rate: Optional[float] = None
    # Bug002: 推荐字段
    is_recommended: bool = False
    
    # ===== 新增：详情页面完整字段 =====
    overview_intro: Optional[str] = None  # 平台概览
    fee_table: Optional[str] = None  # 费用表
    why_choose: Optional[str] = None  # JSON
    trading_conditions: Optional[str] = None  # JSON
    fee_advantages: Optional[str] = None  # JSON
    account_types: Optional[str] = None  # JSON
    trading_tools: Optional[str] = None  # JSON
    opening_steps: Optional[str] = None  # JSON
    safety_info: Optional[str] = None  # 安全信息
    security_measures: Optional[str] = None  # JSON
    customer_support: Optional[str] = None  # JSON
    learning_resources: Optional[str] = None  # JSON
    platform_type: Optional[str] = None  # "专业", "新手友好" 等
    platform_badges: Optional[str] = None  # JSON: ["推荐平台", "新手友好"]
    top_badges: Optional[str] = None  # JSON: ["推荐平台", "新手友好"]: ["推荐平台", "新手友好"]


class PlatformCreate(PlatformBase):
    """创建平台 Schema"""
    pass


class PlatformUpdate(BaseModel):
    """更新平台 Schema"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    rank: Optional[int] = None
    min_leverage: Optional[float] = None
    max_leverage: Optional[float] = None
    commission_rate: Optional[float] = None
    is_regulated: Optional[bool] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    # Bug001: 平台详情页字段
    introduction: Optional[str] = None
    main_features: Optional[str] = None
    fee_structure: Optional[str] = None
    account_opening_link: Optional[str] = None
    # Bug005: 卡片字段
    safety_rating: Optional[str] = None
    founded_year: Optional[int] = None
    fee_rate: Optional[float] = None
    # Bug002: 推荐字段
    is_recommended: Optional[bool] = None
    
    # ===== 新增：详情页面完整字段 =====
    overview_intro: Optional[str] = None  # 平台概览
    fee_table: Optional[str] = None  # 费用表
    why_choose: Optional[str] = None  # JSON
    trading_conditions: Optional[str] = None  # JSON
    fee_advantages: Optional[str] = None  # JSON
    account_types: Optional[str] = None  # JSON
    trading_tools: Optional[str] = None  # JSON
    opening_steps: Optional[str] = None  # JSON
    safety_info: Optional[str] = None  # 安全信息
    security_measures: Optional[str] = None  # JSON
    customer_support: Optional[str] = None  # JSON
    learning_resources: Optional[str] = None  # JSON
    platform_type: Optional[str] = None  # "专业", "新手友好" 等
    platform_badges: Optional[str] = None  # JSON
    top_badges: Optional[str] = None  # JSON: ["推荐平台", "新手友好"]


class PlatformResponse(PlatformBase):
    """平台响应 Schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlatformListResponse(BaseModel):
    """平台列表响应 Schema"""
    data: list[PlatformResponse]
    total: int
    skip: int
    limit: int
