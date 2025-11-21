"""
网站全局设置 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.website_settings import WebsiteSettings
from app.models.admin_user import AdminUser
from app.routes.auth import get_current_user
import json

router = APIRouter(prefix="/api/website-settings", tags=["Website Settings"])

# Pydantic 模型用于请求/响应
from pydantic import BaseModel
from typing import Optional

class WebsiteSettingsUpdate(BaseModel):
    """网站设置更新模型"""
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    site_name: Optional[str] = None
    site_author: Optional[str] = None
    site_favicon: Optional[str] = None
    site_logo: Optional[str] = None
    google_analytics: Optional[str] = None
    baidu_analytics: Optional[str] = None
    custom_scripts: Optional[str] = None
    icp_number: Optional[str] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    footer_links: Optional[str] = None  # JSON 字符串
    
    class Config:
        from_attributes = True


class WebsiteSettingsResponse(BaseModel):
    """网站设置响应模型"""
    id: int
    site_title: str
    site_description: str
    site_keywords: str
    site_name: str
    site_author: str
    site_favicon: Optional[str]
    site_logo: Optional[str]
    google_analytics: Optional[str]
    baidu_analytics: Optional[str]
    custom_scripts: Optional[str]
    icp_number: Optional[str]
    company_name: Optional[str]
    company_address: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    footer_links: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("/")
async def get_website_settings(db: Session = Depends(get_db)):
    """获取网站全局设置（公开）"""
    settings = db.query(WebsiteSettings).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网站设置不存在"
        )
    
    # 手动转换为字典，日期格式化为 ISO 格式
    return {
        "id": settings.id,
        "site_title": settings.site_title,
        "site_description": settings.site_description,
        "site_keywords": settings.site_keywords,
        "site_name": settings.site_name,
        "site_author": settings.site_author,
        "site_favicon": settings.site_favicon,
        "site_logo": settings.site_logo,
        "google_analytics": settings.google_analytics,
        "baidu_analytics": settings.baidu_analytics,
        "custom_scripts": settings.custom_scripts,
        "icp_number": settings.icp_number,
        "company_name": settings.company_name,
        "company_address": settings.company_address,
        "contact_phone": settings.contact_phone,
        "contact_email": settings.contact_email,
        "footer_links": settings.footer_links,
        "created_at": settings.created_at.isoformat() if settings.created_at else None,
        "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
    }


@router.put("/", response_model=WebsiteSettingsResponse)
async def update_website_settings(
    settings_update: WebsiteSettingsUpdate,
    current_admin: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新网站全局设置（仅管理员）"""
    settings = db.query(WebsiteSettings).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网站设置不存在"
        )
    
    # 只更新提供的字段
    update_data = settings_update.dict(exclude_unset=True)
    
    # 验证 footer_links 是有效的 JSON（如果提供了）
    if "footer_links" in update_data and update_data["footer_links"]:
        try:
            json.loads(update_data["footer_links"])
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="footer_links 必须是有效的 JSON 字符串"
            )
    
    for field, value in update_data.items():
        if value is not None:
            setattr(settings, field, value)
    
    from datetime import datetime
    settings.updated_at = datetime.utcnow()
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    # 手动转换为字典
    return {
        "id": settings.id,
        "site_title": settings.site_title,
        "site_description": settings.site_description,
        "site_keywords": settings.site_keywords,
        "site_name": settings.site_name,
        "site_author": settings.site_author,
        "site_favicon": settings.site_favicon,
        "site_logo": settings.site_logo,
        "google_analytics": settings.google_analytics,
        "baidu_analytics": settings.baidu_analytics,
        "custom_scripts": settings.custom_scripts,
        "icp_number": settings.icp_number,
        "company_name": settings.company_name,
        "company_address": settings.company_address,
        "contact_phone": settings.contact_phone,
        "contact_email": settings.contact_email,
        "footer_links": settings.footer_links,
        "created_at": settings.created_at.isoformat() if settings.created_at else None,
        "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
    }


@router.get("/seo")
async def get_seo_settings(db: Session = Depends(get_db)):
    """获取 SEO 相关设置（公开）"""
    settings = db.query(WebsiteSettings).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网站设置不存在"
        )
    
    return {
        "site_title": settings.site_title,
        "site_description": settings.site_description,
        "site_keywords": settings.site_keywords,
        "site_author": settings.site_author,
    }


@router.get("/analytics")
async def get_analytics_settings(
    current_admin: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分析代码配置（仅管理员）"""
    settings = db.query(WebsiteSettings).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网站设置不存在"
        )
    
    return {
        "google_analytics": settings.google_analytics,
        "baidu_analytics": settings.baidu_analytics,
        "custom_scripts": settings.custom_scripts,
    }


@router.get("/footer")
async def get_footer_settings(db: Session = Depends(get_db)):
    """获取页脚相关设置（公开）"""
    settings = db.query(WebsiteSettings).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="网站设置不存在"
        )
    
    footer_links = []
    if settings.footer_links:
        try:
            footer_links = json.loads(settings.footer_links)
        except json.JSONDecodeError:
            footer_links = []
    
    return {
        "company_name": settings.company_name,
        "company_address": settings.company_address,
        "contact_phone": settings.contact_phone,
        "contact_email": settings.contact_email,
        "icp_number": settings.icp_number,
        "footer_links": footer_links,
    }
