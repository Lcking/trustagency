#!/bin/bash
# 完整的后端启动脚本

set -e

cd /Users/ck/Desktop/Project/trustagency/backend

echo "🔧 TrustAgency 后端启动脚本"
echo "================================"

# 步骤 1: 检查并清理旧进程
echo "📋 清理旧的后端进程..."
pkill -f "uvicorn.*8001" 2>/dev/null || echo "❌ 没有找到旧进程"

# 等待几秒钟
sleep 2

# 步骤 2: 激活虚拟环境并安装依赖
echo "📦 确保所有依赖已安装..."
source venv/bin/activate

# 安装关键的缺失包
pip install -q python-slugify text-unidecode 2>/dev/null || true

# 步骤 3: 启动服务器
echo "🚀 启动 FastAPI 后端服务器..."
python -m uvicorn app.main:app --reload --port 8001

echo ""
echo "✅ 服务器已启动！"
echo "📊 访问 API 文档: http://localhost:8001/api/docs"
echo "🔍 访问 ReDoc: http://localhost:8001/api/redoc"
