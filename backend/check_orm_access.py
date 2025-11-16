#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接使用 SQLAlchemy ORM 检查分类数据
"""
import sys
import os

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 直接查询 SQLite 数据库
import sqlite3

db_file = 'trustagency.db'
con = sqlite3.connect(db_file)
cur = con.cursor()

print("=" * 70)
print("数据库分类数据检查")
print("=" * 70)

# 统计
cur.execute("SELECT COUNT(*) FROM categories")
total = cur.fetchone()[0]
print(f"\n总分类数: {total}")

# 按栏目统计
print("\n按栏目统计:")
cur.execute("""
SELECT s.id, s.name, s.slug, COUNT(c.id) as cat_count
FROM sections s
LEFT JOIN categories c ON s.id = c.section_id
GROUP BY s.id
ORDER BY s.id
""")

section_data = {}
for row in cur.fetchall():
    section_id, section_name, section_slug, cat_count = row
    section_data[section_id] = {
        'name': section_name,
        'slug': section_slug,
        'count': cat_count
    }
    print(f"  {section_name:10} ({section_slug:8}): {cat_count:2} 个分类")

# 详细列表
print("\n详细分类列表:")
cur.execute("""
SELECT s.name, c.id, c.name, c.section_id, c.is_active, c.sort_order
FROM categories c
JOIN sections s ON c.section_id = s.id
ORDER BY c.section_id, c.sort_order
""")

for row in cur.fetchall():
    section_name, cat_id, cat_name, section_id, is_active, sort_order = row
    status = "✓" if is_active else "✗"
    print(f"  [{section_name:6}] {cat_name:15} (ID={cat_id:2}, sort={sort_order})")

con.close()

# 现在尝试通过 ORM 访问
print("\n" + "=" * 70)
print("通过 SQLAlchemy ORM 访问数据")
print("=" * 70)

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    DATABASE_URL = f"sqlite:///{db_file}"
    print(f"\nConnecting to: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # 导入模型
    from app.models import Category, Section
    
    # 统计分类
    cat_count = db.query(Category).count()
    print(f"\nORM 查询分类总数: {cat_count}")
    
    # 按栏目统计
    print("\nORM 按栏目统计:")
    sections = db.query(Section).all()
    for section in sections:
        count = db.query(Category).filter(Category.section_id == section.id).count()
        print(f"  {section.name}: {count} 个分类")
    
    # 显示前 10 个分类
    print("\nORM 分类样本 (前 10 个):")
    categories = db.query(Category).limit(10).all()
    for cat in categories:
        print(f"  {cat.name} (section_id={cat.section_id})")
    
    db.close()
    print("\n✅ ORM 访问成功!")
    
except Exception as e:
    print(f"\n❌ ORM 访问失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
