"""
Pydantic Schema 模块
"""
from app.schemas.admin import (
    AdminBase,
    AdminCreate,
    AdminUpdate,
    AdminUserResponse,
    AdminLogin,
    AdminLoginResponse,
    AdminUserCreate,
    AdminUserUpdate,
    PlatformResponse,
    PlatformCreate,
    PlatformUpdate,
    ArticleResponse,
    ArticleCreate,
    ArticleUpdate,
    AITaskResponse,
    AITaskUpdate,
    PaginationResponse,
    StatsResponse,
)

# 向后兼容别名
AdminResponse = AdminUserResponse
__all__ = [
    # Admin
    "AdminBase",
    "AdminCreate",
    "AdminUpdate",
    "AdminUserResponse",
    "AdminResponse",  # 向后兼容
    "AdminLogin",
    "AdminLoginResponse",
    "AdminUserCreate",
    "AdminUserUpdate",
    # Platform
    "PlatformResponse",
    "PlatformCreate",
    "PlatformUpdate",
    "PlatformListResponse",
    # Article
    "ArticleResponse",
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleListResponse",
    # AI Task
    "AITaskResponse",
    "AITaskUpdate",
    "AITaskListResponse",
    # Pagination & Stats
    "PaginationResponse",
    "StatsResponse",
]