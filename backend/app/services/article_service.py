"""
文章管理服务层
处理文章的业务逻辑，包括 CRUD、发布、分类、搜索等
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models import Article, AdminUser, Platform
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from typing import List, Optional, Tuple
from datetime import datetime
from slugify import slugify


class ArticleService:
    """文章管理服务类"""

    @staticmethod
    def create_article(
        db: Session,
        article_data: ArticleCreate,
        author_id: int,
    ) -> Article:
        """
        创建新文章
        
        Args:
            db: 数据库会话
            article_data: 文章创建数据 (包含 section_id 和 platform_id)
            author_id: 作者 ID
            
        Returns:
            创建的文章对象
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证作者存在
        author = db.query(AdminUser).filter(AdminUser.id == author_id).first()
        if not author:
            raise ValueError(f"作者 ID {author_id} 不存在")
        
        # 验证平台存在（如果提供了 platform_id）
        if article_data.platform_id:
            platform = db.query(Platform).filter(Platform.id == article_data.platform_id).first()
            if not platform:
                raise ValueError(f"平台 ID {article_data.platform_id} 不存在")
        
        # 生成 slug
        slug = slugify(article_data.title)
        
        # 检查 slug 唯一性
        existing = db.query(Article).filter(Article.slug == slug).first()
        if existing:
            # 添加时间戳以确保唯一性
            slug = f"{slug}-{datetime.utcnow().timestamp()}"
        
        # 创建文章 - 逐个字段赋值以避免不支持的字段
        article = Article(
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            category_id=article_data.category_id,
            tags=article_data.tags,
            meta_description=article_data.meta_description,
            meta_keywords=article_data.meta_keywords,
            is_featured=article_data.is_featured,
            slug=slug,
            author_id=author_id,
            section_id=article_data.section_id,
            platform_id=article_data.platform_id  # 可能为 None
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def get_article(db: Session, article_id: int) -> Optional[Article]:
        """
        获取单个文章
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            
        Returns:
            文章对象或 None
        """
        article = db.query(Article).options(joinedload(Article.section)).filter(Article.id == article_id).first()
        
        # 增加浏览量
        if article:
            article.view_count = (article.view_count or 0) + 1
            db.add(article)
            db.commit()
        
        return article

    @staticmethod
    def get_articles(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        category_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        author_id: Optional[int] = None,
        is_published: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Article], int]:
        """
        获取文章列表（支持搜索、过滤、排序、分页）
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            search: 搜索关键词（搜索标题、内容、摘要）
            category: 分类过滤（传统字符串字段，用于向后兼容）
            category_id: 分类 ID 过滤（推荐使用）
            platform_id: 平台过滤
            author_id: 作者过滤
            is_published: 发布状态过滤
            is_featured: 精选状态过滤
            sort_by: 排序字段 (title, created_at, updated_at, view_count, like_count)
            sort_order: 排序顺序 (asc, desc)
            
        Returns:
            (文章列表, 总数) 元组
        """
        query = db.query(Article).options(joinedload(Article.category_obj), joinedload(Article.section))

        # 应用搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.summary.ilike(search_pattern),
                    Article.tags.ilike(search_pattern),
                )
            )

        # 应用分类过滤
        if category_id:
            query = query.filter(Article.category_id == category_id)

        # 应用平台过滤
        if platform_id:
            query = query.filter(Article.platform_id == platform_id)

        # 应用作者过滤
        if author_id:
            query = query.filter(Article.author_id == author_id)

        # 应用发布状态过滤
        if is_published is not None:
            query = query.filter(Article.is_published == is_published)

        # 应用精选状态过滤
        if is_featured is not None:
            query = query.filter(Article.is_featured == is_featured)

        # 获取总数（过滤后）
        total = query.count()

        # 应用排序
        sort_columns = {
            "title": Article.title,
            "created_at": Article.created_at,
            "updated_at": Article.updated_at,
            "view_count": Article.view_count,
            "like_count": Article.like_count,
        }

        sort_column = sort_columns.get(sort_by, Article.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # 应用分页
        articles = query.offset(skip).limit(limit).all()

        return articles, total

    @staticmethod
    def update_article(
        db: Session, article_id: int, article_data: ArticleUpdate
    ) -> Optional[Article]:
        """
        更新文章
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            article_data: 更新数据
            
        Returns:
            更新后的文章对象或 None
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise ValueError(f"文章 ID {article_id} 不存在")

        # 更新字段 - 只更新设置了的字段
        update_data = article_data.model_dump(exclude_unset=True)
        
        # 如果更新了标题，重新生成 slug
        if "title" in update_data:
            new_slug = slugify(update_data["title"])
            existing = db.query(Article).filter(
                and_(Article.slug == new_slug, Article.id != article_id)
            ).first()
            if existing:
                new_slug = f"{new_slug}-{datetime.utcnow().timestamp()}"
            update_data["slug"] = new_slug

        # 逐个字段更新，仅更新提供的字段
        for field, value in update_data.items():
            if hasattr(article, field) and field != 'id':  # 不更新 id
                setattr(article, field, value)

        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def delete_article(db: Session, article_id: int) -> bool:
        """
        删除文章
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            
        Returns:
            True 如果删除成功，False 如果文章不存在
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False

        db.delete(article)
        db.commit()
        return True

    @staticmethod
    def publish_article(db: Session, article_id: int) -> Optional[Article]:
        """
        发布文章（更新发布状态和发布时间）
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            
        Returns:
            更新后的文章对象或 None
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None

        article.is_published = True
        article.published_at = datetime.utcnow()
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def unpublish_article(db: Session, article_id: int) -> Optional[Article]:
        """
        取消发布文章
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            
        Returns:
            更新后的文章对象或 None
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None

        article.is_published = False
        article.published_at = None
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def toggle_featured(db: Session, article_id: int) -> Optional[Article]:
        """
        切换文章精选状态
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            
        Returns:
            更新后的文章对象或 None
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None

        article.is_featured = not article.is_featured
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def like_article(db: Session, article_id: int) -> Optional[Article]:
        """
        点赞文章
        
        Args:
            db: 数据库会话
            article_id: 文章 ID
            
        Returns:
            更新后的文章对象或 None
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None

        article.like_count = (article.like_count or 0) + 1
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def get_articles_by_platform(
        db: Session,
        platform_id: int,
        is_published: bool = True,
        limit: int = 10
    ) -> List[Article]:
        """
        获取特定平台的文章
        
        Args:
            db: 数据库会话
            platform_id: 平台 ID
            is_published: 只显示已发布文章
            limit: 最大返回数
            
        Returns:
            文章列表
        """
        query = db.query(Article).filter(Article.platform_id == platform_id)
        
        if is_published:
            query = query.filter(Article.is_published == True)
        
        return query.order_by(Article.created_at.desc()).limit(limit).all()



    @staticmethod
    def get_featured_articles(
        db: Session,
        limit: int = 5
    ) -> List[Article]:
        """
        获取精选文章
        
        Args:
            db: 数据库会话
            limit: 最大返回数
            
        Returns:
            精选文章列表
        """
        return (
            db.query(Article)
            .filter(and_(Article.is_featured == True, Article.is_published == True))
            .order_by(Article.like_count.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_articles_by_author(
        db: Session,
        author_id: int,
        limit: int = 10
    ) -> List[Article]:
        """
        获取作者发布的文章
        
        Args:
            db: 数据库会话
            author_id: 作者 ID
            limit: 最大返回数
            
        Returns:
            作者的文章列表
        """
        return (
            db.query(Article)
            .filter(Article.author_id == author_id)
            .order_by(Article.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_articles(
        db: Session,
        keyword: str,
        limit: int = 20
    ) -> List[Article]:
        """
        搜索已发布的文章
        
        Args:
            db: 数据库会话
            keyword: 搜索关键词
            limit: 最大返回数
            
        Returns:
            搜索结果列表
        """
        search_pattern = f"%{keyword}%"
        return (
            db.query(Article)
            .filter(
                and_(
                    Article.is_published == True,
                    or_(
                        Article.title.ilike(search_pattern),
                        Article.content.ilike(search_pattern),
                        Article.summary.ilike(search_pattern),
                        Article.tags.ilike(search_pattern),
                    )
                )
            )
            .order_by(Article.like_count.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_trending_articles(
        db: Session,
        limit: int = 10
    ) -> List[Article]:
        """
        获取热门文章（按点赞数排序）
        
        Args:
            db: 数据库会话
            limit: 最大返回数
            
        Returns:
            热门文章列表
        """
        return (
            db.query(Article)
            .filter(Article.is_published == True)
            .order_by(Article.like_count.desc(), Article.view_count.desc())
            .limit(limit)
            .all()
        )
