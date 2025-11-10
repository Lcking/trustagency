"""
管理员 Schema (Pydantic 验证)
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, TypeVar, Generic, List
from datetime import datetime

# 分页泛型
T = TypeVar("T")

class PaginationResponse(BaseModel, Generic[T]):
    """分页响应 Schema"""
    total: int
    skip: int
    limit: int
    items: List[T]


class StatsResponse(BaseModel):
    """仪表板统计 Schema"""
    platforms_count: int
    articles_count: int
    published_articles: int
    active_tasks: int
    total_views: int


# ==================== AdminUser Schema ====================

class AdminBase(BaseModel):
    """管理员基础 Schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class AdminCreate(AdminBase):
    """创建管理员 Schema"""
    password: str


class AdminUpdate(BaseModel):
    """更新管理员 Schema"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superadmin: Optional[bool] = None


class AdminUserResponse(AdminBase):
    """管理员响应 Schema"""
    id: int
    is_active: bool
    is_superadmin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminUserCreate(AdminBase):
    """创建管理员用户 Schema"""
    password: str
    is_superadmin: bool = False


class AdminUserUpdate(BaseModel):
    """更新管理员用户 Schema"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superadmin: Optional[bool] = None


class AdminLogin(BaseModel):
    """管理员登录 Schema"""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """管理员登录响应 Schema"""
    access_token: str
    token_type: str
    user: AdminUserResponse


# ==================== Platform Schema ====================

class PlatformResponse(BaseModel):
    """平台响应 Schema"""
    id: int
    name: str
    description: Optional[str] = None
    rating: float
    rank: Optional[int] = None
    min_leverage: float
    max_leverage: float
    commission_rate: float
    is_regulated: bool
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlatformCreate(BaseModel):
    """创建平台 Schema"""
    name: str
    description: Optional[str] = None
    rating: float = 0.0
    rank: Optional[int] = None
    min_leverage: float = 1.0
    max_leverage: float = 100.0
    commission_rate: float = 0.0
    is_regulated: bool = False
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False


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
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


# ==================== Article Schema ====================

class ArticleResponse(BaseModel):
    """文章响应 Schema"""
    id: int
    title: str
    slug: str
    content: str
    summary: Optional[str] = None
    category: str
    tags: Optional[str] = None
    author_id: int
    platform_id: int
    is_published: bool
    is_featured: bool
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    """创建文章 Schema"""
    title: str
    slug: str
    content: str
    summary: Optional[str] = None
    category: str
    tags: Optional[str] = None
    platform_id: int
    is_published: bool = False
    is_featured: bool = False
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class ArticleUpdate(BaseModel):
    """更新文章 Schema"""
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    platform_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


# ==================== AI Task Schema ====================

class AITaskResponse(BaseModel):
    """AI 任务响应 Schema"""
    id: int
    batch_id: str
    batch_name: Optional[str] = None
    titles: Optional[dict] = None
    generated_articles: Optional[dict] = None
    status: str
    progress: int
    total_count: int
    completed_count: int
    failed_count: int
    error_message: Optional[str] = None
    error_details: Optional[dict] = None
    creator_id: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AITaskUpdate(BaseModel):
    """更新 AI 任务 Schema"""
    batch_name: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    completed_count: Optional[int] = None
    failed_count: Optional[int] = None
