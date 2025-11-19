#!/bin/bash

# 🔧 内存不足修复脚本 - 自动处理 OOM 问题
# 使用方法: bash fix-memory-error.sh

set -e

echo "════════════════════════════════════════════════════════"
echo "🔧 Docker 内存不足修复"
echo "════════════════════════════════════════════════════════"
echo ""

cd /opt/trustagency

echo "📊 当前系统状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "可用内存:"
free -h | grep "^Mem:"
echo ""
echo "磁盘空间:"
df -h / | tail -1
echo ""
echo "Docker 使用情况:"
docker system df 2>/dev/null | head -4 || echo "Docker 未启动或无法连接"
echo ""

echo "🧹 步骤 1/4: 停止现有容器..."
docker-compose -f docker-compose.prod.yml down || true
echo "✅ 容器已停止"
echo ""

echo "🧹 步骤 2/4: 清理 Docker 资源..."
echo "  • 删除未使用的容器..."
docker container prune -f > /dev/null 2>&1 || true

echo "  • 删除未使用的镜像..."
docker image prune -a -f > /dev/null 2>&1 || true

echo "  • 删除未使用的卷..."
docker volume prune -f > /dev/null 2>&1 || true

echo "  • 删除构建缓存..."
docker builder prune -a -f > /dev/null 2>&1 || true

echo "✅ Docker 资源已清理"
echo ""

echo "📊 清理后的资源使用:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker system df 2>/dev/null | head -4 || echo "Docker 信息"
echo ""

echo "🚀 步骤 3/4: 重新启动容器..."
echo "  这一步可能需要 5-10 分钟，请耐心等待..."
echo ""

docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

echo ""
echo "⏱️  等待容器初始化..."
sleep 10

echo ""
echo "🔍 步骤 4/4: 验证部署..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查容器状态
echo "容器状态:"
docker-compose -f docker-compose.prod.yml ps || echo "无法获取容器状态"
echo ""

# 测试 API
echo "测试后端 API..."
if curl -s http://localhost:8001/health | grep -q "ok"; then
    echo "✅ 后端 API 正常运行"
else
    echo "⚠️  后端 API 可能未就绪，请稍后重试"
    echo ""
    echo "查看日志:"
    echo "docker-compose -f docker-compose.prod.yml logs backend"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ 修复完成！"
echo "════════════════════════════════════════════════════════"
echo ""

echo "📊 最终系统状态:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "可用内存:"
free -h | grep "^Mem:"
echo ""
echo "磁盘空间:"
df -h / | tail -1
echo ""

echo "🎯 后续步骤:"
echo "  1. 验证所有容器状态"
echo "     docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "  2. 测试 API"
echo "     curl http://localhost:8001/health"
echo ""
echo "  3. 查看日志"
echo "     docker-compose -f docker-compose.prod.yml logs backend"
echo ""
echo "  4. 访问后台"
echo "     http://your-domain.com/admin/"
echo "     用户: admin"
echo "     密码: admin123"
echo ""
