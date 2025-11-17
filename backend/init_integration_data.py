#!/usr/bin/env python3
"""
数据整合初始化脚本
将前端静态数据迁移到后端数据库，创建完整的测试数据集
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import AdminUser, Platform, Article, Section, Category
from app.utils.security import hash_password
from datetime import datetime, timedelta

def init_integration_data():
    """初始化数据整合数据"""
    db = SessionLocal()
    
    try:
        # ========== 1. 确保管理员存在 ==========
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            hashed_pwd = hash_password("admin123")
            admin = AdminUser(
                username="admin",
                email="admin@trustagency.com",
                full_name="平台管理员",
                hashed_password=hashed_pwd,
                is_active=True,
                is_superadmin=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✅ 创建管理员: admin (ID: {admin.id})")
        else:
            print(f"ℹ️  管理员已存在: {admin.username} (ID: {admin.id})")
        
        admin_id = admin.id
        
        # ========== 2. 创建或获取栏目 (Sections) ==========
        print("\n📂 初始化栏目...")
        sections_data = {
            "wiki": {"name": "百科", "description": "杠杆交易知识库", "requires_platform": False},
            "guide": {"name": "指南", "description": "交易和投资指南", "requires_platform": False},
            "faq": {"name": "常见问题", "description": "常见问题解答", "requires_platform": False},
            "review": {"name": "平台评测", "description": "平台验证和评测", "requires_platform": True},
        }
        
        sections = {}
        for slug, section_data in sections_data.items():
            section = db.query(Section).filter(Section.slug == slug).first()
            if not section:
                section = Section(
                    name=section_data["name"],
                    slug=slug,
                    description=section_data["description"],
                    requires_platform=section_data["requires_platform"],
                )
                db.add(section)
                db.commit()
                db.refresh(section)
                print(f"  ✅ 创建栏目: {section.name}")
            else:
                print(f"  ℹ️  栏目已存在: {section.name}")
            sections[slug] = section
        
        # ========== 3. 创建或获取分类 (Categories) ==========
        print("\n📑 初始化分类...")
        categories_data = {
            "wiki": [
                {"name": "基础知识", "description": "杠杆交易基础概念"},
                {"name": "风险管理", "description": "风险管理和控制"},
                {"name": "交易技巧", "description": "交易技巧和策略"},
            ],
            "guide": [
                {"name": "快速开始", "description": "快速入门指南"},
                {"name": "开户步骤", "description": "账户开设流程"},
                {"name": "交易教程", "description": "交易操作指南"},
            ],
            "faq": [
                {"name": "平台相关", "description": "平台相关问题"},
                {"name": "交易相关", "description": "交易相关问题"},
                {"name": "风险相关", "description": "风险相关问题"},
                {"name": "其他", "description": "其他常见问题"},
            ],
        }
        
        categories = {}
        for section_slug, cats in categories_data.items():
            section = sections[section_slug]
            for cat_data in cats:
                key = f"{section_slug}_{cat_data['name']}"
                category = db.query(Category).filter(
                    Category.section_id == section.id,
                    Category.name == cat_data["name"]
                ).first()
                
                if not category:
                    category = Category(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        section_id=section.id,
                    )
                    db.add(category)
                    db.commit()
                    db.refresh(category)
                    print(f"  ✅ 创建分类 ({section.name}): {category.name}")
                else:
                    print(f"  ℹ️  分类已存在 ({section.name}): {category.name}")
                categories[key] = category
        
        # ========== 4. 创建或更新平台数据 ==========
        print("\n🏢 初始化平台...")
        platforms_data = [
            {
                "name": "Alpha Leverage",
                "slug": "alpha-leverage",
                "description": "高杠杆、低费率的专业交易平台，提供完善的风险管理工具和24/7客户支持。",
                "rating": 4.8,
                "rank": 1,
                "min_leverage": 1.0,
                "max_leverage": 100.0,
                "commission_rate": 0.001,
                "is_regulated": True,
                "website_url": "https://alpha-leverage.example.com",
                "is_featured": True,
            },
            {
                "name": "Beta Margin",
                "slug": "beta-margin",
                "description": "风险管理工具完善的保证金交易平台，特别适合风险厌恶型投资者。",
                "rating": 4.5,
                "rank": 2,
                "min_leverage": 1.0,
                "max_leverage": 50.0,
                "commission_rate": 0.0015,
                "is_regulated": True,
                "website_url": "https://beta-margin.example.com",
                "is_featured": True,
            },
            {
                "name": "Gamma Trader",
                "slug": "gamma-trader",
                "description": "新手友好、教育资源丰富的平台，配有详细的交易指南和视频教程。",
                "rating": 4.3,
                "rank": 3,
                "min_leverage": 1.0,
                "max_leverage": 75.0,
                "commission_rate": 0.0013,
                "is_regulated": False,
                "website_url": "https://gamma-trader.example.com",
                "is_featured": False,
            },
        ]
        
        platforms = {}
        for platform_data in platforms_data:
            platform = db.query(Platform).filter(Platform.name == platform_data["name"]).first()
            if not platform:
                platform = Platform(**platform_data, is_active=True)
                db.add(platform)
                db.commit()
                db.refresh(platform)
                print(f"  ✅ 创建平台: {platform.name}")
            else:
                print(f"  ℹ️  平台已存在: {platform.name}")
                # 更新基本信息
                for key, value in platform_data.items():
                    if key not in ["name"]:
                        setattr(platform, key, value)
                db.commit()
            platforms[platform_data["name"]] = platform
        
        # ========== 5. 创建知识库文章 (Wiki Articles) ==========
        print("\n📚 初始化知识库文章...")
        wiki_articles = [
            {
                "title": "什么是股票杠杆交易？",
                "slug": "what-is-leverage",
                "summary": "初学者指南：了解股票杠杆交易的基础知识、原理和风险。",
                "content": """# 什么是股票杠杆交易？

