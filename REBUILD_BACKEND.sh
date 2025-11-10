#!/bin/bash
# 重建后端镜像并重启

cd /Users/ck/Desktop/Project/trustagency

echo "🔨 重新构建后端镜像..."
docker-compose build --no-cache backend

echo "🚀 启动容器..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 20

echo "🧪 测试 API..."
echo ""
echo "1. 测试健康检查:"
curl -s http://localhost:8001/api/health

echo ""
echo "2. 测试 /admin/ 路由:"
curl -s http://localhost:8001/admin/ | head -20

echo ""
echo "✅ 完成"
