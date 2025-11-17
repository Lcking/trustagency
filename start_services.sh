#!/bin/bash

# TrustAgency 快速启动脚本
# 用途: 一键启动后端和前端服务

set -e

PROJECT_ROOT="/Users/ck/Desktop/Project/trustagency"
BACKEND_PORT=8000
FRONTEND_PORT=8001

echo "🚀 TrustAgency 启动脚本"
echo "================================"

# 检查项目目录
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ 项目目录不存在: $PROJECT_ROOT"
    exit 1
fi

# 启动后端
echo -e "\n📦 启动后端服务 (Port $BACKEND_PORT)..."
cd "$PROJECT_ROOT/backend"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > /tmp/trustagency_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端进程 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 验证后端
if ! curl -s http://localhost:$BACKEND_PORT/api/articles?limit=1 > /dev/null 2>&1; then
    echo "❌ 后端启动失败，查看日志:"
    tail -20 /tmp/trustagency_backend.log
    exit 1
fi
echo "✅ 后端服务就绪"

# 启动前端
echo -e "\n🎨 启动前端服务 (Port $FRONTEND_PORT)..."
cd "$PROJECT_ROOT/site"

# 检查前端代理服务器是否存在
if [ ! -f "/tmp/frontend_server.py" ]; then
    echo "⚠️  前端代理服务器不存在，使用默认 HTTP 服务器"
    nohup python3 -m http.server $FRONTEND_PORT > /tmp/trustagency_frontend.log 2>&1 &
else
    nohup python3 /tmp/frontend_server.py > /tmp/trustagency_frontend.log 2>&1 &
fi

FRONTEND_PID=$!
echo "✅ 前端进程 PID: $FRONTEND_PID"

# 等待前端启动
sleep 2

# 验证前端
if ! curl -s -o /dev/null "http://localhost:$FRONTEND_PORT/" 2>&1; then
    echo "❌ 前端启动失败"
    exit 1
fi
echo "✅ 前端服务就绪"

# 显示访问信息
echo -e "\n✅ 所有服务启动成功！"
echo "================================"
echo "🌐 访问地址:"
echo "  首页:     http://localhost:$FRONTEND_PORT/"
echo "  QA 页面:  http://localhost:$FRONTEND_PORT/qa/"
echo "  Wiki:     http://localhost:$FRONTEND_PORT/wiki/"
echo "  文章:     http://localhost:$FRONTEND_PORT/article/?id=6"
echo ""
echo "📡 API 地址:"
echo "  后端 API: http://localhost:$BACKEND_PORT/api/articles"
echo ""
echo "📋 进程信息:"
echo "  后端 PID:  $BACKEND_PID"
echo "  前端 PID:  $FRONTEND_PID"
echo ""
echo "📝 日志文件:"
echo "  后端日志: /tmp/trustagency_backend.log"
echo "  前端日志: /tmp/trustagency_frontend.log"
echo ""
echo "❌ 停止服务:"
echo "  kill $BACKEND_PID  # 停止后端"
echo "  kill $FRONTEND_PID # 停止前端"