股票杠杆交易是指投资者向券商借入资金进行股票交易，以较小的本金控制较大的交易金额，以期放大收益。同时风险也会相应放大。

## 杠杆交易的原理

1. **借用资金**: 投资者通过向券商借钱来增加可用资金
2. **放大收益**: 通过杠杆放大潜在的投资收益
3. **风险放大**: 同时也会放大潜在的损失
4. **利息成本**: 需要支付借用资金的利息

## 杠杆比例

常见的杠杆比例包括：
- 1:2 - 2倍杠杆
- 1:5 - 5倍杠杆
- 1:10 - 10倍杠杆
- 1:100 - 100倍杠杆

## 风险提示

杠杆交易具有高风险。建议充分了解风险后再参与。
""",
                "category": "基础知识",
                "tags": "杠杆交易,初学者,基础知识",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "杠杆交易风险管理指南",
                "slug": "leverage-risk-management",
                "summary": "学习如何有效管理杠杆交易风险，保护你的投资。",
                "content": """# 杠杆交易风险管理指南

## 主要风险

1. **保证金追加风险**: 当账户价值下跌时，经纪商可能要求补充保证金
2. **爆仓风险**: 如果未及时补充保证金，可能被强制平仓
3. **利息风险**: 借用资金需要支付利息成本
4. **市场风险**: 价格波动可能导致重大亏损

## 风险管理策略

### 1. 设置止损单
始终为每个交易设置止损单，限制潜在损失。

### 2. 适度使用杠杆
不要使用过高的杠杆比例。建议初学者从低杠杆开始。

### 3. 资金管理
- 只投入你能承受损失的资金
- 不要把所有资金投入单个交易
- 保持充足的保证金缓冲

### 4. 定期检查
定期检查账户状态，确保保证金充足。

## 常见陷阱

- ❌ 过度交易
- ❌ 忽视风险管理
- ❌ 过度杠杆
- ❌ 感情交易
- ❌ 追求快速利润

## 最佳实践

- ✅ 制定交易计划
- ✅ 严格执行风险管理
- ✅ 持续学习
- ✅ 保持纪律
- ✅ 定期审查交易记录
""",
                "category": "风险管理",
                "tags": "风险管理,保护投资,止损",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "技术分析入门",
                "slug": "technical-analysis-intro",
                "summary": "学习如何使用技术分析工具进行交易决策。",
                "content": """# 技术分析入门

## 什么是技术分析？

技术分析是通过研究历史价格和交易量数据来预测未来价格走势的方法。

## 基本概念

### 趋势
- **上升趋势**: 价格创造更高的高点和高低点
- **下降趋势**: 价格创造更低的高点和低点
- **横盘**: 价格在一个范围内波动

### 支撑和阻力
- **支撑位**: 价格往往会反弹的下方价格
- **阻力位**: 价格往往会下跌的上方价格

## 常用指标

### 移动平均线 (MA)
显示一段时间内的平均价格，帮助识别趋势。

