#!/bin/bash
# 检查服务器现有项目结构

SERVER_IP="106.13.188.99"
SERVER_USER="root"

echo "🔍 检查服务器文件结构..."
echo ""

ssh "${SERVER_USER}@${SERVER_IP}" << 'EOFCHECK'
echo "=== /root 目录 ==="
ls -la /root/ | grep -E "^d|^-"

echo ""
echo "=== /root/trustagency* (如果存在) ==="
ls -la /root/ | grep trustagency || echo "未找到 trustagency 目录"

echo ""
echo "=== /app 目录 (Docker 卷位置) ==="
ls -la /app/ 2>/dev/null | head -20 || echo "/app 不存在或无权限"

echo ""
echo "=== Docker 容器列表 ==="
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" 2>/dev/null | head -10 || echo "Docker 不可用"

echo ""
echo "=== Docker 卷列表 ==="
docker volume ls 2>/dev/null | head -20 || echo "无法列出卷"

echo ""
echo "=== 查找 trustagency.db ==="
find /root -name "trustagency.db" 2>/dev/null || echo "未找到数据库文件"

echo ""
echo "=== 查找 docker-compose*.yml ==="
find /root -name "docker-compose*.yml" 2>/dev/null || echo "未找到 docker-compose 文件"

EOFCHECK

echo ""
echo "✅ 检查完成"
