#!/bin/bash

# ========================================
# TrustAgency 生产环境部署脚本（更新版本）
# ========================================
# 用于在生产服务器上部署 TrustAgency
# 使用方法: ./deploy-prod.sh

set -e

echo "🚀 TrustAgency 生产部署脚本"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== 配置 ====================
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
ENV_FILE="$BACKEND_DIR/.env.prod"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

# ==================== 辅助函数 ====================
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ==================== 预检查 ====================
echo "1️⃣  进行部署前检查..."
echo "---------"

# 检查 .env.prod 文件
if [ ! -f "$ENV_FILE" ]; then
    log_error ".env.prod 文件不存在！请复制 .env.prod.example 并填入生产值。"
fi
log_success ".env.prod 文件存在"

# 检查 docker-compose.prod.yml 文件
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    log_error "docker-compose.prod.yml 文件不存在！"
fi
log_success "docker-compose.prod.yml 文件存在"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker 未安装！请先安装 Docker。"
fi
log_success "Docker 已安装"

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose 未安装！请先安装 docker-compose。"
fi
log_success "docker-compose 已安装"

# ==================== 验证配置 ====================
echo ""
echo "2️⃣  验证 Docker Compose 配置..."
echo "---------"

if ! docker-compose -f $DOCKER_COMPOSE_FILE config > /dev/null 2>&1; then
    log_error "docker-compose.prod.yml 配置有误！"
fi
log_success "Docker Compose 配置有效"

# ==================== 检查敏感值 ====================
echo ""
echo "3️⃣  检查敏感配置..."
echo "---------"

# 检查 DB_PASSWORD 是否已设置
if ! grep -q "^DB_PASSWORD=" "$ENV_FILE"; then
    log_error ".env.prod 中缺少 DB_PASSWORD！"
fi
log_success "DB_PASSWORD 已设置"

# 检查 SECRET_KEY 是否已设置
if ! grep -q "^SECRET_KEY=" "$ENV_FILE"; then
    log_error ".env.prod 中缺少 SECRET_KEY！"
fi
log_success "SECRET_KEY 已设置"

# 确认用户继续
echo ""
echo "⚠️  即将在生产环境启动以下服务："
docker-compose -f $DOCKER_COMPOSE_FILE config --services
echo ""
read -p "确认部署？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warning "用户取消部署"
    exit 1
fi

# ==================== 停止现有服务 ====================
echo ""
echo "4️⃣  停止现有服务（如果运行中）..."
echo "---------"

if [ "$(docker-compose -f $DOCKER_COMPOSE_FILE ps -q | wc -l)" -gt 0 ]; then
    log_info "发现运行中的容器，正在停止..."
    docker-compose -f $DOCKER_COMPOSE_FILE down
    log_success "现有服务已停止"
else
    log_info "没有运行中的服务"
fi

# ==================== 构建镜像 ====================
echo ""
echo "5️⃣  构建 Docker 镜像..."
echo "---------"

log_info "构建后端镜像..."
if docker-compose -f $DOCKER_COMPOSE_FILE build backend; then
    log_success "后端镜像构建成功"
else
    log_error "后端镜像构建失败！"
fi

# ==================== 启动服务 ====================
echo ""
echo "6️⃣  启动服务..."
echo "---------"

log_info "启动所有服务..."
if docker-compose -f $DOCKER_COMPOSE_FILE up -d; then
    log_success "服务启动成功"
else
    log_error "服务启动失败！"
fi

# ==================== 等待服务就绪 ====================
echo ""
echo "7️⃣  等待服务就绪..."
echo "---------"

log_info "等待数据库服务就绪（最多 60 秒）..."
for i in {1..30}; do
    if docker-compose -f $DOCKER_COMPOSE_FILE exec -T db pg_isready -U trustagency > /dev/null 2>&1; then
        log_success "数据库已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "数据库启动超时！"
    fi
    echo -n "."
    sleep 2
done

log_info "等待后端服务就绪（最多 60 秒）..."
for i in {1..30}; do
    if docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend curl -f http://localhost:8001/admin/ > /dev/null 2>&1; then
        log_success "后端已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        log_warning "后端启动可能超时，请检查日志"
        break
    fi
    echo -n "."
    sleep 2
done

# ==================== 数据库迁移 ====================
echo ""
echo "8️⃣  运行数据库迁移..."
echo "---------"

# 如果使用 Alembic，运行迁移
if [ -d "$BACKEND_DIR/migrations" ]; then
    log_info "检测到 Alembic 迁移目录，运行迁移..."
    if docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend alembic upgrade head; then
        log_success "数据库迁移完成"
    else
        log_error "数据库迁移失败！"
    fi
else
    log_info "未找到迁移脚本，跳过"
fi

# ==================== 健康检查 ====================
echo ""
echo "9️⃣  执行健康检查..."
echo "---------"

log_info "检查容器状态..."
docker-compose -f $DOCKER_COMPOSE_FILE ps

echo ""
echo "检查服务健康状态..."
if docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend curl -f http://localhost:8001/admin/ > /dev/null 2>&1; then
    log_success "后端服务健康"
else
    log_warning "无法访问后端服务，请检查日志"
fi

# ==================== 部署完成 ====================
echo ""
echo "================================"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "================================"
echo ""
echo "📊 服务信息："
echo "  • 后端: http://localhost:8001"
echo "  • 管理后台: http://localhost:8001/admin/"
echo ""
echo "📝 查看日志："
echo "  • 后端日志: docker-compose -f $DOCKER_COMPOSE_FILE logs -f backend"
echo "  • 所有日志: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo ""
echo "🛑 停止服务："
echo "  docker-compose -f $DOCKER_COMPOSE_FILE down"
echo ""
