"""
文章管理 API 路由
提供文章的 CRUD 端点、发布、搜索、分类等功能

改进:
- 统一的异常处理 (使用 app.utils.exceptions)
- 标准化的响应格式 (使用 app.schemas.response)
- 清晰的错误消息
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser, Article, Section
from app.routes.auth import get_current_user
from app.services.article_service import ArticleService
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
)
from app.utils.exceptions import (
    ResourceNotFound,
    ValidationError,
    raise_resource_not_found,
)
from typing import Optional
import os

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get(
    "",
    response_model=ArticleListResponse,
    summary="获取文章列表",
    description="获取文章列表，支持搜索、分类、平台、排序和分页过滤",
    responses={
        200: {
            "description": "成功获取文章列表",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": 1,
                                "title": "Bitcoin 初学者指南",
                                "slug": "bitcoin-beginner-guide",
                                "content": "完整的 HTML 内容...",
                                "summary": "快速了解 Bitcoin",
                                "category": "教程",
                                "tags": ["bitcoin", "初学者"],
                                "is_published": True,
                                "is_featured": True,
                                "author": {"id": 1, "username": "admin"},
                                "view_count": 1200,
                                "like_count": 89,
                                "created_at": "2025-11-01T10:00:00",
                                "updated_at": "2025-11-12T15:30:00"
                            }
                        ],
                        "total": 150,
                        "skip": 0,
                        "limit": 10
                    }
                }
            }
        }
    }
)
async def list_articles(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数，最多 100"),
    search: Optional[str] = Query(None, description="搜索关键词（标题、内容、摘要、标签）"),
    category_id: Optional[int] = Query(None, description="分类 ID 过滤"),
    platform_id: Optional[int] = Query(None, description="平台 ID 过滤"),
    author_id: Optional[int] = Query(None, description="作者 ID 过滤"),
    is_published: Optional[bool] = Query(None, description="发布状态：true/false/null(全部)"),
    is_featured: Optional[bool] = Query(None, description="精选状态：true/false/null(全部)"),
    sort_by: str = Query("created_at", description="排序字段：created_at, updated_at, title, view_count, like_count"),
    sort_order: str = Query("desc", description="排序顺序：asc(升序) 或 desc(降序)"),
    db: Session = Depends(get_db),
):
    """
    获取文章列表
    
    支持以下功能：
    - **搜索**: 按标题、内容、摘要、标签搜索
    - **分类过滤**: 按分类ID过滤
    - **平台过滤**: 按平台过滤
    - **排序**: 按多个字段排序
    - **分页**: 支持分页查询
    
    示例:
    ```
    GET /api/articles?search=bitcoin&category_id=5&sort_by=like_count&sort_order=desc&limit=20
    ```
    """
    articles, total = ArticleService.get_articles(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id,
        platform_id=platform_id,
        author_id=author_id,
        is_published=is_published,
        is_featured=is_featured,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    article_responses = [ArticleResponse.model_validate(a) for a in articles]
    return ArticleListResponse(
        data=article_responses, total=total, skip=skip, limit=limit
    )


@router.post("", response_model=ArticleResponse, status_code=201)
async def create_article(
    article_data: ArticleCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新文章
    
    只有管理员可以创建文章。系统会自动：
    - 生成 URL 友好的 slug
    - 设置作者为当前登录用户
    - 设置创建时间和最后更新时间
    - 验证栏目是否需要平台关联
    
    请求体示例:
    ```json
    {
        "title": "Bitcoin 初学者指南",
        "content": "这是一篇完整的 Bitcoin 介绍文章...",
        "summary": "快速了解 Bitcoin 的要点",
        "section_id": 2,
        "category": "教程",
        "tags": ["bitcoin", "加密货币", "初学者"],
        "meta_description": "Learn about Bitcoin",
        "meta_keywords": "bitcoin, cryptocurrency",
        "is_featured": true,
        "platform_id": 1
    }
    ```
    """
    try:
        # 验证栏目是否存在
        section = db.query(Section).filter(Section.id == article_data.section_id).first()
        if not section:
            raise HTTPException(status_code=400, detail=f"栏目 ID {article_data.section_id} 不存在")
        
        # 验证平台关联逻辑
        if section.requires_platform:
            # 该栏目需要关联平台
            if not article_data.platform_id:
                raise HTTPException(status_code=400, detail=f"栏目 '{section.name}' 需要关联平台")
        else:
            # 该栏目不需要平台，设为 None
            article_data.platform_id = None
        
        article = ArticleService.create_article(
            db,
            article_data,
            author_id=current_user.id,
        )
        return ArticleResponse.model_validate(article)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    """
    获取单个文章信息
    
    自动增加文章的浏览量。
    
    Args:
        article_id: 文章 ID
        
    示例:
    ```
    GET /api/articles/1
    ```
    """
    article = ArticleService.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
    return ArticleResponse.model_validate(article)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新文章信息
    
    只有管理员可以更新文章。只需提供要更新的字段。
    
    请求体示例:
    ```json
    {
        "title": "Bitcoin 初学者指南 - 更新版",
        "summary": "新的摘要",
        "is_featured": true
    }
    ```
    """
    try:
        article = ArticleService.update_article(db, article_id, article_data)
        if not article:
            raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
        return ArticleResponse.model_validate(article)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除文章
    
    只有管理员可以删除文章。
    """
    success = ArticleService.delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
    return None


