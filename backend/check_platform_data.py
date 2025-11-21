#!/usr/bin/env python3
"""
直接测试数据库中的平台数据
"""
import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent / "trustagency.db"

if not db_path.exists():
    print(f"❌ 数据库不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row  # 返回字典行
cursor = conn.cursor()

print("=" * 60)
print("🔍 平台数据检查")
print("=" * 60)

# 查询第一个平台的所有字段
cursor.execute("PRAGMA table_info(platforms)")
columns = cursor.fetchall()
print("\n📋 平台表的列:")
for col in columns:
    print(f"   - {col['name']} ({col['type']})")

# 查询平台数据
print("\n📊 平台数据:")
cursor.execute("SELECT * FROM platforms LIMIT 1")
platform = cursor.fetchone()

if platform:
    print(f"\n第一个平台的数据:")
    for key in platform.keys():
        value = platform[key]
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:50]}...  (长度: {len(value)})")
        else:
            print(f"  {key}: {value}")
else:
    print("❌ 没有找到平台数据")

# 统计平台数量
cursor.execute("SELECT COUNT(*) as count FROM platforms")
total = cursor.fetchone()['count']
print(f"\n✅ 总共 {total} 个平台")

conn.close()
