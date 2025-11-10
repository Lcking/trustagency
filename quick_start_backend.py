#!/usr/bin/env python3
"""
快速启动 FastAPI 后端服务
自动处理依赖检查和安装
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("\n" + "="*80)
    print("🚀 TrustAgency 后端启动程序")
    print("="*80 + "\n")
    
    # 项目路径
    backend_dir = Path("/Users/ck/Desktop/Project/trustagency/backend")
    project_root = Path("/Users/ck/Desktop/Project/trustagency")
    
    # 进入后端目录
    os.chdir(backend_dir)
    print(f"✅ 进入目录: {backend_dir}\n")
    
    # 检查必需的包
    required_packages = [
        ("fastapi", "fastapi==0.104.1"),
        ("uvicorn", "uvicorn[standard]==0.24.0"),
        ("python_dotenv", "python-dotenv==1.0.0"),
    ]
    
    print("📦 检查依赖...\n")
    missing_packages = []
    
    for package_import, package_name in required_packages:
        try:
            __import__(package_import)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ⚠️  {package_name} 未安装")
            missing_packages.append(package_name)
    
    # 安装缺失的包
    if missing_packages:
        print(f"\n⏳ 正在安装缺失的包...\n")
        for package in missing_packages:
            print(f"  📥 安装 {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", package],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"  ❌ 安装失败: {result.stderr}")
            else:
                print(f"  ✅ {package} 已安装")
    
    print("\n" + "="*80)
    print("🎯 启动 FastAPI 服务...")
    print("="*80 + "\n")
    
    print("📍 服务地址:")
    print("   - Admin 页面:    http://localhost:8001/admin/")
    print("   - API 文档:      http://localhost:8001/api/docs")
    print("   - OpenAPI JSON:  http://localhost:8001/api/openapi.json")
    print("\n💡 提示:")
    print("   - 按 Ctrl+C 停止服务")
    print("   - 使用 --reload 参数自动重启代码更改")
    print("   - 查看 http://localhost:8001/api/docs 了解 API")
    print("\n" + "="*80 + "\n")
    
    # 启动 uvicorn
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "uvicorn", 
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n\n⏹️  服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