@router.post("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    发布文章
    
    将文章标记为已发布，并记录发布时间。
    """
    article = ArticleService.publish_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
    return ArticleResponse.model_validate(article)


@router.post("/{article_id}/unpublish", response_model=ArticleResponse)
async def unpublish_article(
    article_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    取消发布文章
    
    将文章标记为未发布状态。
    """
    article = ArticleService.unpublish_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
    return ArticleResponse.model_validate(article)


@router.post("/{article_id}/toggle-featured", response_model=ArticleResponse)
async def toggle_featured_article(
    article_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    切换文章精选状态
    
    只有管理员可以切换精选状态。
    """
    article = ArticleService.toggle_featured(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
    return ArticleResponse.model_validate(article)


@router.post("/{article_id}/like", response_model=ArticleResponse)
async def like_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    """
    点赞文章
    
    增加文章的点赞数（不需要认证）。
    """
    article = ArticleService.like_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 ID {article_id} 不存在")
    return ArticleResponse.model_validate(article)


@router.get("/search/by-keyword", response_model=list[ArticleResponse])
async def search_articles(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="最大返回数"),
    db: Session = Depends(get_db),
):
    """
    搜索已发布的文章
    
    按关键词搜索标题、内容、摘要和标签。
    
    示例:
    ```
    GET /api/articles/search/by-keyword?keyword=bitcoin&limit=30
    ```
    """
    articles = ArticleService.search_articles(db, keyword, limit)
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/featured/list", response_model=list[ArticleResponse])
async def get_featured_articles(
    limit: int = Query(5, ge=1, le=20, description="最大返回数"),
    db: Session = Depends(get_db),
):
    """
    获取精选文章列表
    
    获取已标记为精选且已发布的文章。
    
    示例:
    ```
    GET /api/articles/featured/list?limit=10
    ```
    """
    articles = ArticleService.get_featured_articles(db, limit)
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/trending/list", response_model=list[ArticleResponse])
async def get_trending_articles(
    limit: int = Query(10, ge=1, le=50, description="最大返回数"),
    db: Session = Depends(get_db),
):
    """
    获取热门文章列表
    
    按点赞数和浏览量排序的文章列表。
    
    示例:
    ```
    GET /api/articles/trending/list?limit=20
    ```
    """
    articles = ArticleService.get_trending_articles(db, limit)
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/by-platform/{platform_id}", response_model=list[ArticleResponse])
async def get_articles_by_platform(
    platform_id: int,
    limit: int = Query(10, ge=1, le=100, description="最大返回数"),
    db: Session = Depends(get_db),
):
    """
    获取特定平台的文章
    
    示例:
    ```
    GET /api/articles/by-platform/1?limit=20
    ```
    """
    articles = ArticleService.get_articles_by_platform(db, platform_id, limit=limit)
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/by-author/{author_id}", response_model=list[ArticleResponse])
async def get_articles_by_author(
    author_id: int,
    limit: int = Query(10, ge=1, le=100, description="最大返回数"),
    db: Session = Depends(get_db),
):
    """
    获取作者发布的文章
    
    示例:
    ```
    GET /api/articles/by-author/1?limit=20
    ```
    """
    articles = ArticleService.get_articles_by_author(db, author_id, limit=limit)
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/by-slug/{slug}", response_model=ArticleResponse)
async def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    通过 slug 获取单篇已发布文章（用于前端 SEO 友好的 URL）
    
    示例:
    ```
    GET /api/articles/by-slug/bitcoin-beginner-guide
    ```
    """
    article = db.query(Article).filter(
        Article.slug == slug,
        Article.is_published == True
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加浏览量
    article.view_count = (article.view_count or 0) + 1
    db.commit()
    db.refresh(article)
    
    return ArticleResponse.model_validate(article)


@router.get("/by-section/{section_slug}", response_model=list[ArticleResponse])
async def get_articles_by_section(
    section_slug: str,
    limit: int = Query(100, ge=1, le=500, description="最大返回数"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    db: Session = Depends(get_db),
):
    """
    按栏目获取发布的文章（用于前端页面动态加载）
    
    示例:
    ```
    GET /api/articles/by-section/wiki?limit=50
    GET /api/articles/by-section/faq?limit=20
    ```
    
    支持的 section_slug: wiki, faq, guide, review
    """
    from sqlalchemy.orm import joinedload
    
    # 查询栏目
    section = db.query(Section).filter(Section.slug == section_slug).first()
    if not section:
        return []
    
    # 查询该栏目下已发布的文章
    articles = db.query(Article).filter(
        Article.section_id == section.id,
        Article.is_published == True
    ).options(
        joinedload(Article.section),
        joinedload(Article.category_obj)
    ).order_by(
        Article.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [ArticleResponse.model_validate(a) for a in articles]
