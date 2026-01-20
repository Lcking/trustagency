"""
应用配置管理

注意: CORS_ORIGINS 使用字符串类型 (CORS_ORIGINS_STR) 来避免 pydantic-settings v2
从 .env 文件解析 List[str] 时的问题。通过 @property 转换为列表。
"""
import json
from typing import List

# 兼容 pydantic v1 和 v2
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseSettings
    PYDANTIC_V2 = False


class Settings(BaseSettings):
    """应用配置"""
    
    # FastAPI
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_TITLE: str = "TrustAgency API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Admin CMS with AI Content Generation"
    
    # Database
    DATABASE_URL: str = "sqlite:///./trustagency.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    
    # Admin
    ADMIN_EMAIL: str = "admin@trustagency.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Tushare Pro (两融数据)
    TUSHARE_TOKEN: str = ""
    
    # CORS - 使用字符串类型避免 pydantic-settings 解析问题
    # 支持 JSON 数组格式: '["http://localhost:8000", "http://localhost:8001"]'
    # 或逗号分隔格式: 'http://localhost:8000,http://localhost:8001'
    CORS_ORIGINS_STR: str = '["http://localhost:8000", "http://localhost:8001"]'
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """解析 CORS_ORIGINS_STR 为列表"""
        value = self.CORS_ORIGINS_STR
        if not value:
            return ["http://localhost:8000", "http://localhost:8001"]
        
        # 尝试 JSON 解析
        try:
            result = json.loads(value)
            if isinstance(result, list):
                return [str(item) for item in result]
        except json.JSONDecodeError:
            pass
        
        # 尝试逗号分隔格式
        return [s.strip() for s in value.split(',') if s.strip()]
    
    if PYDANTIC_V2:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
        )
    else:
        class Config:
            case_sensitive = True
            env_file = ".env"


# 全局配置对象
settings = Settings()
