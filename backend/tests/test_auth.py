"""
认证系统测试

测试用户认证、登录、令牌管理等功能。
"""

import pytest
from fastapi import status


class TestAuthentication:
    """认证相关测试"""
    
    def test_register_success(self, client):
        """
        测试成功注册用户
        
        验证：
        - 返回 201 状态码
        - 返回用户信息（不含密码）
        - 用户可以登录
        """
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data
        assert "id" in data
    
    def test_register_duplicate_username(self, client, admin_user):
        """
        测试注册重复用户名
        
        验证：
        - 返回 400 错误
        - 返回适当的错误消息
        """
        response = client.post(
            "/api/auth/register",
            json={
                "username": "admin",
                "email": "different@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already" in response.json().get("detail", "").lower()
    
    def test_register_invalid_email(self, client):
        """
        测试使用无效邮箱注册
        
        验证：
        - 返回 422 验证错误
        """
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_weak_password(self, client):
        """
        测试注册弱密码
        
        验证：
        - 返回 422 验证错误
        """
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "123"  # 太短
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """登录相关测试"""
    
    def test_login_success(self, client, admin_user):
        """
        测试成功登录
        
        验证：
        - 返回 200 状态码
        - 返回访问令牌
        - 令牌类型为 Bearer
        """
        response = client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "admin123456"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_username(self, client):
        """
        测试使用无效用户名登录
        
        验证：
        - 返回 401 未授权
        """
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_invalid_password(self, client, admin_user):
        """
        测试使用错误密码登录
        
        验证：
        - 返回 401 未授权
        """
        response = client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, client):
        """
        测试登录缺少必需字段
        
        验证：
        - 返回 422 验证错误
        """
        response = client.post(
            "/api/auth/login",
            json={"username": "admin"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenManagement:
    """令牌管理相关测试"""
    
    def test_get_current_user(self, client, admin_token):
        """
        测试获取当前用户信息
        
        验证：
        - 返回 200 状态码
        - 返回当前用户信息
        - 包含用户的所有基本字段
        """
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
        assert "id" in data
    
    def test_get_current_user_no_token(self, client):
        """
        测试没有令牌时获取当前用户
        
        验证：
        - 返回 403 禁止访问
        """
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_current_user_invalid_token(self, client):
        """
        测试使用无效令牌获取当前用户
        
        验证：
        - 返回 403 禁止访问
        """
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_refresh_token(self, client, admin_user, admin_token):
        """
        测试刷新令牌
        
        验证：
        - 返回 200 状态码
        - 返回新的访问令牌
        - 新令牌可以使用
        """
        response = client.post(
            "/api/auth/refresh-token",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != admin_token  # 新令牌应不同
        
        # 验证新令牌有效
        new_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
        assert new_response.status_code == status.HTTP_200_OK


class TestPasswordSecurity:
    """密码安全相关测试"""
    
    def test_password_hashing(self, admin_user):
        """
        测试密码加密
        
        验证：
        - 密码已被加密
        - 明文密码不存储
        """
        # 密码应该被加密，不是明文
        assert admin_user.password_hash != "admin123456"
        assert admin_user.password_hash.startswith("$2b$")  # bcrypt 前缀
    
    def test_password_verification(self, test_db, admin_user):
        """
        测试密码验证
        
        验证：
        - 正确密码验证成功
        - 错误密码验证失败
        """
        from app.services.auth_service import AuthService
        
        # 正确密码
        assert AuthService.verify_password("admin123456", admin_user.password_hash)
        
        # 错误密码
        assert not AuthService.verify_password("wrongpassword", admin_user.password_hash)


class TestLogout:
    """登出相关测试"""
    
    def test_logout(self, client, admin_token):
        """
        测试登出
        
        验证：
        - 返回 200 状态码
        - 登出后令牌失效
        """
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # 登出后，令牌应该失效
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
