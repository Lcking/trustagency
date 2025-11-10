"""
认证业务逻辑服务
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import AdminUser
from app.schemas import AdminCreate, AdminLogin, AdminResponse
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from datetime import datetime


class AuthService:
    """认证服务"""

    @staticmethod
    def create_admin_user(db: Session, admin_create: AdminCreate) -> AdminUser:
        """
        创建管理员
        
        Args:
            db: 数据库会话
            admin_create: 管理员创建数据
        
        Returns:
            创建的管理员对象
        
        Raises:
            HTTPException: 如果用户名已存在
        """
        # 检查用户是否存在
        existing_user = db.query(AdminUser).filter(
            AdminUser.username == admin_create.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        existing_email = db.query(AdminUser).filter(
            AdminUser.email == admin_create.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 创建新用户
        hashed_password = hash_password(admin_create.password)
        admin_user = AdminUser(
            username=admin_create.username,
            email=admin_create.email,
            full_name=admin_create.full_name,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user

    @staticmethod
    def authenticate_user(db: Session, login: AdminLogin) -> AdminUser:
        """
        验证用户登录信息
        
        Args:
            db: 数据库会话
            login: 登录数据
        
        Returns:
            验证成功的用户对象
        
        Raises:
            HTTPException: 如果认证失败
        """
        user = db.query(AdminUser).filter(
            AdminUser.username == login.username
        ).first()
        
        if not user or not verify_password(login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> AdminUser:
        """
        根据用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
        
        Returns:
            用户对象或 None
        """
        return db.query(AdminUser).filter(AdminUser.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> AdminUser:
        """
        根据 ID 获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
        
        Returns:
            用户对象或 None
        """
        return db.query(AdminUser).filter(AdminUser.id == user_id).first()

    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """
        改变密码
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            是否成功
        
        Raises:
            HTTPException: 如果操作失败
        """
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid old password"
            )
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        return True

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        **update_data
    ) -> AdminUser:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            **update_data: 更新数据
        
        Returns:
            更新后的用户对象
        
        Raises:
            HTTPException: 如果用户不存在
        """
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for field, value in update_data.items():
            if value is not None:
                if field == "password":
                    setattr(user, "hashed_password", hash_password(value))
                else:
                    setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
