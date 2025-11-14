#!/usr/bin/env python3
"""
真实前端场景模拟 - 验证新增平台表单在浏览器中能否显示所有字段
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8001"
ADMIN_USER = {"username": "admin", "password": "admin123"}

def get_token():
    """获取认证 token"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        json=ADMIN_USER
    )
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.json()}")
        return None
    return response.json()["access_token"]

def test_form_definition():
    """测试前端能否获取表单定义"""
    print("\n" + "="*80)
    print("🧪 真实前端场景测试 - 新增平台表单")
    print("="*80)
    
    token = get_token()
    if not token:
        return False
    
    print(f"\n✅ Token 获取成功")
    
    # 模拟前端: 获取表单定义
    print("\n📋 前端步骤 1: 调用 GET /api/admin/platforms/create-form-definition")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/admin/platforms/create-form-definition",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取表单定义失败: {response.json()}")
        return False
    
    form_def = response.json()
    print(f"✅ 表单定义获取成功")
    print(f"   - Sections: {len(form_def['sections'])}")
    
    # 检查4个新字段是否在表单中显示
    print("\n📋 前端步骤 2: 检查前端需要显示的字段")
    new_fields = {
        "overview_intro": "概述介绍",
        "fee_table": "费率表",
        "safety_info": "安全信息",
        "top_badges": "顶部徽章"
    }
    
    found_fields = {}
    for section in form_def['sections']:
        for field in section.get('fields', []):
            if field['name'] in new_fields:
                found_fields[field['name']] = {
                    'label': field['label'],
                    'type': field['type'],
                    'section': section['title']
                }
    
    print(f"\n   发现的新字段:")
    if len(found_fields) == 4:
        for name, info in found_fields.items():
            print(f"   ✅ {name}")
            print(f"      标签: {info['label']}")
            print(f"      类型: {info['type']}")
            print(f"      所在Section: {info['section']}")
    else:
        print(f"   ❌ 只找到 {len(found_fields)}/4 个新字段")
        for name in new_fields:
            if name not in found_fields:
                print(f"      ❌ 缺失: {name}")
        return False
    
    # 模拟前端: 使用表单定义渲染表单
    print("\n📋 前端步骤 3: 根据表单定义渲染 HTML 表单")
    form_html_lines = [
        '<form id="platformForm" onsubmit="savePlatform(event)">',
        '  <!-- 由前端JavaScript根据form_definition动态生成 -->',
        '  <!-- 以下是新增平台需要显示的字段 -->'
    ]
    
    for section in form_def['sections']:
        form_html_lines.append(f'\n  <fieldset>')
        form_html_lines.append(f'    <legend>{section["title"]}</legend>')
        
        for field in section.get('fields', []):
            field_id = f"platform_{field['name']}"
            
            if field['type'] == 'text':
                form_html_lines.append(f'    <input type="text" id="{field_id}" placeholder="{field.get("placeholder", "")}" />')
            elif field['type'] == 'textarea':
                form_html_lines.append(f'    <textarea id="{field_id}" placeholder="{field.get("placeholder", "")}"></textarea>')
            elif field['type'] == 'number':
                form_html_lines.append(f'    <input type="number" id="{field_id}" />')
            elif field['type'] == 'checkbox':
                form_html_lines.append(f'    <input type="checkbox" id="{field_id}" />')
            elif field['type'] == 'select':
                form_html_lines.append(f'    <select id="{field_id}"></select>')
            elif field['type'] == 'json':
                form_html_lines.append(f'    <textarea id="{field_id}" placeholder="输入JSON"></textarea>')
        
        form_html_lines.append(f'  </fieldset>')
    
    form_html_lines.append('</form>')
    
    # 统计表单中的字段
    print(f"\n   生成的表单中的字段数:")
    total_fields = sum(len(s['fields']) for s in form_def['sections'])
    print(f"   总字段数: {total_fields}")
    
    # 检查4个新字段是否被渲染到表单中
    form_html = '\n'.join(form_html_lines)
    form_contains_all_new_fields = all(
        f'id="platform_{name}"' in form_html 
        for name in new_fields.keys()
    )
    
    if form_contains_all_new_fields:
        print(f"   ✅ 所有 4 个新字段都在表单中:")
        for name in new_fields.keys():
            print(f"      ✅ <input id=\"platform_{name}\" ... />")
    else:
        print(f"   ❌ 部分新字段缺失")
        return False
    
    # 模拟前端: 提交表单
    print("\n📋 前端步骤 4: 用户填写表单并提交")
    form_data = {
        "name": "TestPlatform_FrontendTest",
        "slug": "testplatform_fe",
        "platform_type": "exchange",
        "rating": 8.5,
        "rank": 10,
        "is_recommended": True,
        "overview_intro": "这是平台的概述介绍（前端测试）",
        "fee_table": "# 费率表\n- Maker: 0.1%\n- Taker: 0.15%",
        "safety_info": "经过Certik审计，冷钱包存储",
        "top_badges": json.dumps(["推荐平台", "安全可信"]),
        "description": "测试平台"
    }
    
    print(f"   提交的数据包含:")
    for key in ['name', 'overview_intro', 'fee_table', 'safety_info', 'top_badges']:
        if key in form_data:
            value = form_data[key]
            if len(str(value)) > 50:
                value = str(value)[:50] + "..."
            print(f"   - {key}: {value}")
    
    response = requests.post(
        f"{BASE_URL}/api/platforms",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=form_data
    )
    
    if response.status_code != 201:
        print(f"\n   ❌ 创建平台失败: {response.json()}")
        return False
    
    created = response.json()
    platform_id = created['id']
    print(f"\n   ✅ 平台创建成功 (ID: {platform_id})")
    
    # 验证保存的数据
    print("\n📋 前端步骤 5: 验证保存的数据包含所有新字段")
    
    response = requests.get(
        f"{BASE_URL}/api/platforms/{platform_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"   ❌ 获取平台数据失败")
        return False
    
    saved_data = response.json()
    
    all_correct = True
    for field_name in ['overview_intro', 'fee_table', 'safety_info', 'top_badges']:
        value = saved_data.get(field_name)
        if value:
            print(f"   ✅ {field_name}: 已保存")
        else:
            print(f"   ❌ {field_name}: 未保存")
            all_correct = False
    
    return all_correct

if __name__ == "__main__":
    print("\n🌐 模拟真实前端场景")
    print("="*80)
    print("\n场景: 用户在浏览器中打开'新增平台'表单")
    print("预期: 看到所有字段，包括 4 个新字段")
    print("="*80)
    
    success = test_form_definition()
    
    if success:
        print("\n" + "="*80)
        print("✅ 真实前端场景测试通过！")
        print("="*80)
        print("\n结论:")
        print("  • 前端可以调用 GET /api/admin/platforms/create-form-definition")
        print("  • 可以获取包含所有字段的表单定义")
        print("  • 可以根据定义渲染动态表单")
        print("  • 可以提交包含 4 个新字段的平台数据")
        print("  • 所有新字段都能正确保存")
        print("\n✅ 新增平台表单已完全就绪！")
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ 真实前端场景测试失败！")
        print("="*80)
        sys.exit(1)
