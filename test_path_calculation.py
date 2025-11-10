#!/usr/bin/env python3
"""
测试 ADMIN_DIR 路径是否正确
"""
import sys
sys.path.insert(0, '/Users/ck/Desktop/Project/trustagency/backend')

from pathlib import Path
import os

# 模拟 app/main.py 的路径计算
print("=" * 70)
print("🔍 路径计算测试")
print("=" * 70)

# 方法 1: 使用 __file__ (可能有问题)
print("\n[方法 1] 使用 __file__:")
main_file = '/Users/ck/Desktop/Project/trustagency/backend/app/main.py'
BACKEND_DIR_1 = Path(os.path.dirname(os.path.abspath(main_file))).parent
ADMIN_DIR_1 = BACKEND_DIR_1 / "site" / "admin"
print(f"  BACKEND_DIR: {BACKEND_DIR_1}")
print(f"  ADMIN_DIR: {ADMIN_DIR_1}")
print(f"  exists: {(ADMIN_DIR_1 / 'index.html').exists()}")

# 方法 2: 使用硬编码路径 (推荐)
print("\n[方法 2] 使用硬编码路径 (推荐):")
BACKEND_DIR_2 = Path("/Users/ck/Desktop/Project/trustagency/backend").resolve()
ADMIN_DIR_2 = BACKEND_DIR_2 / "site" / "admin"
print(f"  BACKEND_DIR: {BACKEND_DIR_2}")
print(f"  ADMIN_DIR: {ADMIN_DIR_2}")
print(f"  exists: {(ADMIN_DIR_2 / 'index.html').exists()}")

# 方法 3: 使用环境变量
print("\n[方法 3] 使用环境变量:")
env_backend = os.getenv("BACKEND_DIR", "/Users/ck/Desktop/Project/trustagency/backend")
BACKEND_DIR_3 = Path(env_backend).resolve()
ADMIN_DIR_3 = BACKEND_DIR_3 / "site" / "admin"
print(f"  BACKEND_DIR: {BACKEND_DIR_3}")
print(f"  ADMIN_DIR: {ADMIN_DIR_3}")
print(f"  exists: {(ADMIN_DIR_3 / 'index.html').exists()}")

print("\n" + "=" * 70)
print("✅ 测试完成")
print("=" * 70)

# 检查文件
print("\n📁 文件检查:")
for path in [ADMIN_DIR_1 / "index.html", ADMIN_DIR_2 / "index.html", ADMIN_DIR_3 / "index.html"]:
    if path.exists():
        size = path.stat().st_size
        print(f"  ✅ {path} ({size:,} bytes)")
    else:
        print(f"  ❌ {path}")
