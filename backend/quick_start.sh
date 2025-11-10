#!/bin/bash
# 快速启动脚本

cd /Users/ck/Desktop/Project/trustagency/backend

# 使用直接的 pip 安装最关键的包
/Users/ck/Desktop/Project/trustagency/backend/venv/bin/pip install -q python-dotenv fastapi uvicorn sqlalchemy 2>/dev/null

# 启动服务
echo "🚀 启动 FastAPI 服务器..."
/Users/ck/Desktop/Project/trustagency/backend/venv/bin/python -m uvicorn app.main:app --reload --port 8001
