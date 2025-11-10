#!/bin/bash

# TrustAgency Backend 快速启动脚本
# 使用方法: ./start_backend.sh

set -e

PROJECT_ROOT="/Users/ck/Desktop/Project/trustagency"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/venv"
PID_FILE="/tmp/backend.pid"
LOG_FILE="/tmp/backend.log"
PORT=8001
HOST="127.0.0.1"

echo "🚀 启动 TrustAgency 后端服务..."

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ 虚拟环境不存在: $VENV_DIR"
    exit 1
fi

# 检查旧进程
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "⏹️  停止旧进程 (PID: $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
fi

# 初始化数据库（如果需要）
if [ ! -f "$BACKEND_DIR/app.db" ]; then
    echo "📦 初始化数据库..."
    cd "$BACKEND_DIR"
    PYTHONPATH="$BACKEND_DIR" "$VENV_DIR/bin/python" -c "
from app.database import engine, Base
from app.models import AdminUser, Platform, Article, AIGenerationTask
Base.metadata.create_all(bind=engine)
print('✅ 数据库已创建')
"
fi

# 启动后端
echo "📌 启动服务器于 http://$HOST:$PORT"
cd "$BACKEND_DIR"
nohup PYTHONPATH="$BACKEND_DIR" "$VENV_DIR/bin/python" -m uvicorn app.main:app --port $PORT --host $HOST > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

# 等待启动
sleep 2

# 检查是否启动成功
if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
    echo "✅ 后端已启动 (PID: $(cat $PID_FILE))"
    echo "📊 日志文件: $LOG_FILE"
    echo "🔗 API文档: http://$HOST:$PORT/api/docs"
    echo "📈 健康检查: http://$HOST:$PORT/api/health"
    echo "📊 仪表板: http://$HOST:$PORT/api/admin/stats"
else
    echo "❌ 启动失败，查看日志:"
    tail -20 "$LOG_FILE"
    exit 1
fi