### 相对强弱指数 (RSI)
衡量价格变化的速度和幅度，范围 0-100。

### 布林带 (Bollinger Bands)
由三条线组成：中线（移动平均线）和上下各一条标准差线。

## 交易信号

### 买入信号
- 价格突破阻力位
- RSI 从超卖区域反弹
- 价格在移动平均线上方

### 卖出信号
- 价格跌破支撑位
- RSI 进入超买区域
- 价格在移动平均线下方
""",
                "category": "交易技巧",
                "tags": "技术分析,交易工具,指标",
                "is_featured": False,
                "is_published": True,
            },
        ]
        
        wiki_section = sections["wiki"]
        for article_data in wiki_articles:
            article = db.query(Article).filter(Article.slug == article_data["slug"]).first()
            if not article:
                category_name = article_data.pop("category", None)
                tags = article_data.pop("tags", None)
                
                # 找到对应的分类
                category_key = f"wiki_{category_name}"
                category = categories.get(category_key)
                category_id = category.id if category else None
                
                article = Article(
                    **article_data,
                    section_id=wiki_section.id,
                    category=category_name,
                    category_id=category_id,
                    tags=tags,
                    author_id=admin_id,
                    published_at=datetime.utcnow() if article_data.get("is_published") else None,
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                print(f"  ✅ 创建知识库: {article.title}")
            else:
                print(f"  ℹ️  知识库已存在: {article_data['title']}")
        
        # ========== 6. 创建指南文章 (Guide Articles) ==========
        print("\n📖 初始化指南文章...")
        guide_articles = [
            {
                "title": "5分钟快速开始杠杆交易",
                "slug": "quick-start-leverage",
                "summary": "通过5个简单步骤快速开始杠杆交易。",
                "content": """# 5分钟快速开始杠杆交易

## 步骤 1: 理解基础风险知识 (1 分钟)

在开始之前，理解杠杆交易的基本概念至关重要。

### 关键概念
- **杠杆比例**: 表示你可以借多少相对于你的投资
- **保证金**: 你必须存入的初始资金
- **保证金追加**: 当账户价值下跌时，经纪商会要求你存入更多资金
- **借款利息**: 经纪商收取的使用杠杆资金的费用

⚠️ **重要提醒**: 杠杆交易可能导致你失去所有投入资本。

## 步骤 2: 选择合适的交易平台 (1.5 分钟)

考虑以下因素：
- 监管和许可
- 杠杆比例
- 费用结构
- 客户支持

## 步骤 3: 完成账户开设 (1 分钟)

1. 访问平台官方网站
2. 填写注册表格
3. 提交身份验证文件
4. 账户获得批准

## 步骤 4: 存入初始资金 (0.5 分钟)

选择合适的入金方式，存入初始资金（通常最低 $200-$1000）。

## 步骤 5: 执行第一笔交易 (1 分钟)

1. 选择交易对象
2. 确定杠杆比例
3. 设置止损单
4. 下单交易

祝你交易顺利！
""",
                "category": "快速开始",
                "tags": "快速开始,入门指南,新手",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "杠杆平台详细对比指南",
                "slug": "platform-comparison-guide",
                "summary": "详细对比各大杠杆交易平台的特点、优缺点。",
                "content": """# 杠杆平台详细对比指南

## 平台对比维度

### 1. 监管合规性
- **完全监管**: 具有国际金融机构的监管许可
- **部分监管**: 受某些监管机构监督
- **自律监管**: 仅受行业自律组织监管

### 2. 杠杆比例
- 低杠杆 (1:5 以下): 较安全，适合保守投资者
- 中等杠杆 (1:10 - 1:50): 平衡风险和收益
- 高杠杆 (1:100+): 高风险，适合专业交易者

### 3. 费用结构
- **交易手续费**: 每笔交易的成本
- **借款利息**: 使用杠杆资金的年利率
- **隔夜费**: 持仓过夜需要支付的费用

### 4. 交易工具
- 图表和技术分析工具
- 自动交易功能
- 移动应用程序
- API 访问

### 5. 客户支持
- 24/5 或 24/7 支持
- 多语言支持
- 教育资源
- 社区论坛

## 推荐指南

