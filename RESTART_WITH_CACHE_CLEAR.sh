#!/bin/bash
# 完整重启脚本 - 清除缓存并重启

cd /Users/ck/Desktop/Project/trustagency

echo "🔧 步骤 1: 停止所有容器..."
docker-compose down

echo "🔧 步骤 2: 清除 Python 字节码缓存..."
find ./backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ./backend -type f -name "*.pyc" -delete 2>/dev/null || true

echo "🔧 步骤 3: 清除 Docker 卷（可选，保留数据库）..."
# docker volume prune -f  # 仅在必要时取消注释

echo "🔧 步骤 4: 重新启动容器..."
docker-compose up -d

echo "⏳ 等待容器启动..."
sleep 15

echo "✅ 容器已启动"
echo ""
echo "🧪 测试 /admin/ 路由..."
curl -s http://localhost:8001/admin/ | head -20

echo ""
echo "✅ 完成！"
