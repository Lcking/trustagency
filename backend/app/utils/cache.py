"""
API响应缓存工具
提供内存缓存和基于时间的失效机制
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """内存缓存管理器"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 键前缀
            *args, **kwargs: 用于生成键的参数
        
        Returns:
            缓存键
        """
        # 将参数转换为字符串并哈希
        key_parts = [prefix]
        
        if args:
            key_parts.append(str(args))
        
        if kwargs:
            # 排序kwargs以确保一致性
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(str(sorted_kwargs))
        
        key_string = ":".join(key_parts)
        
        # 使用SHA256哈希生成固定长度的键
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值或None(如果不存在或已过期)
        """
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        
        # 检查是否过期
        if cache_entry["expires_at"] < datetime.now():
            # 过期,删除缓存
            del self._cache[key]
            logger.debug(f"缓存过期并删除: {key}")
            return None
        
        logger.debug(f"缓存命中: {key}")
        return cache_entry["value"]
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒),默认5分钟
        """
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now()
        }
        
        logger.debug(f"缓存设置: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"缓存删除: {key}")
    
    def clear(self):
        """清空所有缓存"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"清空所有缓存: {count} 个条目")
    
    def cleanup_expired(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry["expires_at"] < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"清理过期缓存: {len(expired_keys)} 个条目")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        now = datetime.now()
        active_count = sum(
            1 for entry in self._cache.values()
            if entry["expires_at"] >= now
        )
        expired_count = len(self._cache) - active_count
        
        return {
            "total_entries": len(self._cache),
            "active_entries": active_count,
            "expired_entries": expired_count
        }


# 全局缓存实例
cache_manager = CacheManager()


def cached(prefix: str = "api", ttl: int = 300):
    """
    缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        ttl: 过期时间(秒)
    
    Example:
        @cached(prefix="articles", ttl=600)
        def get_articles():
            return fetch_articles_from_db()
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # 根据函数类型返回合适的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
