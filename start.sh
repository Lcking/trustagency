#!/bin/bash
# 快速启动后端脚本

cd /Users/ck/Desktop/Project/trustagency/backend

# 杀死现有进程
killall -9 python 2>/dev/null

# 激活虚拟环境并启动
source venv/bin/activate
python -m uvicorn app.main:app --port 8001 --reload --log-level info
