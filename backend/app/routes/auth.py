"""
认证路由
"""
from datetime import timedelta
from typing import TYPE_CHECKING, Optional, NamedTuple
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser
from app.schemas import (
    AdminLogin,
    AdminCreate,
    AdminResponse,
    AdminLoginResponse,
)
from app.services.auth_service import AuthService
from app.utils.security import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/admin", tags=["authentication"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前登录用户
    
    Args:
        credentials: HTTP Bearer 认证信息
        db: 数据库会话
    
    Returns:
        用户信息
    
    Raises:
        HTTPException: 如果认证失败
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    username = verify_token(token)
    user = AuthService.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post(
    "/login",
    response_model=AdminLoginResponse,
    summary="管理员登录",
    description="使用用户名和密码登录系统，获取 JWT token",
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "username": "admin",
                            "email": "admin@example.com",
                            "full_name": "Administrator",
                            "is_active": True,
                            "is_superadmin": True,
                            "created_at": "2025-01-01T00:00:00",
                            "last_login": "2025-11-12T10:30:00"
                        }
                    }
                }
            }
        },
        401: {
            "description": "认证失败：用户名或密码错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid credentials",
                        "error_code": "CREDENTIALS_INVALID",
                        "status_code": 401
                    }
                }
            }
        },
        400: {
            "description": "请求数据验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "1 validation error for Request body",
                        "error_code": "VALIDATION_ERROR",
                        "status_code": 400
                    }
                }
            }
        }
    }
)
async def login(
    login_data: AdminLogin,
    db: Session = Depends(get_db)
) -> dict:
    """
    管理员登录端点
    
    使用用户名和密码进行身份验证，成功后返回 JWT token。Token 有效期为 24 小时。
    
    Args:
        login_data (AdminLogin): 登录数据，包含:
            - username (str): 用户名，4-20 个字符
            - password (str): 密码，至少 6 个字符
        db (Session): 数据库会话
    
    Returns:
        dict: 登录响应，包含:
            - access_token (str): JWT token，在后续请求中使用
            - token_type (str): token 类型，固定为 "bearer"
            - user (dict): 用户信息对象
    
    Raises:
        HTTPException: 
            - 401: 用户名或密码错误
            - 400: 请求数据验证失败
    
    Example:
        >>> import requests
        >>> response = requests.post(
        ...     "http://localhost:8001/api/admin/login",
        ...     json={"username": "admin", "password": "password123"}
        ... )
        >>> token = response.json()["access_token"]
    """
    # 验证用户
    user = AuthService.authenticate_user(db, login_data)
    
    # 创建 token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superadmin": user.is_superadmin,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
    }


@router.post("/register", response_model=AdminResponse)
async def register(
    admin_create: AdminCreate,
    db: Session = Depends(get_db)
):
    """
    创建新管理员
    
    Args:
        admin_create: 管理员创建数据
        db: 数据库会话
    
    Returns:
        创建的管理员信息
    """
    user = AuthService.create_admin_user(db, admin_create)
    return user


@router.get(
    "/me",
    response_model=AdminResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息",
    responses={
        200: {
            "description": "成功获取用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "full_name": "Administrator",
                        "is_active": True,
                        "is_superadmin": True,
                        "created_at": "2025-01-01T00:00:00",
                        "last_login": "2025-11-12T10:30:00"
                    }
                }
            }
        },
        401: {
            "description": "未认证或 token 过期",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Not authenticated",
                        "error_code": "UNAUTHORIZED",
                        "status_code": 401
                    }
                }
            }
        }
    }
)
async def get_me(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    返回当前登录用户的详细信息。需要在请求头中提供有效的 JWT token。
    
    Args:
        current_user (AdminUser): 当前用户（通过 Bearer token 依赖注入）
    
    Returns:
        AdminResponse: 用户信息对象，包含:
            - id (int): 用户 ID
            - username (str): 用户名
            - email (str): 邮箱
            - full_name (str): 全名
            - is_active (bool): 是否激活
            - is_superadmin (bool): 是否超级管理员
            - created_at (datetime): 创建时间
            - last_login (datetime): 最后登录时间
    
    Raises:
        HTTPException:
            - 401: 未认证或 token 过期
    
    Example:
        >>> import requests
        >>> headers = {"Authorization": "Bearer YOUR_TOKEN"}
        >>> response = requests.get(
        ...     "http://localhost:8001/api/admin/me",
        ...     headers=headers
        ... )
    """
    return current_user


@router.post("/change-password")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    改变密码
    
    Args:
        old_password: 旧密码
        new_password: 新密码
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        成功消息
    """
    AuthService.change_password(db, current_user.id, old_password, new_password)
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user)
) -> dict:
    """
    登出（客户端删除 token）
    
    Args:
        current_user: 当前用户
    
    Returns:
        成功消息
    """
    return {"message": "Logged out successfully"}
