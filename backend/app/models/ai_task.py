"""
AI 内容生成任务模型
"""
from datetime import datetime, timezone, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

# 东八区（UTC+8）时区
CST = timezone(timedelta(hours=8))

def get_cst_now():
    """获取东八区当前时间"""
    return datetime.now(CST)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AIGenerationTask(Base):
    """AI 内容生成任务模型"""
    __tablename__ = "ai_generation_tasks"

    id = Column(Integer, primary_key=True, index=True)

    # 批次信息
    batch_id = Column(String(100), unique=True, index=True, nullable=False)
    batch_name = Column(String(255), nullable=True)

    # 输入和输出
    titles = Column(JSON, nullable=False)  # 标题列表
    generated_articles = Column(JSON, nullable=True)  # 生成的文章列表

    # 目标配置 - 栏目/分类/平台
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=True, index=True)  # 仅验证栏目时必填

    # 任务状态
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    progress = Column(Integer, default=0)  # 0-100
    total_count = Column(Integer, nullable=False)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    # 错误跟踪 - 增强的错误报告机制
    error_message = Column(Text, nullable=True)  # 简短的错误摘要
    error_details = Column(JSON, nullable=True)  # 详细的错误信息和堆栈跟踪
    failed_titles = Column(JSON, nullable=True)  # 失败的文章标题列表及其错误原因
    has_error = Column(Boolean, default=False, index=True)  # 标记是否有错误（方便查询）

    # AI 配置信息
    ai_config_id = Column(Integer, ForeignKey("ai_configs.id"), nullable=True)  # 使用的 AI 配置
    ai_model = Column(String(100), nullable=True)  # 使用的模型名称

    # Celery 集成字段
    celery_task_id = Column(String(100), nullable=True, index=True)  # Celery任务ID
    celery_status = Column(String(50), default='PENDING', nullable=True)  # Celery状态
    last_progress_update = Column(DateTime, nullable=True)  # 最后进度更新时间

    # 创建者
    creator_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=get_cst_now)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    is_current_batch = Column(Boolean, default=True, index=True)  # 是否为当前批次任务

    # 关系
    creator = relationship("AdminUser", back_populates="ai_tasks")
    section = relationship("Section")
    category = relationship("Category")
    platform = relationship("Platform")

    def __repr__(self):
        return f"<AIGenerationTask(id={self.id}, batch_id={self.batch_id}, status={self.status})>"
