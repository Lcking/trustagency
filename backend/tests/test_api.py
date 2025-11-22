"""
后端API测试套件
提供基础的集成测试和单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_trustagency.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAuthentication:
    """认证测试"""
    
    def test_login_without_credentials(self, client):
        """测试无凭证登录"""
        response = client.post("/api/admin/login", json={})
        assert response.status_code == 422  # Validation error
    
    def test_login_with_invalid_credentials(self, client):
        """测试错误凭证登录"""
        response = client.post("/api/admin/login", json={
            "username": "invalid",
            "password": "invalid"
        })
        assert response.status_code == 401 or response.status_code == 400


class TestTaskMonitoring:
    """任务监控测试"""
    
    def test_task_health_without_auth(self, client):
        """测试未认证的健康检查"""
        response = client.get("/api/tasks/health")
        assert response.status_code == 401  # Not authenticated


class TestBackupSystem:
    """备份系统测试"""
    
    def test_backup_list_without_auth(self, client):
        """测试未认证的备份列表"""
        response = client.get("/api/tasks/backup/list")
        assert response.status_code == 401  # Not authenticated


class TestCacheSystem:
    """缓存系统测试"""
    
    def test_cache_stats_without_auth(self, client):
        """测试未认证的缓存统计"""
        response = client.get("/api/tasks/cache/stats")
        assert response.status_code == 401  # Not authenticated


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
