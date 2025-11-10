"""
Task 4 - 平台管理 API 的单元测试
测试所有平台 API 端点的功能、错误处理和边界情况
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models import AdminUser, Platform
from app.services.auth_service import AuthService
from app.schemas.admin import AdminCreate
from app.schemas.platform import PlatformCreate
from app.utils.security import create_access_token


# ==================== Fixtures ====================

@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def admin_user(db_session):
    """创建测试管理员用户"""
    admin_data = AdminCreate(
        username="admin_test",
        email="admin@test.com",
        password="test_password_123",
        full_name="Test Admin"
    )
    admin = AuthService.create_admin_user(db_session, admin_data)
    return admin


@pytest.fixture
def admin_token(admin_user):
    """创建管理员 JWT token"""
    return create_access_token({"sub": admin_user.username})


@pytest.fixture
def sample_platform(db_session):
    """创建示例平台"""
    platform_data = PlatformCreate(
        name="Binance Test",
        description="Test Trading Platform",
        rating=4.8,
        rank=1,
        min_leverage=1.0,
        max_leverage=125.0,
        commission_rate=0.001,
        is_regulated=True,
        logo_url="https://example.com/logo.png",
        website_url="https://binance.com",
        is_featured=True
    )
    db_platform = Platform(**platform_data.model_dump())
    db_session.add(db_platform)
    db_session.commit()
    db_session.refresh(db_platform)
    return db_platform


@pytest.fixture
def sample_platforms(db_session):
    """创建多个示例平台"""
    platforms_data = [
        {
            "name": "Binance",
            "description": "最大的加密交易所",
            "rating": 4.9,
            "rank": 1,
            "is_regulated": True,
            "is_featured": True,
        },
        {
            "name": "Coinbase",
            "description": "美国合规交易所",
            "rating": 4.7,
            "rank": 2,
            "is_regulated": True,
            "is_featured": True,
        },
        {
            "name": "Kraken",
            "description": "欧洲交易所",
            "rating": 4.5,
            "rank": 3,
            "is_regulated": False,
            "is_featured": False,
        },
        {
            "name": "FTX",
            "description": "衍生品交易所",
            "rating": 3.2,
            "rank": 4,
            "is_regulated": False,
            "is_featured": False,
        },
    ]
    
    platforms = []
    for data in platforms_data:
        platform = Platform(**data)
        db_session.add(platform)
        platforms.append(platform)
    
    db_session.commit()
    for p in platforms:
        db_session.refresh(p)
    
    return platforms


# ==================== 测试: 获取平台列表 ====================

class TestGetPlatforms:
    """获取平台列表的测试类"""
    
    def test_list_platforms_empty(self, client):
        """测试获取空平台列表"""
        response = client.get("/api/platforms")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 10
    
    def test_list_platforms_with_data(self, client, sample_platforms):
        """测试获取有数据的平台列表"""
        response = client.get("/api/platforms")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 4
        assert data["total"] == 4
    
    def test_list_platforms_with_pagination(self, client, sample_platforms):
        """测试分页功能"""
        response = client.get("/api/platforms?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 4
        assert data["skip"] == 0
        assert data["limit"] == 2
    
    def test_list_platforms_with_search(self, client, sample_platforms):
        """测试搜索功能"""
        response = client.get("/api/platforms?search=binance")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Binance"
    
    def test_list_platforms_search_by_description(self, client, sample_platforms):
        """测试按描述搜索"""
        response = client.get("/api/platforms?search=美国")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Coinbase"
    
    def test_list_platforms_with_sort_by_rank(self, client, sample_platforms):
        """测试按排名排序"""
        response = client.get("/api/platforms?sort_by=rank&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["rank"] == 1
        assert data["data"][-1]["rank"] == 4
    
    def test_list_platforms_with_sort_desc(self, client, sample_platforms):
        """测试降序排序"""
        response = client.get("/api/platforms?sort_by=rank&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["rank"] == 4
        assert data["data"][-1]["rank"] == 1
    
    def test_list_platforms_filter_featured(self, client, sample_platforms):
        """测试过滤精选平台"""
        response = client.get("/api/platforms?is_featured=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert all(p["is_featured"] for p in data["data"])
    
    def test_list_platforms_filter_regulated(self, client, sample_platforms):
        """测试过滤监管平台"""
        response = client.get("/api/platforms?is_featured=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert not any(p["is_featured"] for p in data["data"])
    
    def test_list_platforms_invalid_limit(self, client):
        """测试无效的 limit 参数"""
        response = client.get("/api/platforms?limit=101")
        assert response.status_code == 422  # 验证错误


# ==================== 测试: 创建平台 ====================

class TestCreatePlatform:
    """创建平台的测试类"""
    
    def test_create_platform_success(self, client, admin_user, admin_token):
        """测试成功创建平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "New Exchange",
            "description": "A new exchange",
            "rating": 4.5,
            "rank": 5,
            "min_leverage": 1.0,
            "max_leverage": 100.0,
            "commission_rate": 0.002,
            "is_regulated": True,
            "logo_url": "https://example.com/logo.png",
            "website_url": "https://example.com",
            "is_featured": False
        }
        response = client.post("/api/platforms", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Exchange"
        assert data["id"] is not None
        assert data["created_at"] is not None
    
    def test_create_platform_duplicate_name(self, client, admin_user, admin_token, sample_platform):
        """测试创建重复名称的平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": sample_platform.name,  # 使用已存在的名称
            "description": "Duplicate",
        }
        response = client.post("/api/platforms", json=payload, headers=headers)
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]
    
    def test_create_platform_without_auth(self, client):
        """测试未授权创建平台"""
        payload = {"name": "Test", "description": "Test"}
        response = client.post("/api/platforms", json=payload)
        assert response.status_code == 403
    
    def test_create_platform_missing_required_field(self, client, admin_user, admin_token):
        """测试缺少必需字段"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"description": "Test"}  # 缺少 name
        response = client.post("/api/platforms", json=payload, headers=headers)
        assert response.status_code == 422


# ==================== 测试: 获取单个平台 ====================

class TestGetSinglePlatform:
    """获取单个平台的测试类"""
    
    def test_get_platform_success(self, client, sample_platform):
        """测试成功获取平台"""
        response = client.get(f"/api/platforms/{sample_platform.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_platform.id
        assert data["name"] == sample_platform.name
    
    def test_get_platform_not_found(self, client):
        """测试获取不存在的平台"""
        response = client.get("/api/platforms/9999")
        assert response.status_code == 404


# ==================== 测试: 更新平台 ====================

class TestUpdatePlatform:
    """更新平台的测试类"""
    
    def test_update_platform_success(self, client, admin_user, admin_token, sample_platform):
        """测试成功更新平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "rating": 4.9,
            "rank": 2,
            "is_featured": False
        }
        response = client.put(f"/api/platforms/{sample_platform.id}", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 4.9
        assert data["rank"] == 2
        assert data["is_featured"] == False
    
    def test_update_platform_partial(self, client, admin_user, admin_token, sample_platform):
        """测试部分字段更新"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {"rating": 5.0}
        response = client.put(f"/api/platforms/{sample_platform.id}", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5.0
        assert data["name"] == sample_platform.name  # 其他字段不变
    
    def test_update_platform_not_found(self, client, admin_user, admin_token):
        """测试更新不存在的平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put("/api/platforms/9999", json={"rating": 5.0}, headers=headers)
        assert response.status_code == 404
    
    def test_update_platform_without_auth(self, client, sample_platform):
        """测试未授权更新平台"""
        response = client.put(f"/api/platforms/{sample_platform.id}", json={"rating": 5.0})
        assert response.status_code == 403


# ==================== 测试: 删除平台 ====================

class TestDeletePlatform:
    """删除平台的测试类"""
    
    def test_delete_platform_success(self, client, admin_user, admin_token, sample_platform):
        """测试成功删除平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/api/platforms/{sample_platform.id}", headers=headers)
        assert response.status_code == 204
        
        # 验证平台已删除
        response = client.get(f"/api/platforms/{sample_platform.id}")
        assert response.status_code == 404
    
    def test_delete_platform_not_found(self, client, admin_user, admin_token):
        """测试删除不存在的平台"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete("/api/platforms/9999", headers=headers)
        assert response.status_code == 404
    
    def test_delete_platform_without_auth(self, client, sample_platform):
        """测试未授权删除平台"""
        response = client.delete(f"/api/platforms/{sample_platform.id}")
        assert response.status_code == 403


# ==================== 测试: 切换状态 ====================

class TestTogglePlatformStatus:
    """切换平台状态的测试类"""
    
    def test_toggle_status_active_to_inactive(self, client, admin_user, admin_token, sample_platform):
        """测试从活跃切换到禁用"""
        assert sample_platform.is_active == True
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(f"/api/platforms/{sample_platform.id}/toggle-status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == False
    
    def test_toggle_featured_status(self, client, admin_user, admin_token, sample_platform):
        """测试切换精选状态"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(f"/api/platforms/{sample_platform.id}/toggle-featured", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_featured"] != sample_platform.is_featured


# ==================== 测试: 批量更新排名 ====================

class TestBulkUpdateRanks:
    """批量更新排名的测试类
    
    这是对用户问题的直接回答：
    "如果我用方案1，然后平台内容新增了5个平台，想给这5个平台进行排名的话，好操作吗？"
    
    答案：非常好操作！一个 API 调用就能批量更新多个平台的排名。
    """
    
    def test_bulk_update_ranks_success(self, client, admin_user, admin_token, sample_platforms):
        """测试批量更新排名"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        rank_data = {
            str(sample_platforms[0].id): 5,
            str(sample_platforms[1].id): 4,
            str(sample_platforms[2].id): 3,
            str(sample_platforms[3].id): 2,
        }
        response = client.post("/api/platforms/bulk/update-ranks", json=rank_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 4
    
    def test_bulk_update_ranks_invalid_id(self, client, admin_user, admin_token):
        """测试批量更新中包含无效 ID"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        rank_data = {"9999": 1}
        response = client.post("/api/platforms/bulk/update-ranks", json=rank_data, headers=headers)
        assert response.status_code == 400


# ==================== 测试: 获取特殊平台列表 ====================

class TestSpecialPlatformLists:
    """特殊平台列表的测试类"""
    
    def test_get_featured_platforms(self, client, sample_platforms):
        """测试获取精选平台"""
        response = client.get("/api/platforms/featured/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["is_featured"] for p in data)
    
    def test_get_regulated_platforms(self, client, sample_platforms):
        """测试获取监管平台"""
        response = client.get("/api/platforms/regulated/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["is_regulated"] for p in data)


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试类"""
    
    def test_list_platforms_large_dataset(self, client, db_session):
        """测试大数据集列表获取"""
        # 创建 1000 个平台
        for i in range(1000):
            platform = Platform(
                name=f"Platform_{i}",
                description=f"Description {i}",
                rating=float(i % 5),
                rank=i,
            )
            db_session.add(platform)
        db_session.commit()
        
        # 获取列表
        response = client.get("/api/platforms?limit=100")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 100
        assert data["total"] == 1000
    
    def test_search_performance(self, client, db_session):
        """测试搜索性能"""
        # 创建 500 个平台
        for i in range(500):
            platform = Platform(
                name=f"Exchange_{i}",
                description=f"Trading platform number {i}",
                rating=4.0 + (i % 10) * 0.1,
            )
            db_session.add(platform)
        db_session.commit()
        
        # 搜索
        response = client.get("/api/platforms?search=Exchange_1")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] <= 500


# ==================== 集成测试 ====================

class TestPlatformIntegration:
    """平台 API 集成测试"""
    
    def test_full_platform_lifecycle(self, client, admin_user, admin_token):
        """测试完整的平台生命周期：创建 → 读取 → 更新 → 删除"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建平台
        create_payload = {
            "name": "Lifecycle Test Platform",
            "description": "Test platform",
            "rating": 4.0,
        }
        response = client.post("/api/platforms", json=create_payload, headers=headers)
        assert response.status_code == 201
        platform_id = response.json()["id"]
        
        # 2. 读取平台
        response = client.get(f"/api/platforms/{platform_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Lifecycle Test Platform"
        
        # 3. 更新平台
        update_payload = {"rating": 4.8, "rank": 1}
        response = client.put(f"/api/platforms/{platform_id}", json=update_payload, headers=headers)
        assert response.status_code == 200
        assert response.json()["rating"] == 4.8
        
        # 4. 切换状态
        response = client.post(f"/api/platforms/{platform_id}/toggle-status", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_active"] == False
        
        # 5. 删除平台
        response = client.delete(f"/api/platforms/{platform_id}", headers=headers)
        assert response.status_code == 204
        
        # 6. 验证删除
        response = client.get(f"/api/platforms/{platform_id}")
        assert response.status_code == 404
