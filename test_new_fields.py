#!/usr/bin/env python3
"""
平台编辑字段测试脚本
验证新增字段 (overview_intro, fee_table, safety_info, top_badges) 的完整性
"""

import requests
import json
import sys
from typing import Dict, List, Tuple

# API 配置
BASE_URL = "http://127.0.0.1:8001"
LOGIN_ENDPOINT = f"{BASE_URL}/api/admin/login"
EDIT_ENDPOINT = f"{BASE_URL}/api/admin/platforms/7/edit"
FORM_DEF_ENDPOINT = f"{BASE_URL}/api/admin/platforms/form-definition"

# 新增字段列表
NEW_FIELDS = ['overview_intro', 'fee_table', 'safety_info', 'top_badges']

def login(username: str, password: str) -> Tuple[bool, str]:
    """登录获取 JWT token"""
    try:
        response = requests.post(
            LOGIN_ENDPOINT,
            json={"username": username, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ 登录成功: {username}")
            return True, token
        else:
            print(f"❌ 登录失败: {response.json()}")
            return False, ""
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return False, ""

def check_edit_api(token: str) -> bool:
    """检查编辑 API 是否返回新字段"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(EDIT_ENDPOINT, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            found_fields = []
            missing_fields = []
            
            for field in NEW_FIELDS:
                if field in data:
                    value = data[field]
                    if value is None:
                        print(f"  ⚠️  {field}: null (字段存在但无数据)")
                    else:
                        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"  ✅ {field}: {display_value}")
                    found_fields.append(field)
                else:
                    print(f"  ❌ {field}: MISSING")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ 编辑 API 缺失字段: {', '.join(missing_fields)}")
                return False
            else:
                print(f"\n✅ 编辑 API 包含所有新字段")
                return True
        else:
            print(f"❌ 编辑 API 错误: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 编辑 API 异常: {e}")
        return False

def check_form_definition(token: str) -> bool:
    """检查表单定义 API 是否包含新字段"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(FORM_DEF_ENDPOINT, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            sections = data.get('sections', [])
            
            found_fields = {}
            all_section_titles = [s['title'] for s in sections]
            
            for section in sections:
                for field in section.get('fields', []):
                    if field.get('name') in NEW_FIELDS:
                        found_fields[field['name']] = section['title']
            
            print(f"\n  📋 Sections ({len(all_section_titles)}): {', '.join(all_section_titles)}\n")
            
            missing_fields = []
            for field in NEW_FIELDS:
                if field in found_fields:
                    print(f"  ✅ {field}: 在 \"{found_fields[field]}\" section")
                else:
                    print(f"  ❌ {field}: MISSING")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ 表单定义缺失字段: {', '.join(missing_fields)}")
                return False
            else:
                print(f"\n✅ 表单定义包含所有新字段")
                return True
        else:
            print(f"❌ 表单定义 API 错误: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 表单定义 API 异常: {e}")
        return False

def main():
    """主测试流程"""
    print("=" * 70)
    print("平台编辑字段验证测试")
    print("=" * 70)
    
    # 1. 登录
    print("\n[1/3] 登录系统...")
    success, token = login("admin", "admin123")
    if not success:
        print("\n❌ 测试失败: 无法登录")
        return False
    
    # 2. 测试编辑 API
    print("\n[2/3] 检查编辑 API 返回新字段...")
    edit_ok = check_edit_api(token)
    
    # 3. 测试表单定义 API
    print("\n[3/3] 检查表单定义 API...")
    form_ok = check_form_definition(token)
    
    # 总结
    print("\n" + "=" * 70)
    if edit_ok and form_ok:
        print("✅ 所有测试通过! 新增字段功能正常")
        print("=" * 70)
        return True
    else:
        print("❌ 有测试未通过，请检查")
        print("=" * 70)
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏸️  测试中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
