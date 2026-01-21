"""
重试工具 - 用于处理临时性错误

支持指数退避和自定义异常处理
"""
import time
import logging
from typing import Callable, Type, Tuple, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """重试失败后抛出的异常"""
    
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟时间（秒）
        backoff: 退避系数（每次重试延迟 = delay * backoff^attempt）
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数 (exception, attempt) -> None
    
    Usage:
        @retry(max_attempts=3, delay=1, exceptions=(ConnectionError,))
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise RetryError(
                            f"Failed after {max_attempts} attempts: {e}",
                            last_exception=e
                        )
                    
                    wait_time = delay * (backoff ** (attempt - 1))
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(wait_time)
            
            # 不应该到达这里
            raise RetryError("Unexpected retry failure", last_exception=last_exception)
        
        return wrapper
    return decorator


async def retry_async(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    异步重试函数
    
    Usage:
        result = await retry_async(
            lambda: some_async_func(),
            max_attempts=3
        )
    """
    import asyncio
    
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            result = func()
            if asyncio.iscoroutine(result):
                return await result
            return result
        except exceptions as e:
            last_exception = e
            
            if attempt == max_attempts:
                raise RetryError(
                    f"Failed after {max_attempts} attempts: {e}",
                    last_exception=e
                )
            
            wait_time = delay * (backoff ** (attempt - 1))
            logger.warning(
                f"Attempt {attempt} failed: {e}. Retrying in {wait_time:.1f}s..."
            )
            
            await asyncio.sleep(wait_time)
    
    raise RetryError("Unexpected retry failure", last_exception=last_exception)