- **新手**: 选择完全监管、低杠杆、教育资源丰富的平台
- **进阶**: 选择中等杠杆、工具齐全的平台
- **专业**: 可选择更高杠杆、提供 API 的平台
""",
                "category": "快速开始",
                "tags": "平台对比,选择平台,评测",
                "is_featured": False,
                "is_published": True,
            },
        ]
        
        guide_section = sections["guide"]
        for article_data in guide_articles:
            article = db.query(Article).filter(Article.slug == article_data["slug"]).first()
            if not article:
                category_name = article_data.pop("category", None)
                tags = article_data.pop("tags", None)
                
                category_key = f"guide_{category_name}"
                category = categories.get(category_key)
                category_id = category.id if category else None
                
                article = Article(
                    **article_data,
                    section_id=guide_section.id,
                    category=category_name,
                    category_id=category_id,
                    tags=tags,
                    author_id=admin_id,
                    published_at=datetime.utcnow() if article_data.get("is_published") else None,
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                print(f"  ✅ 创建指南: {article.title}")
            else:
                print(f"  ℹ️  指南已存在: {article_data['title']}")
        
        # ========== 7. 创建 FAQ 文章 ==========
        print("\n❓ 初始化常见问题...")
        faq_articles = [
            {
                "title": "什么是股票杠杆交易？",
                "slug": "faq-what-is-leverage",
                "summary": "杠杆交易的基本定义和工作原理。",
                "content": "股票杠杆交易是指投资者向券商借入资金进行股票交易，以较小的本金控制较大的交易金额，以期放大收益。同时风险也会相应放大。",
                "category": "平台相关",
                "tags": "FAQ,基础知识",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "杠杆交易的风险有哪些？",
                "slug": "faq-leverage-risks",
                "summary": "杠杆交易的主要风险类型和防控方法。",
                "content": "主要风险包括：保证金追加风险、爆仓风险、利息风险、政策风险等。建议充分了解风险后再参与。",
                "category": "风险相关",
                "tags": "FAQ,风险管理",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "如何选择合适的杠杆倍数？",
                "slug": "faq-choose-leverage",
                "summary": "根据自身情况选择杠杆倍数的建议。",
                "content": "选择杠杆倍数需要根据自身的风险承受能力、交易经验和资金状况综合考虑。一般建议初学者选择较低的杠杆倍数（1:5 以下）。",
                "category": "交易相关",
                "tags": "FAQ,杠杆选择",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "什么是保证金追加（Margin Call）？",
                "slug": "faq-margin-call",
                "summary": "保证金追加的定义和处理方法。",
                "content": "当账户权益下降到一定比例时，券商会要求投资者补充保证金，这就是保证金追加。如果投资者未能及时补充，券商可能会强制平仓。",
                "category": "风险相关",
                "tags": "FAQ,保证金",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "如何避免爆仓？",
                "slug": "faq-avoid-liquidation",
                "summary": "避免爆仓的关键技巧和策略。",
                "content": "避免爆仓的关键是合理控制杠杆、设置止损、定期检查账户、不过度交易。建议同时学习风险管理知识。",
                "category": "风险相关",
                "tags": "FAQ,止损,风险管理",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "各平台的费用如何比较？",
                "slug": "faq-compare-fees",
                "summary": "不同平台费用结构的对比方法。",
                "content": "需要比较手续费、利息费、撤资费等多方面的费用。本站提供详细的平台对比工具帮你进行对比。",
                "category": "平台相关",
                "tags": "FAQ,费用,对比",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "新手应该如何开始？",
                "slug": "faq-beginner-start",
                "summary": "新手入门的建议和步骤。",
                "content": "建议先学习基础知识，选择一个信誉良好的平台，使用小资金进行练习，逐步积累经验。参考本站的新手指南。",
                "category": "交易相关",
                "tags": "FAQ,新手,入门",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "如何设置止损和止盈？",
                "slug": "faq-stoploss-takeprofit",
                "summary": "止损和止盈的设置方法和策略。",
                "content": "止损和止盈应该根据你的交易策略和风险承受能力来设置。一般来说，应该在进入交易之前就设定好这些价位。",
                "category": "交易相关",
                "tags": "FAQ,止损,止盈",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "平台是否安全可靠？",
                "slug": "faq-platform-safety",
                "summary": "选择安全平台的重要指标。",
                "content": "应该选择持有正规牌照、受监管的平台。本站只提供信息参考，不构成投资建议。请先充分调查再决定。",
                "category": "平台相关",
                "tags": "FAQ,安全,选择",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "杠杆交易需要缴税吗？",
                "slug": "faq-tax",
                "summary": "杠杆交易的税收问题。",
                "content": "税收问题因地区而异，需要咨询当地的税务部门或专业税务顾问。本网站不提供税务建议。",
                "category": "其他",
                "tags": "FAQ,税收",
                "is_featured": False,
                "is_published": True,
            },
        ]
        
        faq_section = sections["faq"]
        for article_data in faq_articles:
            article = db.query(Article).filter(Article.slug == article_data["slug"]).first()
            if not article:
                category_name = article_data.pop("category", None)
                tags = article_data.pop("tags", None)
                
                category_key = f"faq_{category_name}"
                category = categories.get(category_key)
                category_id = category.id if category else None
                
                article = Article(
                    **article_data,
                    section_id=faq_section.id,
                    category=category_name,
                    category_id=category_id,
                    tags=tags,
                    author_id=admin_id,
                    published_at=datetime.utcnow() if article_data.get("is_published") else None,
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                print(f"  ✅ 创建 FAQ: {article.title}")
            else:
                print(f"  ℹ️  FAQ 已存在: {article_data['title']}")
        
        # ========== 8. 创建平台评测文章 ==========
        print("\n⭐ 初始化平台评测文章...")
        review_section = sections["review"]
        
        for platform_name, platform in platforms.items():
            review_slug = f"review-{platform_name.lower().replace(' ', '-')}"
            article = db.query(Article).filter(Article.slug == review_slug).first()
            
            if not article:
                review_content = f"""# {platform_name} 详细评测

