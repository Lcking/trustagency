#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加平台详情页面字段
执行: python migrate_db_details.py
"""
import sqlite3
from pathlib import Path

db_path = Path("/Users/ck/Desktop/Project/trustagency/backend/trustagency.db")

def run_migration():
    """执行数据库迁移"""
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔧 开始执行迁移: 添加平台详情页面字段...")
        print("-" * 70)
        
        # 获取现有列
        cursor.execute("PRAGMA table_info(platforms)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"✓ 现有列数: {len(existing_columns)}")
        
        # 定义要添加的新列
        new_columns = [
            ("why_choose", "TEXT"),
            ("trading_conditions", "TEXT"),
            ("fee_advantages", "TEXT"),
            ("account_types", "TEXT"),
            ("trading_tools", "TEXT"),
            ("opening_steps", "TEXT"),
            ("security_measures", "TEXT"),
            ("customer_support", "TEXT"),
            ("learning_resources", "TEXT"),
            ("platform_type", "VARCHAR(50)"),
            ("platform_badges", "TEXT"),
        ]
        
        # 添加缺失的列
        added_count = 0
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                print(f"\n  → 添加列: {col_name} ({col_type})")
                cursor.execute(f"ALTER TABLE platforms ADD COLUMN {col_name} {col_type}")
                added_count += 1
                print(f"    ✅ 成功")
            else:
                print(f"  ⊘ 列已存在: {col_name}")
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        print(f"\n" + "=" * 70)
        print("📋 迁移结果验证:")
        print("-" * 70)
        cursor.execute("PRAGMA table_info(platforms)")
        new_columns_list = cursor.fetchall()
        print(f"✅ 新的列数: {len(new_columns_list)} (新增: {added_count})")
        
        conn.close()
        print(f"\n✅ 迁移完成！")
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
    success = run_migration()
    sys.exit(0 if success else 1)
