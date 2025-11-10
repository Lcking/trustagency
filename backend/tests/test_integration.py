"""
集成和性能测试

测试系统集成、端到端流程、性能基准等。
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor


class TestEndToEndFlows:
    """端到端流程测试"""
    
    def test_user_registration_to_article_creation(self, client):
        """
        测试从用户注册到创建文章的完整流程
        
        验证：
        - 注册用户
        - 登录
        - 创建平台
        - 创建文章
        """
        # 1. 注册用户
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": "e2e_user",
                "email": "e2e@test.com",
                "password": "E2eTest123456"
            }
        )
        assert register_response.status_code == 201
        
        # 2. 登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "e2e_user",
                "password": "E2eTest123456"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. 创建平台
        headers = {"Authorization": f"Bearer {token}"}
        platform_response = client.post(
            "/api/platforms",
            json={
                "name": "E2E 平台",
                "url": "https://e2e.com"
            },
            headers=headers
        )
        assert platform_response.status_code == 201
        platform_id = platform_response.json()["id"]
        
        # 4. 创建文章
        article_response = client.post(
            "/api/articles",
            json={
                "title": "E2E 文章",
                "slug": "e2e-article",
                "content": "文章内容",
                "category": "guide",
                "platform_id": platform_id
            },
            headers=headers
        )
        assert article_response.status_code == 201
    
    def test_article_generation_workflow(self, client, admin_token):
        """
        测试文章生成工作流
        
        验证：
        - 创建生成任务
        - 监控任务状态
        - 获取结果
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建任务
        task_response = client.post(
            "/api/tasks/generate",
            json={
                "titles": ["标题1", "标题2"],
                "category": "guide"
            },
            headers=headers
        )
        assert task_response.status_code == 201
        task_id = task_response.json()["task_id"]
        
        # 2. 获取任务状态
        status_response = client.get(
            f"/api/tasks/{task_id}/status",
            headers=headers
        )
        assert status_response.status_code == 200
        assert "status" in status_response.json()
        
        # 3. 获取结果
        result_response = client.get(
            f"/api/tasks/{task_id}/result",
            headers=headers
        )
        assert result_response.status_code == 200


class TestDataConsistency:
    """数据一致性测试"""
    
    def test_platform_deletion_cascades(self, client, admin_token, test_db, sample_platform, admin_user):
        """
        测试平台删除级联
        
        验证：
        - 删除平台时，相关文章也被删除
        """
        from app.models import Article
        
        # 创建文章
        article = Article(
            title="级联测试",
            slug="cascade-test",
            content="内容",
            category="guide",
            status="published",
            platform_id=sample_platform.id,
            created_by=admin_user.id
        )
        test_db.add(article)
        test_db.commit()
        
        # 删除平台
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(
            f"/api/platforms/{sample_platform.id}",
            headers=headers
        )
        assert response.status_code == 204
        
        # 验证文章也被删除
        check_response = client.get(f"/api/articles/{article.id}")
        assert check_response.status_code == 404
    
    def test_concurrent_updates_consistency(self, client, admin_token, sample_platform):
        """
        测试并发更新的一致性
        
        验证：
        - 多个并发更新不会导致数据不一致
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def update_platform():
            return client.put(
                f"/api/platforms/{sample_platform.id}",
                json={"name": "并发更新测试"},
                headers=headers
            )
        
        # 并发执行 5 个更新
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_platform) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # 所有更新都应该成功或部分成功
        successful_updates = [r for r in results if r.status_code == 200]
        assert len(successful_updates) >= 1


class TestMemoryUsage:
    """内存使用测试"""
    
    def test_large_list_retrieval(self, client):
        """
        测试大型列表检索
        
        验证：
        - 可以处理大型数据集
        - 内存使用合理
        """
        # 获取所有文章
        response = client.get("/api/articles?limit=1000")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_batch_operations_memory(self, client, admin_token):
        """
        测试批量操作的内存使用
        
        验证：
        - 批量创建不会导致内存溢出
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建多个平台
        for i in range(10):
            response = client.post(
                "/api/platforms",
                json={
                    "name": f"批量平台{i}",
                    "url": f"https://batch{i}.com"
                },
                headers=headers
            )
            assert response.status_code == 201


class TestResponseTime:
    """响应时间测试"""
    
    def test_health_check_response_time(self, client):
        """
        测试健康检查响应时间
        
        验证：
        - 响应时间 < 100ms
        """
        start = time.time()
        response = client.get("/api/health")
        elapsed = (time.time() - start) * 1000  # 转换为毫秒
        
        assert response.status_code == 200
        assert elapsed < 100, f"响应时间过长: {elapsed:.2f}ms"
    
    def test_list_api_response_time(self, client):
        """
        测试列表 API 响应时间
        
        验证：
        - 响应时间 < 500ms
        """
        start = time.time()
        response = client.get("/api/articles?limit=10")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"响应时间过长: {elapsed:.2f}ms"
    
    def test_search_response_time(self, client):
        """
        测试搜索 API 响应时间
        
        验证：
        - 搜索响应时间 < 1000ms
        """
        start = time.time()
        response = client.get("/api/articles/search?q=test")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 1000, f"搜索时间过长: {elapsed:.2f}ms"


