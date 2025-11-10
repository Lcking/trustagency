#!/usr/bin/env python3
"""
诊断管理后台问题
"""
import sys
import os
from pathlib import Path

# 检查路径
project_root = Path(__file__).parent
admin_path = project_root / "site" / "admin"
admin_index = admin_path / "index.html"
main_py = project_root / "backend" / "app" / "main.py"

print("=" * 60)
print("诊断管理后台问题")
print("=" * 60)

# 1. 检查文件存在性
print("\n1️⃣  检查文件...")
print(f"  ✓ 项目根: {project_root}")
print(f"  {'✓' if admin_path.exists() else '✗'} 管理后台目录: {admin_path}")
print(f"  {'✓' if admin_index.exists() else '✗'} index.html 文件: {admin_index}")
print(f"  {'✓' if main_py.exists() else '✗'} main.py 文件: {main_py}")

# 2. 检查 main.py 代码
print("\n2️⃣  检查 main.py 配置...")
with open(main_py, 'r') as f:
    content = f.read()
    
checks = [
    ('StaticFiles 导入', 'from fastapi.staticfiles import StaticFiles' in content),
    ('CORS 包含 localhost', '"http://localhost"' in content),
    ('CORS 包含 localhost:80', '"http://localhost:80"' in content),
    ('StaticFiles 挂载', 'app.mount("/admin"' in content),
    ('/admin/ 路由处理', '@app.get("/admin/"' in content),
    ('FileResponse 导入', 'from fastapi.responses import FileResponse' in content),
]

for name, result in checks:
    print(f"  {'✓' if result else '✗'} {name}")

# 3. 尝试访问 API
print("\n3️⃣  尝试访问 API...")
try:
    import requests
    
    # 尝试访问 /admin/
    print("  正在请求 http://localhost:8001/admin/...")
    r = requests.get('http://localhost:8001/admin/', timeout=5)
    print(f"  状态码: {r.status_code}")
    
    if r.status_code == 200:
        print(f"  ✓ 返回了 HTML 内容")
        print(f"  内容长度: {len(r.text)} 字节")
        print(f"  前 100 字符: {r.text[:100]}")
    else:
        print(f"  ✗ 返回了错误: {r.text[:100]}")
        
except Exception as e:
    print(f"  ✗ 无法连接: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
