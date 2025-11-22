"""
AI任务监控工具
提供任务健康检查、超时检测、失败重试等功能
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import AIGenerationTask, TaskStatus
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class TaskMonitor:
    """AI任务监控器"""
    
    # 超时配置(分钟)
    TASK_TIMEOUT_MINUTES = 30
    STUCK_TASK_MINUTES = 10  # 卡住任务检测
    
    @staticmethod
    def check_stuck_tasks(db: Session = None) -> List[AIGenerationTask]:
        """
        检测卡住的任务
        
        条件:
        - 状态为 PROCESSING
        - 超过10分钟没有进度更新
        
        Returns:
            卡住的任务列表
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            timeout_threshold = datetime.utcnow() - timedelta(
                minutes=TaskMonitor.STUCK_TASK_MINUTES
            )
            
            stuck_tasks = db.query(AIGenerationTask).filter(
                and_(
                    AIGenerationTask.status == TaskStatus.PROCESSING,
                    or_(
                        AIGenerationTask.last_progress_update < timeout_threshold,
                        AIGenerationTask.last_progress_update.is_(None)
                    )
                )
            ).all()
            
            if stuck_tasks:
                logger.warning(f"发现 {len(stuck_tasks)} 个卡住的任务")
                
            return stuck_tasks
            
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def check_timeout_tasks(db: Session = None) -> List[AIGenerationTask]:
        """
        检测超时的任务
        
        条件:
        - 状态为 PROCESSING
        - 创建时间超过30分钟
        
        Returns:
            超时的任务列表
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            timeout_threshold = datetime.utcnow() - timedelta(
                minutes=TaskMonitor.TASK_TIMEOUT_MINUTES
            )
            
            timeout_tasks = db.query(AIGenerationTask).filter(
                and_(
                    AIGenerationTask.status == TaskStatus.PROCESSING,
                    AIGenerationTask.created_at < timeout_threshold
                )
            ).all()
            
            if timeout_tasks:
                logger.warning(f"发现 {len(timeout_tasks)} 个超时的任务")
                
            return timeout_tasks
            
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def mark_task_as_failed(
        task: AIGenerationTask,
        error_message: str,
        db: Session = None
    ) -> None:
        """
        将任务标记为失败
        
        Args:
            task: 任务对象
            error_message: 错误消息
            db: 数据库会话
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            task.status = TaskStatus.FAILED
            task.has_error = True
            task.error_message = error_message
            task.completed_at = datetime.utcnow()
            
            db.add(task)
            db.commit()
            
            logger.info(f"任务 {task.batch_id} 已标记为失败: {error_message}")
            
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def get_task_health_status(db: Session = None) -> Dict[str, Any]:
        """
        获取任务健康状态
        
        Returns:
            包含各种统计信息的字典
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            # 统计各状态的任务数
            pending_count = db.query(AIGenerationTask).filter(
                AIGenerationTask.status == TaskStatus.PENDING
            ).count()
            
            processing_count = db.query(AIGenerationTask).filter(
                AIGenerationTask.status == TaskStatus.PROCESSING
            ).count()
            
            completed_count = db.query(AIGenerationTask).filter(
                AIGenerationTask.status == TaskStatus.COMPLETED
            ).count()
            
            failed_count = db.query(AIGenerationTask).filter(
                AIGenerationTask.status == TaskStatus.FAILED
            ).count()
            
            # 检测问题任务
            stuck_tasks = TaskMonitor.check_stuck_tasks(db)
            timeout_tasks = TaskMonitor.check_timeout_tasks(db)
            
            # 计算成功率(最近100个任务)
            recent_tasks = db.query(AIGenerationTask).filter(
                AIGenerationTask.status.in_([TaskStatus.COMPLETED, TaskStatus.FAILED])
            ).order_by(AIGenerationTask.created_at.desc()).limit(100).all()
            
            success_rate = 0.0
            if recent_tasks:
                success_count = sum(1 for t in recent_tasks if t.status == TaskStatus.COMPLETED)
                success_rate = (success_count / len(recent_tasks)) * 100
            
            return {
                "status": "healthy" if len(stuck_tasks) == 0 and len(timeout_tasks) == 0 else "warning",
                "statistics": {
                    "pending": pending_count,
                    "processing": processing_count,
                    "completed": completed_count,
                    "failed": failed_count,
                    "total": pending_count + processing_count + completed_count + failed_count
                },
                "issues": {
                    "stuck_tasks": len(stuck_tasks),
                    "timeout_tasks": len(timeout_tasks)
                },
                "performance": {
                    "success_rate": round(success_rate, 2),
                    "total_evaluated": len(recent_tasks)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def auto_recover_stuck_tasks(db: Session = None) -> int:
        """
        自动恢复卡住的任务
        
        Returns:
            恢复的任务数量
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            stuck_tasks = TaskMonitor.check_stuck_tasks(db)
            
            recovered_count = 0
            for task in stuck_tasks:
                TaskMonitor.mark_task_as_failed(
                    task,
                    f"任务卡住超过 {TaskMonitor.STUCK_TASK_MINUTES} 分钟,已自动标记为失败",
                    db
                )
                recovered_count += 1
            
            return recovered_count
            
        finally:
            if should_close_db:
                db.close()
    
    @staticmethod
    def auto_recover_timeout_tasks(db: Session = None) -> int:
        """
        自动恢复超时的任务
        
        Returns:
            恢复的任务数量
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
            
        try:
            timeout_tasks = TaskMonitor.check_timeout_tasks(db)
            
            recovered_count = 0
            for task in timeout_tasks:
                TaskMonitor.mark_task_as_failed(
                    task,
                    f"任务执行超时(超过 {TaskMonitor.TASK_TIMEOUT_MINUTES} 分钟),已自动标记为失败",
                    db
                )
                recovered_count += 1
            
            return recovered_count
            
        finally:
            if should_close_db:
                db.close()