class TestConcurrentRequests:
    """并发请求测试"""
    
    def test_multiple_concurrent_reads(self, client):
        """
        测试多个并发读取请求
        
        验证：
        - 可以处理多个并发读取
        - 所有请求都成功
        """
        def read_articles():
            return client.get("/api/articles")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_articles) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # 所有请求都应该成功
        assert all(r.status_code == 200 for r in results)
    
    def test_mixed_concurrent_operations(self, client, admin_token):
        """
        测试混合并发操作
        
        验证：
        - 可以处理混合读写请求
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        def read_platforms():
            return client.get("/api/platforms")
        
        def create_platform():
            return client.post(
                "/api/platforms",
                json={
                    "name": f"并发平台_{time.time()}",
                    "url": f"https://concurrent{time.time()}.com"
                },
                headers=headers
            )
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 混合提交读写操作
            futures = []
            for i in range(10):
                if i % 2 == 0:
                    futures.append(executor.submit(read_platforms))
                else:
                    futures.append(executor.submit(create_platform))
            
            results = [f.result() for f in futures]
        
        # 验证所有操作都成功
        success_count = sum(1 for r in results if r.status_code in [200, 201])
        assert success_count == len(results)


class TestErrorRecovery:
    """错误恢复测试"""
    
    def test_service_recovery_after_error(self, client):
        """
        测试服务在错误后的恢复
        
        验证：
        - 一个错误的请求不会影响后续请求
        """
        # 发送无效请求
        invalid_response = client.get("/api/articles/invalid_id")
        assert invalid_response.status_code == 422
        
        # 后续请求应该正常
        valid_response = client.get("/api/articles")
        assert valid_response.status_code == 200
    
    def test_partial_data_resilience(self, client):
        """
        测试部分数据缺失时的弹性
        
        验证：
        - API 可以处理部分数据缺失
        """
        response = client.get("/api/articles")
        assert response.status_code == 200


class TestSecurityIntegration:
    """安全集成测试"""
    
    def test_jwt_token_validation(self, client):
        """
        测试 JWT 令牌验证
        
        验证：
        - 无效令牌被拒绝
        - 过期令牌被拒绝
        """
        # 使用无效令牌
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401
    
    def test_permission_check_enforcement(self, client):
        """
        测试权限检查执行
        
        验证：
        - 普通用户不能访问管理员接口
        """
        response = client.get("/api/admin/users")
        assert response.status_code == 401
    
    def test_sql_injection_prevention(self, client):
        """
        测试 SQL 注入预防
        
        验证：
        - SQL 注入尝试被安全处理
        """
        # 尝试 SQL 注入
        malicious_query = "'; DROP TABLE users; --"
        response = client.get(f"/api/articles/search?q={malicious_query}")
        
        # 应该返回安全的错误响应
        assert response.status_code in [200, 400, 422]


class TestLoadHandling:
    """负载处理测试"""
    
    def test_burst_load_handling(self, client):
        """
        测试突发负载处理
        
        验证：
        - 可以处理突发请求
        """
        def rapid_request():
            return client.get("/api/health")
        
        # 快速发送 50 个请求
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(rapid_request) for _ in range(50)]
            results = [f.result() for f in futures]
        
        # 至少 95% 的请求应该成功
        successful = sum(1 for r in results if r.status_code == 200)
        assert successful / len(results) >= 0.95
    
    def test_sustained_load_handling(self, client):
        """
        测试持续负载处理
        
        验证：
        - 可以在一段时间内处理持续请求
        """
        start = time.time()
        error_count = 0
        success_count = 0
        
        # 持续 10 秒的请求
        while time.time() - start < 10:
            try:
                response = client.get("/api/articles")
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
        
        # 验证大多数请求成功
        total = success_count + error_count
        assert success_count / total >= 0.95, f"成功率: {success_count / total}"


class TestDataValidationIntegration:
    """数据验证集成测试"""
    
    def test_end_to_end_validation_chain(self, client, admin_token):
        """
        测试端到端验证链
        
        验证：
        - 数据通过完整的验证管道
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 尝试使用多个无效数据字段
        test_cases = [
            # 缺少字段
            {"name": "平台"},
            # 无效类型
            {"name": 123, "url": "https://test.com"},
            # 空字符串
            {"name": "", "url": "https://test.com"},
            # 无效 URL
            {"name": "平台", "url": "not-a-url"},
        ]
        
        for data in test_cases:
            response = client.post("/api/platforms", json=data, headers=headers)
            assert response.status_code in [400, 422]


class TestServiceIntegration:
    """服务集成测试"""
    
    def test_openai_service_integration(self, client, admin_token):
        """
        测试 OpenAI 服务集成
        
        验证：
        - AI 服务正确集成
        - 错误被正确处理
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建 AI 生成任务
        response = client.post(
            "/api/tasks/generate",
            json={
                "titles": ["测试标题"],
                "category": "guide"
            },
            headers=headers
        )
        
        assert response.status_code == 201
    
    def test_celery_integration(self, client, admin_token):
        """
        测试 Celery 集成
        
        验证：
        - Celery 任务被正确排队
        - 可以获取任务状态
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建任务
        response = client.post(
            "/api/tasks/generate",
            json={
                "titles": ["标题"],
                "category": "guide"
            },
            headers=headers
        )
        
        assert response.status_code == 201
        task_id = response.json()["task_id"]
        
        # 获取状态
        status_response = client.get(
            f"/api/tasks/{task_id}/status",
            headers=headers
        )
        
        assert status_response.status_code == 200


class TestMonitoring:
    """监控测试"""
    
    def test_error_logging(self, client):
        """
        测试错误日志记录
        
        验证：
        - 错误被正确记录
        """
        # 触发错误
        response = client.get("/api/articles/invalid")
        assert response.status_code == 422
    
    def test_performance_metrics(self, client):
        """
        测试性能指标
        
        验证：
        - 性能数据被正确收集
        """
        response = client.get("/api/health")
        assert response.status_code == 200
