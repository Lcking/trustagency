#!/bin/bash
# 最终完整重启脚本 - 重建镜像并启动

cd /Users/ck/Desktop/Project/trustagency

echo "=========================================="
echo "  TrustAgency 完整重启和修复脚本"
echo "=========================================="
echo ""

echo "📦 步骤 1: 完全清理..."
echo "  - 停止容器"
echo "  - 移除容器"
echo "  - 移除未使用的镜像"
docker-compose down -v
docker rmi -f trustagency-backend-latest 2>/dev/null || true
echo "  ✓ 完成"
echo ""

echo "⏳ 等待 5 秒..."
sleep 5

echo "🔨 步骤 2: 重建后端镜像..."
docker-compose build --no-cache backend
if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi
echo "  ✓ 完成"
echo ""

echo "🚀 步骤 3: 启动所有容器..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ 容器启动失败"
    exit 1
fi
echo "  ✓ 完成"
echo ""

echo "⏳ 步骤 4: 等待服务完全启动..."
echo "  - 等待后端启动 (30 秒)..."
sleep 30
echo "  ✓ 启动完成"
echo ""

echo "✅ 步骤 5: 验证修复..."
echo ""
echo "测试 1: 检查后端健康状态"
echo "  GET http://localhost:8001/api/health"
curl -s http://localhost:8001/api/health
echo ""
echo ""

echo "测试 2: 检查 /admin/ 路由"
echo "  GET http://localhost:8001/admin/"
ADMIN_RESPONSE=$(curl -s http://localhost:8001/admin/)
echo "$ADMIN_RESPONSE" | head -10
echo ""

if echo "$ADMIN_RESPONSE" | grep -q "<!DOCTYPE\|<html"; then
    echo "✅ 成功! /admin/ 返回了 HTML 内容"
elif echo "$ADMIN_RESPONSE" | grep -q "Not Found"; then
    echo "❌ 仍然返回 404 错误"
    echo "   可能的原因："
    echo "   1. StaticFiles 的路径不正确"
    echo "   2. 文件系统同步问题"
    exit 1
else
    echo "⚠️  响应内容无法判断:"
    echo "$ADMIN_RESPONSE"
    exit 1
fi

echo ""
echo "测试 3: 检查 Nginx (http://localhost/admin/)"
curl -s -I http://localhost/admin/ 2>&1 | head -5
echo ""

echo "=========================================="
echo "✅ 所有测试完成"
echo "=========================================="
echo ""
echo "📊 访问地址:"
echo "  - 后端 API: http://localhost:8001"
echo "  - API 文档: http://localhost:8001/api/docs"
echo "  - 管理后台: http://localhost/admin/"
echo "  - 直接访问: http://localhost:8001/admin/"
echo ""
echo "💡 提示:"
echo "  - 容器已启用文件监听 (--reload)"
echo "  - 修改代码后 Uvicorn 会自动重新加载"
echo "  - 查看日志: docker-compose logs -f backend"
echo ""
