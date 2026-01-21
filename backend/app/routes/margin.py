"""
两融数据 API 路由

提供融资融券数据查询接口，包括市场汇总、趋势、排行榜和个股明细
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import logging

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
from app.utils.cache import cached, invalidate_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/margin", tags=["两融数据"])


def _calculate_change_rate(current: float, previous: float) -> float:
    """计算变化率，安全处理除零情况"""
    if not previous or previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 2)


@router.get("/overview", response_model=MarginOverviewResponse)
async def get_margin_overview(db: Session = Depends(get_db)):
    """
    获取两融数据总览
    
    返回最新交易日的市场汇总数据和变化率
    缓存 5 分钟以减少数据库压力
    """
    try:
        service = MarginDataService(db)
        
        # 获取最新数据
        latest_summaries = service.get_latest_summary()
        if not latest_summaries:
            raise HTTPException(
                status_code=404, 
                detail="No margin data available. Please sync data first."
            )
        
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
            
            rzye_change = _calculate_change_rate(total_rzye, prev_rzye)
            rqye_change = _calculate_change_rate(total_rqye, prev_rqye)
            rzrqye_change = _calculate_change_rate(total_rzrqye, prev_rzrqye)
        else:
            rzye_change = rqye_change = rzrqye_change = 0.0
        
        return MarginOverviewResponse(
            trade_date=trade_date,
            total_rzye=total_rzye,
            total_rqye=total_rqye,
            total_rzrqye=total_rzrqye,
            rzye_change=rzye_change,
            rqye_change=rqye_change,
            rzrqye_change=rzrqye_change,
            exchanges=[MarginSummaryResponse(**s) for s in latest_summaries]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get margin overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary", response_model=List[MarginSummaryResponse])
async def get_margin_summary(db: Session = Depends(get_db)):
    """获取最新市场汇总数据"""
    try:
        service = MarginDataService(db)
        summaries = service.get_latest_summary()
        return [MarginSummaryResponse(**s) for s in summaries]
    except Exception as e:
        logger.error(f"Failed to get margin summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
    try:
        service = MarginDataService(db)
        trend_data = service.get_summary_trend(days=days)
        
        return MarginTrendResponse(
            data=[MarginTrendItem(**item) for item in trend_data],
            days=days
        )
    except Exception as e:
        logger.error(f"Failed to get margin trend: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# 有效的排序字段常量
VALID_ORDER_FIELDS = frozenset(["rzye", "rqye", "rzmre", "rqyl", "rqmcl", "net_buy"])


@router.get("/ranking", response_model=MarginRankingResponse)
async def get_margin_ranking(
    order_by: str = Query("rzye", description="排序字段: rzye, rqye, rzmre, rqyl, rqmcl, net_buy"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取两融排行榜
    
    Args:
        order_by: 排序字段
            - rzye: 融资余额
            - rqye: 融券余额
            - rzmre: 融资买入额
            - rqyl: 融券余量
            - rqmcl: 融券卖出量
            - net_buy: 融资净买入
        limit: 返回数量
        trade_date: 指定交易日期
    """
    if order_by not in VALID_ORDER_FIELDS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid order field. Valid options: {', '.join(sorted(VALID_ORDER_FIELDS))}"
        )
    
    try:
        service = MarginDataService(db)
        stocks = service.get_top_stocks(order_by=order_by, limit=limit, trade_date=trade_date)
        
        actual_date = stocks[0]["trade_date"] if stocks else trade_date
        
        return MarginRankingResponse(
            data=[MarginStockItem(**s) for s in stocks],
            order_by=order_by,
            trade_date=actual_date
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get margin ranking: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _normalize_ts_code(ts_code: str) -> str:
    """
    规范化股票代码格式
    
    Args:
        ts_code: 输入的股票代码，如 600519 或 600519.SH
    
    Returns:
        规范化后的股票代码，如 600519.SH
    """
    ts_code = ts_code.strip().upper()
    
    if '.' in ts_code:
        return ts_code
    
    # 根据代码前缀自动添加后缀
    if ts_code.startswith('6'):
        return f"{ts_code}.SH"
    elif ts_code.startswith(('0', '3')):
        return f"{ts_code}.SZ"
    elif ts_code.startswith(('8', '4')):
        return f"{ts_code}.BJ"
    elif ts_code.startswith(('5', '1')):
        # ETF 基金，需要根据交易所判断
        # 5xx 开头是上交所，1xx 开头是深交所
        return f"{ts_code}.SH" if ts_code.startswith('5') else f"{ts_code}.SZ"
    
    return ts_code


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
    try:
        ts_code = _normalize_ts_code(ts_code)
        
        service = MarginDataService(db)
        history = service.get_stock_margin_history(ts_code=ts_code, days=days)
        
        if not history:
            raise HTTPException(
                status_code=404, 
                detail=f"No margin data found for stock {ts_code}"
            )
        
        # 获取股票名称
        latest = db.query(MarginDetail).filter(
            MarginDetail.ts_code == ts_code
        ).order_by(MarginDetail.trade_date.desc()).first()
        
        return MarginStockHistoryResponse(
            ts_code=ts_code,
            name=latest.name if latest else None,
            data=[MarginHistoryItem(**h) for h in history]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stock margin history for {ts_code}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=MarginSearchResponse)
async def search_margin_stocks(
    keyword: str = Query(..., min_length=1, max_length=50, description="搜索关键词（股票代码或名称）"),
    limit: int = Query(20, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    搜索两融标的
    
    Args:
        keyword: 股票代码或名称关键词
        limit: 返回数量
    """
    try:
        # 清理关键词
        keyword = keyword.strip()
        
        service = MarginDataService(db)
        stocks = service.search_stocks(keyword=keyword, limit=limit)
        
        return MarginSearchResponse(
            keyword=keyword,
            data=[MarginSearchItem(**s) for s in stocks]
        )
    except Exception as e:
        logger.error(f"Failed to search margin stocks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        
        # 同步成功后清除相关缓存
        invalidate_cache("margin")
        
        logger.info(f"Margin data sync completed: summary={summary_count}, detail={detail_count}")
        
        return SyncResultResponse(
            success=True,
            message=f"Sync completed: {summary_count} summary records, {detail_count} detail records",
            summary_count=summary_count,
            detail_count=detail_count
        )
    except Exception as e:
        logger.error(f"Failed to sync margin data: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# 交易所名称映射
EXCHANGE_NAMES = {
    "SSE": "沪市",
    "SZSE": "深市", 
    "BSE": "北交所"
}


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
            return {"data": [], "message": "No data available"}
        
        # 获取最新日期的数据
        latest_date = df['trade_date'].max()
        latest_df = df[df['trade_date'] == latest_date]
        
        result = []
        for _, row in latest_df.iterrows():
            exchange_id = row['exchange_id']
            result.append({
                "trade_date": str(row['trade_date']),
                "exchange_id": exchange_id,
                "exchange_name": EXCHANGE_NAMES.get(exchange_id, exchange_id),
                "rzye": int(row.get('rzye', 0) or 0),
                "rzmre": int(row.get('rzmre', 0) or 0),
                "rqye": int(row.get('rqye', 0) or 0),
                "rqyl": int(row.get('rqyl', 0) or 0),
                "rzrqye": int(row.get('rzrqye', 0) or 0),
            })
        
        return {"data": result, "trade_date": str(latest_date)}
    except Exception as e:
        logger.error(f"Failed to get realtime summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch realtime data")


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
    ts_code = _normalize_ts_code(ts_code)
    
    try:
        service = TushareService()
        df = service.get_margin_detail(
            ts_code=ts_code,
            start_date=(datetime.now() - timedelta(days=days)).strftime('%Y%m%d'),
            end_date=datetime.now().strftime('%Y%m%d')
        )
        
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No margin data found for stock {ts_code}"
            )
        
        result = []
        for _, row in df.iterrows():
            rzmre = int(row.get('rzmre', 0) or 0)
            rzche = int(row.get('rzche', 0) or 0)
            result.append({
                "date": str(row['trade_date']),
                "ts_code": row['ts_code'],
                "rzye": int(row.get('rzye', 0) or 0),
                "rzmre": rzmre,
                "rzche": rzche,
                "net_buy": rzmre - rzche,
                "rqye": int(row.get('rqye', 0) or 0),
                "rqyl": int(row.get('rqyl', 0) or 0),
                "rqmcl": int(row.get('rqmcl', 0) or 0),
                "rzrqye": int(row.get('rzrqye', 0) or 0),
            })
        
        # 按日期排序
        result.sort(key=lambda x: x['date'])
        
        return {
            "ts_code": ts_code,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get realtime stock margin for {ts_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch realtime data")
