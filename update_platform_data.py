#!/usr/bin/env python
"""
更新平台数据脚本 - 添加新字段的初始值
执行: python update_platform_data.py
"""
import sqlite3
import json
from pathlib import Path

project_root = Path(__file__).parent
backend_dir = project_root / "backend"
db_path = backend_dir / "trustagency.db"

# 平台数据定义
PLATFORMS_DATA = [
    {
        "name": "AlphaLeverage",
        "slug": "alphaleverage",
        "rating": 4.8,
        "rank": 1,
        "is_recommended": True,
        "safety_rating": "A",
        "founded_year": 2015,
        "fee_rate": 0.5,
        "introduction": "AlphaLeverage是一个专业的外汇交易平台，提供最高500倍的杠杆比例和极具竞争力的交易手续费。平台拥有完善的风险管理系统和24/7的客户支持。",
        "main_features": json.dumps([
            {"title": "高杠杆", "desc": "最高500:1杠杆比例"},
            {"title": "低手续费", "desc": "平均0.5个点的手续费"},
            {"title": "快速执行", "desc": "毫秒级的订单执行速度"},
            {"title": "多货币对", "desc": "支持150+交易对"}
        ]),
        "fee_structure": json.dumps([
            {"type": "手续费", "value": "0.005%", "desc": "按交易金额计算"},
            {"type": "隔夜利息", "value": "浮动", "desc": "根据货币对变化"},
            {"type": "点差", "value": "0-3点", "desc": "主要货币对"}
        ]),
        "account_opening_link": "https://alphaleverage.com/open-account",
    },
    {
        "name": "BetaMargin",
        "slug": "betamargin",
        "rating": 4.5,
        "rank": 2,
        "is_recommended": True,
        "safety_rating": "A",
        "founded_year": 2012,
        "fee_rate": 0.3,
        "introduction": "BetaMargin是一个全球领先的保证金交易平台，专注于提供专业级的交易工具和市场分析。拥有超过100万活跃交易者。",
        "main_features": json.dumps([
            {"title": "专业工具", "desc": "高级交易终端和分析工具"},
            {"title": "高流动性", "desc": "与全球主要银行合作"},
            {"title": "教育资源", "desc": "丰富的交易教程和网络研讨会"},
            {"title": "移动交易", "desc": "支持iOS和Android应用"}
        ]),
        "fee_structure": json.dumps([
            {"type": "手续费", "value": "0.003%", "desc": "行业最低水平"},
            {"type": "隔夜利息", "value": "浮动", "desc": "根据市场利率变化"},
            {"type": "点差", "value": "1-2点", "desc": "主要货币对"}
        ]),
        "account_opening_link": "https://betamargin.com/signup",
    },
    {
        "name": "GammaTrader",
        "slug": "gammatrader",
        "rating": 4.6,
        "rank": 3,
        "is_recommended": False,
        "safety_rating": "B",
        "founded_year": 2018,
        "fee_rate": 0.4,
        "introduction": "GammaTrader是一个创新型的交易平台，致力于为零售交易者提供机构级别的交易体验。平台采用最新的区块链技术。",
        "main_features": json.dumps([
            {"title": "AI助手", "desc": "AI驱动的交易建议系统"},
            {"title": "社交交易", "desc": "跟单和复制交易功能"},
            {"title": "低延迟", "desc": "纽约和伦敦的数据中心"},
            {"title": "多资产", "desc": "外汇、股票、加密货币、大宗商品"}
        ]),
        "fee_structure": json.dumps([
            {"type": "手续费", "value": "0.004%", "desc": "竞争力的费率结构"},
            {"type": "隔夜利息", "value": "浮动", "desc": "根据央行利率"},
            {"type": "点差", "value": "2-4点", "desc": "主要货币对"}
        ]),
        "account_opening_link": "https://gammatrader.com/register",
    },
]

def update_platform_data():
    """更新平台数据"""
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("📝 开始更新平台数据...")
        print("-" * 60)
        
        for platform_data in PLATFORMS_DATA:
            name = platform_data["name"]
            
            # 检查平台是否存在
            cursor.execute("SELECT id FROM platforms WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            if result:
                platform_id = result[0]
                print(f"\n  → 更新平台: {name} (ID: {platform_id})")
                
                # 更新平台数据
                update_sql = """
                    UPDATE platforms 
                    SET 
                        slug = ?,
                        rating = ?,
                        rank = ?,
                        is_recommended = ?,
                        safety_rating = ?,
                        founded_year = ?,
                        fee_rate = ?,
                        introduction = ?,
                        main_features = ?,
                        fee_structure = ?,
                        account_opening_link = ?
                    WHERE id = ?
                """
                
                cursor.execute(update_sql, (
                    platform_data.get("slug"),
                    platform_data.get("rating"),
                    platform_data.get("rank"),
                    1 if platform_data.get("is_recommended") else 0,
                    platform_data.get("safety_rating"),
                    platform_data.get("founded_year"),
                    platform_data.get("fee_rate"),
                    platform_data.get("introduction"),
                    platform_data.get("main_features"),
                    platform_data.get("fee_structure"),
                    platform_data.get("account_opening_link"),
                    platform_id
                ))
                
                print(f"    ✅ 数据更新成功")
            else:
                print(f"\n  ⚠️  平台不存在: {name} (跳过)")
        
        # 提交更改
        conn.commit()
        
        # 验证数据
        print(f"\n" + "=" * 60)
        print("📋 数据验证:")
        print("-" * 60)
        
        cursor.execute("""
            SELECT id, name, rating, is_recommended, safety_rating, founded_year, fee_rate
            FROM platforms 
            WHERE name IN (?, ?, ?)
            ORDER BY rank
        """, tuple(p["name"] for p in PLATFORMS_DATA))
        
        for row in cursor.fetchall():
            platform_id, name, rating, is_recommended, safety_rating, founded_year, fee_rate = row
            print(f"  ID:{platform_id:2d} {name:20s} ⭐{rating:3.1f} "
                  f"{'✓推' if is_recommended else '✗否'}  {safety_rating}等  "
                  f"成立:{founded_year}  费率:{fee_rate}%")
        
        # 检查是否有其他平台
        cursor.execute("SELECT COUNT(*) FROM platforms WHERE name NOT IN (?, ?, ?)",
                      tuple(p["name"] for p in PLATFORMS_DATA))
        other_count = cursor.fetchone()[0]
        if other_count > 0:
            print(f"\n  ℹ️  还有 {other_count} 个其他平台未更新")
        
        conn.close()
        print(f"\n✅ 平台数据更新完成！")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = update_platform_data()
    sys.exit(0 if success else 1)
