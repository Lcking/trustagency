#!/usr/bin/env python3
"""
诊断脚本 - 找出admin页面路由的问题
"""
import os
import sys
from pathlib import Path

# 添加后端路径
sys.path.insert(0, '/Users/ck/Desktop/Project/trustagency/backend')

def diagnose():
    """诊断问题"""
    print("=" * 70)
    print("🔍 诊断Admin页面路由问题")
    print("=" * 70)
    
    # 1. 检查当前工作目录
    print("\n[1] 当前工作目录:")
    cwd = os.getcwd()
    print(f"    CWD: {cwd}")
    print(f"    预期: 任何地方都OK")
    
    # 2. 检查路径计算
    print("\n[2] 路径计算 (按照 app/main.py 的逻辑):")
    main_file = '/Users/ck/Desktop/Project/trustagency/backend/app/main.py'
    BACKEND_DIR = Path(os.path.dirname(os.path.abspath(main_file))).parent
    print(f"    BACKEND_DIR: {BACKEND_DIR}")
    print(f"    预期: /Users/ck/Desktop/Project/trustagency/backend")
    
    ADMIN_DIR = BACKEND_DIR / "site" / "admin"
    print(f"    ADMIN_DIR: {ADMIN_DIR}")
    print(f"    预期: /Users/ck/Desktop/Project/trustagency/backend/site/admin")
    
    # 3. 检查文件存在性
    print("\n[3] 文件存在性检查:")
    admin_index_path = ADMIN_DIR / "index.html"
    print(f"    Admin index 路径: {admin_index_path}")
    print(f"    文件存在: {admin_index_path.exists()}")
    
    if admin_index_path.exists():
        size = admin_index_path.stat().st_size
        print(f"    文件大小: {size:,} 字节")
        print(f"    ✅ 文件存在")
    else:
        print(f"    ❌ 文件不存在！")
        # 列出目录内容
        if (BACKEND_DIR / "site").exists():
            print(f"    site 目录内容: {list((BACKEND_DIR / 'site').iterdir())}")
        if (BACKEND_DIR / "site" / "admin").exists():
            print(f"    site/admin 目录内容: {list((BACKEND_DIR / 'site' / 'admin').iterdir())}")
    
    # 4. 检查 Docker 配置
    print("\n[4] Docker 配置检查:")
    docker_compose_path = Path('/Users/ck/Desktop/Project/trustagency/docker-compose.yml')
    if docker_compose_path.exists():
        print(f"    docker-compose.yml 存在: ✅")
        with open(docker_compose_path) as f:
            content = f.read()
            if '/app/site' in content:
                print(f"    Docker 后端挂载点: /app ⚠️")
                print(f"    Docker 中的admin路径会是: /app/site/admin")
    else:
        print(f"    docker-compose.yml 不存在")
    
    # 5. 检查是否有Docker容器在运行
    print("\n[5] Docker 容器检查:")
    result = os.system('docker ps | grep trustagency-backend > /dev/null 2>&1')
    if result == 0:
        print(f"    ⚠️ trustagency-backend 容器正在运行！")
        print(f"    建议: 停止容器后再运行本地开发版本")
    else:
        print(f"    本地模式: 容器未运行 ✅")
    
    # 6. 检查本地虚拟环境
    print("\n[6] 本地虚拟环境检查:")
    venv_python = Path('/Users/ck/Desktop/Project/trustagency/backend/venv/bin/python')
    if venv_python.exists():
        print(f"    虚拟环境存在: ✅")
    else:
        print(f"    虚拟环境不存在: ❌")
    
    print("\n" + "=" * 70)
    print("📊 诊断总结")
    print("=" * 70)
    
    if admin_index_path.exists():
        print("\n✅ 本地文件 OK - 路径计算也是对的")
        print("   问题可能是:")
        print("   1. Docker 容器仍在运行（返回 /app 路径）")
        print("   2. 缓存代码（__pycache__ 目录）")
        print("   3. 端口冲突")
        print("\n🔧 建议:")
        print("   1. pkill -9 -f 'uvicorn\\|docker\\|python'")
        print("   2. python3 clean_cache.py")
        print("   3. 重新启动后端")
    else:
        print("\n❌ 文件不存在！")
        print("   这是关键问题。")
        print("\n🔧 建议:")
        print("   检查是否真的删除了 site/admin/index.html")
        print("   确保 backend/site/admin/index.html 存在")

if __name__ == "__main__":
    diagnose()
