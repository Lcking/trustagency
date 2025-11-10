#!/bin/bash
# 快速重启后端容器

cd /Users/ck/Desktop/Project/trustagency

echo "🔄 重启后端容器..."
docker-compose restart backend

echo "⏳ 等待 15 秒启动..."
sleep 15

echo "🧪 测试 /admin/ 路由..."
curl -s http://localhost:8001/admin/ | head -20

echo ""
echo "✅ 测试完成"
