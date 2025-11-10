#!/usr/bin/env python3
"""
快速插入示例数据脚本 - 使用SQL直接操作
"""
import sqlite3
from datetime import datetime

def init_data():
    """初始化示例数据"""
    db_path = './trustagency.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platforms'")
        if not cursor.fetchone():
            print("❌ 错误：platforms 表不存在，请先初始化数据库")
            print("运行: alembic upgrade head")
            return
        
        # 清空数据
        cursor.execute("DELETE FROM articles")
        cursor.execute("DELETE FROM platforms")
        print("✓ 已清空现有数据")
        
        # 插入示例平台
        platforms_data = [
            (
                "Alpha Leverage",
                "alpha-leverage",
                "高杠杆、低费率的专业交易平台，提供完善的风险管理工具和24/7客户支持。",
                "https://alpha-leverage.example.com",
                100,
                100,
                0.1,
                4.8,
                1,
                1,
                1,
                2018,
                "新加坡",
                "A+",
                "监管中"
            ),
            (
                "Beta Margin",
                "beta-margin",
                "风险管理工具完善的保证金交易平台，特别适合风险厌恶型投资者。",
                "https://beta-margin.example.com",
                50,
                500,
                0.15,
                4.5,
                1,
                1,
                1,
                2019,
                "香港",
                "A",
                "完全监管"
            ),
            (
                "Gamma Trader",
                "gamma-trader",
                "新手友好、教育资源丰富的平台，配有详细的交易指南和视频教程。",
                "https://gamma-trader.example.com",
                75,
                200,
                0.13,
                4.3,
                0,
                0,
                0,
                2020,
                "英国",
                "B+",
                "部分监管"
            )
        ]
        
        for platform in platforms_data:
            cursor.execute("""
                INSERT INTO platforms (
                    name, slug, description, website, max_leverage, min_deposit,
                    fee_rate, rating, is_active, is_featured, is_recommended,
                    founded_year, country, safety_rating, regulation_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, platform)
        
        conn.commit()
        print(f"✓ 已插入 {len(platforms_data)} 个示例平台")
        
        # 插入示例文章（需要author_id）
        author_id = 1  # 假设管理员ID为1
        
        articles_data = [
            (
                "什么是股票杠杆交易？",
                "what-is-leverage",
                "初学者指南：了解股票杠杆交易的基础知识、原理和风险。",
                "股票杠杆交易是指投资者向券商借入资金进行股票交易...",
                "教育",
                1,
                1,
                author_id
            ),
            (
                "杠杆交易风险管理指南",
                "leverage-risk-management",
                "学习如何有效管理杠杆交易风险，保护你的投资。",
                "杠杆交易的主要风险包括保证金追加风险、爆仓风险等...",
                "风险管理",
                0,
                1,
                author_id
            )
        ]
        
        for article in articles_data:
            cursor.execute("""
                INSERT INTO articles (
                    title, slug, summary, content, category, is_featured, is_active, author_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, article)
        
        conn.commit()
        print(f"✓ 已插入 {len(articles_data)} 篇示例文章")
        
        # 查询验证
        platforms_count = cursor.execute("SELECT COUNT(*) FROM platforms").fetchone()[0]
        articles_count = cursor.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        
        print("\n✅ 数据初始化完成！")
        print(f"\n数据摘要:")
        print(f"  - 平台: {platforms_count}")
        print(f"  - 文章: {articles_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        raise

if __name__ == "__main__":
    init_data()
