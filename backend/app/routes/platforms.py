"""
平台管理 API 路由
提供平台的 CRUD 端点、搜索、排序、分页功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser
from app.routes.auth import get_current_user
from app.services.platform_service import PlatformService
from app.schemas.platform import (
    PlatformCreate,
    PlatformUpdate,
    PlatformResponse,
    PlatformListResponse,
)
from typing import Optional

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


@router.get("", response_model=PlatformListResponse)
async def list_platforms(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    search: Optional[str] = Query(None, description="搜索关键词（名称、描述）"),
    sort_by: str = Query("rank", description="排序字段: name, rank, rating, commission_rate, created_at"),
    sort_order: str = Query("asc", description="排序顺序: asc, desc"),
    is_active: Optional[bool] = Query(None, description="过滤活跃平台"),
    is_featured: Optional[bool] = Query(None, description="过滤精选平台"),
    db: Session = Depends(get_db),
):
    """
    获取平台列表
    
    支持以下功能：
    - **搜索**: 按名称或描述搜索
    - **排序**: 按多个字段排序
    - **分页**: 支持分页查询
    - **过滤**: 按活跃、精选状态过滤
    
    示例:
    ```
    GET /api/platforms?search=binance&sort_by=rank&sort_order=asc&limit=20
    ```
    """
    platforms, total = PlatformService.get_platforms(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
        is_featured=is_featured,
    )

    platform_responses = [PlatformResponse.model_validate(p) for p in platforms]
    return PlatformListResponse(
        data=platform_responses, total=total, skip=skip, limit=limit
    )


@router.post("", response_model=PlatformResponse, status_code=201)
async def create_platform(
    platform_data: PlatformCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新平台
    
    只有管理员可以创建平台。
    
    请求体示例:
    ```json
    {
        "name": "Binance",
        "description": "全球最大的加密货币交易所",
        "rating": 4.8,
        "rank": 1,
        "min_leverage": 1.0,
        "max_leverage": 125.0,
        "commission_rate": 0.001,
        "is_regulated": true,
        "logo_url": "https://...",
        "website_url": "https://binance.com",
        "is_featured": true
    }
    ```
    """
    try:
        platform = PlatformService.create_platform(db, platform_data)
        return PlatformResponse.model_validate(platform)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{platform_id}", response_model=PlatformResponse)
async def get_platform(
    platform_id: int,
    db: Session = Depends(get_db),
):
    """
    获取单个平台信息
    
    Args:
        platform_id: 平台 ID
        
    示例:
    ```
    GET /api/platforms/1
    ```
    """
    platform = PlatformService.get_platform(db, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
    return PlatformResponse.model_validate(platform)


@router.put("/{platform_id}", response_model=PlatformResponse)
async def update_platform(
    platform_id: int,
    platform_data: PlatformUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新平台信息
    
    只有管理员可以更新平台。只需提供要更新的字段。
    
    请求体示例:
    ```json
    {
        "rating": 4.9,
        "rank": 2,
        "is_featured": true
    }
    ```
    """
    try:
        platform = PlatformService.update_platform(db, platform_id, platform_data)
        if not platform:
            raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
        return PlatformResponse.model_validate(platform)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{platform_id}", status_code=204)
async def delete_platform(
    platform_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除平台
    
    只有管理员可以删除平台。
    """
    success = PlatformService.delete_platform(db, platform_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
    return None


@router.post("/{platform_id}/toggle-status", response_model=PlatformResponse)
async def toggle_platform_status(
    platform_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    切换平台活跃状态（启用/禁用）
    
    只有管理员可以切换状态。
    
    示例:
    ```
    POST /api/platforms/1/toggle-status
    ```
    """
    platform = PlatformService.toggle_platform_status(db, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
    return PlatformResponse.model_validate(platform)


@router.post("/{platform_id}/toggle-featured", response_model=PlatformResponse)
async def toggle_platform_featured(
    platform_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    切换平台精选状态
    
    只有管理员可以切换精选状态。
    
    示例:
    ```
    POST /api/platforms/1/toggle-featured
    ```
    """
    platform = PlatformService.toggle_platform_featured(db, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
    return PlatformResponse.model_validate(platform)


@router.post("/bulk/update-ranks", status_code=200)
async def bulk_update_ranks(
    rank_data: dict,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    批量更新平台排名
    
    只有管理员可以更新排名。这是管理员问"如果我用方案1，然后平台内容新增了5个平台，
    想给这5个平台进行排名的话，好操作吗？"的答案。
    
    请求体示例:
    ```json
    {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5
    }
    ```
    
    响应示例:
    ```json
    {
        "updated_count": 5,
        "message": "成功更新 5 个平台的排名"
    }
    ```
    """
    try:
        updated_count = PlatformService.update_platform_ranks(db, rank_data)
        return {
            "updated_count": updated_count,
            "message": f"成功更新 {updated_count} 个平台的排名"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/featured/list", response_model=list[PlatformResponse])
async def get_featured_platforms(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """
    获取精选平台列表
    
    获取已标记为精选且活跃的平台。
    
    示例:
    ```
    GET /api/platforms/featured/list?limit=10
    ```
    """
    platforms = PlatformService.get_featured_platforms(db, limit=limit)
    return [PlatformResponse.model_validate(p) for p in platforms]


@router.get("/regulated/list", response_model=list[PlatformResponse])
async def get_regulated_platforms(
    db: Session = Depends(get_db),
):
    """
    获取监管平台列表
    
    获取所有已监管认证的活跃平台。
    
    示例:
    ```
    GET /api/platforms/regulated/list
    ```
    """
    platforms = PlatformService.get_regulated_platforms(db)
    return [PlatformResponse.model_validate(p) for p in platforms]
