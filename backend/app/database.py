"""
数据库连接和会话配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# 从环境变量获取数据库 URL
# 优先使用SQLite进行本地开发
import os as _os_module
_db_url_env = _os_module.getenv("DATABASE_URL", None)

# 如果环境变量为 PostgreSQL 但我们在本地开发,使用 SQLite
if _db_url_env and "postgresql" in _db_url_env:
    # 本地开发模式，强制使用 SQLite
    DATABASE_URL = "sqlite:///./trustagency.db"
else:
    DATABASE_URL = _db_url_env or "sqlite:///./trustagency.db"

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
    """初始化数据库：创建表、默认管理员、栏目、平台、AI配置"""
    from app.models.admin_user import AdminUser
    from app.models.platform import Platform
    from app.models.section import Section
    from app.models.article import Article
    from app.models.ai_task import AIGenerationTask
    from app.models.ai_config import AIConfig
    from app.utils.security import hash_password
    from datetime import datetime
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")
    
    db = SessionLocal()
    try:
        # 1. 创建默认管理员
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            hashed_pwd = hash_password("admin123")
            admin = AdminUser(
                username="admin",
                email="admin@trustagency.com",
                full_name="Administrator",
                hashed_password=hashed_pwd,
                is_active=True,
                is_superadmin=True,
                created_at=datetime.utcnow(),
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✅ 默认管理员创建成功 (ID: {admin.id}, 用户名: admin, 密码: admin123)")
        else:
            print(f"ℹ️ 管理员已存在 (ID: {admin.id}, 用户名: {admin.username})")
        
        # 2. 创建默认栏目（包含 requires_platform 字段）
        sections_data = [
            {
                "name": "常见问题",
                "slug": "faq",
                "description": "常见问题解答",
                "requires_platform": False,
                "sort_order": 1,
                "is_active": True,
            },
            {
                "name": "百科",
                "slug": "wiki",
                "description": "区块链和加密货币百科",
                "requires_platform": False,
                "sort_order": 2,
                "is_active": True,
            },
            {
                "name": "指南",
                "slug": "guide",
                "description": "交易和投资指南",
                "requires_platform": False,
                "sort_order": 3,
                "is_active": True,
            },
            {
                "name": "验证",
                "slug": "review",
                "description": "平台验证和审查记录",
                "requires_platform": True,  # 该栏目需要关联平台
                "sort_order": 4,
                "is_active": True,
            },
        ]
        
        for section_data in sections_data:
            existing = db.query(Section).filter(Section.slug == section_data["slug"]).first()
            if not existing:
                section = Section(**section_data)
                db.add(section)
        
        db.commit()
        print("✅ 默认栏目创建成功 (FAQ, Wiki, Guide, Review)")
        
        # 2.5. 创建默认分类（针对每个栏目）
        from app.models.category import Category
        
        # 获取创建好的栏目
        sections = {s.slug: s for s in db.query(Section).all()}
        
        categories_data = [
            # 常见问题分类
            {"name": "入门问题", "section_id": sections["faq"].id, "sort_order": 1},
            {"name": "平台选择", "section_id": sections["faq"].id, "sort_order": 2},
            {"name": "交易相关", "section_id": sections["faq"].id, "sort_order": 3},
            {"name": "风险管理", "section_id": sections["faq"].id, "sort_order": 4},
            
            # 百科分类
            {"name": "基础概念", "section_id": sections["wiki"].id, "sort_order": 1},
            {"name": "交易术语", "section_id": sections["wiki"].id, "sort_order": 2},
            {"name": "市场分析", "section_id": sections["wiki"].id, "sort_order": 3},
            {"name": "技术指标", "section_id": sections["wiki"].id, "sort_order": 4},
            
            # 指南分类
            {"name": "新手指南", "section_id": sections["guide"].id, "sort_order": 1},
            {"name": "进阶策略", "section_id": sections["guide"].id, "sort_order": 2},
            {"name": "风险控制", "section_id": sections["guide"].id, "sort_order": 3},
            {"name": "工具使用", "section_id": sections["guide"].id, "sort_order": 4},
            
            # 验证分类
            {"name": "平台验证", "section_id": sections["review"].id, "sort_order": 1},
            {"name": "用户评价", "section_id": sections["review"].id, "sort_order": 2},
            {"name": "安全审计", "section_id": sections["review"].id, "sort_order": 3},
            {"name": "监管信息", "section_id": sections["review"].id, "sort_order": 4},
        ]
        
        for category_data in categories_data:
            existing = db.query(Category).filter(
                Category.name == category_data["name"],
                Category.section_id == category_data["section_id"]
            ).first()
            if not existing:
                category = Category(**category_data)
                db.add(category)
        
        db.commit()
        print("✅ 默认分类创建成功 (16个分类)")
        
        # 3. 创建默认平台
        platforms_data = [
            {
                "name": "AlphaLeverage",
                "description": "Professional forex trading platform",
                "rating": 4.8,
                "rank": 1,
                "min_leverage": 1.0,
                "max_leverage": 500.0,
                "commission_rate": 0.005,
                "is_regulated": True,
                "is_active": True,
            },
            {
                "name": "BetaMargin",
                "description": "Advanced trading with margin",
                "rating": 4.5,
                "rank": 2,
                "min_leverage": 1.0,
                "max_leverage": 300.0,
                "commission_rate": 0.003,
                "is_regulated": True,
                "is_active": True,
            },
            {
                "name": "GammaTrader",
                "description": "Crypto derivatives trading",
                "rating": 4.3,
                "rank": 3,
                "min_leverage": 1.0,
                "max_leverage": 200.0,
                "commission_rate": 0.001,
                "is_regulated": False,
                "is_active": True,
            },
        ]
        
        for platform_data in platforms_data:
            # 使用 raw SQL 检查而不是 ORM，以避免加载不存在的列
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("SELECT id FROM platforms WHERE name = :name"), {"name": platform_data["name"]}).first()
            if not result:
                platform = Platform(**platform_data)
                db.add(platform)
        
        db.commit()
        print("✅ 默认平台创建成功 (AlphaLeverage, BetaMargin, GammaTrader)")
        
        # 4. 创建默认 AI 配置
        ai_configs_data = [
            {
                "name": "OpenAI GPT-4",
                "provider": "openai",
                "api_endpoint": "https://api.openai.com/v1",
                "api_key": "sk-your-key-here",  # 需要实际配置
                "model_name": "gpt-4",
                "model_version": "latest",
                "system_prompt": "你是一个专业的财务内容撰稿人。请用中文撰写关于股票杠杆和交易的高质量文章。",
                "user_prompt_template": "请撰写一篇关于'{title}'的文章，包含详细的解释、示例和建议。文章长度应该在1500-2000字之间。",
                "temperature": 7,
                "max_tokens": 2000,
                "top_p": 90,
                "is_active": True,
                "is_default": True,
                "description": "使用 OpenAI GPT-4 进行内容生成（推荐）",
                "retry_times": 3,
                "timeout_seconds": 120,
            },
            {
                "name": "DeepSeek",
                "provider": "deepseek",
                "api_endpoint": "https://api.deepseek.com/v1",
                "api_key": "sk-your-deepseek-key",  # 需要实际配置
                "model_name": "deepseek-chat",
                "model_version": "latest",
                "system_prompt": "你是一个专业的财务内容撰稿人。请用中文撰写关于股票杠杆和交易的高质量文章。",
                "user_prompt_template": "请撰写一篇关于'{title}'的文章，包含详细的解释、示例和建议。文章长度应该在1500-2000字之间。",
                "temperature": 7,
                "max_tokens": 2000,
                "top_p": 90,
                "is_active": True,
                "is_default": False,
                "description": "使用 DeepSeek 进行内容生成（国内支持）",
                "retry_times": 3,
                "timeout_seconds": 120,
            },
            {
                "name": "OpenAI 中转链接",
                "provider": "relay",
                "api_endpoint": "https://api.relay.com/v1",  # 中转链接
                "api_key": "relay-key-here",
                "model_name": "gpt-3.5-turbo",
                "model_version": "latest",
                "system_prompt": "你是一个专业的财务内容撰稿人。请用中文撰写关于股票杠杆和交易的高质量文章。",
                "user_prompt_template": "请撰写一篇关于'{title}'的文章，包含详细的解释、示例和建议。文章长度应该在1500-2000字之间。",
                "temperature": 7,
                "max_tokens": 2000,
                "top_p": 90,
                "is_active": True,
                "is_default": False,
                "description": "使用中转链接访问 OpenAI（当无法直连时使用）",
                "retry_times": 3,
                "timeout_seconds": 120,
            },
        ]
        
        for config_data in ai_configs_data:
            existing = db.query(AIConfig).filter(AIConfig.name == config_data["name"]).first()
            if not existing:
                config = AIConfig(**config_data)
                db.add(config)
        
        db.commit()
        print("✅ 默认 AI 配置创建成功 (OpenAI GPT-4, DeepSeek, 中转链接)")
        
    except Exception as e:
        print(f"❌ 初始化错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
