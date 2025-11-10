#!/bin/bash
# 启动后端服务脚本

echo "🚀 TrustAgency 后端启动脚本"
echo "================================"

# 进入后端目录
cd /Users/ck/Desktop/Project/trustagency/backend || exit 1

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在：venv"
    echo "请先运行: python -m venv venv"
    exit 1
fi

echo "✅ 虚拟环境找到"

# 激活虚拟环境
source venv/bin/activate

# 检查uvicorn
if ! command -v uvicorn &> /dev/null; then
    echo "⚠️  uvicorn 未安装，正在安装..."
    pip install uvicorn fastapi
fi

echo "✅ 依赖检查完成"
echo ""
echo "🎯 启动后端服务..."
echo "   URL: http://localhost:8001/admin/"
echo "   用户: admin"
echo "   密码: newpassword123"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"

# 启动uvicorn
uvicorn app.main:app --port 8001 --reload --log-level info
