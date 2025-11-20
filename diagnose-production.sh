#!/bin/bash
###############################################################################
# 🔍 TrustAgency 生产环境诊断工具
#
# 功能：检查部署状态，识别问题
# 
# 使用方法：
# bash diagnose-production.sh
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 计数器
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 日志函数
log_check() {
    ((TOTAL_CHECKS++))
    echo -e "${BLUE}→${NC} $1"
}

log_pass() {
    ((PASSED_CHECKS++))
    echo -e "  ${GREEN}✅ PASS${NC}: $1"
}

log_fail() {
    ((FAILED_CHECKS++))
    echo -e "  ${RED}❌ FAIL${NC}: $1"
}

log_warn() {
    echo -e "  ${YELLOW}⚠️  WARN${NC}: $1"
}

log_info() {
    echo -e "  ${CYAN}ℹ️${NC} $1"
}

# 标题
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TrustAgency 生产环境诊断工具                      ║${NC}"
echo -e "${BLUE}║   Diagnostic Tool for Production Environment       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# 第一部分：系统检查
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1️⃣  系统环境检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 Docker
log_check "Docker 安装状态"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_pass "$DOCKER_VERSION"
else
    log_fail "Docker 未安装"
fi

# 检查 Docker Compose
log_check "Docker Compose 安装状态"
if command -v docker-compose &> /dev/null; then
    DC_VERSION=$(docker-compose --version)
    log_pass "$DC_VERSION"
else
    log_fail "Docker Compose 未安装"
fi

# 检查 Nginx
log_check "Nginx 安装状态"
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1)
    log_pass "$NGINX_VERSION"
else
    log_fail "Nginx 未安装"
fi

# 检查 curl
log_check "curl 安装状态"
if command -v curl &> /dev/null; then
    log_pass "curl 已安装"
else
    log_fail "curl 未安装"
fi

# 第二部分：Nginx 检查
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2️⃣  Nginx 配置检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 Nginx 配置文件
log_check "Nginx 配置文件"
if [ -f "/etc/nginx/conf.d/trustagency.conf" ]; then
    log_pass "配置文件存在: /etc/nginx/conf.d/trustagency.conf"
else
    log_fail "配置文件不存在: /etc/nginx/conf.d/trustagency.conf"
    log_info "请运行: sudo bash fix-production-deployment.sh"
fi

# 检查 Nginx 配置语法
log_check "Nginx 配置语法"
if nginx -t 2>&1 | grep -q "successful"; then
    log_pass "Nginx 配置正确"
else
    log_fail "Nginx 配置有错误"
    nginx -t 2>&1 | sed 's/^/    /'
fi

# 检查 Nginx 服务状态
log_check "Nginx 服务状态"
if systemctl is-active --quiet nginx; then
    log_pass "Nginx 服务运行中"
else
    log_fail "Nginx 服务未运行"
    log_info "请运行: sudo systemctl start nginx"
fi

# 检查 Nginx 监听端口
log_check "Nginx 监听端口"
if netstat -tuln 2>/dev/null | grep -q ":80 \|:443 "; then
    log_pass "Nginx 正在监听 80/443 端口"
else
    log_warn "Nginx 可能未正确监听 80/443 端口"
fi

# 第三部分：后端容器检查
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3️⃣  后端 Docker 容器检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查容器是否运行
log_check "FastAPI 后端容器状态"
if docker ps 2>/dev/null | grep -q trustagency-backend; then
    CONTAINER_ID=$(docker ps 2>/dev/null | grep trustagency-backend | awk '{print $1}')
    log_pass "容器运行中 (ID: $CONTAINER_ID)"
else
    log_fail "FastAPI 后端容器未运行"
    log_info "已停止的容器："
    docker ps -a 2>/dev/null | grep trustagency || log_info "  (无历史容器)"
fi

# 检查后端服务端口
log_check "后端服务端口 8001"
if netstat -tuln 2>/dev/null | grep -q ":8001 " || ss -tuln 2>/dev/null | grep -q ":8001 "; then
    log_pass "后端服务监听端口 8001"
else
    log_warn "后端服务未监听端口 8001"
fi

# 第四部分：网络连通性检查
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}4️⃣  网络连通性检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 本地 HTTP 测试
log_check "本地 HTTP 连接测试"
if curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "200\|301\|404\|405"; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null)
    log_pass "HTTP 响应状态: $STATUS"
else
    log_fail "无法连接 HTTP localhost"
    log_info "请检查 Nginx 是否运行: systemctl status nginx"
fi

# 后端 API 测试
log_check "后端 API 连接测试"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health 2>/dev/null | grep -q "200\|401"; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health 2>/dev/null)
    log_pass "后端 API 响应状态: $STATUS"
else
    log_fail "无法连接后端 API (localhost:8001)"
    log_info "请检查后端容器: docker-compose -f docker-compose.prod.yml ps"
fi

# 代理测试
log_check "Nginx 代理转发测试"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health 2>/dev/null | grep -q "200\|401"; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health 2>/dev/null)
    log_pass "代理转发正常，响应状态: $STATUS"
