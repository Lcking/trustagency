#!/bin/bash
# ============================================================================
# 完整初始化和部署脚本
# 用途: 在服务器上创建必要的目录，然后上传数据库文件
# ============================================================================

set -e

# 配置
SERVER_IP="106.13.188.99"
SERVER_USER="root"
LOCAL_DB="/Users/ck/Desktop/Project/trustagency/backend/trustagency.db"

echo "================================"
echo "🚀 完整部署流程"
echo "================================"
echo ""

# ===== 阶段1：初始化服务器 =====
echo "📋 [阶段1] 初始化服务器..."
echo ""

ssh "${SERVER_USER}@${SERVER_IP}" << 'EOFSETUP'
#!/bin/bash

echo "   ✅ 连接成功"
echo ""

# 创建目录
echo "   📁 创建目录结构..."
mkdir -p /root/trustagency/backend/data
mkdir -p /root/trustagency/frontend
mkdir -p /root/trustagency/nginx
echo "   ✅ 目录创建完成"

# 检查 Docker
echo ""
echo "   🐳 检查 Docker..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker 已安装"
    docker ps > /dev/null 2>&1 && echo "   ✅ Docker 守护进程运行中" || echo "   ⚠️  Docker 守护进程未运行"
else
    echo "   ⚠️  Docker 未安装"
fi

# 显示目录
echo ""
echo "   📂 最终目录结构:"
tree -L 3 /root/trustagency 2>/dev/null || find /root/trustagency -type d | sed 's|[^/]*/|  |g'

EOFSETUP

echo ""
echo "✅ 服务器初始化完成"
echo ""

# ===== 阶段2：上传数据库 =====
echo "📋 [阶段2] 上传数据库..."
echo ""

if [ ! -f "$LOCAL_DB" ]; then
    echo "❌ 错误: 本地数据库不存在"
    echo "   位置: $LOCAL_DB"
    echo "   请先运行: python3 /Users/ck/Desktop/Project/trustagency/backend/restore_db.py"
    exit 1
fi

DB_SIZE=$(ls -lh "$LOCAL_DB" | awk '{print $5}')
echo "   💾 本地数据库: $LOCAL_DB"
echo "   📊 文件大小: $DB_SIZE"
echo ""

echo "   📤 上传中..."
scp "$LOCAL_DB" "${SERVER_USER}@${SERVER_IP}:/root/trustagency/backend/"
echo ""
echo "✅ 数据库上传完成"
echo ""

# ===== 阶段3：配置数据卷 =====
echo "📋 [阶段3] 配置 Docker 数据卷..."
echo ""

ssh "${SERVER_USER}@${SERVER_IP}" << 'EOFVOLUME'
#!/bin/bash

echo "   📋 复制数据库到数据卷..."
cp /root/trustagency/backend/trustagency.db /root/trustagency/backend/data/trustagency.db
ls -lh /root/trustagency/backend/data/trustagency.db

echo ""
echo "   ✅ 数据卷配置完成"

EOFVOLUME

echo ""
echo "✅ 数据卷配置完成"
echo ""

# ===== 阶段4：重启容器 =====
echo "📋 [阶段4] 重启 Docker 容器..."
echo ""

ssh "${SERVER_USER}@${SERVER_IP}" << 'EOFDOCKER'
#!/bin/bash

cd /root/trustagency

if [ -f "docker-compose.prod.yml" ]; then
    echo "   🔄 重启后端容器..."
    docker-compose -f docker-compose.prod.yml restart backend
    sleep 5
    echo "   ✅ 容器重启完成"
else
    echo "   ⚠️  docker-compose.prod.yml 未找到"
    echo "   📂 当前目录文件列表:"
    ls -la /root/trustagency/ | head -15
fi

EOFDOCKER

echo ""
echo "✅ 容器重启完成"
echo ""

# ===== 阶段5：验证 =====
echo "📋 [阶段5] 验证部署..."
echo ""

echo "   🔗 等待容器启动 (5 秒)..."
sleep 5

echo ""
echo "   🧪 测试 API 响应..."
RESPONSE=$(curl -s "http://${SERVER_IP}:8001/api/platforms" 2>/dev/null | head -c 300)

if [ -z "$RESPONSE" ]; then
    echo "   ⚠️  无法连接到 API (http://${SERVER_IP}:8001/api/platforms)"
else
    echo "   ✅ API 响应:"
    echo "   $RESPONSE"
fi

echo ""
echo "================================"
echo "🎉 部署完成！"
echo "================================"
echo ""
echo "📊 访问地址:"
echo "   后端 API: http://${SERVER_IP}:8001/api/platforms"
echo "   前端 UI: http://${SERVER_IP}:3000"
echo ""
echo "🔍 调试命令:"
echo "   查看日志: ssh root@${SERVER_IP} 'docker logs -f trustagency-backend'"
echo "   查看容器: ssh root@${SERVER_IP} 'docker ps -a'"
echo "   查看数据库: ssh root@${SERVER_IP} 'sqlite3 /root/trustagency/backend/data/trustagency.db \"SELECT COUNT(*) FROM platforms;\"'"
echo ""
