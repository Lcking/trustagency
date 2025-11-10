#!/bin/bash

echo "========================================"
echo "Admin 访问问题诊断和修复"
echo "========================================"
echo ""

echo "1. 检查 site/admin/index.html 文件..."
if [ -f "./site/admin/index.html" ]; then
    echo "   ✓ 文件存在"
    echo "   大小: $(wc -c < ./site/admin/index.html) 字节"
else
    echo "   ✗ 文件不存在！"
    exit 1
fi

echo ""
echo "2. 检查 Docker 容器状态..."
echo ""
docker-compose ps
echo ""

echo "3. 重启容器应用新配置..."
docker-compose restart backend frontend
echo "   等待服务启动..."
sleep 8

echo ""
echo "4. 测试后端 /admin/ 路由..."
echo ""
echo "   测试 http://localhost:8001/admin/"
curl -s -I http://localhost:8001/admin/ | head -5
echo ""

echo "5. 获取 admin 页面前 20 行..."
echo ""
curl -s http://localhost:8001/admin/ | head -20
echo ""

echo "6. 检查 /api/health..."
curl -s http://localhost:8001/api/health
echo ""
echo ""

echo "========================================"
echo "修复完成！"
echo "现在访问: http://localhost:8001/admin/"
echo "或访问: http://localhost/admin/"
echo "========================================"
