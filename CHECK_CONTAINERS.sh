#!/bin/bash
# 检查 Docker 容器状态

echo "🐳 Docker 容器状态"
echo "===================="
docker-compose ps

echo ""
echo "🔍 后端容器日志（最后 30 行）"
echo "=============================="
docker-compose logs backend --tail=30

echo ""
echo "✅ 检查完成"
