#!/bin/bash

# 终极修复脚本 - 完全重新构建和测试

set -e

cd /Users/ck/Desktop/Project/trustagency

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Admin 访问问题 - 终极修复脚本                     ║"
echo "║     会完全重新构建容器并测试所有功能                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "[1/6] 停止并删除所有容器和镜像..."
docker-compose down
docker rmi trustagency-backend trustagency-frontend 2>/dev/null || true
echo "✓ 完成"
echo ""

sleep 2

echo "[2/6] 从头构建所有镜像..."
docker-compose build --no-cache
echo "✓ 完成"
echo ""

sleep 2

echo "[3/6] 启动所有容器..."
docker-compose up -d
echo "✓ 完成"
echo ""

echo "[4/6] 等待容器启动（20 秒）..."
sleep 20
echo "✓ 完成"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  容器状态检查                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
docker-compose ps
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   功能测试                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "[5/6] 测试后端 /admin/ 路由..."
echo "URL: http://localhost:8001/admin/"
HTTP_CODE=$(curl -s -o /tmp/admin_test.html -w "%{http_code}" http://localhost:8001/admin/)
echo "HTTP 状态码: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 成功！返回 200 OK"
    echo "前 10 行内容:"
    head -10 /tmp/admin_test.html
    echo ""
    ADMIN_WORKS="YES"
else
    echo "❌ 失败！返回 $HTTP_CODE"
    echo "返回内容:"
    cat /tmp/admin_test.html
    echo ""
    ADMIN_WORKS="NO"
fi

echo ""
echo "[6/6] 测试登录 API..."
echo "POST http://localhost:8001/api/admin/login"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "返回:"
echo "$LOGIN_RESPONSE" | head -c 200
echo ""
echo ""

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ 成功！返回有效的 token"
    LOGIN_WORKS="YES"
else
    echo "❌ 失败！"
    LOGIN_WORKS="NO"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   修复结果总结                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$ADMIN_WORKS" = "YES" ]; then
    echo "✅ /admin/ 路由: 成功 (200 OK)"
else
    echo "❌ /admin/ 路由: 失败"
fi

if [ "$LOGIN_WORKS" = "YES" ]; then
    echo "✅ 登录 API: 成功 (返回 token)"
else
    echo "❌ 登录 API: 失败"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   后续操作                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$ADMIN_WORKS" = "YES" ] && [ "$LOGIN_WORKS" = "YES" ]; then
    echo "✅ 所有测试通过！问题已解决。"
    echo ""
    echo "现在可以访问:"
    echo "  • 后端: http://localhost:8001/admin/"
    echo "  • 前端: http://localhost/admin/"
    echo ""
    echo "登录信息:"
    echo "  • 用户名: admin"
    echo "  • 密码: admin123"
    echo ""
    exit 0
else
    echo "⚠️  某些测试失败，请查看上面的错误信息"
    echo ""
    echo "诊断命令:"
    echo "  查看后端日志: docker-compose logs backend | tail -50"
    echo "  查看前端日志: docker-compose logs frontend | tail -50"
    echo "  检查文件: docker-compose exec backend ls -la /app/../../site/admin/"
    echo ""
    exit 1
fi
