#!/bin/bash
# 服务器初始化和数据库部署脚本

set -e

SERVER_IP="106.13.188.99"
SERVER_USER="root"
SERVER_PATH="/root/trustagency"
LOCAL_PATH="/Users/ck/Desktop/Project/trustagency"
DB_FILE="${LOCAL_PATH}/backend/trustagency.db"

echo "🚀 开始部署..."
echo ""

# ===== 第1步：创建服务器目录 =====
echo "📋 步骤1: 在服务器创建必要的目录..."
ssh "${SERVER_USER}@${SERVER_IP}" << 'EOF'
mkdir -p /root/trustagency/backend/data
mkdir -p /root/trustagency/frontend
ls -la /root/trustagency/
EOF
echo "✅ 目录创建完成"
echo ""

# ===== 第2步：验证本地数据库 =====
echo "📋 步骤2: 验证本地数据库..."
if [ ! -f "$DB_FILE" ]; then
    echo "❌ 错误: 数据库文件不存在"
    echo "请先运行: python3 ${LOCAL_PATH}/backend/restore_db.py trustagency.db"
    exit 1
fi

DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo "✅ 数据库文件: $DB_FILE ($DB_SIZE)"
echo ""

# ===== 第3步：复制数据库到服务器 =====
echo "📋 步骤3: 复制数据库到服务器..."
scp "$DB_FILE" "${SERVER_USER}@${SERVER_IP}:/root/trustagency/backend/"
echo "✅ 数据库复制成功"
echo ""

# ===== 第4步：在服务器创建数据卷副本 =====
echo "📋 步骤4: 在服务器创建数据卷目录..."
ssh "${SERVER_USER}@${SERVER_IP}" "cp /root/trustagency/backend/trustagency.db /root/trustagency/backend/data/trustagency.db && ls -lh /root/trustagency/backend/data/"
echo "✅ 数据卷创建成功"
echo ""

# ===== 第5步：重启后端容器 =====
echo "📋 步骤5: 重启后端容器..."
ssh "${SERVER_USER}@${SERVER_IP}" << 'EOF'
cd /root/trustagency
if [ -f "docker-compose.prod.yml" ]; then
    docker-compose -f docker-compose.prod.yml restart backend
    sleep 5
    echo "✅ 容器重启成功"
else
    echo "⚠️  docker-compose.prod.yml 不存在"
    echo "服务器文件列表:"
    ls -la /root/trustagency/
fi
EOF
echo ""

# ===== 第6步：验证 API =====
echo "📋 步骤6: 验证 API 响应..."
sleep 3
RESPONSE=$(curl -s "http://${SERVER_IP}:8001/api/platforms" || echo "无法连接")
echo "API 响应 (前200字): ${RESPONSE:0:200}"
echo ""

echo "🎉 部署完成！"
echo ""
echo "📊 访问地址:"
echo "   前端: http://${SERVER_IP}:3000"
echo "   后端API: http://${SERVER_IP}:8001/api/platforms"
echo ""
