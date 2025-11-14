#!/usr/bin/env python3
"""
测试新增平台的完整工作流
验证所有 4 个新字段都能正确提交和保存
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"
ADMIN_USER = {"username": "admin", "password": "admin123"}

def get_token():
    """获取认证 token"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        json=ADMIN_USER
    )
    if response.status_code != 200:
        raise Exception(f"登录失败: {response.json()}")
    return response.json()["access_token"]

def get_create_form_definition(token):
    """获取新增平台表单定义"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/admin/platforms/create-form-definition",
        headers=headers
    )
    if response.status_code != 200:
        raise Exception(f"获取表单定义失败: {response.json()}")
    return response.json()

def create_platform(token, data):
    """创建新平台"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/platforms",
        headers=headers,
        json=data
    )
    return response

def get_platform(token, platform_id):
    """获取平台详情"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/platforms/{platform_id}",
        headers=headers
    )
    return response.json() if response.status_code == 200 else None

def run_tests():
    """运行测试"""
    print("=" * 80)
    print("新增平台完整工作流测试")
    print("=" * 80)
    
    try:
        # 1. 获取 token
        print("\n1️⃣  获取认证 token...")
        token = get_token()
        print(f"   ✅ Token: {token[:30]}...")
        
        # 2. 获取表单定义
        print("\n2️⃣  获取新增平台表单定义...")
        form_def = get_create_form_definition(token)
        print(f"   ✅ Sections: {len(form_def['sections'])}")
        
        # 检查新字段是否在表单定义中
        print("\n3️⃣  验证新字段在表单定义中...")
        new_fields_in_form = {}
        for section in form_def['sections']:
            for field in section.get('fields', []):
                if field['name'] in ["overview_intro", "fee_table", "safety_info", "top_badges"]:
                    new_fields_in_form[field['name']] = field['label']
        
        for field_name, label in new_fields_in_form.items():
            print(f"   ✅ {field_name}: {label}")
        
        if len(new_fields_in_form) < 4:
            print("   ❌ 缺少新字段！")
            return False
        
        # 4. 创建新平台，包含所有新字段
        print("\n4️⃣  创建新平台（包含新字段）...")
        new_platform_data = {
            "name": f"TestPlatform_{datetime.now().strftime('%s')}",
            "slug": f"testplatform_{datetime.now().strftime('%s')}",
            "platform_type": "exchange",
            "rating": 8.5,
            "rank": 10,
            "is_recommended": True,
            "description": "Test platform description",
            "overview_intro": "这是平台的详细概述和介绍信息",  # 新字段
            "founded_year": 2017,
            "fee_table": "# 费率表\n- Maker: 0.1%\n- Taker: 0.1%",  # 新字段
            "safety_rating": "A",  # 字符串类型
            "safety_info": "经过审计，采用冷钱包存储",  # 新字段
            "logo_url": "https://example.com/logo.png",
            "top_badges": json.dumps(["推荐平台", "安全可信", "高效交易"]),  # JSON 字符串
        }
        
        response = create_platform(token, new_platform_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"   ❌ 创建失败: {response.json()}")
            return False
        
        created_platform = response.json()
        platform_id = created_platform.get("id")
        print(f"   ✅ 平台已创建 (ID: {platform_id})")
        
        # 5. 获取创建的平台，验证新字段是否保存
        print("\n5️⃣  验证新字段是否正确保存...")
        platform = get_platform(token, platform_id)
        
        if not platform:
            print(f"   ❌ 无法获取平台数据")
            return False
        
        # 检查新字段
        field_checks = [
            ("overview_intro", "这是平台的详细概述和介绍信息"),
            ("fee_table", "# 费率表"),
            ("safety_info", "经过审计"),
            ("top_badges", ["推荐平台", "安全可信", "高效交易"])
        ]
        
        all_fields_saved = True
        for field_name, expected_value in field_checks:
            actual_value = platform.get(field_name)
            
            if isinstance(expected_value, list):
                # JSON 字段 - 解析 JSON 字符串
                try:
                    if isinstance(actual_value, str):
                        actual_json = json.loads(actual_value)
                    else:
                        actual_json = actual_value
                    is_correct = actual_json == expected_value
                except (json.JSONDecodeError, TypeError):
                    is_correct = False
                status = "✅" if is_correct else "❌"
                print(f"   {status} {field_name}: {actual_json if 'actual_json' in locals() else actual_value}")
            else:
                # 字符串字段
                is_correct = expected_value in str(actual_value) if actual_value else False
                status = "✅" if is_correct else "❌"
                print(f"   {status} {field_name}: {actual_value[:50] if actual_value else 'None'}...")
            
            if not is_correct:
                all_fields_saved = False
        
        if not all_fields_saved:
            print("   ⚠️  部分新字段未正确保存")
            return False
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        print("\n测试结果摘要：")
        print(f"  • 新增平台表单定义: ✅ 包含 4 个新字段")
        print(f"  • 新增平台 API: ✅ 接受 4 个新字段")
        print(f"  • 数据库保存: ✅ 所有新字段正确保存")
        print(f"  • 数据读取: ✅ 所有新字段正确返回")
        print("\n新增平台功能已完全就绪！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
