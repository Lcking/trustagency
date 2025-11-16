#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试分类 API 端点 - 检查后端是否能正确返回分类数据
"""
import sys
import os
import json

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

# 创建测试客户端
client = TestClient(app)

print("=" * 60)
print("测试分类 API 端点")
print("=" * 60)

# 测试 1: 获取所有栏目
print("\n1️⃣ 测试: GET /api/sections")
response = client.get("/api/sections")
print(f"  状态码: {response.status_code}")
if response.status_code == 200:
    sections = response.json()
    print(f"  栏目数: {len(sections.get('data', []))}")
    for section in sections.get('data', []):
        print(f"    - {section['name']} (ID={section['id']})")
else:
    print(f"  错误: {response.text}")

# 测试 2: 获取第一个栏目的分类
print("\n2️⃣ 测试: GET /api/categories/section/1")
response = client.get("/api/categories/section/1")
print(f"  状态码: {response.status_code}")
if response.status_code == 200:
    categories = response.json()
    print(f"  分类数: {len(categories)}")
    for cat in categories[:5]:
        print(f"    - {cat['name']} (ID={cat['id']})")
else:
    print(f"  错误: {response.text}")

# 测试 3: 获取分类及文章数
print("\n3️⃣ 测试: GET /api/categories/section/1/with-count")
response = client.get("/api/categories/section/1/with-count")
print(f"  状态码: {response.status_code}")
if response.status_code == 200:
    categories = response.json()
    print(f"  分类数: {len(categories)}")
    for cat in categories[:5]:
        print(f"    - {cat['name']} (article_count={cat.get('article_count', 0)})")
else:
    print(f"  错误: {response.text}")

# 测试 4: 直接查询数据库验证
print("\n4️⃣ 数据库验证:")
import sqlite3
con = sqlite3.connect('trustagency.db')
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM categories")
count = cur.fetchone()[0]
print(f"  数据库中分类总数: {count}")
con.close()

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
