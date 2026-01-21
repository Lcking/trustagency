"""
简单的内存缓存工具

用于缓存频繁访问的数据，减少数据库压力
"""
import time
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """简单的内存缓存，支持 TTL"""
    
    def __init__(self):
        self._cache: dict = {}
        self._timestamps: dict = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，如果过期则返回 None"""
        if key not in self._cache:
            return None
        
        timestamp, ttl = self._timestamps.get(key, (0, 0))
        if ttl > 0 and time.time() - timestamp > ttl:
            # 缓存过期
            self.delete(key)
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """设置缓存值，默认 5 分钟过期"""
        self._cache[key] = value
        self._timestamps[key] = (time.time(), ttl)
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._timestamps.clear()
    
    def clear_expired(self) -> int:
        """清理过期缓存，返回清理数量"""
        now = time.time()
        expired_keys = []
        
        for key, (timestamp, ttl) in self._timestamps.items():
            if ttl > 0 and now - timestamp > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)


# 全局缓存实例
cache = SimpleCache()

# 向后兼容别名 (tasks.py 等模块使用)
cache_manager = cache


def make_cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300, prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒），默认 5 分钟
        prefix: 缓存键前缀
    
    Usage:
        @cached(ttl=60, prefix="margin_overview")
        def get_margin_overview():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键（排除 db 等不可序列化参数）
            cache_args = []
            cache_kwargs = {}
            
            for arg in args:
                if not hasattr(arg, '__dict__'):  # 排除对象
                    cache_args.append(arg)
            
            for k, v in kwargs.items():
                if k not in ('db', 'session', 'request') and not hasattr(v, '__dict__'):
                    cache_kwargs[k] = v
            
            key = f"{prefix}:{make_cache_key(*cache_args, **cache_kwargs)}"
            
            # 尝试从缓存获取
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache set: {key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(prefix: str = "") -> int:
    """
    使指定前缀的缓存失效
    
    Returns:
        清理的缓存数量
    """
    if not prefix:
        count = len(cache._cache)
        cache.clear()
        return count
    
    keys_to_delete = [k for k in cache._cache.keys() if k.startswith(prefix)]
    for key in keys_to_delete:
        cache.delete(key)
    
    return len(keys_to_delete)
