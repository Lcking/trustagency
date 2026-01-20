"""
任务模块初始化
"""

from .ai_generation import (
    generate_article_batch,
    generate_single_article,
    update_task_status,
    handle_generation_error,
)

from .margin_sync import (
    sync_margin_summary,
    sync_margin_detail,
    sync_margin_all,
    sync_margin_history,
)

__all__ = [
    'generate_article_batch',
    'generate_single_article',
    'update_task_status',
    'handle_generation_error',
    'sync_margin_summary',
    'sync_margin_detail',
    'sync_margin_all',
    'sync_margin_history',
]
