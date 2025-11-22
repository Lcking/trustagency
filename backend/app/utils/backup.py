"""
数据库备份工具
提供自动备份、定期备份、备份清理等功能
"""
from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil
import logging
import os

logger = logging.getLogger(__name__)


class BackupManager:
    """数据库备份管理器"""
    
    def __init__(
        self,
        db_path: str = "trustagency.db",
        backup_dir: str = "backups",
        max_backups: int = 30,  # 最多保留30个备份
        auto_backup_days: int = 7  # 自动清理7天前的备份
    ):
        """
        初始化备份管理器
        
        Args:
            db_path: 数据库文件路径
            backup_dir: 备份目录
            max_backups: 最大备份数量
            auto_backup_days: 自动备份保留天数
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.auto_backup_days = auto_backup_days
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True, parents=True)
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        创建数据库备份
        
        Args:
            backup_name: 备份文件名(可选),默认使用时间戳
        
        Returns:
            备份信息字典
        """
        try:
            # 检查数据库文件是否存在
            if not self.db_path.exists():
                raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
            
            # 生成备份文件名
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"trustagency_backup_{timestamp}.db"
            
            backup_path = self.backup_dir / backup_name
            
            # 复制数据库文件
            shutil.copy2(self.db_path, backup_path)
            
            # 获取文件大小
            file_size = backup_path.stat().st_size
            
            logger.info(f"✅ 备份创建成功: {backup_path} ({file_size} bytes)")
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "file_size": file_size,
                "created_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ 备份失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份文件
        
        Returns:
            备份文件列表
        """
        backups = []
        
        try:
            for backup_file in sorted(self.backup_dir.glob("*.db"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        except Exception as e:
            logger.error(f"列出备份失败: {str(e)}", exc_info=True)
        
        return backups
    
    def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        从备份恢复数据库
        
        Args:
            backup_name: 备份文件名
        
        Returns:
            恢复结果
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_name}")
            
            # 先备份当前数据库(以防恢复失败)
            current_backup = self.create_backup(
                backup_name=f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            # 恢复备份
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"✅ 数据库恢复成功: {backup_name}")
            
            return {
                "success": True,
                "restored_from": backup_name,
                "current_backup": current_backup,
                "message": "数据库恢复成功"
            }
        
        except Exception as e:
            logger.error(f"❌ 恢复失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        删除指定备份
        
        Args:
            backup_name: 备份文件名
        
        Returns:
            删除结果
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_name}")
            
            backup_path.unlink()
            
            logger.info(f"✅ 备份删除成功: {backup_name}")
            
            return {
                "success": True,
                "deleted": backup_name,
                "message": "备份删除成功"
            }
        
        except Exception as e:
            logger.error(f"❌ 删除备份失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """
        清理旧备份
        
        - 删除超过保留天数的备份
        - 如果备份数量超过最大值,删除最旧的
        
        Returns:
            清理结果
        """
        try:
            backups = self.list_backups()
            deleted_count = 0
            deleted_files = []
            
            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=self.auto_backup_days)
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup["created_at"])
                
                # 删除过期备份
                if backup_date < cutoff_date:
                    result = self.delete_backup(backup["name"])
                    if result["success"]:
                        deleted_count += 1
                        deleted_files.append(backup["name"])
            
            # 如果备份数量仍超过最大值,删除最旧的
            remaining_backups = self.list_backups()
            if len(remaining_backups) > self.max_backups:
                excess = len(remaining_backups) - self.max_backups
                for backup in remaining_backups[-excess:]:
                    result = self.delete_backup(backup["name"])
                    if result["success"]:
                        deleted_count += 1
                        deleted_files.append(backup["name"])
            
            logger.info(f"✅ 清理完成: 删除 {deleted_count} 个旧备份")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "deleted_files": deleted_files,
                "remaining_backups": len(self.list_backups())
            }
        
        except Exception as e:
            logger.error(f"❌ 清理失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """
        获取备份统计信息
        
        Returns:
            统计信息
        """
        backups = self.list_backups()
        
        total_size = sum(b["size"] for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_backup": backups[-1] if backups else None,
            "newest_backup": backups[0] if backups else None,
            "backup_dir": str(self.backup_dir)
        }
