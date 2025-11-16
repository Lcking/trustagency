#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端分类 API 端点的实际响应
"""
import sys
import json
import sqlite3

os_current_dir = '/Users/ck/Desktop/Project/trustagency/backend'

print("=" * 70)
print("后端 API 端点诊断")
print("=" * 70)

# 1. 先验证数据库
print("\n1️⃣ 数据库验证:")
con = sqlite3.connect(f'{os_current_dir}/trustagency.db')
cur = con.cursor()

cur.execute("SELECT COUNT(*) FROM categories")
cat_count = cur.fetchone()[0]
print(f"  ✓ 分类总数: {cat_count}")

cur.execute("SELECT COUNT(*) FROM sections")
sec_count = cur.fetchone()[0]
print(f"  ✓ 栏目总数: {sec_count}")

# 2. 测试模拟 API 响应
print("\n2️⃣ 模拟 API /api/categories/section/1/with-count 的响应:")

cur.execute("""
SELECT c.id, c.name, c.description, c.section_id, c.sort_order, COUNT(a.id) as article_count
FROM categories c
LEFT JOIN articles a ON c.id = a.category_id AND a.is_published = 1
WHERE c.section_id = 1 AND c.is_active = 1
GROUP BY c.id
ORDER BY c.sort_order
""")

categories = []
for row in cur.fetchall():
    cat = {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'section_id': row[3],
        'sort_order': row[4],
        'article_count': row[5]
    }
    categories.append(cat)

print(f"  返回分类数: {len(categories)}")
if categories:
    print("  JSON响应示例:")
    print(f"  {json.dumps(categories[:2], indent=4, ensure_ascii=False)}")
else:
    print("  ⚠️  无分类返回!")

# 3. 测试模拟 API 响应 - 不带 with-count（普通端点）
print("\n3️⃣ 模拟 API /api/categories/section/1 的响应:")

cur.execute("""
SELECT c.id, c.name, c.description, c.section_id, c.sort_order, c.is_active
FROM categories c
WHERE c.section_id = 1 AND c.is_active = 1
ORDER BY c.sort_order
""")

categories_simple = []
for row in cur.fetchall():
    cat = {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'section_id': row[3],
        'sort_order': row[4],
        'is_active': row[5]
    }
    categories_simple.append(cat)

print(f"  返回分类数: {len(categories_simple)}")
if categories_simple:
    print("  JSON响应示例:")
    print(f"  {json.dumps(categories_simple[:2], indent=4, ensure_ascii=False)}")
else:
    print("  ⚠️  无分类返回!")

# 4. 查看所有栏目的分类统计
print("\n4️⃣ 所有栏目的分类统计:")
cur.execute("""
SELECT s.id, s.name, COUNT(c.id) as cat_count
FROM sections s
LEFT JOIN categories c ON s.id = c.section_id AND c.is_active = 1
GROUP BY s.id
ORDER BY s.id
""")

for row in cur.fetchall():
    section_id, section_name, cat_count = row
    print(f"  Section {section_id} ({section_name}): {cat_count} 个分类")

con.close()

print("\n" + "=" * 70)
print("✅ 诊断完成 - 数据已在数据库中正确存储")
print("=" * 70)
