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
    summary_count: int = Field(description="同步的汇总数据条数")
    detail_count: int = Field(description="同步的明细数据条数")
    synced_dates: list = Field(description="成功同步的日期列表")
    skipped_dates: list = Field(description="跳过的日期列表（已有数据或无数据）")
    errors: list = Field(description="错误信息列表")
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
        from app.services.tushare_service import TushareService
        
        service = TushareService(db)
        
        summary_count = 0
        detail_count = 0
        synced_dates = []
        skipped_dates = []
        errors = []
        
        # 同步汇总数据
        try:
            summary_count = service.sync_summary_data()
        except Exception as e:
            errors.append(f"汇总数据同步失败: {str(e)}")
        
        # 同步明细数据（最近 N 天）
        for i in range(request.days):
            trade_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
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
        
        return SyncMarginResponse(
            success=len(errors) == 0,
            summary_count=summary_count,
            detail_count=detail_count,
            synced_dates=synced_dates,
            skipped_dates=skipped_dates,
            errors=errors,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return SyncMarginResponse(
            success=False,
            summary_count=0,
            detail_count=0,
            synced_dates=[],
            skipped_dates=[],
            errors=[str(e)],
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
