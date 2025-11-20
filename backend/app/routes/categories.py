"""
分类管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Category, Section, Article
from app.routes.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    """分类创建模型"""
    name: str
    description: str = None
    section_id: int
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """分类更新模型"""
    name: str = None
    description: str = None
    sort_order: int = None
    is_active: bool = None


class CategoryResponse(BaseModel):
    """分类响应模型"""
    id: int
    name: str
    description: str | None = None
    section_id: int
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class CategoryWithCountResponse(BaseModel):
    """分类及文章数响应模型"""
    id: int
    name: str
    description: str | None = None
    article_count: int
    sort_order: int

    class Config:
        from_attributes = True


@router.get("", response_model=list[CategoryResponse])
async def list_all_categories(
    db: Session = Depends(get_db),
):
    """列出所有分类"""
    categories = db.query(Category).filter(
        Category.is_active == True
    ).order_by(Category.sort_order).all()

    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/section/{section_id}/with-count", response_model=list[CategoryWithCountResponse])
async def list_categories_with_article_count(
    section_id: int,
    db: Session = Depends(get_db),
):
    """获取某个栏目的分类及其文章数"""
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="栏目不存在")

    categories = db.query(Category).filter(
        Category.section_id == section_id,
        Category.is_active == True
    ).order_by(Category.sort_order).all()

    result = []
    for category in categories:
        # 统计该分类下的文章数
        article_count = db.query(func.count(Article.id)).filter(
            Article.category_id == category.id,
            Article.is_published == True
        ).scalar() or 0
        
        result.append(CategoryWithCountResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            article_count=article_count,
            sort_order=category.sort_order
        ))

    return result


@router.get("/section/{section_id}", response_model=list[CategoryResponse])
async def list_categories_by_section(
    section_id: int,
    db: Session = Depends(get_db),
):
    """获取某个栏目的所有分类"""
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="栏目不存在")

    categories = db.query(Category).filter(
        Category.section_id == section_id,
        Category.is_active == True
    ).order_by(Category.sort_order).all()

    return [CategoryResponse.model_validate(c) for c in categories]


@router.post("", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建分类"""
    # 检查栏目是否存在
    section = db.query(Section).filter(Section.id == category_data.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="栏目不存在")

    # 检查分类名是否已在该栏目中存在
    existing = db.query(Category).filter(
        Category.name == category_data.name,
        Category.section_id == category_data.section_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该分类名已存在")

    category = Category(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)

    return CategoryResponse.model_validate(category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """获取单个分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    db.delete(category)
    db.commit()

    return {"message": "分类已删除"}
