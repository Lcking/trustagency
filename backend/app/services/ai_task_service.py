"""
AI 任务管理服务 - 包含错误跟踪和历史清理
"""
from sqlalchemy.orm import Session
from app.models import AIGenerationTask, TaskStatus
from datetime import datetime
from typing import Optional, List


class AITaskService:
    """AI 任务服务"""
    
    @staticmethod
    def create_task(
        db: Session,
        batch_id: str,
        batch_name: str,
        titles: List[str],
        ai_config_id: Optional[int] = None,
        creator_id: Optional[int] = None,
    ) -> AIGenerationTask:
        """
        创建新任务，并清理旧任务历史
        
        新增任务后自动删除之前的历史遗留信息
        """
        # 1. 标记所有旧任务为非当前批次
        db.query(AIGenerationTask).update(
            {AIGenerationTask.is_current_batch: False},
            synchronize_session=False
        )
        db.commit()
        
        # 2. 创建新任务
        task = AIGenerationTask(
            batch_id=batch_id,
            batch_name=batch_name,
            titles=titles,
            total_count=len(titles),
            status=TaskStatus.PENDING,
            ai_config_id=ai_config_id,
            creator_id=creator_id,
            is_current_batch=True,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return task
    
    @staticmethod
    def get_current_tasks(db: Session) -> List[AIGenerationTask]:
        """获取当前批次任务"""
        return db.query(AIGenerationTask).filter(
            AIGenerationTask.is_current_batch == True
        ).all()
    
    @staticmethod
    def record_error(
        db: Session,
        task_id: int,
        error_message: str,
        error_code: Optional[str] = None,
        error_traceback: Optional[str] = None,
        failed_titles: Optional[List[dict]] = None,
    ) -> AIGenerationTask:
        """
        记录任务错误
        
        failed_titles 格式: [{"title": "xxx", "error": "yyy"}]
        """
        task = db.query(AIGenerationTask).filter(AIGenerationTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.has_error = True
        task.error_message = error_message
        task.status = TaskStatus.FAILED
        
        # 记录详细错误信息
        error_detail = {
            "error_code": error_code or "UNKNOWN_ERROR",
            "error_message": error_message,
            "error_traceback": error_traceback,
            "failed_titles": failed_titles or [],
            "retry_count": 0,
        }
        task.error_details = error_detail
        task.failed_titles = failed_titles
        
        db.commit()
        db.refresh(task)
        
        return task
    
    @staticmethod
    def update_progress(
        db: Session,
        task_id: int,
        completed_count: int,
        failed_count: int,
        progress: int,
    ) -> AIGenerationTask:
        """更新任务进度"""
        task = db.query(AIGenerationTask).filter(AIGenerationTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.completed_count = completed_count
        task.failed_count = failed_count
        task.progress = progress
        task.last_progress_update = datetime.utcnow()
        
        if progress >= 100:
            task.completed_at = datetime.utcnow()
            if failed_count == 0:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.COMPLETED  # 部分成功也标记为完成
                task.has_error = True
        elif task.status == TaskStatus.PENDING:
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return task
    
    @staticmethod
    def cleanup_old_tasks(db: Session, keep_recent_days: int = 30) -> int:
        """
        清理旧任务历史
        
        返回删除的任务数量
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=keep_recent_days)
        
        # 仅删除非当前批次的旧任务
        deleted = db.query(AIGenerationTask).filter(
            AIGenerationTask.is_current_batch == False,
            AIGenerationTask.created_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        return deleted
