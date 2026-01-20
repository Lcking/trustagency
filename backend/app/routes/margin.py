"""
两融数据 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.routes.auth import get_current_user
from app.services.tushare_service import TushareService, MarginDataService
from app.schemas.margin import (
    MarginSummaryResponse,
    MarginTrendResponse,
    MarginTrendItem,
    MarginRankingResponse,
    MarginStockItem,
    MarginStockHistoryResponse,
    MarginHistoryItem,
    MarginSearchResponse,
    MarginSearchItem,
    MarginOverviewResponse,
    SyncResultResponse,
)
from app.models.margin import MarginSummary, MarginDetail

router = APIRouter(prefix="/api/margin", tags=["两融数据"])


@router.get("/overview", response_model=MarginOverviewResponse)
async def get_margin_overview(db: Session = Depends(get_db)):
    """
    获取两融数据总览
    
    返回最新交易日的市场汇总数据和变化率
    """
    service = MarginDataService(db)
    
    # 获取最新数据
    latest_summaries = service.get_latest_summary()
    if not latest_summaries:
        raise HTTPException(status_code=404, detail="暂无两融数据，请先同步数据")
    
    trade_date = latest_summaries[0]["trade_date"]
    
    # 计算汇总
    total_rzye = sum(s["rzye"] for s in latest_summaries)
    total_rqye = sum(s["rqye"] for s in latest_summaries)
    total_rzrqye = sum(s["rzrqye"] for s in latest_summaries)
    
    # 获取前一交易日数据计算变化率
    current_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
    
    # 查找最近的前一个交易日
    prev_record = db.query(MarginSummary).filter(
        MarginSummary.trade_date < current_date
    ).order_by(MarginSummary.trade_date.desc()).first()
    
    if prev_record:
        prev_date = prev_record.trade_date
        prev_summaries = db.query(MarginSummary).filter(
            MarginSummary.trade_date == prev_date
        ).all()
        
        prev_rzye = sum(s.rzye for s in prev_summaries)
        prev_rqye = sum(s.rqye for s in prev_summaries)
        prev_rzrqye = sum(s.rzrqye for s in prev_summaries)
        
        rzye_change = ((total_rzye - prev_rzye) / prev_rzye * 100) if prev_rzye else 0
        rqye_change = ((total_rqye - prev_rqye) / prev_rqye * 100) if prev_rqye else 0
        rzrqye_change = ((total_rzrqye - prev_rzrqye) / prev_rzrqye * 100) if prev_rzrqye else 0
    else:
        rzye_change = rqye_change = rzrqye_change = 0.0
    
    return MarginOverviewResponse(
        trade_date=trade_date,
        total_rzye=total_rzye,
        total_rqye=total_rqye,
        total_rzrqye=total_rzrqye,
        rzye_change=round(rzye_change, 2),
        rqye_change=round(rqye_change, 2),
        rzrqye_change=round(rzrqye_change, 2),
        exchanges=[MarginSummaryResponse(**s) for s in latest_summaries]
    )


@router.get("/summary", response_model=List[MarginSummaryResponse])
async def get_margin_summary(db: Session = Depends(get_db)):
    """获取最新市场汇总数据"""
    service = MarginDataService(db)
    summaries = service.get_latest_summary()
    return [MarginSummaryResponse(**s) for s in summaries]


@router.get("/trend", response_model=MarginTrendResponse)
async def get_margin_trend(
    days: int = Query(30, ge=7, le=365, description="天数"),
    db: Session = Depends(get_db)
):
    """
    获取两融趋势数据
    
    Args:
        days: 获取最近多少天的数据 (7-365)
    """
    service = MarginDataService(db)
    trend_data = service.get_summary_trend(days=days)
    
    return MarginTrendResponse(
        data=[MarginTrendItem(**item) for item in trend_data],
        days=days
    )


@router.get("/ranking", response_model=MarginRankingResponse)
async def get_margin_ranking(
    order_by: str = Query("rzye", description="排序字段: rzye, rzmre, rqyl, rqmcl, net_buy"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取两融排行榜
    
    Args:
        order_by: 排序字段
            - rzye: 融资余额
            - rzmre: 融资买入额
            - rqyl: 融券余量
            - rqmcl: 融券卖出量
            - net_buy: 融资净买入
        limit: 返回数量
        trade_date: 指定交易日期
    """
    valid_order_fields = ["rzye", "rzmre", "rqyl", "rqmcl", "net_buy"]
    if order_by not in valid_order_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"无效的排序字段，可选: {', '.join(valid_order_fields)}"
        )
    
    service = MarginDataService(db)
    stocks = service.get_top_stocks(order_by=order_by, limit=limit, trade_date=trade_date)
    
    actual_date = stocks[0]["trade_date"] if stocks else trade_date
    
    return MarginRankingResponse(
        data=[MarginStockItem(**s) for s in stocks],
        order_by=order_by,
        trade_date=actual_date
    )


