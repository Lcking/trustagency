"""
统一 API 响应格式

提供标准化的 API 响应结构，便于前端统一处理
"""
from typing import TypeVar, Generic, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class ResponseMeta(BaseModel):
    """响应元数据"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    request_id: Optional[str] = None


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = 1
    page_size: int = 20
    total: int = 0
    total_pages: int = 0
    
    @classmethod
    def from_query(cls, page: int, page_size: int, total: int) -> "PaginationMeta":
        """从查询参数创建分页元数据"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages
        )


class ApiResponse(BaseModel, Generic[T]):
    """
    统一 API 响应格式
    
    Usage:
        return ApiResponse.success(data=user)
        return ApiResponse.error(message="Not found", code=404)
    """
    success: bool = True
    code: int = 200
    message: str = "OK"
    data: Optional[T] = None
    meta: Optional[ResponseMeta] = None
    
    @classmethod
    def success(
        cls, 
        data: Any = None, 
        message: str = "OK",
        code: int = 200
    ) -> "ApiResponse":
        """创建成功响应"""
        return cls(
            success=True,
            code=code,
            message=message,
            data=data,
            meta=ResponseMeta()
        )
    
    @classmethod
    def error(
        cls, 
        message: str = "Error", 
        code: int = 400,
        data: Any = None
    ) -> "ApiResponse":
        """创建错误响应"""
        return cls(
            success=False,
            code=code,
            message=message,
            data=data,
            meta=ResponseMeta()
        )
    
    @classmethod
    def not_found(cls, message: str = "Resource not found") -> "ApiResponse":
        """创建 404 响应"""
        return cls.error(message=message, code=404)
    
    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> "ApiResponse":
        """创建 401 响应"""
        return cls.error(message=message, code=401)
    
    @classmethod
    def forbidden(cls, message: str = "Forbidden") -> "ApiResponse":
        """创建 403 响应"""
        return cls.error(message=message, code=403)
    
    @classmethod
    def server_error(cls, message: str = "Internal server error") -> "ApiResponse":
        """创建 500 响应"""
        return cls.error(message=message, code=500)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应格式
    
    Usage:
        return PaginatedResponse.create(
            data=items,
            page=1,
            page_size=20,
            total=100
        )
    """
    success: bool = True
    code: int = 200
    message: str = "OK"
    data: List[T] = []
    pagination: PaginationMeta
    meta: Optional[ResponseMeta] = None
    
    @classmethod
    def create(
        cls,
        data: List[Any],
        page: int = 1,
        page_size: int = 20,
        total: int = 0,
        message: str = "OK"
    ) -> "PaginatedResponse":
        """创建分页响应"""
        return cls(
            success=True,
            code=200,
            message=message,
            data=data,
            pagination=PaginationMeta.from_query(page, page_size, total),
            meta=ResponseMeta()
        )


# 常用响应类型别名
SuccessResponse = ApiResponse[None]
ErrorResponse = ApiResponse[None]


# ============= 向后兼容的函数和类型 =============
# 这些是 platforms.py 等模块使用的旧版 API

class ListResponse(BaseModel, Generic[T]):
    """列表响应格式（向后兼容）"""
    items: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    
    class Config:
        from_attributes = True


def success_response(data: Any = None, message: str = "Success") -> dict:
    """
    创建成功响应（向后兼容函数）
    
    Args:
        data: 响应数据
        message: 成功消息
    
    Returns:
        dict: 响应字典
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }


def list_response(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20
) -> dict:
    """
    创建列表响应（向后兼容函数）
    
    Args:
        items: 项目列表
        total: 总数
        page: 当前页
        page_size: 每页大小
    
    Returns:
        dict: 响应字典
    """
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
