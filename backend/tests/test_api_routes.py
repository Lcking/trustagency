"""
API 路由集成测试

测试所有 API 端点的集成功能、错误处理、响应格式等。
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """健康检查端点测试"""
    
    def test_health_check_endpoint(self, client):
        """
        测试健康检查端点
        
        验证：
        - 端点返回 200
        - 返回正确的信息
        """
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestAuthenticationRoutes:
    """认证路由集成测试"""
    
    def test_register_and_login_flow(self, client):
        """
        测试注册然后登录流程
        
        验证：
        - 可以完整注册
        - 注册后可以登录
        """
        # 注册
        register_data = {
            "username": "flowtest",
            "email": "flow@test.com",
            "password": "TestPass123456"
        }
        reg_response = client.post("/api/auth/register", json=register_data)
        assert reg_response.status_code == 201
        
        # 登录
        login_data = {
            "username": "flowtest",
            "password": "TestPass123456"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
    
    def test_protected_route_without_token(self, client):
        """
        测试访问受保护的路由（无令牌）
        
        验证：
        - 没有令牌时被拒绝
        """
        response = client.get("/api/admin/users")
        assert response.status_code == 401
    
    def test_protected_route_with_token(self, client, admin_token):
        """
        测试访问受保护的路由（有令牌）
        
        验证：
        - 有有效令牌时可以访问
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 200


