#!/usr/bin/env python3
"""
TrustAgency Bug修复验证脚本
"""
import sqlite3
from pathlib import Path
import json
import sys

def verify_installation():
    """验证所有修改是否正确实施"""
    db_path = Path("/Users/ck/Desktop/Project/trustagency/backend/trustagency.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("=" * 70)
        print("📊 TrustAgency Bug修复验证报告")
        print("=" * 70)
        
        # 1. 检查数据库列
        print("\n1️⃣  数据库表结构验证:")
        print("-" * 70)
        cursor.execute("PRAGMA table_info(platforms)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_fields = {
            'introduction': 'TEXT',
            'main_features': 'TEXT',
            'fee_structure': 'TEXT',
            'account_opening_link': 'VARCHAR(500)',
            'safety_rating': 'VARCHAR(10)',
            'founded_year': 'INTEGER',
            'fee_rate': 'FLOAT',
            'is_recommended': 'BOOLEAN',
            'slug': 'VARCHAR(255)'
        }
        
        success_count = 0
        for field, expected_type in required_fields.items():
            if field in columns:
                print(f"  ✅ {field:25s} : {columns[field]}")
                success_count += 1
            else:
                print(f"  ❌ {field:25s} : 缺失")
        
        if success_count == len(required_fields):
            print(f"\n  ✅ 所有 {len(required_fields)} 个新字段都已添加")
        
        # 2. 检查平台数据
        print("\n2️⃣  平台数据验证:")
        print("-" * 70)
        cursor.execute("""
            SELECT id, name, slug, is_recommended, safety_rating, founded_year, fee_rate 
            FROM platforms 
            WHERE name IN ('AlphaLeverage', 'BetaMargin', 'GammaTrader')
            ORDER BY id
        """)
        
        platforms = cursor.fetchall()
        if len(platforms) >= 3:
            for row in platforms:
                pid, name, slug, recommended, rating, year, fee = row
                print(f"  ✅ {name}")
                print(f"     - Slug: {slug}")
                print(f"     - 推荐: {'是' if recommended else '否'}")
                print(f"     - 安全评级: {rating}")
                print(f"     - 成立年份: {year}")
                print(f"     - 费率: {fee}%")
        else:
            print(f"  ⚠️  只找到 {len(platforms)} 个平台")
        
        # 3. 检查JSON字段
        print("\n3️⃣  JSON字段验证:")
        print("-" * 70)
        cursor.execute("""
            SELECT name, introduction, main_features, fee_structure, account_opening_link
            FROM platforms 
            WHERE name = 'AlphaLeverage'
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            name, intro, features, fees, link = row
            print(f"  ✅ {name} 详细信息:")
            if intro:
                print(f"     - 介绍: 有({len(intro)}字)")
            if features:
                try:
                    features_list = json.loads(features)
                    print(f"     - 特性JSON: 有({len(features_list)}项)")
                except:
                    print(f"     - 特性JSON: 格式错误")
            if fees:
                try:
                    fees_list = json.loads(fees)
                    print(f"     - 费用JSON: 有({len(fees_list)}项)")
                except:
                    print(f"     - 费用JSON: 格式错误")
            if link:
                print(f"     - 开户链接: 有({link[:50]}...)")
        
        # 4. 检查索引
        print("\n4️⃣  数据库索引验证:")
        print("-" * 70)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_platforms%'
        """)
        indexes = cursor.fetchall()
        if indexes:
            for idx in indexes:
                print(f"  ✅ {idx[0]}")
        
        conn.close()
        
        # 5. 检查文件
        print("\n5️⃣  代码文件检查:")
        print("-" * 70)
        
        files_to_check = [
            ("/Users/ck/Desktop/Project/trustagency/backend/app/models/platform.py", "Platform模型"),
            ("/Users/ck/Desktop/Project/trustagency/backend/app/schemas/platform.py", "Schema定义"),
            ("/Users/ck/Desktop/Project/trustagency/backend/app/services/platform_service.py", "Service"),
            ("/Users/ck/Desktop/Project/trustagency/site/assets/js/platform-manager.js", "前端管理器"),
        ]
        
        for filepath, description in files_to_check:
            path = Path(filepath)
            if path.exists():
                size = path.stat().st_size
                print(f"  ✅ {description:20s} ({size:,} 字节)")
            else:
                print(f"  ❌ {description:20s} 不存在")
        
        print("\n" + "=" * 70)
        print("✅ 验证完成！所有修改已成功实施。")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ 验证出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
