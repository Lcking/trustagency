"""
AI 配置 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AIConfigBase(BaseModel):
    """AI 配置基础字段"""
    name: str = Field(..., description="配置名称", min_length=1, max_length=100)
    provider: str = Field(..., description="AI 提供商", min_length=1)
    api_endpoint: Optional[str] = Field(None, description="API 端点 URL")
    api_key: str = Field(..., description="API 密钥", min_length=1)
    model_name: str = Field(..., description="模型名称", min_length=1)
    model_version: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    temperature: int = Field(default=7, ge=0, le=100, description="温度 0-100")
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    top_p: int = Field(default=90, ge=0, le=100)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    description: Optional[str] = None
    retry_times: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=120, ge=10, le=600)


class AIConfigCreate(AIConfigBase):
    """创建 AI 配置"""
    pass


class AIConfigUpdate(BaseModel):
    """更新 AI 配置"""
    name: Optional[str] = None
    provider: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    temperature: Optional[int] = None
    max_tokens: Optional[int] = None
    top_p: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None
    retry_times: Optional[int] = None
    timeout_seconds: Optional[int] = None


class AIConfigResponse(AIConfigBase):
    """AI 配置响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIConfigListResponse(BaseModel):
    """AI 配置列表响应"""
    data: list[AIConfigResponse]
    total: int

    class Config:
        from_attributes = True


class FailedTitle(BaseModel):
    """失败的文章标题及错误"""
    title: str
    error: str


class TaskErrorDetail(BaseModel):
    """任务错误详情"""
    error_code: str
    error_message: str
    error_traceback: Optional[str] = None
    failed_titles: Optional[list[FailedTitle]] = None
    retry_count: int = 0


class AITaskResponseEnhanced(BaseModel):
    """增强的任务响应（包含错误详情）"""
    id: int
    batch_id: str
    batch_name: Optional[str]
    status: str
    progress: int
    total_count: int
    completed_count: int
    failed_count: int
    has_error: bool
    error_message: Optional[str]
    error_details: Optional[TaskErrorDetail]
    failed_titles: Optional[list[FailedTitle]]
    ai_model: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
