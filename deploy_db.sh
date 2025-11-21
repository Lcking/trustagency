#!/bin/bash
# 数据库部署脚本 - 恢复到9a98d02提交时的完整状态
# 用法: bash deploy_db.sh

set -e

SERVER_IP="106.13.188.99"
SERVER_USER="root"
SERVER_PATH="/root/trustagency"
LOCAL_PATH="/Users/ck/Desktop/Project/trustagency"
DB_FILE="${LOCAL_PATH}/backend/trustagency.db"

echo "🚀 开始部署数据库到生产服务器..."
echo "📍 服务器: ${SERVER_IP}"
echo "👤 用户: ${SERVER_USER}"
echo ""

# 步骤1: 验证本地数据库存在
echo "📋 步骤1: 检查本地数据库..."
if [ ! -f "$DB_FILE" ]; then
    echo "❌ 错误: 数据库文件不存在: $DB_FILE"
    echo "请先运行: python3 ${LOCAL_PATH}/backend/restore_db.py"
    exit 1
fi

DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo "✅ 数据库文件找到 (大小: $DB_SIZE)"
echo ""

# 步骤2: 验证数据库内容
echo "📋 步骤2: 验证数据库内容..."
PLATFORM_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM platforms")
CATEGORY_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM categories")
ADMIN_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM admin_users")

echo "   ✅ 平台数: $PLATFORM_COUNT"
echo "   ✅ 分类数: $CATEGORY_COUNT"
echo "   ✅ 管理员数: $ADMIN_COUNT"

if [ "$PLATFORM_COUNT" != "4" ] || [ "$CATEGORY_COUNT" != "20" ]; then
    echo "❌ 错误: 数据库数据不完整"
    exit 1
fi
echo ""

# 步骤3: 复制数据库到服务器
echo "📋 步骤3: 复制数据库到服务器..."
echo "命令: scp $DB_FILE ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/backend/"
scp "$DB_FILE" "${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/backend/" || {
    echo "❌ scp 失败，请检查:"
    echo "   1. 服务器是否在线 (ping ${SERVER_IP})"
    echo "   2. SSH 密钥配置是否正确"
    echo "   3. 用户是否有权限"
    exit 1
}
echo "✅ 数据库复制成功"
echo ""

# 步骤4: 在服务器上创建数据目录
echo "📋 步骤4: 在服务器上创建数据目录..."
ssh "${SERVER_USER}@${SERVER_IP}" "mkdir -p ${SERVER_PATH}/backend/data && cp ${SERVER_PATH}/backend/trustagency.db ${SERVER_PATH}/backend/data/"
echo "✅ 数据目录创建成功"
echo ""

# 步骤5: 重启后端容器
echo "📋 步骤5: 重启后端容器..."
ssh "${SERVER_USER}@${SERVER_IP}" "cd ${SERVER_PATH} && docker-compose -f docker-compose.prod.yml restart backend"
echo "✅ 容器重启成功"
echo ""

# 步骤6: 等待容器启动
echo "📋 步骤6: 等待容器启动..."
sleep 5
echo "✅ 等待完成"
echo ""

# 步骤7: 验证API
echo "📋 步骤7: 验证API响应..."
RESPONSE=$(curl -s "http://${SERVER_IP}:8001/api/platforms" | head -c 100)
if echo "$RESPONSE" | grep -q "AlphaLeverage"; then
    echo "✅ API 响应正常"
else
    echo "⚠️  API 响应: $RESPONSE"
fi
echo ""

echo "🎉 部署完成！"
echo "📊 现在可以访问:"
echo "   前端: http://${SERVER_IP}:3000"
echo "   后端API: http://${SERVER_IP}:8001/api/platforms"
echo ""
