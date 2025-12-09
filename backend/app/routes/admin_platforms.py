"""
平台管理 API 路由 - 用于后台管理系统
提供平台编辑、表单定义等管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser
from app.routes.auth import get_current_user
from app.schemas.platform_admin import (
    PlatformEditForm,
    PlatformEditResponse,
    PlatformEditListResponse,
    PlatformEditFormDefinition,
)
from app.services.platform_service import PlatformService
from typing import Optional

router = APIRouter(prefix="/api/admin/platforms", tags=["admin-platforms"])


@router.get("/form-definition", response_model=PlatformEditFormDefinition)
async def get_edit_form_definition(
    current_user: AdminUser = Depends(get_current_user),
):
    """
    获取平台编辑表单的字段定义
    
    用于前端动态生成编辑表单。返回所有可编辑字段的定义、类型、验证规则等。
    """
    form_definition = {
        "sections": [
            {
                "title": "基础信息",
                "fields": [
                    {
                        "name": "name",
                        "label": "平台名称",
                        "type": "text",
                        "required": True,
                        "placeholder": "例: AlphaLeverage"
                    },
                    {
                        "name": "slug",
                        "label": "URL标识(Slug)",
                        "type": "text",
                        "required": True,
                        "placeholder": "例: alphaleverage (小写, 用-分隔)"
                    },
                    {
                        "name": "description",
                        "label": "平台描述",
                        "type": "textarea",
                        "placeholder": "一行简短描述"
                    },
                    {
                        "name": "website_url",
                        "label": "官方网站",
                        "type": "text",
                        "placeholder": "https://..."
                    },
                    {
                        "name": "logo_url",
                        "label": "Logo URL",
                        "type": "text",
                        "placeholder": "https://... (平台Logo图片)"
                    },
                ]
            },
            {
                "title": "平台评分和分类",
                "fields": [
                    {
                        "name": "rating",
                        "label": "评分 (0-5)",
                        "type": "number",
                        "min": 0,
                        "max": 5,
                        "step": 0.1,
                        "placeholder": "4.5"
                    },
                    {
                        "name": "rank",
                        "label": "排名",
                        "type": "number",
                        "placeholder": "1"
                    },
                    {
                        "name": "founded_year",
                        "label": "成立年份",
                        "type": "number",
                        "placeholder": "2015"
                    },
                    {
                        "name": "safety_rating",
                        "label": "安全评级 (A-D级)",
                        "type": "select",
                        "options": [
                            {"label": "A - 最安全", "value": "A"},
                            {"label": "B - 安全", "value": "B"},
                            {"label": "C - 一般", "value": "C"},
                            {"label": "D - 风险", "value": "D"}
                        ]
                    },
                    {
                        "name": "platform_type",
                        "label": "平台等级",
                        "type": "select",
                        "options": [
                            {"label": "新手", "value": "新手"},
                            {"label": "进阶", "value": "进阶"},
                            {"label": "活跃", "value": "活跃"},
                            {"label": "专业", "value": "专业"}
                        ]
                    },
                    {
                        "name": "platform_source",
                        "label": "平台来源",
                        "type": "select",
                        "required": True,
                        "options": [
                            {"label": "🏦 券商平台", "value": "券商平台"},
                            {"label": "🏢 民间平台", "value": "民间平台"},
                            {"label": "⚠️ 黑名单", "value": "黑名单"}
                        ]
                    },
                ]
            },
            {
                "title": "交易参数",
                "fields": [
                    {
                        "name": "min_leverage",
                        "label": "最小杠杆",
                        "type": "number",
                        "placeholder": "1.0"
                    },
                    {
                        "name": "max_leverage",
                        "label": "最大杠杆",
                        "type": "number",
                        "placeholder": "500"
                    },
                    {
                        "name": "commission_rate",
                        "label": "佣金率 (0-1)",
                        "type": "number",
                        "min": 0,
                        "max": 1,
                        "step": 0.0001,
                        "placeholder": "0.005 (小数形式，例: 0.001, 0.005)"
                    },
                    {
                        "name": "fee_rate",
                        "label": "费率 (0-1)",
                        "type": "number",
                        "min": 0,
                        "max": 1,
                        "step": 0.0001,
                        "placeholder": "0.005 (小数形式，例: 0.001, 0.5)"
                    },
                ]
            },
            {
                "title": "平台标志",
                "fields": [
                    {
                        "name": "is_active",
                        "label": "是否活跃",
                        "type": "boolean"
                    },
                    {
                        "name": "is_featured",
                        "label": "是否精选",
                        "type": "boolean"
                    },
                    {
                        "name": "is_recommended",
                        "label": "是否推荐",
                        "type": "boolean"
                    },
                    {
                        "name": "is_regulated",
                        "label": "是否受监管",
                        "type": "boolean"
                    },
                ]
            },
            {
                "title": "平台介绍",
                "fields": [
                    {
                        "name": "introduction",
                        "label": "平台介绍",
                        "type": "textarea",
                        "placeholder": "详细介绍平台的基本信息"
                    },
                    {
                        "name": "overview_intro",
                        "label": "平台概览介绍",
                        "type": "textarea",
                        "placeholder": "简明扼要的平台介绍，用于详情页面顶部"
                    },
                    {
                        "name": "main_features",
                        "label": "主要特性 (JSON)",
                        "type": "json",
                        "placeholder": '[{"title":"特性1","desc":"描述1"},...]'
                    },
                    {
                        "name": "fee_structure",
                        "label": "费用结构 (JSON)",
                        "type": "json",
                        "placeholder": '[{"type":"手续费","value":"0.5%","desc":"..."},...]'
                    },
                    {
                        "name": "fee_table",
                        "label": "费用表格 (JSON)",
                        "type": "json",
                        "placeholder": '[{"type":"交易手续费","basic":"0.20%","vip":"0.10%"},...]'
                    },
                    {
                        "name": "account_opening_link",
                        "label": "开户链接",
                        "type": "text",
                        "placeholder": "https://..."
                    }
                ]
            },
            {
                "title": "为什么选择该平台",
                "description": "展示平台的独特优势 (仅适用于新手友好型平台)",
                "fields": [
                    {
                        "name": "why_choose",
                        "label": "为什么选择 (JSON)",
                        "type": "json",
                        "placeholder": '[{"icon":"📚","title":"优点1","description":"..."},...]'
                    }
                ]
            },
            {
                "title": "交易条件和费用",
                "fields": [
                    {
                        "name": "trading_conditions",
                        "label": "交易条件 (JSON)",
                        "type": "json",
                        "placeholder": '[{"label":"最大杠杆","value":"1:500"},...]'
                    },
                    {
                        "name": "fee_advantages",
                        "label": "费用优势 (JSON)",
                        "type": "json",
                        "placeholder": '[{"label":"交易手续费","value":"0.5点"},...]'
                    }
                ]
            },
            {
                "title": "账户类型",
                "fields": [
                    {
                        "name": "account_types",
                        "label": "账户类型 (JSON)",
                        "type": "json",
                        "placeholder": '[{"name":"基础","leverage":"1:10","min_deposit":"$1000"},...]'
                    }
                ]
            },
            {
                "title": "工具和开户",
                "fields": [
                    {
                        "name": "trading_tools",
                        "label": "交易工具 (JSON)",
                        "type": "json",
                        "placeholder": '[{"title":"工具1","description":"..."},...]'
                    },
                    {
                        "name": "opening_steps",
                        "label": "开户步骤 (JSON)",
                        "type": "json",
                        "placeholder": '[{"step_number":1,"title":"...","description":"..."},...]'
                    }
                ]
            },
            {
                "title": "安全和支持",
                "fields": [
                    {
                        "name": "security_measures",
                        "label": "安全措施 (JSON)",
                        "type": "json",
                        "placeholder": '[{"text":"✓ 安全措施1"},...]'
                    },
                    {
                        "name": "safety_info",
                        "label": "安全信息",
                        "type": "textarea",
                        "placeholder": "详细的安全信息说明"
                    },
                    {
                        "name": "customer_support",
                        "label": "客户支持 (JSON)",
                        "type": "json",
                        "placeholder": '[{"type":"24/5支持","description":"..."},...]'
                    }
                ]
            },
            {
                "title": "平台徽章和标签",
                "fields": [
                    {
                        "name": "platform_badges",
                        "label": "平台徽章 (JSON)",
                        "type": "json",
                        "placeholder": '["推荐平台","新手友好","低成本"]'
                    },
                    {
                        "name": "top_badges",
                        "label": "顶部徽章 (JSON)",
                        "type": "json",
                        "placeholder": '["推荐平台","专业级交易","最高杠杆"]'
                    }
                ]
            },
            {
                "title": "学习资源",
                "fields": [
                    {
                        "name": "learning_resources",
                        "label": "学习资源 (JSON)",
                        "type": "json",
                        "placeholder": '[{"title":"资源","description":"...","link":"..."},...]'
                    }
                ]
            }
        ]
    }
    
    return PlatformEditFormDefinition(**form_definition)


@router.get("/create-form-definition", response_model=PlatformEditFormDefinition)
async def get_create_form_definition(
    current_user: AdminUser = Depends(get_current_user),
):
    """
    获取新增平台表单定义
    
    返回新增平台所需的所有字段及其元数据。
    """
    form_definition = {
        "sections": [
            {
                "title": "基础信息 (必填)",
                "fields": [
                    {
                        "name": "name",
                        "label": "平台名称 *",
                        "type": "text",
                        "required": True,
                        "placeholder": "例如: 平台A"
                    },
                    {
                        "name": "slug",
                        "label": "URL Slug *",
                        "type": "text",
                        "required": True,
                        "placeholder": "例如: platform-a (只能包含字母、数字和连字符)"
                    },
                    {
                        "name": "platform_type",
                        "label": "平台等级 *",
                        "type": "select",
                        "required": True,
                        "options": [
                            {"value": "新手", "label": "新手"},
                            {"value": "进阶", "label": "进阶"},
                            {"value": "活跃", "label": "活跃"},
                            {"value": "专业", "label": "专业"}
                        ]
                    },
                    {
                        "name": "rating",
                        "label": "评分 (0-5) *",
                        "type": "number",
                        "required": True,
                        "min": 0,
                        "max": 5,
                        "step": 0.1,
                        "placeholder": "例如: 4.5"
                    },
                    {
                        "name": "rank",
                        "label": "排名 *",
                        "type": "number",
                        "required": True,
                        "min": 1,
                        "placeholder": "例如: 1"
                    }
                ]
            },
            {
                "title": "状态设置",
                "fields": [
                    {
                        "name": "is_active",
                        "label": "是否激活",
                        "type": "checkbox",
                        "default": True
                    },
                    {
                        "name": "is_recommended",
                        "label": "是否推荐",
                        "type": "checkbox",
                        "default": False
                    }
                ]
            },
            {
                "title": "平台描述",
                "fields": [
                    {
                        "name": "description",
                        "label": "简短描述",
                        "type": "textarea",
                        "placeholder": "平台的一句话描述"
                    },
                    {
                        "name": "overview_intro",
                        "label": "详细介绍",
                        "type": "textarea",
                        "placeholder": "平台的详细介绍和特点"
                    }
                ]
            },
            {
                "title": "交易信息",
                "fields": [
                    {
                        "name": "founded_year",
                        "label": "成立年份",
                        "type": "number",
                        "min": 2000,
                        "max": 2100,
                        "placeholder": "例如: 2015"
                    },
                    {
                        "name": "fee_table",
                        "label": "费率信息",
                        "type": "textarea",
                        "placeholder": "平台的费率详情或说明"
                    }
                ]
            },
            {
                "title": "安全信息",
                "fields": [
                    {
                        "name": "safety_rating",
                        "label": "安全评级 (A-D级)",
                        "type": "select",
                        "options": [
                            {"value": "A", "label": "A - 最安全"},
                            {"value": "B", "label": "B - 安全"},
                            {"value": "C", "label": "C - 一般"},
                            {"value": "D", "label": "D - 风险"}
                        ]
                    },
                    {
                        "name": "safety_info",
                        "label": "安全说明",
                        "type": "textarea",
                        "placeholder": "安全特性、审计情况等信息"
                    }
                ]
            },
            {
                "title": "媒体资源",
                "fields": [
                    {
                        "name": "logo_url",
                        "label": "Logo URL",
                        "type": "text",
                        "placeholder": "https://example.com/logo.png"
                    },
                    {
                        "name": "website_url",
                        "label": "官方网站",
                        "type": "text",
                        "placeholder": "https://example.com"
                    }
                ]
            },
            {
                "title": "平台徽章和标签",
                "fields": [
                    {
                        "name": "platform_badges",
                        "label": "平台徽章 (JSON)",
                        "type": "json",
                        "placeholder": '["推荐","新手友好","低成本"]'
                    },
                    {
                        "name": "top_badges",
                        "label": "顶部徽章 (JSON)",
                        "type": "json",
                        "placeholder": '["推荐平台","专业交易"]'
                    }
                ]
            },
            {
                "title": "为什么选择该平台",
                "description": "展示平台的独特优势 (仅适用于新手友好型平台)",
                "fields": [
                    {
                        "name": "why_choose",
                        "label": "为什么选择 (JSON)",
                        "type": "json",
                        "placeholder": '[{"icon":"📚","title":"优点1","description":"..."},...]'
                    }
                ]
            },
            {
                "title": "交易条件和费用",
                "fields": [
                    {
                        "name": "trading_conditions",
                        "label": "交易条件 (JSON)",
                        "type": "json",
                        "placeholder": '[{"label":"最大杠杆","value":"1:500"},...]'
                    },
                    {
                        "name": "fee_advantages",
                        "label": "费用优势 (JSON)",
                        "type": "json",
                        "placeholder": '[{"label":"交易手续费","value":"0.5点"},...]'
                    }
                ]
            },
            {
                "title": "账户类型",
                "fields": [
                    {
                        "name": "account_types",
                        "label": "账户类型 (JSON)",
                        "type": "json",
                        "placeholder": '[{"name":"基础","leverage":"1:10","min_deposit":"$1000"},...]'
                    }
                ]
            },
            {
                "title": "工具和开户",
                "fields": [
                    {
                        "name": "trading_tools",
                        "label": "交易工具 (JSON)",
                        "type": "json",
                        "placeholder": '[{"title":"工具1","description":"..."},...]'
                    },
                    {
                        "name": "opening_steps",
                        "label": "开户步骤 (JSON)",
                        "type": "json",
                        "placeholder": '[{"step_number":1,"title":"...","description":"..."},...]'
                    }
                ]
            },
            {
                "title": "安全和支持",
                "fields": [
                    {
                        "name": "security_measures",
                        "label": "安全措施 (JSON)",
                        "type": "json",
                        "placeholder": '[{"text":"✓ 安全措施1"},...]'
                    },
                    {
                        "name": "customer_support",
                        "label": "客户支持 (JSON)",
                        "type": "json",
                        "placeholder": '[{"type":"24/5支持","description":"..."},...]'
                    }
                ]
            },
            {
                "title": "学习资源",
                "fields": [
                    {
                        "name": "learning_resources",
                        "label": "学习资源 (JSON)",
                        "type": "json",
                        "placeholder": '[{"title":"资源","description":"...","link":"..."},...]'
                    }
                ]
            },
            {
                "title": "平台介绍信息",
                "fields": [
                    {
                        "name": "introduction",
                        "label": "平台介绍",
                        "type": "textarea",
                        "placeholder": "详细介绍平台的基本信息"
                    },
                    {
                        "name": "main_features",
                        "label": "主要特性 (JSON)",
                        "type": "json",
                        "placeholder": '[{"title":"特性1","desc":"描述1"},...]'
                    },
                    {
                        "name": "fee_structure",
                        "label": "费用结构 (JSON)",
                        "type": "json",
                        "placeholder": '[{"type":"手续费","value":"0.5%","desc":"..."},...]'
                    },
                    {
                        "name": "account_opening_link",
                        "label": "开户链接",
                        "type": "text",
                        "placeholder": "https://..."
                    }
                ]
            },
            {
                "title": "交易参数",
                "fields": [
                    {
                        "name": "min_leverage",
                        "label": "最小杠杆",
                        "type": "number",
                        "placeholder": "1.0"
                    },
                    {
                        "name": "max_leverage",
                        "label": "最大杠杆",
                        "type": "number",
                        "placeholder": "500"
                    },
                    {
                        "name": "commission_rate",
                        "label": "佣金率 (0-1)",
                        "type": "number",
                        "min": 0,
                        "max": 1,
                        "step": 0.0001,
                        "placeholder": "0.005 (小数形式，例: 0.001, 0.005)"
                    },
                    {
                        "name": "fee_rate",
                        "label": "费率 (0-1)",
                        "type": "number",
                        "min": 0,
                        "max": 1,
                        "step": 0.0001,
                        "placeholder": "0.005 (小数形式，例: 0.001, 0.5)"
                    }
                ]
            },
            {
                "title": "其他信息",
                "fields": [
                    {
                        "name": "is_regulated",
                        "label": "是否受监管",
                        "type": "checkbox",
                        "default": False
                    },
                    {
                        "name": "is_featured",
                        "label": "是否精选",
                        "type": "checkbox",
                        "default": False
                    }
                ]
            }
        ]
    }
    
    return PlatformEditFormDefinition(**form_definition)


@router.get("/edit-list")
async def list_platforms_for_edit(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取平台列表 - 用于管理界面
    
    返回简化版本，仅包含基础信息和关键字段。
    """
    platforms, total = PlatformService.get_platforms(
        db, skip=skip, limit=limit
    )
    
    items = []
    for p in platforms:
        items.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "rating": p.rating,
            "rank": p.rank,
            "platform_type": p.platform_type,
            "platform_source": p.platform_source,
            "is_active": p.is_active,
            "is_recommended": p.is_recommended,
            "updated_at": p.updated_at,
        })
    
    return PlatformEditListResponse(items=items, total=total)


@router.get("/{platform_id}/edit", response_model=PlatformEditResponse)
async def get_platform_for_edit(
    platform_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取单个平台详情 - 用于编辑表单
    
    返回所有可编辑字段。
    """
    platform = PlatformService.get_platform(db, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
    
    return PlatformEditResponse.model_validate(platform)


@router.post("/{platform_id}/edit", response_model=PlatformEditResponse)
async def update_platform_details(
    platform_id: int,
    platform_data: PlatformEditForm,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新平台详情 - 用于编辑表单
    
    更新所有平台字段，包括详情页面的所有内容。
    """
    try:
        # 转换为Update模型
        from app.schemas.platform import PlatformUpdate
        update_data = PlatformUpdate(**platform_data.model_dump(exclude_unset=True))
        
        platform = PlatformService.update_platform(db, platform_id, update_data)
        if not platform:
            raise HTTPException(status_code=404, detail=f"平台 ID {platform_id} 不存在")
        
        return PlatformEditResponse.model_validate(platform)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
