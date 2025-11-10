#!/usr/bin/env python3
"""
Python 脚本来完成最终重启测试
"""
import subprocess
import time
import sys

def run_cmd(cmd, description, wait=0):
    """执行命令"""
    print(f"\n{description}")
    print("=" * 60)
    result = subprocess.run(cmd, shell=True, cwd="/Users/ck/Desktop/Project/trustagency")
    if wait > 0:
        print(f"⏳ 等待 {wait} 秒...")
        time.sleep(wait)
    return result.returncode == 0

# 执行
print("🔄 最终修复和测试")
print("=" * 60)

# 1. 停止
run_cmd("docker-compose down", "1️⃣  停止容器")

# 2. 启动
run_cmd("docker-compose up -d", "2️⃣  启动容器", wait=20)

# 3. 测试
print("\n3️⃣  测试管理后台")
print("=" * 60)
result = subprocess.run(
    "curl -s http://localhost:8001/admin/ | head -20",
    shell=True,
    capture_output=True,
    text=True,
    cwd="/Users/ck/Desktop/Project/trustagency"
)

print(result.stdout)

if "<!DOCTYPE" in result.stdout or "<html" in result.stdout:
    print("\n✅ 成功！管理后台已加载")
    sys.exit(0)
elif "Admin page not found" in result.stdout:
    print("\n❌ 仍然失败：文件仍然找不到")
    sys.exit(1)
else:
    print("\n⚠️  无法判断结果")
    sys.exit(1)
