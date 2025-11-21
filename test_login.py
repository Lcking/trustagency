#!/usr/bin/env python3
"""
测试登录API
"""
import requests
import json

print("🧪 测试后端登录API\n")

# 测试1: 检查端点是否响应
print("1️⃣  检查 /api/admin/login 是否存在...")
try:
    response = requests.options('http://localhost:8001/api/admin/login', timeout=5)
    print(f"   状态码: {response.status_code}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("")

# 测试2: 尝试登录
print("2️⃣  尝试登录...")
try:
    response = requests.post(
        'http://localhost:8001/api/admin/login',
        json={'username': 'admin', 'password': 'admin123'},
        timeout=5
    )
    print(f"   状态码: {response.status_code}")
    print(f"   内容类型: {response.headers.get('content-type')}")
    print(f"   响应长度: {len(response.text)} 字符")
    print(f"   响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ JSON 解析成功")
            print(f"   返回的数据:")
            print(f"   - access_token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   - token_type: {data.get('token_type')}")
            print(f"   - user: {data.get('user')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 解析失败: {e}")
    else:
        print(f"   ⚠️  状态码异常")
        try:
            data = response.json()
            print(f"   错误信息: {data}")
        except:
            print(f"   响应不是JSON: {response.text[:200]}")
            
except requests.exceptions.ConnectionError:
    print(f"   ❌ 无法连接到 http://localhost:8001")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("")

# 测试3: 检查数据库中的管理员
print("3️⃣  检查数据库中的管理员用户...")
try:
    import sqlite3
    conn = sqlite3.connect('/Users/ck/Desktop/Project/trustagency/backend/trustagency.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, is_active FROM admin_users LIMIT 1')
    row = cursor.fetchone()
    if row:
        print(f"   ✅ 找到管理员: ID={row[0]}, username={row[1]}, is_active={row[2]}")
    else:
        print(f"   ❌ 数据库中没有管理员用户")
    conn.close()
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("")
print("✅ 测试完成")
