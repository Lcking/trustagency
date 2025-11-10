"""
栏目管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Section, Category
from app.routes.auth import get_current_user
from app.schemas.section import SectionResponse, SectionListResponse, SectionCreate, SectionUpdate

router = APIRouter(prefix="/api/sections", tags=["sections"])


@router.get("", response_model=SectionListResponse)
async def list_sections(
    db: Session = Depends(get_db),
):
    """
    获取所有栏目列表（包括 requires_platform 字段和分类数）
    
    前端可使用此端点动态加载栏目选项及其平台关联需求
    
    示例:
    ```
    GET /api/sections
    ```
    """
    sections = db.query(Section).filter(Section.is_active == True).order_by(Section.sort_order).all()
    
    result = []
    for section in sections:
        # 统计该栏目下的分类数
        category_count = db.query(func.count(Category.id)).filter(
            Category.section_id == section.id,
            Category.is_active == True
        ).scalar() or 0
        
        section_response = SectionResponse.model_validate(section)
        # 手动设置 category_count
        section_response.category_count = category_count
        result.append(section_response)
    
    total = len(result)
    return SectionListResponse(
        data=result,
        total=total,
    )


@router.get("/{section_id}", response_model=SectionResponse)
async def get_section(
    section_id: int,
    db: Session = Depends(get_db),
):
    """
    获取单个栏目信息
    
    Args:
        section_id: 栏目 ID
        
    示例:
    ```
    GET /api/sections/1
    ```
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail=f"栏目 ID {section_id} 不存在")
    return SectionResponse.model_validate(section)


@router.post("", response_model=SectionResponse)
async def create_section(
    section_data: SectionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新栏目（仅管理员）
    """
    # 检查别名是否已存在
    existing = db.query(Section).filter(Section.slug == section_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"别名 '{section_data.slug}' 已存在")
    
    section = Section(
        name=section_data.name,
        slug=section_data.slug,
        description=section_data.description,
        requires_platform=section_data.requires_platform,
        sort_order=section_data.sort_order,
        is_active=section_data.is_active,
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return SectionResponse.model_validate(section)


@router.put("/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int,
    section_data: SectionUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新栏目信息（仅管理员）
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail=f"栏目 ID {section_id} 不存在")
    
    # 检查别名是否已被其他栏目使用
    if section_data.slug and section_data.slug != section.slug:
        existing = db.query(Section).filter(
            Section.slug == section_data.slug,
            Section.id != section_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"别名 '{section_data.slug}' 已被其他栏目使用")
    
    # 更新字段
    if section_data.name:
        section.name = section_data.name
    if section_data.slug:
        section.slug = section_data.slug
    if section_data.description is not None:
        section.description = section_data.description
    if section_data.requires_platform is not None:
        section.requires_platform = section_data.requires_platform
    if section_data.sort_order is not None:
        section.sort_order = section_data.sort_order
    if section_data.is_active is not None:
        section.is_active = section_data.is_active
    
    db.commit()
    db.refresh(section)
    return SectionResponse.model_validate(section)


@router.delete("/{section_id}")
async def delete_section(
    section_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除栏目（仅管理员）
    """
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail=f"栏目 ID {section_id} 不存在")
    
    db.delete(section)
    db.commit()
    return {"message": "栏目已删除"}
