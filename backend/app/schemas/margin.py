"""
两融数据 Pydantic 模式
"""
from pydantic import BaseModel
from typing import Optional, List


class MarginSummaryResponse(BaseModel):
    """市场汇总响应"""
    trade_date: str
    exchange_id: str
    exchange_name: str
    rzye: int          # 融资余额
    rzmre: int         # 融资买入额
    rzche: int = 0     # 融资偿还额
    rqye: int          # 融券余额
    rqyl: int          # 融券余量
    rqmcl: int         # 融券卖出量
    rzrqye: int        # 融资融券余额
    
    class Config:
        from_attributes = True


class MarginTrendItem(BaseModel):
    """趋势数据项"""
    date: str
    rzye: int          # 融资余额
    rqye: int          # 融券余额
    rzrqye: int        # 融资融券余额


class MarginTrendResponse(BaseModel):
    """趋势数据响应"""
    data: List[MarginTrendItem]
    days: int


class MarginStockItem(BaseModel):
    """个股两融数据"""
    ts_code: str
    name: str
    trade_date: str
    rzye: int          # 融资余额
    rzmre: int         # 融资买入额
    rzche: int         # 融资偿还额
    net_buy: int       # 融资净买入
    rqye: int          # 融券余额
    rqyl: int          # 融券余量
    rqmcl: int         # 融券卖出量
    rzrqye: int        # 融资融券余额


class MarginRankingResponse(BaseModel):
    """排行榜响应"""
    data: List[MarginStockItem]
    order_by: str
    trade_date: Optional[str] = None


class MarginHistoryItem(BaseModel):
    """历史数据项"""
    date: str
    rzye: int
    rzmre: int
    rzche: int
    net_buy: int
    rqye: int
    rqyl: int
    rqmcl: int
    rzrqye: int


class MarginStockHistoryResponse(BaseModel):
    """个股历史数据响应"""
    ts_code: str
    name: Optional[str] = None
    data: List[MarginHistoryItem]


class MarginSearchItem(BaseModel):
    """搜索结果项"""
    ts_code: str
    name: str
    rzye: int
    rqyl: int


class MarginSearchResponse(BaseModel):
    """搜索响应"""
    keyword: str
    data: List[MarginSearchItem]


class MarginOverviewResponse(BaseModel):
    """两融总览响应"""
    trade_date: str
    total_rzye: int        # 总融资余额
    total_rqye: int        # 总融券余额
    total_rzrqye: int      # 总两融余额
    rzye_change: float     # 融资余额变化率
    rqye_change: float     # 融券余额变化率
    rzrqye_change: float   # 两融余额变化率
    exchanges: List[MarginSummaryResponse]


class SyncResultResponse(BaseModel):
    """数据同步结果"""
    success: bool
    message: str
    summary_count: int = 0
    detail_count: int = 0
