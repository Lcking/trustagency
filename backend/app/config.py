"""
应用配置管理
"""
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # FastAPI
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    API_TITLE: str = os.getenv("API_TITLE", "TrustAgency API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "Admin CMS with AI Content Generation")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trustagency.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Admin
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@trustagency.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", 2000))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # CORS
    CORS_ORIGINS: list = []
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **data):
        super().__init__(**data)
        # 处理 CORS 配置
        cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:8000", "http://localhost:8001"]')
        if isinstance(cors_origins_str, str):
            import json
            try:
                self.CORS_ORIGINS = json.loads(cors_origins_str)
            except:
                self.CORS_ORIGINS = ["http://localhost:8000", "http://localhost:8001"]

# 全局配置对象
settings = Settings()
