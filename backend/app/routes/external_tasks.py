"""
外部任务 API 端点

用于 OpenClaw 等外部系统调用，使用 API Key 认证。
"""

import os
import time
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db

router = APIRouter(prefix="/api/external", tags=["external"])


# ============= API Key 认证 =============

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    验证 API Key
    
    API Key 从环境变量 EXTERNAL_API_KEY 读取。
    可以设置多个 Key，用逗号分隔。
    """
    valid_keys = os.getenv("EXTERNAL_API_KEY", "").split(",")
    valid_keys = [k.strip() for k in valid_keys if k.strip()]
    
    if not valid_keys:
        raise HTTPException(
            status_code=500,
            detail="API Key 未配置，请联系管理员"
        )
    
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=401,
            detail="无效的 API Key"
        )
    
    return x_api_key


# ============= Schemas =============

class SyncMarginRequest(BaseModel):
    """两融数据同步请求"""
    days: int = Field(default=3, ge=1, le=30, description="同步最近N天的数据")
    force: bool = Field(default=False, description="强制重新同步（即使数据已存在）")


class SyncMarginResponse(BaseModel):
    """两融数据同步响应"""
    success: bool
    result: str = Field(description="执行结果：updated/no_new_data/partial_success/failed")
    message: str = Field(description="给自动化系统读取的简短说明")
    summary_count: int = Field(description="同步的汇总数据条数")
    detail_count: int = Field(description="同步的明细数据条数")
    synced_dates: list[str] = Field(description="成功同步的日期列表")
    skipped_dates: list[str] = Field(description="跳过的日期列表（已有数据或无数据）")
    requested_dates: list[str] = Field(description="本次尝试同步的日期列表")
    errors: list[str] = Field(description="错误信息列表")
    latest_summary_date: Optional[str] = Field(default=None, description="当前库内最新汇总数据日期")
    latest_detail_date: Optional[str] = Field(default=None, description="当前库内最新明细数据日期")
    duration_ms: int = Field(description="执行耗时（毫秒）")
    timestamp: str = Field(description="执行时间")


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_name: str
    last_run: Optional[str]
    next_run: Optional[str]
    status: str


class SystemHealthResponse(BaseModel):
    """系统健康状态响应"""
    status: str
    database: str
    celery_worker: str
    celery_beat: str
    margin_data_latest_date: Optional[str]
    timestamp: str


# ============= API 端点 =============

@router.post("/tasks/sync-margin", response_model=SyncMarginResponse)
async def sync_margin_data(
    request: SyncMarginRequest = None,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    同步两融数据
    
    从 Tushare API 获取融资融券数据并存入数据库。
    
    - **days**: 同步最近 N 天的数据（默认 3 天）
    - **force**: 是否强制重新同步已存在的数据（默认 False）
    
    返回:
    - **summary_count**: 同步的汇总数据条数
    - **detail_count**: 同步的明细数据条数
    - **synced_dates**: 成功同步的日期列表
    - **duration_ms**: 执行耗时
    """
    if request is None:
        request = SyncMarginRequest()
    
    start_time = time.time()
    
    try:
        from app.services.tushare_service import MarginDataService
        from app.models.margin import MarginSummary, MarginDetail
        
        service = MarginDataService(db)
        
        summary_count = 0
        detail_count = 0
        synced_dates = []
        skipped_dates = []
        requested_dates = []
        errors = []
        
        # 同步汇总数据
        try:
            summary_count = service.sync_summary_data(days=request.days)
        except Exception as e:
            errors.append(f"汇总数据同步失败: {str(e)}")
        
        # 同步明细数据（最近 N 天）
        for i in range(request.days):
            trade_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            requested_dates.append(trade_date)
            try:
                count = service.sync_detail_data(trade_date=trade_date)
                if count > 0:
                    detail_count += count
                    synced_dates.append(trade_date)
                else:
                    skipped_dates.append(trade_date)
                # API 频率限制
                time.sleep(0.3)
            except Exception as e:
                errors.append(f"{trade_date} 同步失败: {str(e)}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        latest_summary = db.query(MarginSummary).order_by(MarginSummary.trade_date.desc()).first()
        latest_detail = db.query(MarginDetail).order_by(MarginDetail.trade_date.desc()).first()

        if errors:
            result = "partial_success" if (summary_count > 0 or detail_count > 0 or synced_dates) else "failed"
            message = "部分同步失败，请检查 errors" if result == "partial_success" else "同步失败，请检查 errors"
        elif summary_count > 0 or detail_count > 0 or synced_dates:
            result = "updated"
            message = "同步成功，已有新数据写入"
        else:
            result = "no_new_data"
            message = "接口执行成功，但本次未发现可写入的新数据"
        
        return SyncMarginResponse(
            success=len(errors) == 0,
            result=result,
            message=message,
            summary_count=summary_count,
            detail_count=detail_count,
            synced_dates=synced_dates,
            skipped_dates=skipped_dates,
            requested_dates=requested_dates,
            errors=errors,
            latest_summary_date=latest_summary.trade_date.strftime('%Y-%m-%d') if latest_summary else None,
            latest_detail_date=latest_detail.trade_date.strftime('%Y-%m-%d') if latest_detail else None,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return SyncMarginResponse(
            success=False,
            result="failed",
            message="同步失败，请检查 errors",
            summary_count=0,
            detail_count=0,
            synced_dates=[],
            skipped_dates=[],
            requested_dates=[],
            errors=[str(e)],
            latest_summary_date=None,
            latest_detail_date=None,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )


@router.get("/tasks/margin-status")
async def get_margin_status(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取两融数据状态
    
    返回:
    - 最新数据日期
    - 数据总条数
    - 最近同步时间
    """
    from app.models.margin import MarginSummary, MarginDetail
    
    # 获取最新汇总数据日期
    latest_summary = db.query(MarginSummary).order_by(
        MarginSummary.trade_date.desc()
    ).first()
    
    # 获取最新明细数据日期
    latest_detail = db.query(MarginDetail).order_by(
        MarginDetail.trade_date.desc()
    ).first()
    
    # 统计总数
    summary_total = db.query(MarginSummary).count()
    detail_total = db.query(MarginDetail).count()
    
    return {
        "status": "ok",
        "summary": {
            "latest_date": latest_summary.trade_date.strftime('%Y-%m-%d') if latest_summary else None,
            "total_count": summary_total
        },
        "detail": {
            "latest_date": latest_detail.trade_date.strftime('%Y-%m-%d') if latest_detail else None,
            "total_count": detail_total
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/health")
async def health_check(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    系统健康检查
    
    检查:
    - 数据库连接
    - Celery Worker 状态
    - 两融数据更新状态
    """
    from app.models.margin import MarginDetail
    
    # 检查数据库
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # 检查 Celery Worker
    try:
        from app.celery_app import app as celery_app
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        celery_status = "healthy" if active_workers else "no_workers"
    except Exception as e:
        celery_status = f"error: {str(e)}"
    
    # 检查两融数据最新日期
    latest_detail = db.query(MarginDetail).order_by(
        MarginDetail.trade_date.desc()
    ).first()
    
    latest_date = latest_detail.trade_date.strftime('%Y-%m-%d') if latest_detail else None
    
    # 判断数据是否过期（超过 2 个工作日）
    data_status = "ok"
    if latest_detail:
        days_old = (datetime.now().date() - latest_detail.trade_date).days
        if days_old > 3:
            data_status = f"stale ({days_old} days old)"
    else:
        data_status = "no_data"
    
    return SystemHealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        celery_worker=celery_status,
        celery_beat="check_logs",
        margin_data_latest_date=latest_date,
        timestamp=datetime.now().isoformat()
    )


@router.get("/ping")
async def ping():
    """
    简单的 ping 测试（无需认证）
    
    用于检查 API 是否可达。
    """
    return {
        "status": "pong",
        "timestamp": datetime.now().isoformat()
    }


# ============= 内容管理 API =============

@router.get("/content/sections")
async def get_sections(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取所有栏目列表
    
    返回栏目 ID、名称、slug 等信息。
    """
    from app.models import Section
    
    sections = db.query(Section).filter(Section.is_active == True).all()
    
    return {
        "sections": [
            {
                "id": s.id,
                "name": s.name,
                "slug": s.slug,
                "description": s.description,
                "requires_platform": s.requires_platform
            }
            for s in sections
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/content/categories")
async def get_categories(
    section_id: Optional[int] = None,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取分类列表
    
    - **section_id**: 可选，筛选指定栏目的分类
    """
    from app.models import Category
    
    query = db.query(Category).filter(Category.is_active == True)
    if section_id:
        query = query.filter(Category.section_id == section_id)
    
    categories = query.all()
    
    return {
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "section_id": c.section_id,
                "description": c.description
            }
            for c in categories
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/content/platforms")
async def get_platforms(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取平台列表
    
    用于 Review 栏目关联平台。
    """
    from app.models import Platform
    
    platforms = db.query(Platform).filter(Platform.is_active == True).all()
    
    return {
        "platforms": [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug
            }
            for p in platforms
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/content/ai-configs")
async def get_ai_configs(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取 AI 配置列表
    
    用于选择文章生成使用的 AI 模型配置。
    """
    from app.models import AIConfig
    
    configs = db.query(AIConfig).filter(AIConfig.is_active == True).all()
    
    return {
        "ai_configs": [
            {
                "id": c.id,
                "name": c.name,
                "model": c.model,
                "is_default": c.is_default
            }
            for c in configs
        ],
        "timestamp": datetime.now().isoformat()
    }


# ============= AI 文章生成 API =============

class ArticleGenerationRequest(BaseModel):
    """文章生成请求"""
    titles: list = Field(..., description="文章标题列表")
    section_id: int = Field(..., description="栏目ID")
    category_id: int = Field(..., description="分类ID")
    platform_id: Optional[int] = Field(None, description="平台ID（Review 栏目需要）")
    ai_config_id: Optional[int] = Field(None, description="AI配置ID")
    batch_name: Optional[str] = Field(None, description="批次名称")
    auto_publish: bool = Field(False, description="生成后是否直接发布")


@router.post("/tasks/generate-articles")
async def generate_articles(
    request: ArticleGenerationRequest,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    提交 AI 文章生成任务
    
    - **titles**: 文章标题列表（最多 100 个）
    - **section_id**: 目标栏目 ID
    - **category_id**: 目标分类 ID
    - **platform_id**: 平台 ID（Review 栏目必须）
    - **ai_config_id**: AI 配置 ID（可选，使用默认）
    - **auto_publish**: 是否自动发布（默认 false）
    
    返回:
    - **task_id**: 任务 ID，用于查询状态
    - **celery_task_id**: Celery 任务 ID
    """
    from app.models import Section, Platform, AdminUser, AIGenerationTask
    from app.tasks.ai_generation import generate_article_batch
    
    # 验证标题
    if not request.titles:
        raise HTTPException(status_code=400, detail="标题列表不能为空")
    if len(request.titles) > 100:
        raise HTTPException(status_code=400, detail="单次最多提交 100 个标题")
    
    # 验证栏目
    section = db.query(Section).filter(Section.id == request.section_id).first()
    if not section:
        raise HTTPException(status_code=400, detail=f"栏目ID {request.section_id} 不存在")
    
    # 验证平台（如果栏目需要）
    if section.requires_platform:
        if not request.platform_id:
            raise HTTPException(status_code=400, detail="该栏目需要关联平台")
        platform = db.query(Platform).filter(Platform.id == request.platform_id).first()
        if not platform:
            raise HTTPException(status_code=400, detail=f"平台ID {request.platform_id} 不存在")
    
    # 使用系统管理员作为创建者（外部 API 调用）
    admin = db.query(AdminUser).filter(AdminUser.is_superadmin == True).first()
    if not admin:
        raise HTTPException(status_code=500, detail="未找到管理员账户")
    
    try:
        # 创建任务记录
        batch_id = f"batch_{datetime.utcnow().timestamp()}_{hash(str(request.titles)) % 10000}"
        task = AIGenerationTask(
            batch_id=batch_id,
            batch_name=request.batch_name or f"OpenClaw Batch {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            titles=request.titles,
            total_count=len(request.titles),
            status="pending",
            creator_id=admin.id,
            ai_config_id=request.ai_config_id,
            section_id=request.section_id,
            category_id=request.category_id,
            platform_id=request.platform_id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 提交 Celery 任务
        celery_task = generate_article_batch.apply_async(
            args=(
                task.batch_id,
                request.titles,
                request.section_id,
                request.category_id,
                request.platform_id,
                admin.id,
                request.auto_publish
            ),
            queue='ai_generation'
        )
        
        # 保存 Celery 任务 ID
        task.celery_task_id = celery_task.id
        task.celery_status = 'PENDING'
        db.commit()
        
        return {
            "success": True,
            "task_id": task.batch_id,
            "celery_task_id": celery_task.id,
            "status": "pending",
            "message": f"已提交 {len(request.titles)} 篇文章生成任务",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    查询任务状态
    
    - **task_id**: 任务 ID（从 generate-articles 返回）
    
    返回任务进度和状态。
    """
    from app.models import AIGenerationTask
    
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
        "celery_status": task.celery_status,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/content/stats")
async def get_content_stats(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    获取内容统计
    
    返回文章、平台等数量统计。
    """
    from app.models import Article, Platform, Section, Category
    
    return {
        "stats": {
            "articles_total": db.query(Article).count(),
            "articles_published": db.query(Article).filter(Article.is_published == True).count(),
            "articles_draft": db.query(Article).filter(Article.is_published == False).count(),
            "platforms": db.query(Platform).filter(Platform.is_active == True).count(),
            "sections": db.query(Section).filter(Section.is_active == True).count(),
            "categories": db.query(Category).filter(Category.is_active == True).count()
        },
        "timestamp": datetime.now().isoformat()
    }
