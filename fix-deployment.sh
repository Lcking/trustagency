#!/bin/bash

# 🔧 TrustAgency 部署快速修复脚本
# 使用方法：
# 1. 上传此脚本到服务器：scp fix-deployment.sh root@your-server:/opt/trustagency/
# 2. 执行：bash /opt/trustagency/fix-deployment.sh
# 3. 按照提示输入 SECRET_KEY（或留空让脚本自动生成）

set -e

echo "=========================================="
echo "🔧 TrustAgency 部署快速修复"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：docker-compose.prod.yml 不存在"
    echo "   请在项目根目录运行此脚本"
    exit 1
fi

# 第1步：生成或获取 SECRET_KEY
echo "📝 步骤 1/5：生成 SECRET_KEY..."
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
fi
echo "✅ SECRET_KEY: $SECRET_KEY"
echo ""

# 第2步：配置 .env.prod
echo "📝 步骤 2/5：配置 .env.prod..."
if [ -f ".env.prod" ]; then
    echo "   ℹ️  .env.prod 已存在，进行更新..."
    cp .env.prod .env.prod.backup
else
    echo "   ℹ️  创建新的 .env.prod..."
    cp .env.prod.example .env.prod
fi

# 更新 SECRET_KEY（兼容 Linux 和 macOS）
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env.prod
else
    # Linux
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env.prod
fi

echo "✅ .env.prod 已配置"
echo ""

# 第3步：配置 Docker 镜像源
echo "📝 步骤 3/5：配置 Docker 国内镜像源..."
if sudo test -w /etc/docker/daemon.json 2>/dev/null || [ "$EUID" -eq 0 ]; then
    sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com",
    "https://docker.ycjszz.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    echo "✅ Docker 镜像源已配置并重启"
else
    echo "⚠️  跳过 Docker 镜像源配置（需要 sudo 权限）"
    echo "   请手动执行："
    echo "   sudo tee /etc/docker/daemon.json << 'EOF'"
    cat <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com"
  ]
}
EOF
    echo "   然后运行：sudo systemctl daemon-reload && sudo systemctl restart docker"
fi
echo ""

# 第4步：停止并重启容器
echo "📝 步骤 4/5：停止并重启容器..."
echo "   ℹ️  停止现有容器..."
docker-compose -f docker-compose.prod.yml down || true

sleep 2

echo "   ℹ️  启动新容器..."
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

echo "✅ 容器已启动"
echo ""

# 第5步：验证部署
echo "📝 步骤 5/5：验证部署状态..."
sleep 5

echo "   容器状态："
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "✅ 部署修复完成！"
echo "=========================================="
echo ""

# 验证后端健康
echo "🔍 验证后端服务..."
if curl -s http://localhost:8001/health | grep -q "ok"; then
    echo "✅ 后端服务正常运行"
else
    echo "⚠️  后端服务可能未就绪，请稍候后再试"
    echo "   查看日志：docker-compose -f docker-compose.prod.yml logs backend"
fi

echo ""
echo "📋 后续步骤："
echo ""
echo "1. 检查实时日志（等待所有服务就绪）："
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "2. 访问后台管理系统："
echo "   http://your-domain.com/admin/"
echo "   用户名: admin"
echo "   默认密码: admin123"
echo "   ⚠️  立即修改默认密码！"
echo ""
echo "3. 如果有问题，查看详细日志："
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
echo ""
echo "祝部署顺利！🚀"
