"""
平台 Schema (Pydantic 验证)
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlatformBase(BaseModel):
    """平台基础 Schema"""
    name: str
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


class PlatformCreate(PlatformBase):
    """创建平台 Schema"""
    pass


class PlatformUpdate(BaseModel):
    """更新平台 Schema"""
    name: Optional[str] = None
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
