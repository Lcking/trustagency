"""
工具类单元测试
"""
import pytest
from datetime import datetime, timedelta
from app.utils.cache import CacheManager
from app.utils.task_monitor import TaskMonitor


class TestCacheManager:
    """缓存管理器测试"""
    
    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = CacheManager()
        cache.set("test_key", "test_value", ttl=60)
        
        value = cache.get("test_key")
        assert value == "test_value"
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = CacheManager()
        cache.set("test_key", "test_value", ttl=0)  # 立即过期
        
        import time
        time.sleep(1)
        
        value = cache.get("test_key")
        assert value is None
    
    def test_cache_clear(self):
        """测试缓存清空"""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 0
    
    def test_cache_stats(self):
        """测试缓存统计"""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2


class TestTaskMonitor:
    """任务监控测试"""
    
    def test_task_timeout_minutes(self):
        """测试超时配置"""
        assert TaskMonitor.TASK_TIMEOUT_MINUTES == 30
        assert TaskMonitor.STUCK_TASK_MINUTES == 10


class TestBackupManager:
    """备份管理器测试"""
    
    def test_backup_initialization(self):
        """测试备份管理器初始化"""
        from app.utils.backup import BackupManager
        backup_manager = BackupManager()
        
        assert backup_manager.max_backups == 30
        assert backup_manager.auto_backup_days == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
