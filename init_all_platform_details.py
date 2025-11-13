#!/usr/bin/env python3
"""
完整的平台详情数据初始化脚本
步骤1: 执行数据库迁移
步骤2: 初始化平台详情数据
"""
import sqlite3
import json
import sys
from pathlib import Path

# 平台详情数据
from platform_details_template import PLATFORM_DETAILS_MAP

db_path = Path("/Users/ck/Desktop/Project/trustagency/backend/trustagency.db")

def step1_migrate_database():
    """第一步：执行数据库迁移"""
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("\n" + "=" * 70)
        print("第一步: 数据库迁移")
        print("=" * 70)
        print("🔧 开始添加新字段...")
        print("-" * 70)
        
        # 获取现有列
        cursor.execute("PRAGMA table_info(platforms)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
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
                print(f"  → 添加列: {col_name:25s} ({col_type})")
                try:
                    cursor.execute(f"ALTER TABLE platforms ADD COLUMN {col_name} {col_type}")
                    added_count += 1
                    print(f"    ✅ 成功")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"    ⊘ 列已存在")
                    else:
                        raise
            else:
                print(f"  ⊘ 列已存在: {col_name}")
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        print(f"\n✅ 迁移完成: 新增 {added_count} 个字段")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 第一步失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def step2_init_data():
    """第二步：初始化平台详情数据"""
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("\n" + "=" * 70)
        print("第二步: 初始化平台详情数据")
        print("=" * 70)
        print("📝 开始填充平台详情数据...")
        print("-" * 70)
        
        for slug, (platform_id, details) in PLATFORM_DETAILS_MAP.items():
            print(f"\n  → 更新平台: {slug} (ID: {platform_id})")
            
            # 构建UPDATE SQL语句
            update_sql = """
                UPDATE platforms 
                SET 
                    why_choose = ?,
                    trading_conditions = ?,
                    fee_advantages = ?,
                    account_types = ?,
                    trading_tools = ?,
                    opening_steps = ?,
                    security_measures = ?,
                    customer_support = ?,
                    learning_resources = ?,
                    platform_type = ?,
                    platform_badges = ?
                WHERE id = ?
            """
            
            # 准备数据
            data = (
                details.get("why_choose"),
                details.get("trading_conditions"),
                details.get("fee_advantages"),
                details.get("account_types"),
                details.get("trading_tools"),
                details.get("opening_steps"),
                details.get("security_measures"),
                details.get("customer_support"),
                details.get("learning_resources"),
                details.get("platform_type"),
                details.get("platform_badges"),
                platform_id
            )
            
            cursor.execute(update_sql, data)
            
            # 统计字段数
            field_count = sum(1 for v in details.values() if v is not None)
            print(f"    ✅ 已填充 {field_count} 个字段")
        
        # 提交更改
        conn.commit()
        
        # 验证数据
        print(f"\n" + "-" * 70)
        print("📋 验证填充结果:")
        print("-" * 70)
        
        for slug, (platform_id, _) in PLATFORM_DETAILS_MAP.items():
            cursor.execute("""
                SELECT name, platform_type FROM platforms WHERE id = ?
            """, (platform_id,))
            
            row = cursor.fetchone()
            if row:
                name, ptype = row
                print(f"  ✅ {name:20s} - 类型: {ptype or '未设置'}")
        
        conn.close()
        print(f"\n✅ 第二步完成: 平台详情数据已初始化")
        return True
        
    except Exception as e:
        print(f"❌ 第二步失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 完整的平台详情数据初始化")
    print("=" * 70)
    
    # 执行第一步
    if not step1_migrate_database():
        print("\n❌ 初始化失败！")
        return False
    
    # 执行第二步
    if not step2_init_data():
        print("\n❌ 初始化失败！")
        return False
    
    # 成功
    print("\n" + "=" * 70)
    print("✅ 所有步骤完成！平台详情数据已完全初始化。")
    print("=" * 70)
    print("\n现在可以：")
    print("1. 重启后端服务")
    print("2. 测试API获取平台详情: GET /api/platforms/1")
    print("3. 前端可以使用新的详情字段来渲染平台页面")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
