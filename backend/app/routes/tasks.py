"""
异步任务 API 端点

提供任务提交、进度查询、状态管理等接口。
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import AIGenerationTask, AdminUser
from app.tasks.ai_generation import generate_article_batch, monitor_task_progress
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# ============= Schemas =============

class TaskGenerationRequest(BaseModel):
    """任务生成请求"""
    titles: List[str] = Field(..., description="文章标题列表")
    section_id: int = Field(..., description="栏目ID")
    category_id: int = Field(..., description="分类ID")
    platform_id: Optional[int] = Field(None, description="平台ID (某些栏目需要)")
    batch_name: Optional[str] = Field(None, description="批次名称")
    ai_config_id: Optional[int] = Field(None, description="AI配置ID")

    class Config:
        schema_extra = {
            "example": {
                "titles": ["Python 入门指南", "FastAPI 最佳实践"],
                "category": "guide",
                "batch_name": "November 2025 Batch"
            }
        }


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    batch_id: str
    status: str
    progress: int
    celery_status: Optional[str]
    celery_task_id: Optional[str]
    total_count: int
    completed_count: int
    failed_count: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_update: Optional[datetime]

    class Config:
        from_attributes = True


class TaskProgressResponse(BaseModel):
    """任务进度响应"""
    task_id: str
    progress: int
    current: int
    total: int
    status: str
    celery_status: Optional[str]
    last_update: Optional[datetime]
    estimated_remaining_time: Optional[int]  # 预计剩余时间（秒）

    class Config:
        from_attributes = True


class TaskSubmitResponse(BaseModel):
    """任务提交响应"""
    task_id: str
    celery_task_id: str
    status: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "celery_task_id": "abc123def456",
                "status": "pending",
                "message": "任务已提交"
            }
        }


class TaskCancelResponse(BaseModel):
    """任务取消响应"""
    task_id: str
    status: str
    message: str


# ============= API 端点 =============

@router.post("/generate-articles", response_model=TaskSubmitResponse)
def submit_article_generation_task(
    request: TaskGenerationRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交文章生成任务（新逻辑）
    
    - **titles**: 要生成的文章标题列表
    - **section_id**: 栏目ID
    - **category_id**: 分类ID (或分类名称)
    - **platform_id**: 平台ID (某些栏目需要，可选)
    - **batch_name**: 批次名称 (可选)
    - **ai_config_id**: AI配置ID (可选)
    
    返回: 任务ID和Celery任务ID
    """
    if not request.titles:
        raise HTTPException(status_code=400, detail="标题列表不能为空")

    if len(request.titles) > 100:
        raise HTTPException(status_code=400, detail="单次最多提交100个标题")

    # 验证栏目存在
    from app.models import Section
    section = db.query(Section).filter(Section.id == request.section_id).first()
    if not section:
        raise HTTPException(status_code=400, detail=f"栏目ID {request.section_id} 不存在")
    
    # 验证平台（如果栏目需要）
    if section.requires_platform:
        if not request.platform_id:
            raise HTTPException(status_code=400, detail="该栏目需要关联平台")
        from app.models import Platform
        platform = db.query(Platform).filter(Platform.id == request.platform_id).first()
        if not platform:
            raise HTTPException(status_code=400, detail=f"平台ID {request.platform_id} 不存在")

    try:
        # 创建任务记录
        task = AIGenerationTask(
            batch_id=f"batch_{datetime.utcnow().timestamp()}_{hash(str(request.titles)) % 10000}",
            batch_name=request.batch_name or f"Batch {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            titles=request.titles,
            total_count=len(request.titles),
            status="pending",
            creator_id=current_user.id,
            ai_config_id=request.ai_config_id  # 保存AI配置ID
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # 提交 Celery 任务 - 传递新参数
        celery_task = generate_article_batch.apply_async(
            args=(
                task.batch_id, 
                request.titles, 
                request.section_id,
                request.category_id,  # 改为ID而不是字符串
                request.platform_id,
                current_user.id
            ),
            queue='ai_generation'
        )

        # 保存 Celery 任务ID
        task.celery_task_id = celery_task.id
        task.celery_status = 'PENDING'
        db.commit()

        return TaskSubmitResponse(
            task_id=str(task.batch_id),
            celery_task_id=celery_task.id,
            status="pending",
            message="任务已成功提交"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")




@router.get("/{task_id}/status", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    获取任务状态
    
    - **task_id**: 任务ID
    
    返回: 完整的任务状态信息
    """
    task = db.query(AIGenerationTask).filter(
        AIGenerationTask.batch_id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")

    return TaskStatusResponse(
        task_id=task.batch_id,
        batch_id=task.batch_id,
        status=task.status.value if hasattr(task.status, 'value') else task.status,
        progress=task.progress,
        celery_status=task.celery_status,
        celery_task_id=task.celery_task_id,
        total_count=task.total_count,
        completed_count=task.completed_count,
        failed_count=task.failed_count,
        error_message=task.error_message,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        last_update=task.last_progress_update
    )


@router.get("/{task_id}/progress", response_model=TaskProgressResponse)
def get_task_progress(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    获取任务进度
    
    - **task_id**: 任务ID
    
    返回: 任务进度信息（包括完成百分比）
    """
    task = db.query(AIGenerationTask).filter(
        AIGenerationTask.batch_id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")

    # 计算预计剩余时间（简单估算）
    estimated_remaining_time = None
    if task.progress > 0 and task.progress < 100:
        elapsed = (datetime.utcnow() - task.created_at).total_seconds()
        rate = task.progress / elapsed if elapsed > 0 else 0
        if rate > 0:
            estimated_remaining_time = int((100 - task.progress) / rate)

    return TaskProgressResponse(
        task_id=task.batch_id,
        progress=task.progress,
        current=task.completed_count,
        total=task.total_count,
        status=task.status.value if hasattr(task.status, 'value') else task.status,
        celery_status=task.celery_status,
        last_update=task.last_progress_update,
        estimated_remaining_time=estimated_remaining_time
    )


@router.post("/{task_id}/cancel", response_model=TaskCancelResponse)
def cancel_task(
    task_id: str,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消任务
    
    - **task_id**: 任务ID
    
    返回: 取消结果
    """
    task = db.query(AIGenerationTask).filter(
        AIGenerationTask.batch_id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")

    # 只有创建者或管理员可以取消任务
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限取消此任务")

    try:
        # 撤销 Celery 任务
        if task.celery_task_id:
            from app.celery_app import app as celery_app
            celery_app.control.revoke(task.celery_task_id, terminate=True)

        # 更新任务状态
        task.status = "failed"
        task.error_message = "用户已取消"
        task.celery_status = 'REVOKED'
        db.commit()

        return TaskCancelResponse(
            task_id=task.batch_id,
            status="cancelled",
            message="任务已成功取消"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@router.get("", description="列出所有任务")
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    列出当前用户的所有任务
    
    - **skip**: 跳过记录数 (分页)
    - **limit**: 返回记录数 (最多100条)
    - **status**: 筛选状态 (pending/processing/completed/failed)
    
    返回: 任务列表
    """
    query = db.query(AIGenerationTask).filter(
        AIGenerationTask.creator_id == current_user.id
    )

    if status:
        query = query.filter(AIGenerationTask.status == status)

    total = query.count()
    tasks = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "task_id": task.batch_id,
                "batch_name": task.batch_name,
                "status": task.status.value if hasattr(task.status, 'value') else task.status,
                "progress": task.progress,
                "total_count": task.total_count,
                "completed_count": task.completed_count,
                "celery_status": task.celery_status,
                "created_at": task.created_at,
                "updated_at": task.last_progress_update
            }
            for task in tasks
        ]
    }


@router.get("/{task_id}/details", description="获取任务详细信息")
def get_task_details(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    获取任务的详细信息（包括生成的文章列表）
    
    - **task_id**: 任务ID
    
    返回: 详细的任务信息
    """
    task = db.query(AIGenerationTask).filter(
        AIGenerationTask.batch_id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")

    return {
        "task_id": task.batch_id,
        "batch_name": task.batch_name,
        "status": task.status.value if hasattr(task.status, 'value') else task.status,
        "progress": task.progress,
        "total_count": task.total_count,
        "completed_count": task.completed_count,
        "failed_count": task.failed_count,
        "titles": task.titles,
        "generated_articles": task.generated_articles,
        "error_message": task.error_message,
        "celery_status": task.celery_status,
        "celery_task_id": task.celery_task_id,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "last_update": task.last_progress_update
    }
