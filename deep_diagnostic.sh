#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Admin 路由深度诊断脚本                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/ck/Desktop/Project/trustagency

echo "[1/6] 显示当前容器状态..."
docker-compose ps
echo ""

echo "[2/6] 重建后端镜像（应用新的 main.py）..."
docker-compose build backend
echo ""

echo "[3/6] 重启容器..."
docker-compose down
sleep 2
docker-compose up -d
echo "等待容器启动... 15 秒"
sleep 15
echo ""

echo "[4/6] 检查容器状态..."
docker-compose ps
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   API 端点测试                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "✓ 测试 1: 后端健康检查"
echo "GET http://localhost:8001/api/health"
curl -s http://localhost:8001/api/health | head -3
echo ""
echo ""

echo "✓ 测试 2: 后端 Admin 路由（应返回 HTML）"
echo "GET http://localhost:8001/admin/"
HTTP_CODE=$(curl -s -o /tmp/admin_response.html -w "%{http_code}" http://localhost:8001/admin/)
echo "HTTP 状态码: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 成功！返回 200 OK"
    head -5 /tmp/admin_response.html
    echo "..."
else
    echo "✗ 失败！"
    cat /tmp/admin_response.html | head -20
fi
echo ""

echo "✓ 测试 3: 登录 API（测试 CORS）"
echo "POST http://localhost:8001/api/admin/login"
curl -s -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | head -10
echo ""
echo ""

echo "✓ 测试 4: 前端静态页面"
echo "GET http://localhost/admin/"
HTTP_CODE=$(curl -s -o /tmp/nginx_admin.html -w "%{http_code}" http://localhost/admin/)
echo "HTTP 状态码: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 成功！返回 200 OK"
    head -5 /tmp/nginx_admin.html
else
    echo "✗ 失败！"
    cat /tmp/nginx_admin.html | head -10
fi
echo ""

echo "✓ 测试 5: 后端日志检查"
echo "查看后端容器最后 20 行日志..."
docker-compose logs backend | tail -20
echo ""

echo "✓ 测试 6: 前端日志检查"
echo "查看前端容器最后 10 行日志..."
docker-compose logs frontend | tail -10
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   诊断完成                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "下一步操作:"
echo "1. 访问 http://localhost:8001/admin/ (从后端访问)"
echo "2. 访问 http://localhost/admin/ (从前端访问)"
echo "3. 尝试登录 (admin / admin123)"
echo "4. 如果仍有问题，查看浏览器开发者工具的网络标签"
echo ""
