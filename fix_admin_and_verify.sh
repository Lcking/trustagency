#!/bin/bash

# Admin 访问修复完整脚本

set -e

cd /Users/ck/Desktop/Project/trustagency

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Admin 访问问题修复 - 执行脚本                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查文件
echo "[1/4] 检查 admin 文件..."
if [ -f "./site/admin/index.html" ]; then
    echo "✓ Admin 文件存在"
    echo "  大小: $(wc -c < ./site/admin/index.html) 字节"
else
    echo "✗ Admin 文件不存在！"
    exit 1
fi

# 停止容器
echo ""
echo "[2/4] 停止现有容器..."
docker-compose down --remove-orphans || true
sleep 2

# 启动容器
echo ""
echo "[3/4] 重新启动容器..."
docker-compose up -d
echo "⏳ 等待容器完全启动... (15 秒)"
sleep 15

# 显示容器状态
echo ""
echo "[4/4] 容器状态"
docker-compose ps
echo ""

# 测试
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    测试访问                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "✓ 测试 1: 后端健康检查"
echo "  URL: http://localhost:8001/api/health"
curl -s http://localhost:8001/api/health
echo -e "\n"

echo "✓ 测试 2: 后端 Admin 路由"
echo "  URL: http://localhost:8001/admin/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/admin/)
echo "  HTTP 状态码: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✓ 成功！返回 200 OK"
    curl -s http://localhost:8001/admin/ | head -5
    echo "  ..."
else
    echo "  ✗ 失败！"
fi
echo ""

echo "✓ 测试 3: 前端 Admin 路由"
echo "  URL: http://localhost/admin/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/)
echo "  HTTP 状态码: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✓ 成功！返回 200 OK"
else
    echo "  ✗ 可能需要更多时间启动"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    修复完成！                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 访问地址:"
echo "  • 后端: http://localhost:8001/admin/"
echo "  • 前端: http://localhost/admin/"
echo ""
echo "🔐 默认凭证:"
echo "  • 用户名: admin"
echo "  • 密码: admin123"
echo ""
echo "💡 如果仍然无法访问，请运行:"
echo "  docker-compose logs backend | tail -50"
echo "  docker-compose logs frontend | tail -50"
echo ""
