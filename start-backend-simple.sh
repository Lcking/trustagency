#!/bin/bash
# 简化的后端启动脚本 - 不使用reload避免卡顿

# 杀死现有的uvicorn进程
pkill -f "uvicorn" 2>/dev/null || true
sleep 1

# 进入后端目录
cd /Users/ck/Desktop/Project/trustagency/backend

# 激活虚拟环境并启动
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 1
