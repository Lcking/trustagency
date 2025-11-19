#!/bin/bash
# 🎯 部署快速修复命令 - 可直接复制粘贴到服务器

# ==================================================
# 方案A：一条长命令搞定（推荐）
# ==================================================

cd /opt/trustagency && \
docker-compose -f docker-compose.prod.yml down && \
sudo tee /etc/docker/daemon.json > /dev/null <<'DAEMON' && \
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com"
  ]
}
DAEMON
sudo systemctl daemon-reload && \
sudo systemctl restart docker && \
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") && \
cp .env.prod.example .env.prod && \
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env.prod && \
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d && \
sleep 5 && \
docker-compose -f docker-compose.prod.yml ps

# ==================================================
# 方案B：分步执行（推荐用于学习）
# ==================================================

# 1. 停止容器
cd /opt/trustagency
docker-compose -f docker-compose.prod.yml down

# 2. 配置 Docker 国内镜像
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# 3. 生成 SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "生成的 SECRET_KEY: $SECRET_KEY"

# 4. 配置 .env.prod
cp .env.prod.example .env.prod
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env.prod

# 5. 启动容器
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 6. 验证状态
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/health

# ==================================================
# 方案C：使用自动修复脚本
# ==================================================

cd /opt/trustagency
bash fix-deployment.sh

# ==================================================
# 故障排查命令
# ==================================================

# 查看所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看实时日志（所有服务）
docker-compose -f docker-compose.prod.yml logs -f

# 查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 查看 Redis 日志
docker-compose -f docker-compose.prod.yml logs -f redis

# 查看 Celery Worker 日志
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# 测试后端健康检查
curl http://localhost:8001/health

# 测试登录 API
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 查看 Docker 镜像源配置
docker info | grep -A 5 "Registry Mirrors"

# 查看环境变量是否正确加载
docker-compose -f docker-compose.prod.yml exec backend env | grep SECRET_KEY

# ==================================================
# 如果需要重置所有容器和数据
# ==================================================

# 警告：此操作会删除所有容器和卷中的数据！

cd /opt/trustagency
docker-compose -f docker-compose.prod.yml down -v
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# ==================================================
# 快速参考：问题诊断树
# ==================================================

# ❌ 问题：容器无法启动
# → 检查日志：docker-compose logs backend
# → 检查 SECRET_KEY：cat .env.prod | grep SECRET_KEY
# → 检查端口占用：lsof -i :8001

# ❌ 问题：网络超时
# → 配置镜像源：/etc/docker/daemon.json
# → 重启 Docker：sudo systemctl restart docker
# → 预加载镜像：docker pull redis:7-alpine

# ❌ 问题：密码验证失败
# → 检查默认密码：admin/admin123
# → 重新初始化数据库：docker-compose down -v && docker-compose up -d

# ❌ 问题：无法连接数据库
# → 查看 SQLite 文件：docker-compose exec backend ls -lh /app/data/
# → 检查权限：docker-compose exec backend stat /app/data/trustagency.db

# ==================================================
# 验证部署成功
# ==================================================

# ✅ 全部完成的标志：
# 1. docker-compose ps 中所有容器状态为 Up 或 (healthy)
# 2. curl http://localhost:8001/health 返回 {"status": "ok"}
# 3. 后端日志中显示 "✅ 数据库初始化成功"
# 4. 能够访问 http://your-domain.com/admin/
# 5. 能够用 admin/admin123 登录

# ==================================================
# 打印有用的链接
# ==================================================

echo ""
echo "===========================================" 
echo "📚 有用的链接："
echo "==========================================="
echo ""
echo "1. 后台管理系统："
echo "   http://your-domain.com/admin/"
echo ""
echo "2. API 文档："
echo "   http://your-domain.com/api/docs"
echo ""
echo "3. 查看部署指南："
echo "   cat DEPLOYMENT_QUICK_FIX.md"
echo ""
echo "4. 实时日志："
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "==========================================="
