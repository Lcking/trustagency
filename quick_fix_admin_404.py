#!/usr/bin/env python3
"""
快速修复脚本 - 一键解决 Admin 404 问题
"""
import os
import subprocess
import shutil
import sys
import time

def run_cmd(cmd, description=""):
    """运行命令"""
    if description:
        print(f"\n▶️  {description}")
    print(f"   $ {cmd}")
    result = os.system(cmd)
    return result == 0

def clean_pycache():
    """清理 Python 缓存"""
    print("\n🧹 清理 Python 缓存...")
    backend_path = "/Users/ck/Desktop/Project/trustagency/backend"
    
    # 清理 __pycache__
    count1 = 0
    for root, dirs, files in os.walk(backend_path):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            print(f"   删除: {cache_dir}")
            shutil.rmtree(cache_dir, ignore_errors=True)
            count1 += 1
    
    # 清理 .pyc
    count2 = 0
    for root, dirs, files in os.walk(backend_path):
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                count2 += 1
    
    print(f"   ✅ 清理了 {count1} 个缓存目录和 {count2} 个 .pyc 文件")

def stop_docker():
    """停止 Docker 容器"""
    print("\n🐳 停止 Docker 容器...")
    
    # 查看正在运行的容器
    result = os.system("docker ps | grep trustagency > /dev/null 2>&1")
    if result == 0:
        print("   发现 TrustAgency 容器，正在停止...")
        os.system("docker stop trustagency-backend 2>/dev/null")
        os.system("docker stop trustagency-frontend 2>/dev/null")
        time.sleep(2)
        print("   ✅ Docker 容器已停止")
    else:
        print("   ℹ️  没有运行的 TrustAgency 容器")

def kill_processes():
    """杀死 Python 进程"""
    print("\n⏹️  停止 Python 进程...")
    os.system("pkill -9 -f 'uvicorn' 2>/dev/null")
    os.system("pkill -9 -f 'python' 2>/dev/null")
    time.sleep(2)
    print("   ✅ Python 进程已停止")

def verify_files():
    """验证文件"""
    print("\n📁 验证文件...")
    
    admin_file = "/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html"
    
    if os.path.exists(admin_file):
        size = os.path.getsize(admin_file)
        lines = len(open(admin_file).readlines())
        print(f"   ✅ 文件存在: {admin_file}")
        print(f"      大小: {size:,} 字节")
        print(f"      行数: {lines:,} 行")
        return True
    else:
        print(f"   ❌ 文件不存在: {admin_file}")
        return False

def start_backend():
    """启动后端"""
    print("\n🚀 启动后端...")
    print("   $ cd /Users/ck/Desktop/Project/trustagency/backend")
    print("   $ source venv/bin/activate")
    print("   $ python -m uvicorn app.main:app --port 8001 --reload")
    print("\n   ⏳ 后端启动中，请稍候...")
    print("   📍 一旦看到 'Application startup complete' 就可以访问了")
    print("\n   在新终端中，访问:")
    print("   $ curl http://localhost:8001/admin/")
    print("   或打开浏览器: http://localhost:8001/admin/")

def main():
    """主函数"""
    print("=" * 70)
    print("🔧 Admin 404 问题快速修复脚本")
    print("=" * 70)
    
    # 验证文件
    if not verify_files():
        print("\n❌ 关键文件不存在！无法修复。")
        sys.exit(1)
    
    # 执行修复
    print("\n" + "=" * 70)
    print("执行修复步骤...")
    print("=" * 70)
    
    # 1. 停止 Docker
    stop_docker()
    
    # 2. 杀死进程
    kill_processes()
    
    # 3. 清理缓存
    clean_pycache()
    
    # 4. 启动后端
    print("\n" + "=" * 70)
    print("✅ 修复完成！")
    print("=" * 70)
    start_backend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
