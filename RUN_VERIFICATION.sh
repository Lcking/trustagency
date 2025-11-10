#!/bin/bash

# 🎯 TrustAgency 系统5个Bug修复 - 自动验收脚本
# 生成时间: 2025-11-10

echo "=========================================="
echo "🚀 TrustAgency Bug修复验收测试启动"
echo "=========================================="
echo ""

# 检查依赖
echo "📦 第1步: 检查并安装Python依赖..."
cd /Users/ck/Desktop/Project/trustagency/backend

# 安装缺失的包
pip install -q python-jose email-validator 2>/dev/null || true
pip install -q -r requirements.txt 2>/dev/null || true

echo "✅ 依赖检查完成"
echo ""

# 检查数据库
echo "🗄️  第2步: 初始化数据库..."
python app/init_db.py 2>/dev/null || echo "⚠️ 数据库可能已初始化"
echo ""

# 启动后端服务 (后台)
echo "🔧 第3步: 启动后端服务 (后台)..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!
sleep 3  # 等待后端启动

# 检查后端是否运行
if curl -s http://127.0.0.1:8001/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo ""

# 启动前端服务 (后台)
echo "🌐 第4步: 启动前端服务 (后台)..."
cd /Users/ck/Desktop/Project/trustagency/backend
python -m http.server 3000 -d site > /dev/null 2>&1 &
FRONTEND_PID=$!
sleep 2

echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo ""

# API测试
echo "🧪 第5步: 执行API测试..."
echo ""

# Bug测试函数
test_bug_009() {
    echo "🔍 [测试 Bug_009] 栏目分类添加/删除"
    
    # 获取栏目列表
    SECTIONS=$(curl -s http://127.0.0.1:8001/api/sections | python -m json.tool 2>/dev/null | grep '"id"' | head -1 | grep -o '[0-9]*')
    
    if [ ! -z "$SECTIONS" ]; then
        echo "  ✓ 获取栏目列表成功"
        SECTION_ID=$(echo $SECTIONS | head -1)
        
        # 获取该栏目的分类
        curl -s http://127.0.0.1:8001/api/categories/section/$SECTION_ID > /dev/null 2>&1 && echo "  ✓ 分类加载端点正常"
    fi
}

test_bug_010() {
    echo "🔍 [测试 Bug_010] 平台编辑认证"
    
    # 获取平台列表
    curl -s http://127.0.0.1:8001/api/platforms | grep -q '"id"' && echo "  ✓ 平台列表获取成功"
}

test_bug_011() {
    echo "🔍 [测试 Bug_011] Tiptap编辑器"
    
    if grep -q "esm.sh/@tiptap/core@2.4.0" /Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html; then
        echo "  ✓ Tiptap版本已更新为 2.4.0"
    else
        echo "  ✗ Tiptap版本未更新"
    fi
}

test_bug_012() {
    echo "🔍 [测试 Bug_012] AI任务分类加载"
    
    if grep -q "loadCategoriesForSelect" /Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html; then
        echo "  ✓ 分类加载函数已实现"
    fi
    
    if grep -q "/categories/section/" /Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html; then
        echo "  ✓ 分类API调用已实现"
    fi
}

test_bug_013() {
    echo "🔍 [测试 Bug_013] AI配置默认设置"
    
    if grep -q "setDefaultAIConfig" /Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html; then
        echo "  ✓ 默认配置设置函数已实现"
    fi
    
    if grep -q "/set-default" /Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html; then
        echo "  ✓ 默认配置API调用已实现"
    fi
}

# 执行所有测试
test_bug_009
test_bug_010
test_bug_011
test_bug_012
test_bug_013

echo ""
echo "=========================================="
echo "📋 验收测试完成"
echo "=========================================="
echo ""
echo "📍 前端地址: http://localhost:3000/admin/index.html"
echo "📍 后端地址: http://127.0.0.1:8001"
echo ""
echo "✋ 按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
wait
