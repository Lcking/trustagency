"""
数据库初始化脚本
"""
from app.database import engine, SessionLocal, Base
from app.models.admin_user import AdminUser
from app.models.platform import Platform
from app.models.article import Article
from app.models.ai_task import AIGenerationTask
from app.models.section import Section
from app.models.category import Category
from app.models.ai_config import AIConfig
from app.utils.security import hash_password
from datetime import datetime


def init_db():
    """初始化数据库，创建表和默认管理员"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")

    db = SessionLocal()
    try:
        # 检查是否存在默认管理员
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            # 创建默认管理员
            admin = AdminUser(
                username="admin",
                email="admin@trustagency.com",
                full_name="Administrator",
                hashed_password=hash_password("newpassword123"),
                is_active=True,
                is_superadmin=True,
                created_at=datetime.utcnow(),
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✅ 默认管理员创建成功 (用户名: admin / 密码: newpassword123)")
        else:
            print("✅ 管理员已存在")

        # 创建默认栏目
        sections = [
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
                "requires_platform": True,  # ← 该栏目需要关联平台
                "sort_order": 4,
                "is_active": True,
            },
        ]

        for section_data in sections:
            existing = db.query(Section).filter(
                Section.slug == section_data["slug"]
            ).first()
            if not existing:
                section = Section(**section_data)
                db.add(section)

        db.commit()
        print("✅ 默认栏目创建成功 (FAQ, Wiki, Guide, Review)")

        # 为每个栏目创建默认分类
        default_categories = {
            "faq": ["基础知识", "账户管理", "交易问题", "安全", "其他"],
            "wiki": ["基础概念", "交易对", "技术分析", "风险管理", "法规"],
            "guide": ["新手教程", "交易策略", "风险管理", "资金管理", "高级技巧"],
            "review": ["安全评估", "功能评测", "用户评价", "监管许可", "服务评分"],
        }

        for section_data in sections:
            section = db.query(Section).filter(
                Section.slug == section_data["slug"]
            ).first()
            if section and section_data["slug"] in default_categories:
                # 为该栏目创建分类
                for idx, cat_name in enumerate(default_categories[section_data["slug"]], 1):
                    existing_cat = db.query(Category).filter(
                        Category.section_id == section.id,
                        Category.name == cat_name
                    ).first()
                    if not existing_cat:
                        category = Category(
                            name=cat_name,
                            section_id=section.id,
                            sort_order=idx,
                            is_active=True,
                        )
                        db.add(category)
        
        db.commit()
        print("✅ 默认分类创建成功 (每个栏目 5 个分类)")

        # 创建默认平台示例
        platforms = [
            {
                "name": "AlphaLeverage",
                "description": "Professional forex trading platform",
                "website_url": "https://alphaleverage.com",
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
                "website_url": "https://betamargin.com",
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
                "description": "Professional trading platform",
                "website_url": "https://gammatrader.com",
                "rating": 4.6,
                "rank": 3,
                "min_leverage": 1.0,
                "max_leverage": 400.0,
                "commission_rate": 0.004,
                "is_regulated": True,
                "is_active": True,
            },
        ]

        for platform_data in platforms:
            existing = db.query(Platform).filter(
                Platform.name == platform_data["name"]
            ).first()
            if not existing:
                platform = Platform(**platform_data)
                db.add(platform)
            else:
                # 如果平台已存在，更新website_url
                if not existing.website_url or existing.website_url != platform_data.get("website_url"):
                    existing.website_url = platform_data.get("website_url")
                    print(f"✅ 已更新平台 {existing.name} 的website_url")

        db.commit()
        print("✅ 默认平台创建/更新成功")

        # 创建默认 AI 生成任务配置
        ai_configs = [
            {
                "name": "OpenAI GPT-4",
                "provider": "openai",
                "model_name": "gpt-4",
                "api_key": "sk-xxxxx",
                "is_active": False,
                "description": "OpenAI GPT-4 model",
                "temperature": 70,
                "max_tokens": 2000,
                "top_p": 90,
            },
            {
                "name": "DeepSeek",
                "provider": "deepseek",
                "model_name": "deepseek-chat",
                "api_key": "sk-xxxxx",
                "is_active": False,
                "description": "DeepSeek model",
                "temperature": 70,
                "max_tokens": 2000,
                "top_p": 90,
            },
            {
                "name": "中转链接",
                "provider": "midpoint",
                "model_name": "gpt-3.5-turbo",
                "api_key": "sk-xxxxx",
                "is_active": False,
                "description": "Midpoint API",
                "temperature": 70,
                "max_tokens": 2000,
                "top_p": 90,
            },
        ]

        for config_data in ai_configs:
            existing = db.query(AIConfig).filter(
                AIConfig.name == config_data["name"]
            ).first()
            if not existing:
                ai_config = AIConfig(**config_data)
                db.add(ai_config)

        db.commit()
        print("✅ 默认 AI 配置创建成功 (OpenAI GPT-4, DeepSeek, 中转链接)")

        # 创建示例文章，用于演示分类统计功能
        print("\n📝 创建示例文章以演示分类统计...")
        
        # 为 FAQ 栏目的"基础知识"分类创建文章
        faq_section = db.query(Section).filter(Section.slug == "faq").first()
        if faq_section:
            basic_category = db.query(Category).filter(
                Category.section_id == faq_section.id,
                Category.name == "基础知识"
            ).first()
            
            if basic_category:
                # 创建 3 篇示例文章
                sample_articles = [
                    {
                        "title": "什么是杠杆交易？",
                        "content": "杠杆交易是一种使用借来的资金进行更大规模交易的方式。了解杠杆风险对成功交易至关重要。",
                        "summary": "杠杆交易基础概念",
                        "category_id": basic_category.id,
                        "platform_id": None,
                        "is_published": True,
                        "views": 150,
                    },
                    {
                        "title": "如何选择交易平台？",
                        "content": "选择交易平台时需要考虑安全性、手续费、杠杆比例和用户体验等多个因素。",
                        "summary": "平台选择指南",
                        "category_id": basic_category.id,
                        "platform_id": None,
                        "is_published": True,
                        "views": 200,
                    },
                    {
                        "title": "风险管理基础",
                        "content": "良好的风险管理是长期交易成功的基石。学会控制风险比追求高收益更重要。",
                        "summary": "风险管理入门",
                        "category_id": basic_category.id,
                        "platform_id": None,
                        "is_published": True,
                        "views": 180,
                    },
                ]
                
                for article_data in sample_articles:
                    existing_article = db.query(Article).filter(
                        Article.title == article_data["title"]
                    ).first()
                    if not existing_article:
                        article = Article(
                            **article_data,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(article)
                        print(f"  ✅ 创建文章: {article_data['title']}")
                
                db.commit()
                print(f"✅ 已为分类 '{basic_category.name}' 创建 3 篇示例文章")

    except Exception as e:
        db.rollback()
        print(f"❌ 初始化错误: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("\n✅ 数据库初始化完成！")
