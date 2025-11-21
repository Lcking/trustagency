#!/usr/bin/env python3
"""
测试登录API - 详细版本
"""
import json
import requests
from urllib.parse import urljoin

BASE_URL = "http://localhost:8001"

def test_login():
    """测试登录端点"""
    print("=" * 60)
    print("🔐 测试登录 API")
    print("=" * 60)
    
    # 测试数据
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    endpoint = urljoin(BASE_URL, "/api/admin/login")
    print(f"\n📤 POST {endpoint}")
    print(f"📦 请求体: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            json=login_data,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 响应状态: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        print(f"\n📝 响应体:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(f"   (非 JSON): {response.text}")
        
        if response.status_code == 200:
            print("\n✅ 登录成功！")
            return True
        else:
            print(f"\n❌ 登录失败! HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("   确认后端是否运行在 http://localhost:8001")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False

if __name__ == "__main__":
    test_login()
