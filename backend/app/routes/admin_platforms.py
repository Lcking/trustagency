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
                        "label": "安全评级",
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
                        "label": "平台类型",
                        "type": "select",
                        "options": [
                            {"label": "专业", "value": "专业"},
                            {"label": "平衡", "value": "平衡"},
                            {"label": "新手友好", "value": "新手友好"},
                            {"label": "高风险", "value": "高风险"}
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
                        "label": "佣金率",
                        "type": "number",
                        "placeholder": "0.005 (小数形式)"
                    },
                    {
                        "name": "fee_rate",
                        "label": "费率 (%)",
                        "type": "number",
                        "placeholder": "0.5 (百分比形式)"
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
    包括基础信息、详细内容、媒体、交易信息等所有字段。
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
                        "placeholder": "例如: Binance"
                    },
                    {
                        "name": "slug",
                        "label": "URL Slug *",
                        "type": "text",
                        "required": True,
                        "placeholder": "例如: binance (只能包含字母、数字和连字符)"
                    },
                    {
                        "name": "platform_type",
                        "label": "平台类型 *",
                        "type": "select",
                        "required": True,
                        "options": [
                            {"value": "exchange", "label": "交易所"},
                            {"value": "cex", "label": "中心化交易所"},
                            {"value": "dex", "label": "去中心化交易所"},
                            {"value": "broker", "label": "经纪商"},
                            {"value": "wallet", "label": "钱包"},
                            {"value": "other", "label": "其他"}
                        ]
                    },
                    {
                        "name": "rating",
                        "label": "评分 (0-10) *",
                        "type": "number",
                        "required": True,
                        "min": 0,
                        "max": 10
                    },
                    {
                        "name": "rank",
                        "label": "排名 *",
                        "type": "number",
                        "required": True,
                        "min": 1
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
                "title": "平台概述",
                "fields": [
                    {
                        "name": "description",
                        "label": "描述",
                        "type": "textarea",
                        "placeholder": "平台的简短描述"
                    },
                    {
                        "name": "overview_intro",
                        "label": "概述介绍",
                        "type": "textarea",
                        "placeholder": "平台的详细概述和介绍"
                    }
                ]
            },
            {
                "title": "交易信息",
                "fields": [
                    {
                        "name": "trading_pairs",
                        "label": "交易对 (JSON)",
                        "type": "number",
                        "placeholder": "例如: 1000"
                    },
                    {
                        "name": "daily_volume",
                        "label": "日均交易量 (美元)",
                        "type": "text",
                        "placeholder": "例如: $10 Billion"
                    },
                    {
                        "name": "founded_year",
                        "label": "成立年份",
                        "type": "number",
                        "min": 2000,
                        "max": 2100,
                        "placeholder": "例如: 2017"
                    },
                    {
                        "name": "fee_table",
                        "label": "费率表 (HTML/Markdown)",
                        "type": "textarea",
                        "placeholder": "平台的详细费率表"
                    }
                ]
            },
            {
                "title": "安全信息",
                "fields": [
                    {
                        "name": "safety_rating",
                        "label": "安全评级 (0-10)",
                        "type": "number",
                        "min": 0,
                        "max": 10,
                        "placeholder": "平台安全评分"
                    },
                    {
                        "name": "safety_info",
                        "label": "安全信息",
                        "type": "textarea",
                        "placeholder": "安全特性、审计报告等信息"
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
                        "name": "official_website",
                        "label": "官方网站",
                        "type": "text",
                        "placeholder": "https://example.com"
                    },
                    {
                        "name": "twitter_url",
                        "label": "Twitter URL",
                        "type": "text",
                        "placeholder": "https://twitter.com/..."
                    }
                ]
            },
            {
                "title": "优势和特性",
                "fields": [
                    {
                        "name": "advantages",
                        "label": "优势 (JSON)",
                        "type": "json",
                        "placeholder": '["低费率","高安全性","多币种"]'
                    },
                    {
                        "name": "features",
                        "label": "特性 (JSON)",
                        "type": "json",
                        "placeholder": '["现货交易","合约交易","杠杆交易"]'
                    }
                ]
            },
            {
                "title": "支持的币种",
                "fields": [
                    {
                        "name": "supported_coins",
                        "label": "支持的币种 (JSON)",
                        "type": "json",
                        "placeholder": '["Bitcoin","Ethereum","Ripple"]'
                    }
                ]
            },
            {
                "title": "入金/出金方式",
                "fields": [
                    {
                        "name": "deposit_methods",
                        "label": "入金方式 (JSON)",
                        "type": "json",
                        "placeholder": '["银行转账","信用卡","加密货币"]'
                    },
                    {
                        "name": "withdrawal_methods",
                        "label": "出金方式 (JSON)",
                        "type": "json",
                        "placeholder": '["银行转账","信用卡","加密货币"]'
                    }
                ]
            },
            {
                "title": "用户体验",
                "fields": [
                    {
                        "name": "user_experience",
                        "label": "用户体验描述",
                        "type": "textarea",
                        "placeholder": "平台的易用性、界面设计等"
                    },
                    {
                        "name": "pros",
                        "label": "优点 (JSON)",
                        "type": "json",
                        "placeholder": '["优点1","优点2"]'
                    },
                    {
                        "name": "cons",
                        "label": "缺点 (JSON)",
                        "type": "json",
                        "placeholder": '["缺点1","缺点2"]'
                    }
                ]
            },
            {
                "title": "市场信息",
                "fields": [
                    {
                        "name": "market_cap",
                        "label": "市值排名",
                        "type": "number",
                        "placeholder": "例如: 1"
                    },
                    {
                        "name": "market_share",
                        "label": "市场份额 (%)",
                        "type": "number",
                        "min": 0,
                        "max": 100,
                        "placeholder": "例如: 25.5"
                    }
                ]
            },
            {
                "title": "监管信息",
                "fields": [
                    {
                        "name": "regulation_status",
                        "label": "监管状态",
                        "type": "text",
                        "placeholder": "例如: 正规军、灰色地带、不合规"
                    },
                    {
                        "name": "license_info",
                        "label": "许可证信息 (JSON)",
                        "type": "json",
                        "placeholder": '[{"country":"新加坡","license":"MSB"}]'
                    }
                ]
            },
            {
                "title": "客服和支持",
                "fields": [
                    {
                        "name": "customer_service",
                        "label": "客服描述",
                        "type": "textarea",
                        "placeholder": "客服可用性、支持语言等"
                    },
                    {
                        "name": "support_languages",
                        "label": "支持语言 (JSON)",
                        "type": "json",
                        "placeholder": '["中文","英文","日文"]'
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
