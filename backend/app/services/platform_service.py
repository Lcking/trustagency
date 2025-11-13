"""
平台管理服务层
处理平台的业务逻辑，包括 CRUD、搜索、排序、分页等
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate, PlatformResponse
from typing import List, Optional, Tuple


class PlatformService:
    """平台管理服务类"""

    @staticmethod
    def create_platform(db: Session, platform_data: PlatformCreate) -> Platform:
        """
        创建新平台
        
        Args:
            db: 数据库会话
            platform_data: 平台创建数据
            
        Returns:
            创建的平台对象
            
        Raises:
            ValueError: 平台名称已存在
        """
        # 检查平台名称是否已存在
        existing = db.query(Platform).filter(Platform.name == platform_data.name).first()
        if existing:
            raise ValueError(f"平台名称 '{platform_data.name}' 已存在")

        # 创建新平台
        db_platform = Platform(**platform_data.model_dump())
        db.add(db_platform)
        db.commit()
        db.refresh(db_platform)
        return db_platform

    @staticmethod
    def get_platform(db: Session, platform_id: int) -> Optional[Platform]:
        """
        获取单个平台
        
        Args:
            db: 数据库会话
            platform_id: 平台 ID
            
        Returns:
            平台对象或 None
        """
        return db.query(Platform).filter(Platform.id == platform_id).first()

    @staticmethod
    def get_platforms(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "rank",
        sort_order: str = "asc",
        is_active: Optional[bool] = None,
        is_featured: Optional[bool] = None,
    ) -> Tuple[List[Platform], int]:
        """
        获取平台列表（支持搜索、排序、分页）
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            search: 搜索关键词（搜索名称和描述）
            sort_by: 排序字段 (name, rank, rating, commission_rate, created_at, recommended)
            sort_order: 排序顺序 (asc, desc)
            is_active: 过滤活跃状态
            is_featured: 过滤精选状态
            
        Returns:
            (平台列表, 总数) 元组
        """
        query = db.query(Platform)

        # 应用搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Platform.name.ilike(search_pattern),
                    Platform.description.ilike(search_pattern),
                )
            )

        # 应用状态过滤
        if is_active is not None:
            query = query.filter(Platform.is_active == is_active)

        if is_featured is not None:
            query = query.filter(Platform.is_featured == is_featured)

        # 获取总数（过滤后）
        total = query.count()

        # Bug004修复：应用排序 - 支持推荐排序
        if sort_by == "rating":
            # 评分最高排在前面
            query = query.order_by(Platform.rating.desc())
        elif sort_by == "leverage":
            # 杠杆最高排在前面
            query = query.order_by(Platform.max_leverage.desc())
        elif sort_by == "fee":
            # 费率最低排在前面
            query = query.order_by(Platform.commission_rate.asc())
        elif sort_by == "recommended":
            # Bug002修复：推荐排序 - 推荐的平台优先，然后按评分排序
            query = query.order_by(Platform.is_recommended.desc(), Platform.rating.desc())
        elif sort_by == "ranking":
            # 推荐排序（默认）
            query = query.order_by(Platform.is_recommended.desc(), Platform.rating.desc())
        else:
            # 默认排序字段
            sort_columns = {
                "name": Platform.name,
                "rank": Platform.rank,
                "commission_rate": Platform.commission_rate,
                "created_at": Platform.created_at,
            }
            sort_column = sort_columns.get(sort_by, Platform.rank)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # 应用分页
        platforms = query.offset(skip).limit(limit).all()

        return platforms, total

    @staticmethod
    def update_platform(
        db: Session, platform_id: int, platform_data: PlatformUpdate
    ) -> Optional[Platform]:
        """
        更新平台
        
        Args:
            db: 数据库会话
            platform_id: 平台 ID
            platform_data: 更新数据
            
        Returns:
            更新后的平台对象或 None
            
        Raises:
            ValueError: 平台名称已存在或平台不存在
        """
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not db_platform:
            raise ValueError(f"平台 ID {platform_id} 不存在")

        # 检查新名称是否已被其他平台使用
        if platform_data.name:
            existing = db.query(Platform).filter(
                and_(Platform.name == platform_data.name, Platform.id != platform_id)
            ).first()
            if existing:
                raise ValueError(f"平台名称 '{platform_data.name}' 已存在")

        # 更新字段
        update_data = platform_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_platform, field, value)

        db.add(db_platform)
        db.commit()
        db.refresh(db_platform)
        return db_platform

    @staticmethod
    def delete_platform(db: Session, platform_id: int) -> bool:
        """
        删除平台
        
        Args:
            db: 数据库会话
            platform_id: 平台 ID
            
        Returns:
            True 如果删除成功，False 如果平台不存在
        """
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not db_platform:
            return False

        db.delete(db_platform)
        db.commit()
        return True

    @staticmethod
    def update_platform_ranks(db: Session, rank_data: dict) -> int:
        """
        批量更新平台排名
        
        Args:
            db: 数据库会话
            rank_data: 排名数据 {platform_id: rank_value}
            
        Returns:
            更新的平台数量
            
        Raises:
            ValueError: 无效的平台 ID
        """
        updated_count = 0

        for platform_id, rank in rank_data.items():
            db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
            if not db_platform:
                raise ValueError(f"平台 ID {platform_id} 不存在")

            db_platform.rank = rank
            db.add(db_platform)
            updated_count += 1

        db.commit()
        return updated_count

    @staticmethod
    def get_featured_platforms(db: Session, limit: int = 5) -> List[Platform]:
        """
        获取精选平台
        
        Args:
            db: 数据库会话
            limit: 返回的最大数量
            
        Returns:
            精选平台列表
        """
        return (
            db.query(Platform)
            .filter(and_(Platform.is_featured == True, Platform.is_active == True))
            .order_by(Platform.rank.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_regulated_platforms(db: Session) -> List[Platform]:
        """
        获取所有监管平台
        
        Args:
            db: 数据库会话
            
        Returns:
            监管平台列表
        """
        return (
            db.query(Platform)
            .filter(and_(Platform.is_regulated == True, Platform.is_active == True))
            .order_by(Platform.rank.asc())
            .all()
        )

    @staticmethod
    def toggle_platform_status(db: Session, platform_id: int) -> Optional[Platform]:
        """
        切换平台活跃状态
        
        Args:
            db: 数据库会话
            platform_id: 平台 ID
            
        Returns:
            更新后的平台对象或 None
        """
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not db_platform:
            return None

        db_platform.is_active = not db_platform.is_active
        db.add(db_platform)
        db.commit()
        db.refresh(db_platform)
        return db_platform

    @staticmethod
    def toggle_platform_featured(db: Session, platform_id: int) -> Optional[Platform]:
        """
        切换平台精选状态
        
        Args:
            db: 数据库会话
            platform_id: 平台 ID
            
        Returns:
            更新后的平台对象或 None
        """
        db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not db_platform:
            return None

        db_platform.is_featured = not db_platform.is_featured
        db.add(db_platform)
        db.commit()
        db.refresh(db_platform)
        return db_platform
