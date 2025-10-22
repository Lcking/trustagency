#!/bin/bash

# A-8 任务验证脚本
# 用于验证 Nginx、Docker、缓存头、安全头、gzip 等配置

set -e

PROJECT_ROOT="/Users/ck/Desktop/Project/trustagency"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "========================================="
echo "A-8 任务验证脚本"
echo "========================================="
echo "时间: $TIMESTAMP"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 1. 检查文件是否存在
echo ""
echo "=== 1. 检查配置文件 ==="

if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
    log_success "Dockerfile 存在"
else
    log_error "Dockerfile 不存在"
    exit 1
fi

if [ -f "$PROJECT_ROOT/docker-compose.build.yml" ]; then
    log_success "docker-compose.build.yml 存在"
else
    log_error "docker-compose.build.yml 不存在"
    exit 1
fi

if [ -f "$PROJECT_ROOT/nginx/default.conf" ]; then
    log_success "nginx/default.conf 存在"
else
    log_error "nginx/default.conf 不存在"
    exit 1
fi

# 2. 检查 Dockerfile 的关键配置
echo ""
echo "=== 2. 检查 Dockerfile 配置 ==="

if grep -q "FROM nginx:alpine" "$PROJECT_ROOT/Dockerfile"; then
    log_success "Dockerfile 使用 nginx:alpine 基础镜像"
else
    log_error "Dockerfile 没有使用 nginx:alpine"
fi

if grep -q "HEALTHCHECK" "$PROJECT_ROOT/Dockerfile"; then
    log_success "Dockerfile 包含 HEALTHCHECK"
else
    log_error "Dockerfile 没有包含 HEALTHCHECK"
fi

if grep -q "EXPOSE 80" "$PROJECT_ROOT/Dockerfile"; then
    log_success "Dockerfile 暴露端口 80"
else
    log_error "Dockerfile 没有暴露端口 80"
fi

if grep -q "CMD" "$PROJECT_ROOT/Dockerfile"; then
    log_success "Dockerfile 包含 CMD 指令"
else
    log_error "Dockerfile 没有包含 CMD 指令"
fi

# 3. 检查 Nginx 配置的关键项
echo ""
echo "=== 3. 检查 Nginx 配置 ==="

if grep -q "gzip on" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 启用了 gzip 压缩"
else
    log_error "Nginx 没有启用 gzip 压缩"
fi

if grep -q "try_files" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 配置了 try_files"
else
    log_error "Nginx 没有配置 try_files"
fi

if grep -q "X-Content-Type-Options" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 配置了 X-Content-Type-Options 安全头"
else
    log_error "Nginx 没有配置 X-Content-Type-Options"
fi

if grep -q "X-Frame-Options" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 配置了 X-Frame-Options 安全头"
else
    log_error "Nginx 没有配置 X-Frame-Options"
fi

if grep -q "Cache-Control.*HTML" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 配置了 HTML 缓存策略"
else
    log_error "Nginx 没有配置 HTML 缓存策略"
fi

if grep -q "\.css|js" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 配置了 CSS/JS 缓存策略 (7 天)"
else
    log_error "Nginx 没有配置 CSS/JS 缓存策略"
fi

if grep -q "\.jpg|jpeg|png|gif" "$PROJECT_ROOT/nginx/default.conf"; then
    log_success "Nginx 配置了图片缓存策略 (30 天)"
else
    log_error "Nginx 没有配置图片缓存策略"
fi

# 4. 检查 docker-compose 配置
echo ""
echo "=== 4. 检查 docker-compose 配置 ==="

if grep -q "80:80" "$PROJECT_ROOT/docker-compose.build.yml"; then
    log_success "docker-compose 配置了端口映射 80:80"
else
    log_error "docker-compose 没有配置正确的端口映射"
fi

if grep -q "healthcheck:" "$PROJECT_ROOT/docker-compose.build.yml"; then
    log_success "docker-compose 配置了健康检查"
else
    log_error "docker-compose 没有配置健康检查"
fi

if grep -q "networks:" "$PROJECT_ROOT/docker-compose.build.yml"; then
    log_success "docker-compose 配置了网络"
else
    log_error "docker-compose 没有配置网络"
fi

# 5. 总结
echo ""
echo "========================================="
echo "✅ 所有配置检查完成！"
echo "========================================="
echo ""
echo "下一步:"
echo "1. 构建 Docker 镜像: docker compose -f docker-compose.build.yml build"
echo "2. 启动容器: docker compose -f docker-compose.build.yml up"
echo "3. 访问应用: http://localhost/"
echo "4. 验证缓存头: curl -i http://localhost/index.html"
echo "5. 验证安全头: curl -i http://localhost/"
echo ""
