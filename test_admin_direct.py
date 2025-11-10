#!/usr/bin/env python3
"""
直接测试 admin 路由
"""
import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

# 导入 FastAPI 应用
try:
    from app.main import app
    print("✅ 成功导入 FastAPI 应用")
except ImportError as e:
    print(f"❌ 无法导入应用: {e}")
    sys.exit(1)

# 检查 StaticFiles 挂载
print("\n📋 检查应用配置...")
print(f"路由总数: {len(app.routes)}")

# 列出所有挂载
mounts = [(route, type(route).__name__) for route in app.routes]
for route, route_type in mounts:
    if hasattr(route, 'name'):
        print(f"  - {route.name} ({route_type})")
    elif hasattr(route, 'path'):
        print(f"  - {route.path} ({route_type})")
    else:
        print(f"  - ({route_type})")

# 检查 CORS 中间件
print("\n🔐 检查 CORS 配置...")
for middleware in app.user_middleware:
    if 'CORS' in str(middleware):
        print(f"  ✓ 找到 CORS 中间件")
        break

# 查看源代码中的关键部分
print("\n🔍 检查源代码...")
main_py_path = backend_dir / "app" / "main.py"
if main_py_path.exists():
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    # 检查关键代码行
    checks = [
        ('app.mount("/admin"', 'StaticFiles 挂载'),
        ('@app.get("/admin/"', '显式 /admin/ 路由'),
        ('"http://localhost"', 'CORS 包含 localhost'),
        ('"http://localhost:80"', 'CORS 包含 localhost:80'),
    ]
    
    for keyword, description in checks:
        if keyword in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")

print("\n✅ 诊断完成")