else
    log_fail "Nginx 代理转发失败"
    log_info "请检查 Nginx 配置是否正确指向后端"
fi

# HTTPS 测试（如果域名可用）
log_check "HTTPS 连接测试"
if curl -s -I --insecure https://yycr.net 2>/dev/null | head -1; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --insecure https://yycr.net 2>/dev/null)
    if [ "$HTTP_STATUS" = "405" ]; then
        log_warn "HTTPS 响应 405 Method Not Allowed (这是 HEAD 方法不被允许)"
        log_info "💡 解决方案: 确保 Nginx 配置中有 proxy_method \$request_method;"
    elif [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "200" ]; then
        log_pass "HTTPS 连接正常，响应: $HTTP_STATUS"
    else
        log_fail "HTTPS 响应异常: $HTTP_STATUS"
    fi
else
    log_warn "HTTPS 测试跳过（域名不可达或证书问题）"
fi

# 第五部分：前端文件检查
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}5️⃣  前端文件检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查前端目录
log_check "前端静态文件目录"
if [ -d "/usr/share/nginx/html/admin" ]; then
    FILE_COUNT=$(find /usr/share/nginx/html/admin -type f 2>/dev/null | wc -l)
    log_pass "前端目录存在，包含 $FILE_COUNT 个文件"
    
    # 检查 index.html
    if [ -f "/usr/share/nginx/html/admin/index.html" ]; then
        log_pass "index.html 存在"
    else
        log_fail "index.html 不存在"
        log_info "请上传前端文件或从后端复制: cp backend/site/admin/index.html /usr/share/nginx/html/admin/"
    fi
else
    log_fail "前端目录不存在: /usr/share/nginx/html/admin"
    log_info "请创建目录: sudo mkdir -p /usr/share/nginx/html/admin"
fi

# 第六部分：数据库检查
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}6️⃣  数据库检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 SQLite 数据库
log_check "SQLite 数据库"
if docker ps 2>/dev/null | grep -q trustagency-backend; then
    DB_PATH="/opt/trustagency/backend/data/trustagency.db"
    if [ -f "$DB_PATH" ]; then
        SIZE=$(du -h "$DB_PATH" 2>/dev/null | cut -f1)
        log_pass "数据库文件存在，大小: $SIZE"
    else
        log_warn "数据库文件不存在（可能尚未初始化）"
        log_info "请运行: curl http://localhost:8001/api/init"
    fi
else
    log_warn "后端容器未运行，跳过数据库检查"
fi

# 第七部分：SSL/TLS 证书检查
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}7️⃣  SSL/TLS 证书检查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查证书
log_check "SSL 证书文件"
if [ -f "/etc/nginx/ssl/cert.pem" ] && [ -f "/etc/nginx/ssl/key.pem" ]; then
    log_pass "证书文件存在"
    
    # 检查证书有效期
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/nginx/ssl/cert.pem 2>/dev/null | cut -d= -f2)
    if [ -n "$EXPIRY" ]; then
        log_info "证书有效期至: $EXPIRY"
    fi
else
    log_fail "SSL 证书文件不存在"
    log_info "需要证书文件: /etc/nginx/ssl/cert.pem 和 /etc/nginx/ssl/key.pem"
fi

# 最后：总结报告
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📊 诊断总结${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PASS_RATE=$(( PASSED_CHECKS * 100 / TOTAL_CHECKS ))

echo -e "总检查项数:  ${CYAN}$TOTAL_CHECKS${NC}"
echo -e "通过检查:   ${GREEN}$PASSED_CHECKS${NC}"
echo -e "失败检查:   ${RED}$FAILED_CHECKS${NC}"
echo -e "通过率:     ${BLUE}$PASS_RATE%${NC}"

echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！系统运行正常。${NC}"
    echo ""
    echo -e "${GREEN}🎉 你可以访问：${NC}"
    echo -e "  HTTP:   ${CYAN}http://localhost/admin/${NC}"
    echo -e "  HTTPS:  ${CYAN}https://yycr.net/admin/${NC}"
elif [ $FAILED_CHECKS -le 2 ]; then
    echo -e "${YELLOW}⚠️  有 $FAILED_CHECKS 个检查失败，但系统可能仍可正常工作。${NC}"
    echo ""
    echo -e "${YELLOW}建议采取行动：${NC}"
    echo -e "  1. 查看上面的失败项"
    echo -e "  2. 运行推荐的修复命令"
    echo -e "  3. 重新运行本诊断工具进行验证"
else
    echo -e "${RED}❌ 检查失败数较多，需要进行修复。${NC}"
    echo ""
    echo -e "${RED}建议行动：${NC}"
    echo -e "  1. 运行完整修复脚本: ${CYAN}sudo bash fix-production-deployment.sh${NC}"
    echo -e "  2. 查看详细文档: ${CYAN}cat PRODUCTION_DEPLOYMENT_ARCHITECTURE.md${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}诊断完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

