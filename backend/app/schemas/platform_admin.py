"""
平台管理编辑接口 - 用于后台管理系统
提供平台详情页面所有字段的编辑和管理功能
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== 管理编辑用的Schema =====

class PlatformEditForm(BaseModel):
    """平台编辑表单 - 包含所有可编辑字段"""
    
    # 基础信息
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    account_opening_link: Optional[str] = None
    
    # 评分和排序
    rating: Optional[float] = None
    rank: Optional[int] = None
    founded_year: Optional[int] = None
    
    # 交易参数
    min_leverage: Optional[float] = None
    max_leverage: Optional[float] = None
    commission_rate: Optional[float] = None
    fee_rate: Optional[float] = None
    
    # 状态和分类
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False
    is_recommended: Optional[bool] = False
    is_regulated: Optional[bool] = False
    platform_type: Optional[str] = None
    safety_rating: Optional[str] = None
    
    # 详情页面内容 - JSON字符串
    introduction: Optional[str] = None
    main_features: Optional[str] = None
    fee_structure: Optional[str] = None
    overview_intro: Optional[str] = None
    fee_table: Optional[str] = None
    
    why_choose: Optional[str] = None
    trading_conditions: Optional[str] = None
    fee_advantages: Optional[str] = None
    account_types: Optional[str] = None
    trading_tools: Optional[str] = None
    opening_steps: Optional[str] = None
    safety_info: Optional[str] = None
    security_measures: Optional[str] = None
    customer_support: Optional[str] = None
    learning_resources: Optional[str] = None
    platform_badges: Optional[str] = None
    top_badges: Optional[str] = None


class PlatformEditResponse(BaseModel):
    """平台编辑响应 - 包含所有字段和元数据"""
    id: int
    name: str
    slug: Optional[str]
    
    # 基础信息
    description: Optional[str]
    introduction: Optional[str]
    website_url: Optional[str]
    logo_url: Optional[str]
    account_opening_link: Optional[str]
    
    # 评分和分类
    rating: float
    rank: Optional[int]
    founded_year: Optional[int]
    platform_type: Optional[str]
    safety_rating: Optional[str]
    
    # 标志
    is_active: bool
    is_featured: bool
    is_recommended: bool
    is_regulated: bool
    platform_badges: Optional[str]
    top_badges: Optional[str]
    
    # 交易参数
    min_leverage: float
    max_leverage: float
    commission_rate: float
    fee_rate: Optional[float]
    
    # 详情页面内容
    main_features: Optional[str]
    fee_structure: Optional[str]
    overview_intro: Optional[str]
    fee_table: Optional[str]
    why_choose: Optional[str]
    trading_conditions: Optional[str]
    fee_advantages: Optional[str]
    account_types: Optional[str]
    trading_tools: Optional[str]
    opening_steps: Optional[str]
    safety_info: Optional[str]
    security_measures: Optional[str]
    customer_support: Optional[str]
    learning_resources: Optional[str]
    
    # 元数据
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlatformEditListResponse(BaseModel):
    """平台编辑列表响应"""
    items: List[Dict[str, Any]]  # 简化版本，仅包含基础信息和一些关键字段
    total: int
    
    
class FormFieldDefinition(BaseModel):
    """表单字段定义 - 用于前端动态生成表单"""
    name: str
    label: str
    type: str  # "text", "textarea", "number", "select", "json", "boolean" 等
    description: Optional[str] = None
    required: bool = False
    placeholder: Optional[str] = None
    default_value: Optional[Any] = None
    options: Optional[List[Dict[str, Any]]] = None  # 用于select类型


class PlatformEditFormDefinition(BaseModel):
    """平台编辑表单定义 - 返回给前端用于动态生成编辑表单"""
    sections: List[Dict[str, Any]]
    
    # 示例结构:
    # {
    #     "sections": [
    #         {
    #             "title": "基础信息",
    #             "fields": [
    #                 {
    #                     "name": "name",
    #                     "label": "平台名称",
    #                     "type": "text",
    #                     "required": true
    #                 },
    #                 ...
    #             ]
    #         },
    #         ...
    #     ]
    # }
