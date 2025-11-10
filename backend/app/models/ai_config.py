"""
AI 配置模型（API 配置、模型选择、提示词）
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AIConfig(Base):
    """AI 配置模型 - 存储 API 密钥和模型配置"""
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, index=True)

    # 配置名称和类型
    name = Column(String(100), unique=True, nullable=False, index=True)  # 例: "openai", "deepseek", "relay"
    
    # AI 服务提供商信息
    provider = Column(String(50), nullable=False)  # openai, deepseek, relay 等
    api_endpoint = Column(String(500), nullable=True)  # API 端点 URL
    api_key = Column(String(500), nullable=False)  # API 密钥（加密存储）
    
    # 模型信息
    model_name = Column(String(100), nullable=False)  # gpt-4, gpt-3.5-turbo, deepseek-chat 等
    model_version = Column(String(50), nullable=True)  # 模型版本
    
    # 提示词配置
    system_prompt = Column(Text, nullable=True)  # 系统级提示词
    user_prompt_template = Column(Text, nullable=True)  # 用户提示词模板（支持 {title} 占位符）
    
    # 参数配置
    temperature = Column(Integer, default=7, nullable=False)  # 温度 0-100（存储为百分比）
    max_tokens = Column(Integer, default=2000, nullable=False)  # 最大令牌数
    top_p = Column(Integer, default=90, nullable=False)  # Top P 采样 0-100
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认配置
    
    # 备注和使用说明
    description = Column(Text, nullable=True)  # 配置说明
    retry_times = Column(Integer, default=3, nullable=False)  # 重试次数
    timeout_seconds = Column(Integer, default=120, nullable=False)  # 超时时间（秒）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIConfig(id={self.id}, name={self.name}, provider={self.provider}, active={self.is_active})>"
