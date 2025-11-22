"""
统一的 API 响应格式

提供标准化的响应结构，确保所有 API 端点返回一致的格式。

响应格式类型：
1. SuccessResponse[T] - 成功响应（单个资源或操作结果）
2. ListResponse[T] - 列表响应（包含分页信息）
3. ErrorResponse - 错误响应
4. BulkResponse[T] - 批量操作响应

使用示例：
    from app.schemas.response import SuccessResponse, ListResponse
    from app.models import Article
    
    # 单个资源响应
    article = db.query(Article).filter(Article.id == 1).first()
    return SuccessResponse[ArticleResponse](data=ArticleResponse.from_orm(article))
    
    # 列表响应
    articles = db.query(Article).all()
    return ListResponse[ArticleResponse](
        data=[ArticleResponse.from_orm(a) for a in articles],
        total=len(articles)
    )
"""

from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Optional, Any
from datetime import datetime

# 泛型类型变量
T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """
    成功响应 - 用于单个资源或操作成功响应
    
    示例:
    {
        "code": 0,
        "message": "Success",
        "data": {...},
        "timestamp": "2025-11-21T10:30:00Z"
    }
    """
    code: int = Field(0, description="响应代码 (0 = 成功)")
    message: str = Field("Success", description="响应消息")
    data: T = Field(..., description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "Success",
                "data": {"id": 1, "name": "Example"},
                "timestamp": "2025-11-21T10:30:00Z"
            }
        }


class ListResponse(BaseModel, Generic[T]):
    """
    列表响应 - 用于分页列表响应
    
    示例:
    {
        "code": 0,
        "message": "Success",
        "data": [...],
        "pagination": {
            "total": 100,
            "page": 1,
            "page_size": 10,
            "total_pages": 10
        },
        "timestamp": "2025-11-21T10:30:00Z"
    }
    """
    code: int = Field(0, description="响应代码")
    message: str = Field("Success", description="响应消息")
    data: List[T] = Field(default_factory=list, description="数据列表")
    
    # 兼容旧格式的字段
    total: int = Field(0, description="总记录数")
    skip: int = Field(0, description="跳过的记录数")
    limit: int = Field(10, description="每页记录数")
    
    # 新格式的分页信息
    pagination: Optional[dict] = Field(None, description="分页信息")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    def __init__(self, **data):
        """初始化时自动计算分页信息"""
        super().__init__(**data)
        if self.pagination is None and self.total > 0:
            # 自动计算分页信息
            page = self.skip // max(self.limit, 1) + 1 if self.skip > 0 else 1
            total_pages = (self.total + self.limit - 1) // self.limit
            self.pagination = {
                "total": self.total,
                "page": page,
                "page_size": self.limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "Success",
                "data": [{"id": 1, "name": "Item 1"}],
                "total": 100,
                "skip": 0,
                "limit": 10,
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 10,
                    "has_next": True,
                    "has_prev": False
                },
                "timestamp": "2025-11-21T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """
    错误响应 - 用于所有错误情况
    
    示例:
    {
        "code": 404,
        "message": "Resource not found",
        "error_code": "RESOURCE_NOT_FOUND",
        "details": {},
        "timestamp": "2025-11-21T10:30:00Z"
    }
    """
    code: int = Field(..., description="HTTP 状态码")
    message: str = Field(..., description="错误消息")
    error_code: str = Field(..., description="错误代码（用于前端定位）")
    details: dict = Field(default_factory=dict, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 404,
                "message": "User with ID 123 not found",
                "error_code": "RESOURCE_NOT_FOUND",
                "details": {
                    "resource_type": "User",
                    "resource_id": 123
                },
                "timestamp": "2025-11-21T10:30:00Z"
            }
        }


class BulkResponse(BaseModel, Generic[T]):
    """
    批量操作响应 - 用于批量创建、更新、删除等操作
    
    示例:
    {
        "code": 0,
        "message": "Bulk operation completed",
        "data": {
            "succeeded": [...],
            "failed": [...],
            "total": 100,
            "success_count": 95,
            "failed_count": 5
        },
        "timestamp": "2025-11-21T10:30:00Z"
    }
    """
    code: int = Field(0, description="响应代码")
    message: str = Field("Bulk operation completed", description="响应消息")
    succeeded: List[T] = Field(default_factory=list, description="成功的项目")
    failed: List[dict] = Field(default_factory=list, description="失败的项目及原因")
    
    success_count: int = Field(0, description="成功数")
    failed_count: int = Field(0, description="失败数")
    total: int = Field(0, description="总数")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "Bulk operation completed",
                "succeeded": [{"id": 1}, {"id": 2}],
                "failed": [{"id": 3, "error": "Invalid data"}],
                "success_count": 2,
                "failed_count": 1,
                "total": 3,
                "timestamp": "2025-11-21T10:30:00Z"
            }
        }


class PaginationInfo(BaseModel):
    """分页信息"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


# ==================== 便捷函数 ====================

def success_response(
    data: Any = None,
    message: str = "Success",
    code: int = 0,
) -> SuccessResponse:
    """创建成功响应"""
    return SuccessResponse(
        code=code,
        message=message,
        data=data,
    )


def list_response(
    data: List[Any],
    total: int,
    skip: int = 0,
    limit: int = 10,
    message: str = "Success",
) -> ListResponse:
    """创建列表响应"""
    return ListResponse(
        code=0,
        message=message,
        data=data,
        total=total,
        skip=skip,
        limit=limit,
    )


def error_response(
    code: int,
    message: str,
    error_code: str,
    details: Optional[dict] = None,
) -> ErrorResponse:
    """创建错误响应"""
    return ErrorResponse(
        code=code,
        message=message,
        error_code=error_code,
        details=details or {},
    )