## 平台概述

{platform.description}

## 核心指标

| 指标 | 值 |
|------|-----|
| 评分 | ⭐ {platform.rating}/5 |
| 排名 | #{platform.rank} |
| 最大杠杆 | 1:{platform.max_leverage} |
| 最小杠杆 | 1:{platform.min_leverage} |
| 交易手续费 | {platform.commission_rate * 100}% |
| 监管状态 | {"✅ 已监管" if platform.is_regulated else "⚠️ 未完全监管"} |
| 官方网站 | {platform.website_url} |

## 优势

- 平台具有竞争力的杠杆比例
- 费用结构清晰透明
- 优质的客户支持服务
- 完善的风险管理工具

## 劣势

- 不同市场可能有监管差异
- 某些交易对可能有时间限制
- 需要满足最低存款要求

## 适合人群

- 交易经验: {"新手到进阶" if platform.rating >= 4.5 else "进阶交易者"}
- 风险承受力: {"保守到中等" if platform.commission_rate < 0.0015 else "中等到激进"}
- 资金规模: {"小到中等" if platform.min_leverage >= 1.0 else "任何规模"}

## 总体评价

{platform_name} 是一个{"值得推荐" if platform.rating >= 4.5 else "有一定价值"}的杠杆交易平台。

## 开户步骤

1. 访问 {platform.website_url}
2. 点击"注册"或"开户"
3. 填写个人信息
4. 验证身份
5. 存入初始资金
6. 开始交易
"""
                
                category_name = "平台评测"
                category_key = f"review_{category_name}"
                category = categories.get(category_key)
                category_id = category.id if category else None
                
                article = Article(
                    title=f"{platform_name} 详细评测",
                    slug=review_slug,
                    summary=f"{platform_name} 平台的详细评测和使用体验报告。",
                    content=review_content,
                    section_id=review_section.id,
                    category=category_name,
                    category_id=category_id,
                    tags="平台评测,详细评测",
                    author_id=admin_id,
                    platform_id=platform.id,
                    is_active=True,
                    is_published=True,
                    is_featured=platform.is_featured,
                    published_at=datetime.utcnow(),
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                print(f"  ✅ 创建评测: {platform_name} 详细评测")
            else:
                print(f"  ℹ️  评测已存在: {platform_name}")
        
        # ========== 9. 统计信息 ==========
        print("\n" + "=" * 50)
        print("📊 数据整合完成统计")
        print("=" * 50)
        
        total_platforms = db.query(Platform).count()
        total_articles = db.query(Article).count()
        total_categories = db.query(Category).count()
        
        print(f"✅ 平台总数: {total_platforms}")
        print(f"✅ 文章总数: {total_articles}")
        print(f"✅ 分类总数: {total_categories}")
        print(f"✅ 栏目总数: {len(sections)}")
        print("\n✨ 数据整合初始化成功!")
        print(f"📝 管理员账户: admin / admin123")
        print(f"🌐 后端 API: http://127.0.0.1:8001")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化数据整合...\n")
    init_integration_data()
