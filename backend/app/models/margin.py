"""
两融数据模型 - 融资融券数据存储
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index, BigInteger
from sqlalchemy.sql import func
from app.database import Base


class MarginSummary(Base):
    """两融市场汇总数据"""
    __tablename__ = "margin_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, nullable=False, index=True)
    exchange_id = Column(String(10), nullable=False)  # SSE(沪市), SZSE(深市), BSE(北交所)
    
    # 融资数据
    rzye = Column(BigInteger, default=0)      # 融资余额（元）
    rzmre = Column(BigInteger, default=0)     # 融资买入额（元）
    rzche = Column(BigInteger, default=0)     # 融资偿还额（元）
    
    # 融券数据
    rqye = Column(BigInteger, default=0)      # 融券余额（元）
    rqyl = Column(BigInteger, default=0)      # 融券余量（股）
    rqmcl = Column(BigInteger, default=0)     # 融券卖出量（股）
    rqchl = Column(BigInteger, default=0)     # 融券偿还量（股）
    
    # 两融合计
    rzrqye = Column(BigInteger, default=0)    # 融资融券余额（元）
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('ix_margin_summary_date_exchange', 'trade_date', 'exchange_id', unique=True),
    )
    
    def __repr__(self):
        return f"<MarginSummary(date={self.trade_date}, exchange={self.exchange_id})>"


class MarginDetail(Base):
    """两融个股明细数据"""
    __tablename__ = "margin_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, nullable=False, index=True)
    ts_code = Column(String(20), nullable=False, index=True)  # 股票代码 如 600519.SH
    name = Column(String(50))                                  # 股票名称
    
    # 融资数据
    rzye = Column(BigInteger, default=0)      # 融资余额（元）
    rzmre = Column(BigInteger, default=0)     # 融资买入额（元）
    rzche = Column(BigInteger, default=0)     # 融资偿还额（元）
    
    # 融券数据
    rqye = Column(BigInteger, default=0)      # 融券余额（元）
    rqyl = Column(BigInteger, default=0)      # 融券余量（股）
    rqmcl = Column(BigInteger, default=0)     # 融券卖出量（股）
    rqchl = Column(BigInteger, default=0)     # 融券偿还量（股）
    
    # 两融合计
    rzrqye = Column(BigInteger, default=0)    # 融资融券余额（元）
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('ix_margin_detail_date_code', 'trade_date', 'ts_code', unique=True),
    )
    
    def __repr__(self):
        return f"<MarginDetail(date={self.trade_date}, code={self.ts_code})>"


class MarginStock(Base):
    """两融标的股票列表"""
    __tablename__ = "margin_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(50))
    exchange_id = Column(String(10))          # 交易所
    mg_type = Column(String(10))              # B-可融资, S-可融券
    in_date = Column(Date)                    # 纳入日期
    out_date = Column(Date)                   # 剔除日期
    is_active = Column(Integer, default=1)    # 是否有效
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MarginStock(code={self.ts_code}, name={self.name})>"
