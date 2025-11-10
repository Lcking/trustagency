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


@router.post("/login", response_model=AdminLoginResponse)
async def login(
    login_data: AdminLogin,
    db: Session = Depends(get_db)
) -> dict:
    """
    管理员登录
    
    Args:
        login_data: 登录数据
        db: 数据库会话
    
    Returns:
        登录响应（包含 token 和用户信息）
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


@router.get("/me", response_model=AdminResponse)
async def get_me(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户（通过依赖注入）
    
    Returns:
        当前用户信息
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
