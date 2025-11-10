"""
Pytest 配置和共享夹具

提供测试环境设置、数据库、用户、令牌和其他测试工具。
"""

import pytest
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# 添加后端模块到路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.main import app
from app.database import Base, get_db
from app.models import AdminUser, Platform, Article, AIGenerationTask
from app.utils.security import hash_password


# ============================================================================
# 数据库配置
# ============================================================================

# 测试数据库 URL - 使用内存数据库
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """
    创建测试数据库 fixture
    
    对每个测试函数创建一个新的内存数据库，确保测试隔离。
    """
    # 创建引擎和会话
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # 将数据库会话注入到应用中
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield db
    
    # 清理
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# ============================================================================
# API 客户端
# ============================================================================

@pytest.fixture
def client(test_db):
    """
    创建 FastAPI TestClient fixture
    
    用于进行 API 测试。
    """
    return TestClient(app)


# ============================================================================
# 用户 Fixtures
# ============================================================================

@pytest.fixture
def admin_user(test_db) -> AdminUser:
    """
    创建管理员用户夹具
    """
    user = AdminUser(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123456"),
        is_superadmin=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def regular_user(test_db) -> AdminUser:
    """
    创建普通用户夹具
    """
    user = AdminUser(
        username="testuser",
        email="testuser@example.com",
        hashed_password=hash_password("TestUser123456"),
        is_superadmin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


# ============================================================================
# 认证 Token
# ============================================================================

@pytest.fixture
def admin_token(client, admin_user):
    """
    获取管理员令牌
    """
    response = client.post(
        "/api/auth/login",
        json={
            "username": admin_user.username,
            "password": "admin123456"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
def user_token(client, regular_user):
    """
    获取普通用户令牌
    """
    response = client.post(
        "/api/auth/login",
        json={
            "username": regular_user.username,
            "password": "TestUser123456"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


# ============================================================================
# 数据夹具
# ============================================================================

@pytest.fixture
def sample_platform(test_db, admin_user) -> Platform:
    """
    创建示例平台
    """
    platform = Platform(
        name="测试平台",
        url="https://test-platform.com",
        created_by=admin_user.id
    )
    test_db.add(platform)
    test_db.commit()
    test_db.refresh(platform)
    return platform


@pytest.fixture
def sample_article(test_db, admin_user, sample_platform) -> Article:
    """
    创建示例文章
    """
    article = Article(
        title="测试文章",
        slug="test-article",
        content="这是一篇测试文章",
        category="guide",
        status="published",
        platform_id=sample_platform.id,
        author_id=admin_user.id
    )
    test_db.add(article)
    test_db.commit()
    test_db.refresh(article)
    return article


@pytest.fixture
def sample_ai_task(test_db, admin_user) -> AIGenerationTask:
    """
    创建示例 AI 生成任务
    """
    task = AIGenerationTask(
        titles=["标题1", "标题2"],
        category="guide",
        status="pending",
        creator_id=admin_user.id
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task


# ============================================================================
# 辅助函数
# ============================================================================

@pytest.fixture
def assert_status_code():
    """
    断言状态码辅助函数
    """
    def _assert(response, expected_code):
        assert response.status_code == expected_code, f"Expected {expected_code}, got {response.status_code}. Response: {response.text}"
    return _assert


@pytest.fixture
def assert_json_response():
    """
    断言 JSON 响应辅助函数
    """
    def _assert(response, keys=None):
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        if keys:
            for key in keys:
                assert key in data, f"Missing key '{key}' in response"
        return data
    return _assert


# ============================================================================
# Pytest 配置
# ============================================================================

def pytest_configure(config):
    """
    配置 pytest 标记
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests as authentication tests"
    )


# ============================================================================
# 钩子函数
# ============================================================================

@pytest.fixture(autouse=True)
def reset_db(test_db):
    """
    在每个测试前重置数据库
    """
    yield
    # 测试后的清理由 test_db fixture 处理
