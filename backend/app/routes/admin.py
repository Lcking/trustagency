"""
管理后台路由模块
提供基本的数据管理API和统计功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import AdminUser, Platform, Article, AIGenerationTask
from app.schemas import (
    PlatformResponse,
    ArticleResponse,
    AITaskResponse,
    PaginationResponse,
    StatsResponse,
)

# 创建路由
admin_router = APIRouter()


# ==================== 仪表板统计 ====================

@admin_router.get(
    "/stats",
    response_model=StatsResponse,
    summary="获取仪表板统计数据"
)
async def get_dashboard_stats(
    db: Session = Depends(get_db)
) -> StatsResponse:
    """获取平台、文章、任务的统计数据"""
    
    platforms_count = db.query(func.count(Platform.id)).scalar()
    articles_count = db.query(func.count(Article.id)).scalar()
    published_articles = db.query(func.count(Article.id)).filter(Article.is_published == True).scalar()
    active_tasks = db.query(func.count(AIGenerationTask.id)).filter(
        AIGenerationTask.status.in_(["pending", "processing"])
    ).scalar()
    total_views = db.query(func.sum(Article.view_count)).scalar() or 0
    
    return StatsResponse(
        platforms_count=platforms_count,
        articles_count=articles_count,
        published_articles=published_articles,
        active_tasks=active_tasks,
        total_views=int(total_views)
    )


# ==================== 平台管理 ====================

@admin_router.get(
    "/platforms",
    response_model=PaginationResponse[PlatformResponse],
    summary="获取平台列表"
)
async def list_platforms(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
) -> PaginationResponse[PlatformResponse]:
    """获取平台列表"""
    
    query = db.query(Platform)
    
    if search:
        query = query.filter(
            (Platform.name.ilike(f"%{search}%")) |
            (Platform.description.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.filter(Platform.is_active == is_active)
    
    total = query.count()
    platforms = query.offset(skip).limit(limit).all()
    
    return PaginationResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[PlatformResponse.from_orm(p) for p in platforms]
    )


# ==================== 文章管理 ====================

@admin_router.get(
    "/articles",
    response_model=PaginationResponse[ArticleResponse],
    summary="获取文章列表"
)
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
) -> PaginationResponse[ArticleResponse]:
    """获取文章列表"""
    
    query = db.query(Article)
    
    if search:
        query = query.filter(
            (Article.title.ilike(f"%{search}%")) |
            (Article.slug.ilike(f"%{search}%"))
        )
    
    if category_id:
        query = query.filter(Article.category_id == category_id)
    
    total = query.count()
    articles = query.offset(skip).limit(limit).all()
    
    return PaginationResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[ArticleResponse.from_orm(a) for a in articles]
    )


# ==================== AI 生成任务管理 ====================

@admin_router.get(
    "/ai-tasks",
    response_model=PaginationResponse[AITaskResponse],
    summary="获取AI任务列表"
)
async def list_ai_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> PaginationResponse[AITaskResponse]:
    """获取AI生成任务列表"""
    
    query = db.query(AIGenerationTask)
    
    if status:
        query = query.filter(AIGenerationTask.status == status)
    
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    
    return PaginationResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[AITaskResponse.from_orm(t) for t in tasks]
    )


# ==================== OpenAI 服务检查 ====================

@admin_router.get(
    "/openai-health",
    summary="检查 OpenAI 服务状态"
)
async def check_openai_health():
    """检查 OpenAI API 连接状态"""
    try:
        from app.services.openai_service import OpenAIService
        health = OpenAIService.health_check()
        return health
    except Exception as e:
        return {
            "status": "error",
            "message": "OpenAI 服务检查失败",
            "error": str(e)
        }
