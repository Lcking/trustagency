#!/usr/bin/env python3
"""
Python 脚本来重启 Docker 容器并测试
"""
import subprocess
import time
import os
import sys

os.chdir('/Users/ck/Desktop/Project/trustagency')

def run_command(cmd, description, timeout=30):
    """执行命令并打印输出"""
    print(f"\n🔧 {description}...")
    print(f"执行: {cmd}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠️  命令超时 ({timeout}秒)")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

# 步骤 1: 停止容器
run_command(
    "docker-compose down -v",
    "停止并移除所有容器和卷"
)

# 步骤 2: 等待
print("\n⏳ 等待 5 秒...")
time.sleep(5)

# 步骤 3: 启动容器
run_command(
    "docker-compose up -d",
    "启动所有容器",
    timeout=60
)

# 步骤 4: 等待服务启动
print("\n⏳ 等待 30 秒让服务启动...")
time.sleep(30)

# 步骤 5: 测试
print("\n🧪 测试后端...")
result = subprocess.run(
    "curl -s http://localhost:8001/admin/ | head -20",
    shell=True,
    capture_output=True,
    text=True,
    timeout=10
)

print("响应:")
print("=" * 60)
print(result.stdout)
print("=" * 60)

if '{"detail"' in result.stdout:
    print("❌ 仍然返回 404 错误")
    sys.exit(1)
elif '<!DOCTYPE' in result.stdout or '<html' in result.stdout:
    print("✅ 成功！返回了 HTML 内容")
    sys.exit(0)
else:
    print("⚠️  无法判断响应类型")
    sys.exit(1)
