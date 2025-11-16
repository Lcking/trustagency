#!/usr/bin/env python3
"""
验证API URL修复是否有效
"""

import re
from pathlib import Path

# 检查修复是否已应用
html_file = Path("/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html")

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找getAPIUrl函数
pattern = r'const getAPIUrl = \(\) => \{(.*?)\};'
match = re.search(pattern, content, re.DOTALL)

if match:
    func_body = match.group(1)
    
    # 检查是否有正确的修复
    if '${port || 8000}' in func_body or 'port || 8000' in func_body:
        print("✅ API URL 修复已应用")
        print("\n修复内容：")
        print(func_body.strip()[:300] + "...")
    elif ':8001' in func_body:
        print("❌ API URL 仍然硬编码为8001")
        print("\n当前内容：")
        print(func_body.strip()[:300] + "...")
    else:
        print("⚠️  无法判断修复状态")
        print("\n当前内容：")
        print(func_body.strip()[:300] + "...")
else:
    print("❌ 无法找到 getAPIUrl 函数")

print("\n" + "="*60)
print("预期的修复内容应该包含：")
print("- port || 8000  （动态端口）")
print("- 不应该有硬编码的 :8001")
print("="*60)
