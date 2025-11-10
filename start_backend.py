#!/usr/bin/env python3
"""
启动 TrustAgency 后端服务的 Python 脚本
"""
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """启动后端服务"""
    
    # 后端目录
    backend_dir = Path("/Users/ck/Desktop/Project/trustagency/backend")
    venv_python = backend_dir / "venv" / "bin" / "python"
    
    print("=" * 70)
    print("🚀 TrustAgency 后端启动")
    print("=" * 70)
    
    # 检查虚拟环境
    if not venv_python.exists():
        print(f"❌ 错误: 虚拟环境中的 Python 不存在")
        print(f"   路径: {venv_python}")
        print(f"\n请先创建虚拟环境:")
        print(f"   cd {backend_dir}")
        print(f"   python -m venv venv")
        return False
    
    print(f"✅ 虚拟环境 Python: {venv_python}")
    
    # 进入后端目录
    os.chdir(backend_dir)
    print(f"✅ 工作目录: {backend_dir}")
    
    # 检查依赖
    print("\n🔍 检查依赖...")
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "uvicorn" not in result.stdout:
            print("⚠️  uvicorn 未安装，正在安装...")
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "-q", "uvicorn"],
                timeout=30
            )
            print("✅ uvicorn 安装完成")
        else:
            print("✅ uvicorn 已安装")
        
        if "fastapi" not in result.stdout:
            print("⚠️  fastapi 未安装，正在安装...")
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "-q", "fastapi"],
                timeout=30
            )
            print("✅ fastapi 安装完成")
        else:
            print("✅ fastapi 已安装")
            
    except Exception as e:
        print(f"⚠️  依赖检查失败: {e}")
    
    # 启动服务
    print("\n" + "=" * 70)
    print("🎯 启动后端服务...")
    print("=" * 70)
    print(f"📍 URL: http://localhost:8001/admin/")
    print(f"👤 用户: admin")
    print(f"🔑 密码: newpassword123")
    print(f"⏹️  按 Ctrl+C 停止服务")
    print("=" * 70 + "\n")
    
    try:
        subprocess.run(
            [str(venv_python), "-m", "uvicorn", "app.main:app", "--port", "8001", "--reload"],
            cwd=str(backend_dir)
        )
    except KeyboardInterrupt:
        print("\n\n⏹️  服务已停止")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = start_backend()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
