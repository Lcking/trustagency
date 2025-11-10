#!/bin/bash
# 最终测试脚本 - 应用所有修复

cd /Users/ck/Desktop/Project/trustagency

echo "📦 完整重启（应用卷挂载修复）"
echo "================================"

echo ""
echo "1️⃣  停止容器..."
docker-compose down

echo ""
echo "2️⃣  启动容器（新的卷挂载生效）..."
docker-compose up -d

echo ""
echo "3️⃣  等待 20 秒..."
sleep 20

echo ""
echo "4️⃣  测试 /admin/ 路由..."
echo "请求: GET http://localhost:8001/admin/"
echo "========================================"
curl -s http://localhost:8001/admin/ | head -20

echo ""
echo "✅ 完成"
