#!/bin/bash
# 快速启动后端脚本

echo "🚀 启动TrustAgency后端..."
echo ""

cd /Users/ck/Desktop/Project/trustagency/backend

# 检查虚拟环境
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ 虚拟环境不存在"
    exit 1
fi

# 清理旧进程
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 1

# 激活虚拟环境并启动服务
source venv/bin/activate
python -m uvicorn app.main:app --port 8001 --reload

# 按 Ctrl+C 停止服务
