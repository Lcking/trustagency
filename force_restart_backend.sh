#!/bin/bash
# 完全重启容器（不是仅 reload）

cd /Users/ck/Desktop/Project/trustagency

echo "🛑 停止后端容器..."
docker-compose stop backend

echo "⏳ 等待 2 秒..."
sleep 2

echo "🚀 启动后端容器..."
docker-compose start backend

echo "⏳ 等待 20 秒启动..."
sleep 20

echo "🧪 测试 /admin/ 路由..."
echo "请求: GET http://localhost:8001/admin/"
echo "======================================"
curl -s http://localhost:8001/admin/ | head -20

echo ""
echo "✅ 测试完成"
