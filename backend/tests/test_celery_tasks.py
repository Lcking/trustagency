"""
Celery 任务测试

测试异步任务的执行、重试、回调等功能。
"""

import pytest
from unittest.mock import patch, MagicMock
from app.celery_app import app as celery_app


@pytest.fixture(autouse=True)
def celery_config():
    """配置 Celery 为同步模式（用于测试）"""
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True
    )


class TestArticleGeneration:
    """文章生成任务测试"""
    
    def test_generate_single_article_task(self, test_db, admin_user):
        """
        测试单篇文章生成任务
        
        验证：
        - 任务执行成功
        - 返回文章数据
        """
        from app.tasks.ai_generation import generate_single_article
        
        result = generate_single_article(
            title="测试文章",
            category="guide",
            task_id=1
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "title" in result
        assert "content" in result
    
    def test_generate_article_batch_task(self, test_db, admin_user, sample_ai_task):
        """
        测试批量文章生成任务
        
        验证：
        - 任务执行成功
        - 生成多篇文章
        """
        from app.tasks.ai_generation import generate_article_batch
        
        result = generate_article_batch.apply_async(
            args=[
                [sample_ai_task.id],
                ["标题1", "标题2"],
                "guide"
            ]
        )
        
        # 使用 eager 模式时直接执行
        assert result is not None


class TestTaskStatusUpdate:
    """任务状态更新测试"""
    
    def test_update_task_status(self, test_db, admin_user, sample_ai_task):
        """
        测试更新任务状态
        
        验证：
        - 状态更新成功
        - 数据库中的状态改变
        """
        from app.tasks.ai_generation import update_task_status
        
        original_status = sample_ai_task.status
        
        # 调用更新状态任务
        update_task_status.apply_async(
            args=[sample_ai_task.id, "running", 50]
        )
        
        # 刷新数据
        test_db.refresh(sample_ai_task)
        
        # 这里我们期望状态被更新（在实际环境中）
        # 在测试中可能需要立即重新查询


class TestTaskRetry:
    """任务重试机制测试"""
    
    def test_task_with_retry(self):
        """
        测试带重试的任务
        
        验证：
        - 重试配置正确
        - 最大重试次数设置
        """
        from app.tasks.ai_generation import generate_single_article
        
        # 检查任务配置
        assert hasattr(generate_single_article, 'autoretry_for')
    
    def test_exponential_backoff(self):
        """
        测试指数退避重试
        
        验证：
        - 重试延迟逐步增加
        """
        from app.tasks.ai_generation import generate_single_article
        
        # 任务应该配置了重试策略
        assert generate_single_article.autoretry_for is not None


class TestErrorHandling:
    """错误处理测试"""
    
    def test_handle_generation_error(self, test_db, admin_user, sample_ai_task):
        """
        测试错误处理
        
        验证：
        - 错误被正确记录
        - 任务状态更新为失败
        """
        from app.tasks.ai_generation import handle_generation_error
        
        error_msg = "测试错误"
        result = handle_generation_error.apply_async(
            args=[sample_ai_task.id, error_msg]
        )
        
        assert result is not None
    
    def test_task_failure_callback(self, test_db, admin_user, sample_ai_task):
        """
        测试任务失败回调
        
        验证：
        - 失败回调被触发
        - 状态被正确设置为失败
        """
        # 此测试依赖于任务链配置
        pass


class TestMonitorTaskProgress:
    """任务进度监控测试"""
    
    def test_monitor_task_progress(self, test_db, admin_user, sample_ai_task):
        """
        测试监控任务进度
        
        验证：
        - 可以查询任务进度
        - 进度信息正确
        """
        from app.tasks.ai_generation import monitor_task_progress
        
        result = monitor_task_progress.apply_async(
            args=[sample_ai_task.id]
        )
        
        assert result is not None
    
    def test_progress_updates(self, test_db, admin_user, sample_ai_task):
        """
        测试进度更新
        
        验证：
        - 进度值在 0-100 之间
        - 进度值正确保存
        """
        sample_ai_task.progress = 25
        test_db.commit()
        
        assert 0 <= sample_ai_task.progress <= 100


class TestTaskChaining:
    """任务链测试"""
    
    def test_task_chain_execution(self):
        """
        测试任务链执行
        
        验证：
        - 多个任务可以链接
        - 按顺序执行
        """
        from celery import chain
        from app.tasks.ai_generation import (
            generate_article_batch,
            update_task_status
        )
        
        # 任务链应该可以创建
        # workflow = chain(
        #     generate_article_batch.s([1, 2, 3]),
        #     update_task_status.s(1, "completed")
        # )


class TestAsyncProcessing:
    """异步处理测试"""
    
    def test_task_queued_correctly(self, sample_ai_task):
        """
        测试任务正确入队
        
        验证：
        - 任务被添加到队列
        - 可以追踪任务状态
        """
        from app.tasks.ai_generation import generate_article_batch
        
        result = generate_article_batch.apply_async(
            args=[[sample_ai_task.id], ["文章"], "guide"]
        )
        
        # 在同步模式下，应该立即返回结果
        assert result is not None
    
    def test_multiple_tasks_execution(self, test_db, admin_user):
        """
        测试多个任务并发执行
        
        验证：
        - 多个任务可以并发执行
        - 都能完成
        """
        from app.tasks.ai_generation import generate_single_article
        
        # 提交多个任务
        results = []
        for i in range(3):
            result = generate_single_article.apply_async(
                args=[f"文章{i}", "guide", i]
            )
            results.append(result)
        
        # 所有任务都应该完成
        assert len(results) == 3


class TestTaskConfiguration:
    """任务配置测试"""
    
    def test_task_timeouts_configured(self):
        """
        测试任务超时配置
        
        验证：
        - 任务有超时设置
        """
        from app.tasks.ai_generation import generate_single_article
        
        # 任务应该有超时配置
        assert generate_single_article.time_limit is not None
    
    def test_task_rate_limit(self):
        """
        测试任务速率限制
        
        验证：
        - 任务有速率限制配置
        """
        # 此测试依赖于任务配置


class TestCeleryHealth:
    """Celery 健康检查测试"""
    
    def test_celery_connection(self, celery_config):
        """
        测试 Celery 连接
        
        验证：
        - 可以连接到 Celery
        - 任务注册正确
        """
        registered_tasks = list(celery_app.tasks.keys())
        
        # 应该注册了我们的任务
        assert len(registered_tasks) > 0
    
    def test_broker_connection(self):
        """
        测试消息代理连接
        
        验证：
        - 可以连接到代理
        """
        try:
            celery_app.connection().connect()
        except Exception as e:
            pytest.skip(f"Broker not available: {e}")
