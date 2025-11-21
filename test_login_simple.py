#!/usr/bin/env python3
import requests
import json

print("测试登录API...")
print("=" * 50)

url = "http://localhost:8001/api/admin/login"
data = {
    "username": "admin",
    "password": "admin123"
}

print(f"POST {url}")
print(f"数据: {json.dumps(data, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应体: {response.text}")
    
    if response.status_code == 200:
        try:
            json_response = response.json()
            print(f"\n✅ 登录成功!")
            print(f"Token: {json_response.get('access_token', 'N/A')[:50]}...")
        except:
            print(f"\n❌ 响应不是有效的JSON")
    else:
        print(f"\n❌ 登录失败 (HTTP {response.status_code})")
        
except Exception as e:
    print(f"❌ 错误: {e}")