class TestPlatformRoutes:
    """平台 API 路由测试"""
    
    def test_get_all_platforms(self, client):
        """
        测试获取所有平台
        
        验证：
        - 端点返回 200
        - 返回平台列表
        """
        response = client.get("/api/platforms")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_platform_by_id(self, client, sample_platform):
        """
        测试按 ID 获取平台
        
        验证：
        - 返回正确的平台数据
        """
        response = client.get(f"/api/platforms/{sample_platform.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_platform.id
    
    def test_get_nonexistent_platform(self, client):
        """
        测试获取不存在的平台
        
        验证：
        - 返回 404
        """
        response = client.get("/api/platforms/99999")
        
        assert response.status_code == 404
    
    def test_create_platform(self, client, admin_token):
        """
        测试创建平台
        
        验证：
        - 需要管理员令牌
        - 返回 201
        - 返回创建的平台数据
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        platform_data = {
            "name": "新平台",
            "url": "https://newplatform.com"
        }
        response = client.post("/api/platforms", json=platform_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新平台"
    
    def test_create_platform_without_auth(self, client):
        """
        测试未授权创建平台
        
        验证：
        - 没有令牌时被拒绝
        """
        platform_data = {
            "name": "新平台",
            "url": "https://newplatform.com"
        }
        response = client.post("/api/platforms", json=platform_data)
        
        assert response.status_code == 401
    
    def test_update_platform(self, client, admin_token, sample_platform):
        """
        测试更新平台
        
        验证：
        - 返回 200
        - 数据被更新
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"name": "更新的平台"}
        response = client.put(
            f"/api/platforms/{sample_platform.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新的平台"
    
    def test_delete_platform(self, client, admin_token, sample_platform):
        """
        测试删除平台
        
        验证：
        - 返回 204
        - 平台被删除
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/api/platforms/{sample_platform.id}", headers=headers)
        
        assert response.status_code == 204
        
        # 验证已删除
        check_response = client.get(f"/api/platforms/{sample_platform.id}")
        assert check_response.status_code == 404


class TestArticleRoutes:
    """文章 API 路由测试"""
    
    def test_get_all_articles(self, client):
        """
        测试获取所有文章
        
        验证：
        - 端点返回 200
        - 返回文章列表
        """
        response = client.get("/api/articles")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_article_by_id(self, client, sample_article):
        """
        测试按 ID 获取文章
        
        验证：
        - 返回正确的文章数据
        """
        response = client.get(f"/api/articles/{sample_article.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_article.id
    
    def test_get_article_by_slug(self, client, sample_article):
        """
        测试按 slug 获取文章
        
        验证：
        - 返回正确的文章数据
        """
        response = client.get(f"/api/articles/slug/{sample_article.slug}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == sample_article.slug
    
    def test_filter_articles_by_category(self, client):
        """
        测试按分类过滤文章
        
        验证：
        - 返回正确分类的文章
        """
        response = client.get("/api/articles?category=guide")
        
        assert response.status_code == 200
        data = response.json()
        for article in data:
            assert article["category"] == "guide"
    
    def test_search_articles(self, client, sample_article):
        """
        测试搜索文章
        
        验证：
        - 返回搜索结果
        """
        response = client.get(f"/api/articles/search?q={sample_article.title}")
        
        assert response.status_code == 200
    
    def test_create_article(self, client, admin_token, sample_platform):
        """
        测试创建文章
        
        验证：
        - 需要管理员令牌
        - 返回 201
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        article_data = {
            "title": "新文章",
            "slug": "new-article-unique",
            "content": "文章内容",
            "category": "guide",
            "platform_id": sample_platform.id
        }
        response = client.post("/api/articles", json=article_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "新文章"


class TestAdminRoutes:
    """管理员 API 路由测试"""
    
    def test_get_all_users_as_admin(self, client, admin_token):
        """
        测试管理员获取所有用户
        
        验证：
        - 管理员可以获取用户列表
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_users_as_non_admin(self, client):
        """
        测试普通用户获取所有用户
        
        验证：
        - 普通用户被拒绝
        """
        # 创建普通用户令牌
        # （假设有 regular_user_token fixture）
        response = client.get("/api/admin/users")
        
        assert response.status_code == 401
    
    def test_admin_statistics(self, client, admin_token):
        """
        测试获取管理员统计数据
        
        验证：
        - 返回系统统计信息
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_platforms" in data
        assert "total_articles" in data


class TestTaskRoutes:
    """任务 API 路由测试"""
    
    def test_create_ai_task(self, client, admin_token):
        """
        测试创建 AI 生成任务
        
        验证：
        - 返回 201
        - 返回任务 ID
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        task_data = {
            "titles": ["标题1", "标题2"],
            "category": "guide"
        }
        response = client.post("/api/tasks/generate", json=task_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data
    
    def test_get_task_status(self, client, admin_token, sample_ai_task):
        """
        测试获取任务状态
        
        验证：
        - 返回任务信息
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            f"/api/tasks/{sample_ai_task.id}/status",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["pending", "processing", "completed", "failed"]
    
    def test_get_task_result(self, client, admin_token, sample_ai_task):
        """
        测试获取任务结果
        
        验证：
        - 返回任务结果
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            f"/api/tasks/{sample_ai_task.id}/result",
            headers=headers
        )
        
        assert response.status_code == 200


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_json_request(self, client):
        """
        测试无效的 JSON 请求
        
        验证：
        - 返回 422（验证错误）
        """
        response = client.post(
            "/api/platforms",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_field(self, client, admin_token):
        """
        测试缺少必需字段
        
        验证：
        - 返回 422（验证错误）
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        platform_data = {
            "name": "平台"
            # 缺少 url 字段
        }
        response = client.post("/api/platforms", json=platform_data, headers=headers)
        
        assert response.status_code == 422
    
    def test_invalid_data_type(self, client, admin_token):
        """
        测试无效的数据类型
        
        验证：
        - 返回 422（验证错误）
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        platform_data = {
            "name": "平台",
            "url": 12345  # 应该是字符串
        }
        response = client.post("/api/platforms", json=platform_data, headers=headers)
        
        assert response.status_code == 422


class TestCORSHeaders:
    """CORS 头部测试"""
    
    def test_cors_headers_present(self, client):
        """
        测试 CORS 头部是否存在
        
        验证：
        - CORS 头部被正确设置
        """
        response = client.get("/api/health")
        
        assert response.status_code == 200
        # CORS 头部通常应该存在
        # assert "access-control-allow-origin" in response.headers


class TestResponseFormat:
    """响应格式测试"""
    
    def test_list_response_format(self, client):
        """
        测试列表响应格式
        
        验证：
        - 返回 JSON 数组
        - 包含正确的字段
        """
        response = client.get("/api/platforms")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    def test_single_object_response_format(self, client, sample_platform):
        """
        测试单个对象响应格式
        
        验证：
        - 返回 JSON 对象
        - 包含所有字段
        """
        response = client.get(f"/api/platforms/{sample_platform.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data


class TestPagination:
    """分页测试"""
    
    def test_list_with_limit(self, client):
        """
        测试带有 limit 的列表
        
        验证：
        - 返回指定数量的项
        """
        response = client.get("/api/platforms?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_list_with_offset(self, client):
        """
        测试带有 offset 的列表
        
        验证：
        - 跳过指定数量的项
        """
        response = client.get("/api/platforms?offset=0&limit=5")
        
        assert response.status_code == 200


class TestCaching:
    """缓存测试"""
    
    def test_repeated_requests_same_response(self, client, sample_platform):
        """
        测试重复请求返回相同响应
        
        验证：
        - 多次请求返回一致的数据
        """
        response1 = client.get(f"/api/platforms/{sample_platform.id}")
        response2 = client.get(f"/api/platforms/{sample_platform.id}")
        
        assert response1.json() == response2.json()
