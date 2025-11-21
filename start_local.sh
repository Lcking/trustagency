#!/bin/bash
# 本地开发环境启动脚本 - 清除缓存并启动前端/后端

set -e

PROJECT_DIR="/Users/ck/Desktop/Project/trustagency"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 本地开发环境启动"
echo "================================"
echo ""

# ===== 步骤1: 清除后端缓存 =====
echo "📋 步骤1: 清除后端缓存..."
cd "$BACKEND_DIR"

# 清除Python缓存
echo "   🗑️  清除Python缓存..."
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find . -type f -name '*.pyc' -delete 2>/dev/null || true
find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true

# 清除虚拟环境缓存（如果存在）
if [ -d "venv" ]; then
    echo "   🗑️  清除venv缓存..."
    rm -rf venv/.cache 2>/dev/null || true
fi

echo "   ✅ 后端缓存清除完成"
echo ""

# ===== 步骤2: 清除前端缓存 =====
echo "📋 步骤2: 清除前端缓存..."
cd "$FRONTEND_DIR"

# 清除node缓存
echo "   🗑️  清除Node缓存..."
rm -rf node_modules/.cache 2>/dev/null || true
rm -rf .next 2>/dev/null || true
rm -rf dist 2>/dev/null || true
rm -rf build 2>/dev/null || true

# 清除npm缓存
npm cache clean --force 2>/dev/null || true

echo "   ✅ 前端缓存清除完成"
echo ""

# ===== 步骤3: 生成本地数据库 =====
echo "📋 步骤3: 生成本地SQLite数据库..."
cd "$BACKEND_DIR"

# 检查是否需要生成数据库
if [ -f "trustagency.db" ]; then
    echo "   ⚠️  数据库已存在，是否删除重新生成? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm trustagency.db
        echo "   🗑️  旧数据库已删除"
    else
        echo "   ⏭️  保留现有数据库"
    fi
else
    echo "   📦 数据库不存在，即将生成..."
fi

# 生成数据库
if [ ! -f "trustagency.db" ]; then
    python3 restore_db.py trustagency.db
    echo "   ✅ 本地数据库生成完成"
fi

echo ""

# ===== 步骤4: 启动后端 =====
echo "📋 步骤4: 启动后端服务..."
cd "$BACKEND_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "   🔧 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "   📦 检查/安装依赖..."
pip install -q -r requirements.txt 2>/dev/null || echo "   ⚠️  依赖安装可能有问题，继续..."

echo "   🚀 启动后端服务 (端口 8001)..."
echo ""
echo "================================"
echo "后端日志:"
echo "================================"

# 启动后端（在后台）
export DATABASE_URL="sqlite:///./trustagency.db"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 3

echo ""
echo "================================"
echo "后端启动完成 (PID: $BACKEND_PID)"
echo "================================"
echo ""

# ===== 步骤5: 启动前端 =====
echo "📋 步骤5: 启动前端服务..."
cd "$FRONTEND_DIR"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "   📦 安装前端依赖..."
    npm install --silent
fi

echo "   🚀 启动前端服务 (端口 3000)..."
echo ""
echo "================================"
echo "前端日志:"
echo "================================"

# 启动前端（在后台）
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 3

echo ""
echo "================================"
echo "前端启动完成 (PID: $FRONTEND_PID)"
echo "================================"
echo ""

# ===== 步骤6: 显示访问信息 =====
echo "🎉 服务启动完成！"
echo ""
echo "📱 访问地址:"
echo "   前端UI: http://localhost:3000"
echo "   后端API: http://localhost:8001"
echo "   API文档: http://localhost:8001/docs"
echo ""
echo "🔍 验证数据:"
echo "   平台列表: http://localhost:8001/api/platforms"
echo "   分类列表: http://localhost:8001/api/categories"
echo ""
echo "📝 进程信息:"
echo "   后端进程: $BACKEND_PID"
echo "   前端进程: $FRONTEND_PID"
echo ""
echo "⛔ 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 保持运行
wait $BACKEND_PID $FRONTEND_PID
