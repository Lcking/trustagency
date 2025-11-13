#!/usr/bin/env python
"""
数据库迁移脚本 - 添加Platform新字段
执行: python migrate_db.py
"""
import sqlite3
import sys
from pathlib import Path

# 获取项目路径
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
db_path = backend_dir / "trustagency.db"

def run_migration():
    """执行数据库迁移"""
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔧 开始执行迁移: 添加Platform新字段...")
        print("-" * 60)
        
        # 获取现有列
        cursor.execute("PRAGMA table_info(platforms)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"✓ 现有列数: {len(existing_columns)}")
        print(f"  列名: {sorted(existing_columns)}")
        
        # 定义要添加的列
        columns_to_add = [
            ("introduction", "TEXT"),
            ("main_features", "TEXT"),
            ("fee_structure", "TEXT"),
            ("account_opening_link", "VARCHAR(500)"),
            ("safety_rating", "VARCHAR(10)"),
            ("founded_year", "INTEGER"),
            ("fee_rate", "FLOAT"),
            ("is_recommended", "BOOLEAN"),
            ("slug", "VARCHAR(255)"),
        ]
        
        # 添加缺失的列
        added_count = 0
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"\n  → 添加列: {col_name} ({col_type})")
                
                # 为不同列提供不同的默认值
                if col_name == "safety_rating":
                    cursor.execute(f"ALTER TABLE platforms ADD COLUMN {col_name} {col_type} DEFAULT 'B'")
                elif col_name == "is_recommended":
                    cursor.execute(f"ALTER TABLE platforms ADD COLUMN {col_name} {col_type} DEFAULT 0")
                else:
                    cursor.execute(f"ALTER TABLE platforms ADD COLUMN {col_name} {col_type}")
                
                added_count += 1
                print(f"    ✅ 成功")
            else:
                print(f"  ⊘ 列已存在: {col_name}")
        
        # 为slug列生成值（基于name转换为小写并用-替换空格）
        print(f"\n  → 为slug列生成值...")
        cursor.execute("""
            UPDATE platforms 
            SET slug = LOWER(REPLACE(name, ' ', '-'))
            WHERE slug IS NULL OR slug = ''
        """)
        print(f"    ✅ 成功")
        
        # 创建索引
        print(f"\n  → 创建索引...")
        indexes = [
            ("idx_platforms_slug", "slug"),
            ("idx_platforms_is_recommended", "is_recommended"),
            ("idx_platforms_safety_rating", "safety_rating"),
        ]
        
        for idx_name, col_name in indexes:
            try:
                # 检查索引是否已存在
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx_name}'")
                if not cursor.fetchone():
                    cursor.execute(f"CREATE INDEX {idx_name} ON platforms({col_name})")
                    print(f"    ✅ 索引创建: {idx_name}")
                else:
                    print(f"    ⊘ 索引已存在: {idx_name}")
            except sqlite3.OperationalError as e:
                print(f"    ⚠️  索引创建失败: {idx_name} - {e}")
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        print(f"\n" + "=" * 60)
        print("📋 迁移结果验证:")
        print("-" * 60)
        cursor.execute("PRAGMA table_info(platforms)")
        new_columns = cursor.fetchall()
        print(f"✅ 新的列数: {len(new_columns)} (原有: {len(existing_columns)}, 新增: {added_count})")
        print(f"\n列详情:")
        for row in new_columns:
            col_id, col_name, col_type, not_null, default, pk = row
            print(f"  [{col_id:2d}] {col_name:25s} {col_type:15s} {'NOT NULL' if not_null else ''} {f'DEFAULT {default}' if default else ''}")
        
        # 检查数据
        print(f"\n" + "=" * 60)
        print("📊 数据验证:")
        print("-" * 60)
        cursor.execute("SELECT COUNT(*) FROM platforms")
        platform_count = cursor.fetchone()[0]
        print(f"✅ 平台记录数: {platform_count}")
        
        # 显示平台列表
        if platform_count > 0:
            cursor.execute("SELECT id, name, slug, is_recommended, safety_rating FROM platforms")
            for row in cursor.fetchall():
                print(f"  ID:{row[0]:2d} {row[1]:20s} slug={row[2]:20s} recommended={'Yes' if row[3] else 'No':3s} rating={row[4]}")
        
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
    success = run_migration()
    sys.exit(0 if success else 1)
