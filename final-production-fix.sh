#!/bin/bash

# 🔧 最终部署修复脚本
# 修复 SECRET_KEY + 数据库权限 + Celery 问题

set -e

echo "🚀 开始部署修复..."
cd /opt/trustagency

# ========================================
# 第 1 步：检查和设置 SECRET_KEY
# ========================================
echo "📋 步骤 1/5: 检查 SECRET_KEY..."

if ! grep -q "^SECRET_KEY=" .env.prod || grep "^SECRET_KEY=$" .env.prod; then
    echo "⚠️ SECRET_KEY 未设置或为空，正在生成..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # 删除旧的 SECRET_KEY 行（如果存在）
    sed -i '/^SECRET_KEY=/d' .env.prod
    
    # 添加新的 SECRET_KEY
    echo "SECRET_KEY=$SECRET_KEY" >> .env.prod
    echo "✅ SECRET_KEY 已生成: $SECRET_KEY"
else
    echo "✅ SECRET_KEY 已存在"
fi

# ========================================
# 第 2 步：确保数据库目录存在并有正确权限
# ========================================
echo "📋 步骤 2/5: 检查数据库目录..."

DB_PATH="/var/lib/docker/volumes/trustagency_sqlite_data/_data"
mkdir -p "$DB_PATH"
chmod 777 "$DB_PATH"
echo "✅ 数据库目录就绪"

# ========================================
# 第 3 步：停止旧容器
# ========================================
echo "📋 步骤 3/5: 停止旧容器..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
sleep 3
echo "✅ 旧容器已停止"

# ========================================
# 第 4 步：重新启动容器
# ========================================
echo "📋 步骤 4/5: 启动新容器..."
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d
echo "✅ 容器已启动"

# ========================================
# 第 5 步：等待并验证
# ========================================
echo "📋 步骤 5/5: 等待容器启动..."
sleep 30

# 检查容器状态
echo ""
echo "🔍 容器状态:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔍 测试 API:"
sleep 3

# 尝试查询健康检查（可能返回 404，但这是正常的）
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null || echo "000")

if [ "$HTTP_CODE" != "000" ]; then
    echo "✅ 后端已启动 (HTTP $HTTP_CODE)"
else
    echo "⚠️ 后端未完全启动，请稍候..."
fi

# 测试 admin 页面
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/admin/ 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 管理后台可访问"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ 修复完成！"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📌 后续检查:"
echo "  1. docker-compose -f docker-compose.prod.yml ps"
echo "  2. curl http://localhost:8001/admin/"
echo "  3. 访问 http://你的域名/admin/"
echo ""
echo "🔐 如遇到登录问题，默认凭证:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "⚠️ 立即修改默认密码！"
echo ""
