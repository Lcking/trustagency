#!/bin/bash

cd /Users/ck/Desktop/Project/trustagency

echo "🛑 完全停止所有容器..."
docker-compose down -v

echo "⏳ 等待 5 秒..."
sleep 5

echo "🚀 启动所有容器..."
docker-compose up -d

echo "⏳ 等待 30 秒让服务完全启动..."
sleep 30

echo "🧪 测试后端 /admin/ 路由..."
echo "正在请求 http://localhost:8001/admin/"
echo "=========================="
curl -v http://localhost:8001/admin/ 2>&1 | head -40

echo ""
echo "=========================="
echo "✅ 测试完成"
