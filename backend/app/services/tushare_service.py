"""
Tushare Pro 服务 - 获取融资融券数据

注意：日期时间使用服务器本地时间，假设服务器时区与中国市场时区一致（CST）
"""
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.config import settings
from app.models.margin import MarginSummary, MarginDetail
import logging

logger = logging.getLogger(__name__)


class TushareService:
    """Tushare Pro API 服务（延迟初始化）"""
    
    def __init__(self, token: str = None):
        self.token = token or settings.TUSHARE_TOKEN
        if not self.token:
            raise ValueError("Tushare token is required. Set TUSHARE_TOKEN in .env")
        # 延迟初始化：在首次使用时才设置 token 和创建 API 客户端
        self._pro = None
    
    @property
    def pro(self):
        """延迟初始化 Tushare Pro 客户端"""
        if self._pro is None:
            ts.set_token(self.token)
            self._pro = ts.pro_api()
        return self._pro
    
    def get_margin_summary(
        self, 
        start_date: str = None, 
        end_date: str = None,
        trade_date: str = None
    ) -> pd.DataFrame:
        """
        获取两融市场汇总数据
        
        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            trade_date: 指定交易日
        
        Returns:
            DataFrame with columns: trade_date, exchange_id, rzye, rzmre, rzche, rqye, rqyl, rqmcl, rzrqye
        """
        try:
            if trade_date:
                df = self.pro.margin(trade_date=trade_date)
            else:
                if not start_date:
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                if not end_date:
                    end_date = datetime.now().strftime('%Y%m%d')
                df = self.pro.margin(start_date=start_date, end_date=end_date)
            
            if df is None or df.empty:
                logger.warning("No margin summary data returned from Tushare")
                return pd.DataFrame()
            
            return df
        except Exception as e:
            logger.error(f"Failed to fetch margin summary: {e}")
            raise
    
    def get_margin_detail(
        self,
        ts_code: str = None,
        trade_date: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        获取两融个股明细数据
        
        Args:
            ts_code: 股票代码 如 600519.SH
            trade_date: 交易日期
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            DataFrame with margin detail data
        """
        try:
            if ts_code:
                if not start_date:
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                if not end_date:
                    end_date = datetime.now().strftime('%Y%m%d')
                df = self.pro.margin_detail(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif trade_date:
                df = self.pro.margin_detail(trade_date=trade_date)
            else:
                # 默认获取最近一个交易日的数据
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
                df = self.pro.margin_detail(start_date=start_date, end_date=end_date)
            
            if df is None or df.empty:
                logger.warning("No margin detail data returned from Tushare")
                return pd.DataFrame()
            
            # 处理 NaN 值
            df = df.fillna(0)
            
            return df
        except Exception as e:
            logger.error(f"Failed to fetch margin detail: {e}")
            raise
    
    def get_margin_stocks(self) -> pd.DataFrame:
        """获取两融标的列表"""
        try:
            df = self.pro.margin_target(is_new='Y')
            if df is None or df.empty:
                logger.warning("No margin stocks data returned from Tushare")
                return pd.DataFrame()
            return df
        except Exception as e:
            logger.error(f"Failed to fetch margin stocks: {e}")
            raise
    
    def get_stock_basic(self, ts_code: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            df = self.pro.stock_basic(ts_code=ts_code)
            if df is not None and not df.empty:
                return df.iloc[0].to_dict()
            return {}
        except Exception as e:
            logger.error(f"Failed to fetch stock basic info: {e}")
            return {}
    
    def get_all_stock_names(self) -> Dict[str, str]:
        """获取所有股票/ETF名称映射"""
        stock_names = {}
        try:
            # 获取股票
            df_stock = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
            if df_stock is not None and not df_stock.empty:
                stock_names.update(dict(zip(df_stock['ts_code'], df_stock['name'])))
            
            # 获取ETF
            df_fund = self.pro.fund_basic(market='E', status='L', fields='ts_code,name')
            if df_fund is not None and not df_fund.empty:
                stock_names.update(dict(zip(df_fund['ts_code'], df_fund['name'])))
            
            logger.info(f"Loaded {len(stock_names)} stock/ETF names")
            return stock_names
        except Exception as e:
            logger.error(f"Failed to fetch stock names: {e}")
            return stock_names


class MarginDataService:
    """两融数据服务 - 数据库操作"""
    
    def __init__(self, db: Session):
        self.db = db
        self._tushare = None  # 延迟初始化
        self._stock_names_cache: Dict[str, str] = None  # 实例变量
        self._stock_names_loaded = False  # 标记是否已尝试加载
    
    @property
    def tushare(self) -> TushareService:
        """延迟初始化 TushareService"""
        if self._tushare is None:
            self._tushare = TushareService()
        return self._tushare
    
    def sync_summary_data(self, days: int = 30) -> int:
        """
        同步市场汇总数据到数据库
        
        Args:
            days: 同步最近多少天的数据
        
        Returns:
            同步的记录数
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        df = self.tushare.get_margin_summary(start_date=start_date, end_date=end_date)
        if df.empty:
            return 0
        
        count = 0
        for _, row in df.iterrows():
            trade_date = datetime.strptime(str(row['trade_date']), '%Y%m%d').date()
            
            # 检查是否已存在
            existing = self.db.query(MarginSummary).filter(
                MarginSummary.trade_date == trade_date,
                MarginSummary.exchange_id == row['exchange_id']
            ).first()
            
            if existing:
                # 更新
                existing.rzye = int(row.get('rzye', 0) or 0)
                existing.rzmre = int(row.get('rzmre', 0) or 0)
                existing.rzche = int(row.get('rzche', 0) or 0)
                existing.rqye = int(row.get('rqye', 0) or 0)
                existing.rqyl = int(row.get('rqyl', 0) or 0)
                existing.rqmcl = int(row.get('rqmcl', 0) or 0)
                existing.rzrqye = int(row.get('rzrqye', 0) or 0)
            else:
                # 新增
                summary = MarginSummary(
                    trade_date=trade_date,
                    exchange_id=row['exchange_id'],
                    rzye=int(row.get('rzye', 0) or 0),
                    rzmre=int(row.get('rzmre', 0) or 0),
                    rzche=int(row.get('rzche', 0) or 0),
                    rqye=int(row.get('rqye', 0) or 0),
                    rqyl=int(row.get('rqyl', 0) or 0),
                    rqmcl=int(row.get('rqmcl', 0) or 0),
                    rzrqye=int(row.get('rzrqye', 0) or 0),
                )
                self.db.add(summary)
                count += 1
        
        self.db.commit()
        logger.info(f"Synced {count} margin summary records")
        return count
    
    def _get_stock_names(self) -> Dict[str, str]:
        """获取股票名称缓存（只加载一次，即使结果为空）"""
        if not self._stock_names_loaded:
            self._stock_names_cache = self.tushare.get_all_stock_names()
            self._stock_names_loaded = True
        return self._stock_names_cache or {}
    
    def sync_detail_data(self, trade_date: str = None) -> int:
        """
        同步个股明细数据到数据库
        
        Args:
            trade_date: 交易日期 YYYYMMDD，默认为最近交易日
        
        Returns:
            同步的记录数
        """
        if not trade_date:
            # 获取最近的交易日
            trade_date = datetime.now().strftime('%Y%m%d')
        
        df = self.tushare.get_margin_detail(trade_date=trade_date)
        if df.empty:
            return 0
        
        # 获取股票名称映射
        stock_names = self._get_stock_names()
        
        count = 0
        trade_date_obj = datetime.strptime(trade_date, '%Y%m%d').date()
        
        for _, row in df.iterrows():
            ts_code = row['ts_code']
            # 优先使用API返回的名称，否则从映射表获取
            name = row.get('name') or stock_names.get(ts_code, ts_code.split('.')[0])
            
            # 检查是否已存在
            existing = self.db.query(MarginDetail).filter(
                MarginDetail.trade_date == trade_date_obj,
                MarginDetail.ts_code == ts_code
            ).first()
            
            if not existing:
                detail = MarginDetail(
                    trade_date=trade_date_obj,
                    ts_code=ts_code,
                    name=name,
                    rzye=int(row.get('rzye', 0) or 0),
                    rzmre=int(row.get('rzmre', 0) or 0),
                    rzche=int(row.get('rzche', 0) or 0),
                    rqye=int(row.get('rqye', 0) or 0),
                    rqyl=int(row.get('rqyl', 0) or 0),
                    rqmcl=int(row.get('rqmcl', 0) or 0),
                    rqchl=int(row.get('rqchl', 0) or 0),
                    rzrqye=int(row.get('rzrqye', 0) or 0),
                )
                self.db.add(detail)
                count += 1
        
        self.db.commit()
        logger.info(f"Synced {count} margin detail records for {trade_date}")
        return count
    
    def update_stock_names(self) -> int:
        """更新数据库中缺失的股票名称（分批处理，基于ID分页避免偏移问题）"""
        stock_names = self._get_stock_names()
        if not stock_names:
            logger.warning("No stock names available for update")
            return 0
        
        batch_size = 1000
        total_count = 0
        last_id = 0
        
        while True:
            # 使用 ID 分页避免 offset 在数据变化时的问题
            batch = self.db.query(MarginDetail).filter(
                MarginDetail.id > last_id,
                MarginDetail.name.is_(None) | (MarginDetail.name == '')
            ).order_by(MarginDetail.id).limit(batch_size).all()
            
            if not batch:
                break
            
            last_id = batch[-1].id
            updated_in_batch = 0
            
            for record in batch:
                if record.ts_code in stock_names:
                    record.name = stock_names[record.ts_code]
                    updated_in_batch += 1
            
            if updated_in_batch:
                self.db.commit()
                total_count += updated_in_batch
        
        logger.info(f"Updated {total_count} stock names")
        return total_count
    
    def get_latest_summary(self) -> List[Dict[str, Any]]:
        """获取最新的市场汇总数据"""
        # 获取最新交易日
        latest = self.db.query(MarginSummary).order_by(
            MarginSummary.trade_date.desc()
        ).first()
        
        if not latest:
            return []
        
        summaries = self.db.query(MarginSummary).filter(
            MarginSummary.trade_date == latest.trade_date
        ).all()
        
        return [
            {
                "trade_date": s.trade_date.strftime('%Y-%m-%d'),
                "exchange_id": s.exchange_id,
                "exchange_name": {"SSE": "沪市", "SZSE": "深市", "BSE": "北交所"}.get(s.exchange_id, s.exchange_id),
                "rzye": s.rzye,
                "rzmre": s.rzmre,
                "rzche": s.rzche,
                "rqye": s.rqye,
                "rqyl": s.rqyl,
                "rqmcl": s.rqmcl,
                "rzrqye": s.rzrqye,
            }
            for s in summaries
        ]
    
    def get_summary_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取市场汇总趋势数据"""
        from sqlalchemy import func
        
        # 获取最新交易日作为基准
        latest = self.db.query(MarginSummary).order_by(
            MarginSummary.trade_date.desc()
        ).first()
        
        if not latest:
            return []
        
        start_date = latest.trade_date - timedelta(days=days)
        
        # 按日期聚合所有交易所数据
        results = self.db.query(
            MarginSummary.trade_date,
            func.sum(MarginSummary.rzye).label('total_rzye'),
            func.sum(MarginSummary.rqye).label('total_rqye'),
            func.sum(MarginSummary.rzrqye).label('total_rzrqye'),
        ).filter(
            MarginSummary.trade_date >= start_date
        ).group_by(
            MarginSummary.trade_date
        ).order_by(
            MarginSummary.trade_date
        ).all()
        
        return [
            {
                "date": r.trade_date.strftime('%Y-%m-%d'),
                "rzye": r.total_rzye or 0,
                "rqye": r.total_rqye or 0,
                "rzrqye": r.total_rzrqye or 0,
            }
            for r in results
        ]
    
    def get_top_stocks(
        self, 
        order_by: str = "rzye", 
        limit: int = 10,
        trade_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取排行榜数据
        
        Args:
            order_by: 排序字段 (rzye, rzmre, rqyl, rqmcl, net_buy)
            limit: 返回数量
            trade_date: 交易日期
        """
        if trade_date:
            date_obj = datetime.strptime(trade_date, '%Y-%m-%d').date()
        else:
            # 获取最新交易日
            latest = self.db.query(MarginDetail).order_by(
                MarginDetail.trade_date.desc()
            ).first()
            if not latest:
                return []
            date_obj = latest.trade_date
        
        query = self.db.query(MarginDetail).filter(
            MarginDetail.trade_date == date_obj
        )
        
        if order_by == "net_buy":
            # 融资净买入 = 融资买入 - 融资偿还
            from sqlalchemy import desc
            query = query.order_by(desc(MarginDetail.rzmre - MarginDetail.rzche))
        elif order_by == "rzye":
            query = query.order_by(MarginDetail.rzye.desc())
        elif order_by == "rqye":
            query = query.order_by(MarginDetail.rqye.desc())
        elif order_by == "rzmre":
            query = query.order_by(MarginDetail.rzmre.desc())
        elif order_by == "rqyl":
            query = query.order_by(MarginDetail.rqyl.desc())
        elif order_by == "rqmcl":
            query = query.order_by(MarginDetail.rqmcl.desc())
        else:
            query = query.order_by(MarginDetail.rzye.desc())
        
        stocks = query.limit(limit).all()
        
        return [
            {
                "ts_code": s.ts_code,
                "name": s.name or s.ts_code.split('.')[0],
                "trade_date": s.trade_date.strftime('%Y-%m-%d'),
                "rzye": s.rzye,
                "rzmre": s.rzmre,
                "rzche": s.rzche,
                "net_buy": s.rzmre - s.rzche,
                "rqye": s.rqye,
                "rqyl": s.rqyl,
                "rqmcl": s.rqmcl,
                "rzrqye": s.rzrqye,
            }
            for s in stocks
        ]
    
    def get_stock_margin_history(
        self, 
        ts_code: str, 
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """获取个股两融历史数据"""
        # 获取该股票的最新交易日作为基准
        latest = self.db.query(MarginDetail).filter(
            MarginDetail.ts_code == ts_code
        ).order_by(
            MarginDetail.trade_date.desc()
        ).first()
        
        if not latest:
            return []
        
        start_date = latest.trade_date - timedelta(days=days)
        
        details = self.db.query(MarginDetail).filter(
            MarginDetail.ts_code == ts_code,
            MarginDetail.trade_date >= start_date
        ).order_by(
            MarginDetail.trade_date
        ).all()
        
        return [
            {
                "date": d.trade_date.strftime('%Y-%m-%d'),
                "rzye": d.rzye,
                "rzmre": d.rzmre,
                "rzche": d.rzche,
                "net_buy": d.rzmre - d.rzche,
                "rqye": d.rqye,
                "rqyl": d.rqyl,
                "rqmcl": d.rqmcl,
                "rzrqye": d.rzrqye,
            }
            for d in details
        ]
    
    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索两融标的"""
        # 从明细数据中搜索（有历史数据的股票）
        from sqlalchemy import or_
        
        # 获取最新交易日
        latest = self.db.query(MarginDetail).order_by(
            MarginDetail.trade_date.desc()
        ).first()
        
        if not latest:
            return []
        
        stocks = self.db.query(MarginDetail).filter(
            MarginDetail.trade_date == latest.trade_date,
            or_(
                MarginDetail.ts_code.contains(keyword.upper()),
                MarginDetail.name.contains(keyword)
            )
        ).limit(limit).all()
        
        return [
            {
                "ts_code": s.ts_code,
                "name": s.name or s.ts_code.split('.')[0],
                "rzye": s.rzye,
                "rqyl": s.rqyl,
            }
            for s in stocks
        ]
