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
from app.schemas.response import (
    ApiResponse,
    PaginatedResponse,
    ResponseMeta,
    PaginationMeta,
)

# 向后兼容别名
AdminResponse = AdminUserResponse
__all__ = [
    # 统一响应格式
    "ApiResponse",
    "PaginatedResponse",
    "ResponseMeta",
    "PaginationMeta",
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