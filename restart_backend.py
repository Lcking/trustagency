#!/usr/bin/env python3
"""
重启后端脚本
"""
import subprocess
import time
import os

print("⏹️  停止现有后端进程...")
os.system('pkill -f "uvicorn app.main:app"')
time.sleep(2)

print("🚀 启动新后端进程...")
os.system('cd /Users/ck/Desktop/Project/trustagency/backend && source venv/bin/activate && python -m uvicorn app.main:app --port 8001 --reload > /tmp/backend.log 2>&1 &')

time.sleep(3)

print("✅ 后端已启动")
print("🌐 访问地址: http://localhost:8001/admin/")
print("\n检查日志: tail -f /tmp/backend.log")
