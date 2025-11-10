#!/bin/bash

# 环境设置脚本
# 用于修复虚拟环境和依赖安装问题

set -e

echo "🔧 开始修复 Backend 环境..."
cd /Users/ck/Desktop/Project/trustagency/backend

# 步骤 1: 检查虚拟环境
if [ -d "venv" ]; then
    echo "✅ 虚拟环境已存在"
else
    echo "🚀 创建新的虚拟环境..."
    python3 -m venv venv
fi

# 步骤 2: 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 步骤 3: 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip setuptools wheel

# 步骤 4: 安装依赖
echo "📥 安装项目依赖..."
pip install -r requirements.txt

# 步骤 5: 验证关键包
echo "✨ 验证安装..."
python -c "import fastapi; import uvicorn; print('✅ FastAPI 和 Uvicorn 已就绪')"

echo ""
echo "================================"
echo "🎉 环境设置完成！"
echo "================================"
echo ""
echo "现在可以运行:"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --reload"
echo ""
