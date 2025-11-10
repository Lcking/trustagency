"""
任务模块初始化
"""

from .ai_generation import (
    generate_article_batch,
    generate_single_article,
    update_task_status,
    handle_generation_error,
)

__all__ = [
    'generate_article_batch',
    'generate_single_article',
    'update_task_status',
    'handle_generation_error',
]
