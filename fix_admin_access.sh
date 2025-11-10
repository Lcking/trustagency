#!/bin/bash

# 修复 admin 路由问题

echo "========================================="
echo "修复 Admin 访问问题"
echo "========================================="

# 停止容器
echo "1. 停止容器..."
cd /Users/ck/Desktop/Project/trustagency
docker-compose down

# 等待
sleep 2

# 重新启动
echo "2. 重新启动容器..."
docker-compose up -d

# 等待服务启动
sleep 10

# 测试
echo "3. 测试 /admin/ 路由..."
curl -s http://localhost:8001/admin/ | head -20

echo ""
echo "4. 测试 /api/health..."
curl -s http://localhost:8001/api/health

echo ""
echo "========================================="
echo "修复完成！"
echo "访问: http://localhost:8001/admin/"
echo "========================================="
