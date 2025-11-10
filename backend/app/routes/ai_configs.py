"""
AI 配置管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx
from app.database import get_db
from app.models import AIConfig
from app.routes.auth import get_current_user
from app.schemas.ai_config import AIConfigCreate, AIConfigUpdate, AIConfigResponse, AIConfigListResponse

router = APIRouter(prefix="/api/ai-configs", tags=["ai-configs"])


class AIConfigTestRequest(BaseModel):
    """测试 AI 配置的请求体"""
    api_endpoint: str
    api_key: str
    model_name: str


class AIConfigTestResponse(BaseModel):
    """测试 AI 配置的响应"""
    success: bool
    message: str
    error: str = None
    response_time: float = None


@router.post("/test", response_model=AIConfigTestResponse)
async def test_ai_config(
    test_data: AIConfigTestRequest,
    current_user = Depends(get_current_user),
):
    """
    测试 AI 配置连接
    
    验证 API 端点和密钥的有效性
    """
    try:
        headers = {
            "Authorization": f"Bearer {test_data.api_key}",
            "Content-Type": "application/json"
        }
        
        # 准备简单的测试请求体（模拟常见的 LLM API 格式）
        test_payload = {
            "model": test_data.model_name,
            "messages": [
                {"role": "user", "content": "test"}
            ],
            "max_tokens": 10
        }
        
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 尝试向 API 端点发送请求
            response = await client.post(
                test_data.api_endpoint,
                json=test_payload,
                headers=headers
            )
        
        response_time = time.time() - start_time
        
        # 检查响应状态
        if response.status_code in [200, 201]:
            return AIConfigTestResponse(
                success=True,
                message=f"✅ 连接成功（响应时间: {response_time:.2f}s）",
                response_time=response_time
            )
        elif response.status_code == 401:
            return AIConfigTestResponse(
                success=False,
                message="❌ API 密钥无效或已过期",
                error=f"HTTP {response.status_code}: Unauthorized"
            )
        elif response.status_code == 404:
            return AIConfigTestResponse(
                success=False,
                message="❌ API 端点不存在",
                error=f"HTTP {response.status_code}: Not Found"
            )
        elif response.status_code >= 500:
            return AIConfigTestResponse(
                success=False,
                message="❌ API 服务器错误",
                error=f"HTTP {response.status_code}: Server Error"
            )
        else:
            return AIConfigTestResponse(
                success=False,
                message=f"❌ 请求失败",
                error=f"HTTP {response.status_code}"
            )
    
    except httpx.TimeoutException:
        return AIConfigTestResponse(
            success=False,
            message="❌ 连接超时（10秒）",
            error="Connection timeout"
        )
    except httpx.ConnectError as e:
        return AIConfigTestResponse(
            success=False,
            message="❌ 无法连接到 API 服务器",
            error=str(e)
        )
    except Exception as e:
        return AIConfigTestResponse(
            success=False,
            message="❌ 测试过程中出错",
            error=str(e)
        )


@router.get("", response_model=AIConfigListResponse)
async def list_ai_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: bool = Query(None, description="筛选活跃配置"),
    db: Session = Depends(get_db),
):
    """
    获取 AI 配置列表
    
    支持活跃状态过滤
    """
    query = db.query(AIConfig)
    
    if is_active is not None:
        query = query.filter(AIConfig.is_active == is_active)
    
    total = query.count()
    configs = query.offset(skip).limit(limit).all()
    
    return AIConfigListResponse(
        data=[AIConfigResponse.model_validate(c) for c in configs],
        total=total,
    )


@router.post("", response_model=AIConfigResponse, status_code=201)
async def create_ai_config(
    config_data: AIConfigCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建 AI 配置
    
    仅管理员可操作
    """
    # 检查配置名称是否已存在
    existing = db.query(AIConfig).filter(AIConfig.name == config_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"配置名称 '{config_data.name}' 已存在")
    
    # 如果设为默认，取消其他配置的默认标记
    if config_data.is_default:
        db.query(AIConfig).update({AIConfig.is_default: False})
    
    config = AIConfig(**config_data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return AIConfigResponse.model_validate(config)


@router.get("/{config_id}", response_model=AIConfigResponse)
async def get_ai_config(
    config_id: int,
    db: Session = Depends(get_db),
):
    """获取单个 AI 配置"""
    config = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置 ID {config_id} 不存在")
    return AIConfigResponse.model_validate(config)


@router.put("/{config_id}", response_model=AIConfigResponse)
async def update_ai_config(
    config_id: int,
    config_data: AIConfigUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新 AI 配置
    
    仅管理员可操作
    """
    config = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置 ID {config_id} 不存在")
    
    # 如果更新为默认，取消其他配置的默认标记
    if config_data.is_default:
        db.query(AIConfig).filter(AIConfig.id != config_id).update({AIConfig.is_default: False})
    
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return AIConfigResponse.model_validate(config)


@router.delete("/{config_id}", status_code=204)
async def delete_ai_config(
    config_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除 AI 配置
    
    仅管理员可操作
    """
    config = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置 ID {config_id} 不存在")
    
    db.delete(config)
    db.commit()
    return None


@router.get("/default/config", response_model=AIConfigResponse)
async def get_default_ai_config(
    db: Session = Depends(get_db),
):
    """获取默认 AI 配置"""
    config = db.query(AIConfig).filter(AIConfig.is_default == True, AIConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=404, detail="没有默认的 AI 配置")
    return AIConfigResponse.model_validate(config)


@router.post("/{config_id}/set-default", response_model=AIConfigResponse)
async def set_default_ai_config(
    config_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """设置为默认 AI 配置"""
    config = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail=f"配置 ID {config_id} 不存在")
    
    # 取消其他配置的默认标记
    db.query(AIConfig).update({AIConfig.is_default: False})
    config.is_default = True
    
    db.commit()
    db.refresh(config)
    return AIConfigResponse.model_validate(config)
