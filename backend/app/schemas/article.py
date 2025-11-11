"""
文章 Schema (Pydantic 验证)
"""
from pydantic import BaseModel, root_validator
from typing import Optional
from datetime import datetime


class ArticleBase(BaseModel):
    """文章基础 Schema"""
    title: str
    content: str
    summary: Optional[str] = None
    section_id: int  # 新增: 栏目 ID
    category: Optional[str] = None  # 改为可选: 向后兼容
    category_id: Optional[int] = None  # 新增: 分类 ID (后续使用)
    tags: Optional[str] = None
    platform_id: Optional[int] = None  # 改为可选: 不是所有栏目都需要
    is_featured: bool = False
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class ArticleCreate(ArticleBase):
    """创建文章 Schema"""
    pass


class ArticleUpdate(BaseModel):
    """更新文章 Schema"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    platform_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class ArticleResponse(ArticleBase):
    """文章响应 Schema"""
    id: int
    slug: str
    section_id: int  # 新增
    author_id: int
    is_published: bool
    view_count: int
    like_count: int
    created_at: datetime
    published_at: Optional[datetime] = None
    category_name: Optional[str] = None

    @root_validator(pre=False, skip_on_failure=True)
    def _populate_category_name(cls, values):
        # 在Pydantic验证后调用，只处理转换后的值
        # 如果category_id已填充，尝试从关系对象获取category_name
        if not values.get('category_name'):
            # 如果直接有category字段，使用它
            values['category_name'] = values.get('category')
        return values

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应 Schema"""
    data: list[ArticleResponse]
    total: int
    skip: int
    limit: int
