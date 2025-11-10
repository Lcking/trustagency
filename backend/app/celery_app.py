"""
Celery 应用配置和初始化模块

提供异步任务队列支持，用于处理长时间运行的任务如 AI 文章生成。
"""

import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

# 创建 Celery 应用实例
app = Celery(
    'trustagency',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Celery 配置
app.conf.update(
    # 消息序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 时区设置
    timezone='UTC',
    enable_utc=True,
    
    # 任务执行配置
    task_track_started=True,           # 跟踪任务开始状态
    task_time_limit=30 * 60,           # 30分钟硬限制（强制kill）
    task_soft_time_limit=25 * 60,      # 25分钟软限制（发送SIGTERM）
    
    # 结果后端配置
    result_expires=3600,               # 结果保留1小时
    result_extended=True,              # 保存额外的状态信息
    
    # 重试配置
    task_autoretry_for=(Exception,),   # 异常时自动重试
    task_max_retries=3,                # 最多重试3次
    
    # 路由配置
    task_routes={
        'app.tasks.ai_generation.*': {'queue': 'ai_generation'},
        'app.tasks.default.*': {'queue': 'default'},
    },
    
    # Worker 配置
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# 任务预处理信号
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """任务开始前的处理"""
    print(f"[TASK START] Task ID: {task_id}, Task Name: {task.name}")


# 任务后处理信号
@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, **kwargs):
    """任务完成后的处理"""
    print(f"[TASK COMPLETE] Task ID: {task_id}, Task Name: {task.name}, Result: {retval}")


# 任务失败处理
@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """任务失败时的处理"""
    print(f"[TASK FAILED] Task ID: {task_id}, Exception: {exception}")


# 调试任务（用于测试）
@app.task(bind=True)
def debug_task(self):
    """
    调试任务，用于验证 Celery 是否正常工作
    
    Returns:
        dict: 包含请求信息的字典
    """
    print(f'[DEBUG] Request: {self.request!r}')
    return {
        'task_id': self.request.id,
        'task_name': self.name,
        'args': self.request.args,
        'kwargs': self.request.kwargs,
    }


# 健康检查任务
@app.task(bind=True)
def health_check(self):
    """
    健康检查任务
    
    Returns:
        dict: 包含健康检查信息的字典
    """
    return {
        'status': 'healthy',
        'task_id': self.request.id,
        'timestamp': str(__import__('datetime').datetime.utcnow()),
    }
