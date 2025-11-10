"""
栏目相关的 Pydantic 模型
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SectionBase(BaseModel):
    """栏目基础信息"""
    name: str
    slug: str
    description: Optional[str] = None
    requires_platform: bool = False
    sort_order: int = 0
    is_active: bool = True


class SectionCreate(SectionBase):
    """创建栏目"""
    pass


class SectionUpdate(BaseModel):
    """更新栏目"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    requires_platform: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class SectionResponse(SectionBase):
    """栏目响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    category_count: int = 0  # 栏目下的分类数

    class Config:
        from_attributes = True


class SectionListResponse(BaseModel):
    """栏目列表响应"""
    data: list[SectionResponse]
    total: int

    class Config:
        from_attributes = True
