"""
AI 任务 Schema (Pydantic 验证)
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AITaskCreate(BaseModel):
    """创建 AI 任务 Schema"""
    batch_name: Optional[str] = None
    titles: List[str]


class AITaskResponse(BaseModel):
    """AI 任务响应 Schema"""
    id: int
    batch_id: str
    batch_name: Optional[str] = None
    status: str
    progress: int
    total_count: int
    completed_count: int
    failed_count: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AITaskListResponse(BaseModel):
    """AI 任务列表响应 Schema"""
    data: list[AITaskResponse]
    total: int
    skip: int
    limit: int
