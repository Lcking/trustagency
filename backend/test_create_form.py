#!/usr/bin/env python3
"""
测试新增平台表单定义 API
"""
import requests
import json

BASE_URL = "http://localhost:8001"

# 1. 登录获取 token
print("1. 获取认证 token...")
login_response = requests.post(
    f"{BASE_URL}/api/admin/login",
    json={"username": "admin", "password": "admin123"}
)
print(f"   Status: {login_response.status_code}")
if login_response.status_code != 200:
    print(f"   Response: {login_response.json()}")
    # 尝试用户注册
    print("   尝试注册用户...")
    reg_response = requests.post(
        f"{BASE_URL}/api/admin/register",
        json={"username": "admin", "password": "admin123", "email": "admin@example.com", "full_name": "Admin"}
    )
    print(f"   Register Status: {reg_response.status_code}")
    if reg_response.status_code == 200:
        token = reg_response.json().get("access_token")
    else:
        print(f"   Register Response: {reg_response.json()}")
        exit(1)
else:
    token = login_response.json().get("access_token")

print(f"   Token: {token[:50]}...")

# 2. 获取新增平台表单定义
print("\n2. 获取新增平台表单定义...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{BASE_URL}/api/admin/platforms/create-form-definition",
    headers=headers
)
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   ✅ 成功获取表单定义")
    print(f"   Sections: {len(data['sections'])}")
    
    # 检查新字段是否在表单定义中
    new_fields = ["overview_intro", "fee_table", "safety_info", "top_badges"]
    print("\n3. 检查新字段是否在表单定义中...")
    for section in data['sections']:
        for field in section.get('fields', []):
            if field['name'] in new_fields:
                print(f"   ✅ {field['name']}: {field['label']}")
    
    # 打印完整的表单定义
    print("\n4. 完整的表单定义：")
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f"   ❌ Error: {response.json()}")
    exit(1)

print("\n✅ 测试完成！新增平台表单定义 API 工作正常")
