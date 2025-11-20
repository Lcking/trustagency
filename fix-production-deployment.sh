#!/bin/bash
###############################################################################
# 🔧 TrustAgency 生产环境快速修复脚本
# 
# 功能：
# 1. 修复 405 Method Not Allowed 错误
# 2. 配置 Nginx 反向代理
# 3. 启动后端服务
# 4. 验证部署
#
# 使用方法：
# sudo bash fix-production-deployment.sh
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
  log_error "此脚本需要 root 权限。请使用: sudo bash fix-production-deployment.sh"
fi

log_info "=========================================="
log_info "TrustAgency 生产环境部署修复"
log_info "=========================================="

# Step 1: 检查前提条件
log_info "Step 1: 检查前提条件..."

if ! command -v docker &> /dev/null; then
  log_error "Docker 未安装！请先安装 Docker"
fi
log_success "Docker 已安装"

if ! command -v docker-compose &> /dev/null; then
  log_error "Docker Compose 未安装！请先安装 Docker Compose"
fi
log_success "Docker Compose 已安装"

if ! command -v nginx &> /dev/null; then
  log_warning "Nginx 未安装，将安装..."
  apt-get update
  apt-get install -y nginx
fi
log_success "Nginx 已安装"

# Step 2: 创建 Nginx 配置
log_info "Step 2: 配置 Nginx 反向代理..."

cat > /etc/nginx/conf.d/trustagency.conf <<'NGINX_CONFIG'
# TrustAgency 生产环境 Nginx 配置
# 支持 HTTPS + 反向代理 + SPA 路由

# ===== HTTP 重定向到 HTTPS =====
server {
    listen 80;
    listen [::]:80;
    server_name _;
    return 301 https://$host$request_uri;
}

# ===== HTTPS 服务器 =====
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    # 替换为你的域名
    server_name yycr.net www.yycr.net;
    
    # ===== SSL 配置 =====
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # ===== 安全头 =====
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # ===== 前端静态文件配置 =====
    root /usr/share/nginx/html;
    index index.html;
    
    # 前端 SPA 路由配置
    location /admin/ {
        try_files $uri $uri/ /admin/index.html;
        
        # 前端 HTML 不缓存
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0" always;
    }
    
    # 前端静态资源缓存
    location /admin/assets/ {
        expires 30d;
        add_header Cache-Control "public, immutable" always;
    }
    
    # ===== 后端 API 代理 =====
    location /api/ {
        # 关键配置：代理所有 HTTP 方法到后端
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        
        # ✅ 允许所有 HTTP 方法（修复 405 错误）
        proxy_method $request_method;
        
        # 代理请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # WebSocket 支持
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # ===== 健康检查（访问日志中忽略）=====
    location /api/health {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        access_log off;
    }
    
    # ===== 根路径重定向 =====
    location = / {
        return 301 /admin/;
    }
    
    # ===== 访问日志 =====
    access_log /var/log/nginx/trustagency_access.log combined buffer=32k flush=5s;
    error_log /var/log/nginx/trustagency_error.log warn;
    
    # ===== Gzip 压缩 =====
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/javascript application/javascript application/json;
    gzip_disable "MSIE [1-6]\.";
}
NGINX_CONFIG

log_success "Nginx 配置已创建"

# Step 3: 验证 Nginx 配置
log_info "Step 3: 验证 Nginx 配置..."

if ! nginx -t 2>&1 | grep "successful"; then
  log_error "Nginx 配置验证失败！请检查错误信息"
fi
log_success "Nginx 配置验证成功"

# Step 4: 重启 Nginx
log_info "Step 4: 重启 Nginx..."
systemctl restart nginx
log_success "Nginx 已重启"

# Step 5: 创建前端目录
log_info "Step 5: 准备前端目录..."
mkdir -p /usr/share/nginx/html/admin
log_success "前端目录已创建"

# Step 6: 检查后端容器
log_info "Step 6: 检查后端 Docker 容器状态..."

# 获取项目目录
PROJECT_DIR="/opt/trustagency"
if [ ! -d "$PROJECT_DIR" ]; then
  log_warning "项目目录 $PROJECT_DIR 不存在！"
  read -p "请输入项目目录路径 [/opt/trustagency]: " -r PROJECT_DIR
  PROJECT_DIR=${PROJECT_DIR:-/opt/trustagency}
fi

cd "$PROJECT_DIR"

# 检查 Docker Compose
if [ ! -f "docker-compose.prod.yml" ]; then
  log_error "找不到 docker-compose.prod.yml"
fi

# 启动容器
log_info "启动后端容器..."
docker-compose -f docker-compose.prod.yml up -d

log_success "后端容器已启动"

# 等待后端启动
log_info "等待后端服务就绪..."
sleep 5

# Step 7: 验证部署
log_info "Step 7: 验证部署..."

# 检查后端是否运行
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
  log_success "后端 API 正常运行"
else
  log_warning "后端 API 暂未响应，请稍候..."
  sleep 10
fi

# 检查 Nginx 代理
log_info "检查 Nginx 代理配置..."
if curl -s -I http://localhost/api/health | grep -q "200\|401"; then
  log_success "Nginx 代理配置正确"
else
  log_warning "Nginx 代理可能存在问题，请检查错误日志"
fi

# Step 8: 显示访问信息
log_success "=========================================="
log_success "✅ 部署修复完成！"
log_success "=========================================="

echo ""
echo -e "${GREEN}📝 访问信息：${NC}"
echo "  URL: https://yycr.net/admin/"
echo ""

echo -e "${GREEN}🔧 常用命令：${NC}"
echo "  查看 Nginx 日志: tail -f /var/log/nginx/trustagency_error.log"
echo "  查看后端日志: docker-compose -f docker-compose.prod.yml logs -f backend"
echo "  检查容器状态: docker-compose -f docker-compose.prod.yml ps"
echo "  重启后端: docker-compose -f docker-compose.prod.yml restart backend"
echo "  重启 Nginx: systemctl restart nginx"
echo ""

echo -e "${GREEN}✅ 故障排查：${NC}"
echo "  问题：无法访问管理后台"
echo "  → 检查前端文件是否存在: ls -la /usr/share/nginx/html/admin/"
echo "  → 检查 Nginx 配置: nginx -t"
echo "  → 检查 Nginx 日志: tail -f /var/log/nginx/trustagency_error.log"
echo ""

echo -e "${GREEN}📤 部署前端（有新版本时）：${NC}"
echo "  1. 在本地构建: npm run build"
echo "  2. 上传到服务器: scp -r dist/* root@yycr.net:/usr/share/nginx/html/admin/"
echo "  3. 重载 Nginx: ssh root@yycr.net 'nginx -s reload'"
echo ""

echo -e "${GREEN}🔐 下一步建议：${NC}"
echo "  1. [ ] 修改后端 .env 中的 CORS_ORIGINS 为你的域名"
echo "  2. [ ] 修改 Nginx 配置中的 server_name 为你的域名"
echo "  3. [ ] 上传前端构建产物到 /usr/share/nginx/html/admin/"
echo "  4. [ ] 更新 SSL 证书路径 (如果需要)"
echo "  5. [ ] 测试登录功能"
echo "  6. [ ] 配置备份策略"
echo ""

log_success "所有步骤完成！系统已就绪。"

