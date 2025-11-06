"""
数据库连接和会话配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# 从环境变量获取数据库 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trustagency.db")

# 根据数据库类型配置引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite 配置（开发环境）
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL 配置（生产环境）
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类（用于 ORM 模型）
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    from app.models.admin_user import AdminUser
    from app.models.platform import Platform
    from app.models.article import Article
    from app.models.ai_task import AIGenerationTask
    
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化成功")
