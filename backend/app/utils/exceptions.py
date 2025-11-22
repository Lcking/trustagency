"""
统一的异常处理和错误管理系统

提供：
1. 自定义异常类
2. 异常处理装饰器
3. 统一的错误响应格式
4. HTTP 异常映射

使用示例：
    from app.utils.exceptions import ResourceNotFound
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFound(resource_type="User", resource_id=user_id)
"""

from typing import Optional, Any
from fastapi import HTTPException, status
from datetime import datetime


class APIException(Exception):
    """
    基础 API 异常类
    
    所有自定义异常都应继承此类
    """
    def __init__(
        self,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        message: str = "Internal Server Error",
        details: Optional[dict] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """转换为 FastAPI HTTPException"""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "error_code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


# ==================== 具体异常类 ====================

class ValidationError(APIException):
    """数据验证失败异常"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict] = None):
        _details = {"field": field} if field else {}
        if details:
            _details.update(details)
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            details=_details,
        )


class ResourceNotFound(APIException):
    """资源不存在异常"""
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Any] = None,
        message: Optional[str] = None,
    ):
        if message is None:
            if resource_id:
                message = f"{resource_type} with ID {resource_id} not found"
            else:
                message = f"{resource_type} not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=message,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ResourceAlreadyExists(APIException):
    """资源已存在异常"""
    def __init__(
        self,
        resource_type: str,
        resource_name: Optional[str] = None,
        message: Optional[str] = None,
    ):
        if message is None:
            if resource_name:
                message = f"{resource_type} '{resource_name}' already exists"
            else:
                message = f"{resource_type} already exists"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="RESOURCE_ALREADY_EXISTS",
            message=message,
            details={"resource_type": resource_type, "resource_name": resource_name},
        )


class AuthenticationError(APIException):
    """身份验证失败异常"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            message=message,
        )


class AuthorizationError(APIException):
    """授权失败异常"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            message=message,
        )


class DuplicateResourceError(APIException):
    """重复资源异常（用于唯一字段冲突）"""
    def __init__(
        self,
        resource_type: str,
        field_name: str,
        field_value: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"{resource_type} with {field_name} '{field_value}' already exists"
        
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            message=message,
            details={
                "resource_type": resource_type,
                "field_name": field_name,
                "field_value": field_value,
            },
        )


class InvalidOperationError(APIException):
    """无效操作异常"""
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[dict] = None):
        _details = {"operation": operation} if operation else {}
        if details:
            _details.update(details)
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_OPERATION",
            message=message,
            details=_details,
        )


class ExternalServiceError(APIException):
    """外部服务错误异常"""
    def __init__(
        self,
        service_name: str,
        message: str,
        error_details: Optional[dict] = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            message=f"Error from {service_name}: {message}",
            details={"service_name": service_name, "error_details": error_details or {}},
        )


class FileOperationError(APIException):
    """文件操作异常"""
    def __init__(
        self,
        operation: str,
        filename: str,
        reason: str,
    ):
        message = f"Failed to {operation} file '{filename}': {reason}"
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="FILE_OPERATION_ERROR",
            message=message,
            details={
                "operation": operation,
                "filename": filename,
                "reason": reason,
            },
        )


class RateLimitError(APIException):
    """限流异常"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message=message,
        )


class ConfigurationError(APIException):
    """配置错误异常"""
    def __init__(self, setting_name: str, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CONFIGURATION_ERROR",
            message=f"Configuration error for '{setting_name}': {message}",
            details={"setting_name": setting_name},
        )


# ==================== 异常映射工具 ====================

def map_exception_to_http(exc: Exception) -> HTTPException:
    """
    将任何异常映射到 HTTPException
    
    Args:
        exc: 任何异常对象
    
    Returns:
        HTTPException 对象
    """
    if isinstance(exc, APIException):
        return exc.to_http_exception()
    
    elif isinstance(exc, HTTPException):
        return exc
    
    elif isinstance(exc, ValueError):
        return ValidationError(str(exc)).to_http_exception()
    
    else:
        # 对于未预期的异常，返回 500 错误
        return APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"exception_type": type(exc).__name__},
        ).to_http_exception()


# ==================== 便捷函数 ====================

def raise_resource_not_found(resource_type: str, resource_id: Optional[Any] = None):
    """便捷函数：抛出资源不存在异常"""
    raise ResourceNotFound(resource_type=resource_type, resource_id=resource_id)


def raise_already_exists(
    resource_type: str,
    resource_name: Optional[str] = None,
    field_name: Optional[str] = None,
):
    """便捷函数：抛出资源已存在异常"""
    if field_name:
        raise DuplicateResourceError(
            resource_type=resource_type,
            field_name=field_name,
            field_value=resource_name,
        )
    else:
        raise ResourceAlreadyExists(
            resource_type=resource_type,
            resource_name=resource_name,
        )


def raise_validation_error(message: str, field: Optional[str] = None):
    """便捷函数：抛出验证错误异常"""
    raise ValidationError(message=message, field=field)


def raise_authentication_error(message: str = "Authentication failed"):
    """便捷函数：抛出认证错误异常"""
    raise AuthenticationError(message=message)


def raise_authorization_error(message: str = "Insufficient permissions"):
    """便捷函数：抛出授权错误异常"""
    raise AuthorizationError(message=message)
