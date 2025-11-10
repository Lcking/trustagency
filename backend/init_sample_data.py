#!/usr/bin/env python3
"""
初始化数据库示例数据脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import AdminUser, Platform, Article, AIGenerationTask
from datetime import datetime

def init_data():
    """初始化示例数据"""
    db = SessionLocal()
    
    try:
        # 清空现有数据
        db.query(AIGenerationTask).delete()
        db.query(Article).delete()
        db.query(Platform).delete()
        print("✓ 已清空现有数据")

        # 检查是否已有管理员
        admin = db.query(AdminUser).first()
        if not admin:
            # 使用API创建的或数据库中已有的管理员
            print("⚠️  未找到管理员用户，需要先通过API创建用户")
            admin_id = 1
        else:
            admin_id = admin.id
            print("✓ 使用现有管理员用户")

        # 创建示例平台
        platforms_data = [
            {
                "name": "Alpha Leverage",
                "slug": "alpha-leverage",
                "description": "高杠杆、低费率的专业交易平台，提供完善的风险管理工具和24/7客户支持。",
                "website": "https://alpha-leverage.example.com",
                "max_leverage": 100,
                "min_deposit": 100,
                "fee_rate": 0.1,
                "rating": 4.8,
                "is_active": True,
                "is_featured": True,
                "is_recommended": True,
                "founded_year": 2018,
                "country": "新加坡",
                "safety_rating": "A+",
                "regulation_status": "监管中",
                "features": ["高杠杆", "低费率", "24/7支持"],
                "pros": ["费率低", "杠杆高", "工具完善"],
                "cons": ["风险高"],
                "rank": 1
            },
            {
                "name": "Beta Margin",
                "slug": "beta-margin",
                "description": "风险管理工具完善的保证金交易平台，特别适合风险厌恶型投资者。",
                "website": "https://beta-margin.example.com",
                "max_leverage": 50,
                "min_deposit": 500,
                "fee_rate": 0.15,
                "rating": 4.5,
                "is_active": True,
                "is_featured": True,
                "is_recommended": True,
                "founded_year": 2019,
                "country": "香港",
                "safety_rating": "A",
                "regulation_status": "完全监管",
                "features": ["风险管理", "教育资源", "客户支持"],
                "pros": ["安全可靠", "工具强大"],
                "cons": ["费率较高", "杠杆受限"],
                "rank": 2
            },
            {
                "name": "Gamma Trader",
                "slug": "gamma-trader",
                "description": "新手友好、教育资源丰富的平台，配有详细的交易指南和视频教程。",
                "website": "https://gamma-trader.example.com",
                "max_leverage": 75,
                "min_deposit": 200,
                "fee_rate": 0.13,
                "rating": 4.3,
                "is_active": True,
                "is_featured": False,
                "is_recommended": False,
                "founded_year": 2020,
                "country": "英国",
                "safety_rating": "B+",
                "regulation_status": "部分监管",
                "features": ["教育资源", "新手友好", "中文支持"],
                "pros": ["易于入门", "教学完善"],
                "cons": ["监管风险"],
                "rank": 3
            }
        ]

        for platform_data in platforms_data:
            platform = Platform(**platform_data)
            db.add(platform)
        db.commit()
        print(f"✓ 已创建 {len(platforms_data)} 个示例平台")

        # 创建示例文章
        articles_data = [
            {
                "title": "什么是股票杠杆交易？",
                "slug": "what-is-leverage",
                "summary": "初学者指南：了解股票杠杆交易的基础知识、原理和风险。",
                "content": """
# 什么是股票杠杆交易？

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
                "category": "教育",
                "tags": ["杠杆交易", "初学者", "基础知识"],
                "is_featured": True,
                "is_active": True,
                "author_id": admin_id
            },
            {
                "title": "杠杆交易风险管理指南",
                "slug": "leverage-risk-management",
                "summary": "学习如何有效管理杠杆交易风险，保护你的投资。",
                "content": """
# 杠杆交易风险管理指南

## 主要风险

1. **保证金追加风险**: 市场波动可能触发追加保证金
2. **爆仓风险**: 账户亏损可能超过初始投资
3. **利息成本**: 长期持仓的利息费用
4. **市场风险**: 价格波动快速导致亏损
5. **政策风险**: 监管政策变化

## 风险管理策略

### 1. 设置止损单
- 在合适的价格设置自动止损
- 限制最大单笔亏损比例

### 2. 控制杠杆比例
- 选择较低的杠杆倍数
- 根据风险承受能力调整

### 3. 分散投资
- 不要将所有资金投入单一交易
- 分散风险

### 4. 定期检查
- 监控持仓状态
- 及时调整策略

## 建议

- 从小额开始学习
- 先用模拟账户练习
- 充分学习后再实际操作
- 从低杠杆开始
                """,
                "category": "风险管理",
                "tags": ["风险管理", "止损", "策略"],
                "is_featured": False,
                "is_active": True,
                "author_id": admin_id
            }
        ]

        for article_data in articles_data:
            article = Article(**article_data)
            db.add(article)
        db.commit()
        print(f"✓ 已创建 {len(articles_data)} 篇示例文章")

        print("\n✅ 数据初始化完成！")
        print("\n数据摘要:")
        print(f"  - 用户: {db.query(AdminUser).count()}")
        print(f"  - 平台: {db.query(Platform).count()}")
        print(f"  - 文章: {db.query(Article).count()}")

    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
