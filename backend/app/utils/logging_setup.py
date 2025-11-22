"""
日志配置初始化
提供结构化日志系统
"""
import logging
import logging.config
import json
from pathlib import Path


def setup_logging(config_path: str = "logging_config.json", logs_dir: str = "logs"):
    """
    配置日志系统
    
    Args:
        config_path: 日志配置文件路径
        logs_dir: 日志目录
    """
    # 确保日志目录存在
    log_path = Path(logs_dir)
    log_path.mkdir(exist_ok=True, parents=True)
    
    # 加载日志配置
    config_file = Path(config_path)
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logging.config.dictConfig(config)
            logging.info("✅ 日志系统初始化成功")
        except Exception as e:
            # 如果配置文件加载失败,使用基本配置
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            logging.warning(f"⚠️ 日志配置加载失败,使用默认配置: {str(e)}")
    else:
        # 配置文件不存在,使用基本配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_path / 'app.log', encoding='utf-8')
            ]
        )
        logging.warning(f"⚠️ 日志配置文件不存在: {config_path},使用默认配置")


def get_logger(name: str) -> logging.Logger:
    """
    获取logger实例
    
    Args:
        name: logger名称,通常使用 __name__
    
    Returns:
        Logger实例
    """
    return logging.getLogger(name)
