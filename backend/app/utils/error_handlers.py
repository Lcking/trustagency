"""
统一错误处理工具
提供用户友好的错误消息和详细的日志记录
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """应用基础异常类"""
    def __init__(
        self, 
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(AppError):
    """数据库操作错误"""
    def __init__(self, message: str = "数据库操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ValidationError(AppError):
    """数据验证错误"""
    def __init__(self, message: str = "数据验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ResourceNotFoundError(AppError):
    """资源未找到错误"""
    def __init__(self, resource: str = "资源", resource_id: Any = None):
        message = f"{resource}未找到"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": resource_id}
        )


class AuthenticationError(AppError):
    """认证错误"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={}
        )


class PermissionError(AppError):
    """权限错误"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details={}
        )


class AIServiceError(AppError):
    """AI服务错误"""
    def __init__(self, message: str = "AI服务调用失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


def error_response(
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None,
    log_error: bool = True
) -> JSONResponse:
    """
    创建统一格式的错误响应
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        details: 额外的错误详情
        log_error: 是否记录到日志
    
    Returns:
        JSONResponse: 格式化的错误响应
    """
    if log_error:
        logger.error(f"Error {status_code}: {message}", extra={"details": details})
    
    response_data = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if details:
        response_data["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


def handle_app_error(error: AppError) -> JSONResponse:
    """处理应用自定义错误"""
    logger.error(
        f"{type(error).__name__}: {error.message}",
        extra={"details": error.details}
    )
    
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": True,
            "message": error.message,
            "status_code": error.status_code,
            "details": error.details
        }
    )


def handle_validation_error(exc: Exception) -> JSONResponse:
    """处理Pydantic验证错误"""
    errors = []
    
    # 提取验证错误详情
    if hasattr(exc, 'errors'):
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error.get('loc', []))
            msg = error.get('msg', 'Unknown error')
            errors.append({
                "field": field,
                "message": msg
            })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "请求数据验证失败",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "errors": errors
            }
        }
    )


def handle_database_error(exc: Exception) -> JSONResponse:
    """处理数据库错误"""
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    
    # 不向用户暴露详细的数据库错误
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "数据库操作失败,请稍后重试",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )


def handle_general_error(exc: Exception) -> JSONResponse:
    """处理通用异常"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "服务器内部错误,请稍后重试",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )
