"""
两融数据同步 Celery 任务
"""
from celery import shared_task
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name="tasks.sync_margin_summary")
def sync_margin_summary(days: int = 7):
    """
    同步两融市场汇总数据
    
    Args:
        days: 同步最近多少天的数据
    """
    from app.database import SessionLocal
    from app.services.tushare_service import MarginDataService
    
    logger.info(f"开始同步两融汇总数据 (最近{days}天)")
    
    db = SessionLocal()
    try:
        service = MarginDataService(db)
        count = service.sync_summary_data(days=days)
        logger.info(f"两融汇总数据同步完成，共 {count} 条记录")
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"两融汇总数据同步失败: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="tasks.sync_margin_detail")
def sync_margin_detail(trade_date: str = None):
    """
    同步两融个股明细数据
    
    Args:
        trade_date: 交易日期 YYYYMMDD，默认为最近交易日
    """
    from app.database import SessionLocal
    from app.services.tushare_service import MarginDataService
    
    if not trade_date:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    logger.info(f"开始同步两融明细数据 ({trade_date})")
    
    db = SessionLocal()
    try:
        service = MarginDataService(db)
        count = service.sync_detail_data(trade_date=trade_date)
        logger.info(f"两融明细数据同步完成，共 {count} 条记录")
        return {"success": True, "count": count, "trade_date": trade_date}
    except Exception as e:
        logger.error(f"两融明细数据同步失败: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="tasks.sync_margin_all")
def sync_margin_all():
    """
    完整同步两融数据（汇总 + 明细）
    
    建议每日收盘后运行（如 17:30）
    """
    from app.database import SessionLocal
    from app.services.tushare_service import MarginDataService
    import time
    
    logger.info("开始完整同步两融数据")
    
    db = SessionLocal()
    try:
        service = MarginDataService(db)
        
        # 同步最近7天的汇总数据
        summary_count = service.sync_summary_data(days=7)
        
        # 同步最近3天的明细数据（避免当天数据未发布的问题）
        detail_count = 0
        for i in range(3):
            trade_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            try:
                count = service.sync_detail_data(trade_date=trade_date)
                detail_count += count
                if count > 0:
                    logger.info(f"同步 {trade_date} 明细: {count} 条")
                # API 频率限制
                time.sleep(0.3)
            except Exception as e:
                logger.warning(f"同步 {trade_date} 明细失败: {e}")
        
        logger.info(f"两融数据同步完成: 汇总 {summary_count} 条, 明细 {detail_count} 条")
        return {
            "success": True, 
            "summary_count": summary_count, 
            "detail_count": detail_count
        }
    except Exception as e:
        logger.error(f"两融数据同步失败: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="tasks.sync_margin_history")
def sync_margin_history(days: int = 90):
    """
    同步历史两融数据（首次初始化或回补数据）
    
    Args:
        days: 同步最近多少天的历史数据
    """
    import time
    from app.database import SessionLocal
    from app.services.tushare_service import MarginDataService
    from app.models.margin import MarginDetail
    
    logger.info(f"开始同步历史两融数据 (最近{days}天)")
    
    db = SessionLocal()
    try:
        service = MarginDataService(db)
        
        # 同步汇总数据
        summary_count = service.sync_summary_data(days=days)
        
        # 同步每天的明细数据（注意 Tushare API 频率限制）
        detail_count = 0
        end_date = datetime.now()
        max_retries = 3
        backoff_base = 1.0
        
        for i in range(days):
            trade_date = (end_date - timedelta(days=i)).strftime('%Y%m%d')
            
            # 检查是否已有该日数据
            existing = db.query(MarginDetail).filter(
                MarginDetail.trade_date == datetime.strptime(trade_date, '%Y%m%d').date()
            ).first()
            
            if existing:
                continue
            
            # 指数退避重试
            for attempt in range(max_retries):
                try:
                    count = service.sync_detail_data(trade_date=trade_date)
                    detail_count += count
                    logger.info(f"同步 {trade_date} 明细: {count} 条")
                    # API 频率限制：成功后等待0.5秒
                    time.sleep(0.5)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = backoff_base * (2 ** attempt)
                        logger.warning(f"同步 {trade_date} 失败 (重试 {attempt + 1}/{max_retries}): {e}")
                        time.sleep(wait_time)
                    else:
                        logger.warning(f"同步 {trade_date} 明细失败 (已达最大重试): {e}")
        
        logger.info(f"历史数据同步完成: 汇总 {summary_count} 条, 明细 {detail_count} 条")
        return {
            "success": True,
            "summary_count": summary_count,
            "detail_count": detail_count
        }
    except Exception as e:
        logger.error(f"历史数据同步失败: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()
