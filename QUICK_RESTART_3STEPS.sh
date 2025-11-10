#!/bin/bash
# 【最简单的3步重启方案】 
# 将此脚本复制到终端并执行

# ============================
# 第1步: 完全重启
# ============================

cd /Users/ck/Desktop/Project/trustagency

# 彻底清理旧容器
docker-compose down -v --remove-orphans

# 删除旧镜像
docker rmi -f $(docker images --filter=dangling=true -q) 2>/dev/null || true

# 等待
sleep 5

# 重建镜像（这次添加了 --reload）
docker-compose build --no-cache backend

# 启动新容器  
docker-compose up -d

# 等待启动完成
sleep 30

# ============================
# 第2步: 验证修复
# ============================

echo ""
echo "【验证1】检查 /admin/ 返回 HTML："
curl -s http://localhost:8001/admin/ | head -5

echo ""
echo "【验证2】检查健康状态："
curl -s http://localhost:8001/api/health

echo ""
echo "【完成】"
echo "✅ 后端地址: http://localhost:8001/admin/"
echo "✅ Nginx地址: http://localhost/admin/"
