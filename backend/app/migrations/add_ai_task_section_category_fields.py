"""
添加 AI 任务的栏目、分类、平台字段

这个迁移脚本为 ai_generation_tasks 表添加以下字段：
- section_id: 栏目ID（外键指向sections表）
- category_id: 分类ID（外键指向categories表）
- platform_id: 平台ID（外键指向platforms表，可选）

执行方式：
    python -m app.migrations.add_ai_task_section_category_fields
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
import os

def upgrade():
    """升级数据库：添加新字段"""
    # 获取数据库路径
    db_path = os.path.join(project_root, "backend", "trustagency.db")
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        print("开始数据库迁移...")
        
        # 检查字段是否已存在
        result = conn.execute(text("PRAGMA table_info(ai_generation_tasks)"))
        columns = [row[1] for row in result]
        
        # 添加 section_id 字段
        if 'section_id' not in columns:
            print("添加 section_id 字段...")
            conn.execute(text("""
                ALTER TABLE ai_generation_tasks 
                ADD COLUMN section_id INTEGER 
                REFERENCES sections(id)
            """))
            conn.commit()
            print("✅ section_id 字段已添加")
        else:
            print("⏭️  section_id 字段已存在，跳过")
        
        # 添加 category_id 字段
        if 'category_id' not in columns:
            print("添加 category_id 字段...")
            conn.execute(text("""
                ALTER TABLE ai_generation_tasks 
                ADD COLUMN category_id INTEGER 
                REFERENCES categories(id)
            """))
            conn.commit()
            print("✅ category_id 字段已添加")
        else:
            print("⏭️  category_id 字段已存在，跳过")
        
        # 添加 platform_id 字段
        if 'platform_id' not in columns:
            print("添加 platform_id 字段...")
            conn.execute(text("""
                ALTER TABLE ai_generation_tasks 
                ADD COLUMN platform_id INTEGER 
                REFERENCES platforms(id)
            """))
            conn.commit()
            print("✅ platform_id 字段已添加")
        else:
            print("⏭️  platform_id 字段已存在，跳过")
        
        print("\n✅ 数据库迁移完成！")
        print("\n新增字段：")
        print("  - section_id (INTEGER, FK -> sections.id)")
        print("  - category_id (INTEGER, FK -> categories.id)")
        print("  - platform_id (INTEGER, FK -> platforms.id, 可选)")


def downgrade():
    """降级数据库：删除新字段（SQLite不支持DROP COLUMN）"""
    print("⚠️  警告：SQLite 不支持 DROP COLUMN 操作")
    print("如需回退，请手动删除数据库文件并重新初始化")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI任务表字段迁移脚本')
    parser.add_argument('--downgrade', action='store_true', help='回退迁移（警告：SQLite不支持）')
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()
