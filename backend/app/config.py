"""
应用配置管理
"""
import json
from typing import List, Any

# 兼容 pydantic v1 和 v2
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import field_validator
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseSettings, validator
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
    
    # CORS - 支持 JSON 字符串或列表
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:8001"]
    
    if PYDANTIC_V2:
        @field_validator('CORS_ORIGINS', mode='before')
        @classmethod
        def parse_cors_origins(cls, v: Any) -> List[str]:
            """解析 CORS_ORIGINS，支持 JSON 字符串或列表"""
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    # 尝试逗号分隔格式
                    return [s.strip() for s in v.split(',') if s.strip()]
            return v
        
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
        )
    else:
        @validator('CORS_ORIGINS', pre=True)
        def parse_cors_origins_v1(cls, v):
            """解析 CORS_ORIGINS，支持 JSON 字符串或列表"""
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [s.strip() for s in v.split(',') if s.strip()]
            return v
        
        class Config:
            case_sensitive = True
            env_file = ".env"


# 全局配置对象
settings = Settings()