@router.get("/stock/{ts_code}", response_model=MarginStockHistoryResponse)
async def get_stock_margin_history(
    ts_code: str,
    days: int = Query(90, ge=7, le=365, description="历史天数"),
    db: Session = Depends(get_db)
):
    """
    获取个股两融历史数据
    
    Args:
        ts_code: 股票代码，如 600519.SH 或 600519
        days: 获取最近多少天的数据
    """
    # 规范化股票代码
    if '.' not in ts_code:
        # 尝试添加后缀
        if ts_code.startswith('6'):
            ts_code = f"{ts_code}.SH"
        elif ts_code.startswith(('0', '3')):
            ts_code = f"{ts_code}.SZ"
        elif ts_code.startswith('8') or ts_code.startswith('4'):
            ts_code = f"{ts_code}.BJ"
    
    ts_code = ts_code.upper()
    
    service = MarginDataService(db)
    history = service.get_stock_margin_history(ts_code=ts_code, days=days)
    
    if not history:
        raise HTTPException(status_code=404, detail=f"未找到股票 {ts_code} 的两融数据")
    
    # 获取股票名称
    latest = db.query(MarginDetail).filter(
        MarginDetail.ts_code == ts_code
    ).order_by(MarginDetail.trade_date.desc()).first()
    
    return MarginStockHistoryResponse(
        ts_code=ts_code,
        name=latest.name if latest else None,
        data=[MarginHistoryItem(**h) for h in history]
    )


@router.get("/search", response_model=MarginSearchResponse)
async def search_margin_stocks(
    keyword: str = Query(..., min_length=1, description="搜索关键词（股票代码或名称）"),
    limit: int = Query(20, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    搜索两融标的
    
    Args:
        keyword: 股票代码或名称关键词
        limit: 返回数量
    """
    service = MarginDataService(db)
    stocks = service.search_stocks(keyword=keyword, limit=limit)
    
    return MarginSearchResponse(
        keyword=keyword,
        data=[MarginSearchItem(**s) for s in stocks]
    )


@router.post("/sync", response_model=SyncResultResponse)
async def sync_margin_data(
    days: int = Query(30, ge=1, le=365, description="同步天数"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    同步两融数据（需要登录用户权限，生产环境由定时任务执行）
    
    Args:
        days: 同步最近多少天的数据
    """
    try:
        service = MarginDataService(db)
        
        # 同步汇总数据
        summary_count = service.sync_summary_data(days=days)
        
        # 同步最新一天的明细数据
        detail_count = service.sync_detail_data()
        
        return SyncResultResponse(
            success=True,
            message=f"同步完成：汇总 {summary_count} 条，明细 {detail_count} 条",
            summary_count=summary_count,
            detail_count=detail_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/realtime/summary")
async def get_realtime_summary(
    current_user = Depends(get_current_user)
):
    """
    获取实时两融汇总数据（直接从 Tushare 获取，不经过数据库）
    
    注意：此接口调用 Tushare API，有频率限制，需要登录
    """
    try:
        service = TushareService()
        df = service.get_margin_summary(
            start_date=(datetime.now() - timedelta(days=7)).strftime('%Y%m%d'),
            end_date=datetime.now().strftime('%Y%m%d')
        )
        
        if df.empty:
            return {"data": [], "message": "暂无数据"}
        
        # 获取最新日期的数据
        latest_date = df['trade_date'].max()
        latest_df = df[df['trade_date'] == latest_date]
        
        result = []
        for _, row in latest_df.iterrows():
            result.append({
                "trade_date": str(row['trade_date']),
                "exchange_id": row['exchange_id'],
                "exchange_name": {"SSE": "沪市", "SZSE": "深市", "BSE": "北交所"}.get(row['exchange_id'], row['exchange_id']),
                "rzye": int(row.get('rzye', 0) or 0),
                "rzmre": int(row.get('rzmre', 0) or 0),
                "rqye": int(row.get('rqye', 0) or 0),
                "rqyl": int(row.get('rqyl', 0) or 0),
                "rzrqye": int(row.get('rzrqye', 0) or 0),
            })
        
        return {"data": result, "trade_date": str(latest_date)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实时数据失败: {str(e)}")


@router.get("/realtime/stock/{ts_code}")
async def get_realtime_stock_margin(
    ts_code: str,
    days: int = Query(30, ge=1, le=90, description="天数"),
    current_user = Depends(get_current_user)
):
    """
    获取个股实时两融数据（直接从 Tushare 获取）
    
    注意：此接口调用 Tushare API，有频率限制，需要登录
    """
    # 规范化股票代码
    if '.' not in ts_code:
        if ts_code.startswith('6'):
            ts_code = f"{ts_code}.SH"
        elif ts_code.startswith(('0', '3')):
            ts_code = f"{ts_code}.SZ"
        elif ts_code.startswith('8') or ts_code.startswith('4'):
            ts_code = f"{ts_code}.BJ"
    
    ts_code = ts_code.upper()
    
    try:
        service = TushareService()
        df = service.get_margin_detail(
            ts_code=ts_code,
            start_date=(datetime.now() - timedelta(days=days)).strftime('%Y%m%d'),
            end_date=datetime.now().strftime('%Y%m%d')
        )
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"未找到股票 {ts_code} 的两融数据")
        
        result = []
        for _, row in df.iterrows():
            result.append({
                "date": str(row['trade_date']),
                "ts_code": row['ts_code'],
                "rzye": int(row.get('rzye', 0) or 0),
                "rzmre": int(row.get('rzmre', 0) or 0),
                "rzche": int(row.get('rzche', 0) or 0),
                "net_buy": int((row.get('rzmre', 0) or 0) - (row.get('rzche', 0) or 0)),
                "rqye": int(row.get('rqye', 0) or 0),
                "rqyl": int(row.get('rqyl', 0) or 0),
                "rqmcl": int(row.get('rqmcl', 0) or 0),
                "rzrqye": int(row.get('rzrqye', 0) or 0),
            })
        
        return {
            "ts_code": ts_code,
            "data": sorted(result, key=lambda x: x['date'])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实时数据失败: {str(e)}")
