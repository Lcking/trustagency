#!/bin/bash

# 🔍 TrustAgency 日常系统检查脚本
# 用途: 每天开始开发前运行，防止系统问题
# 用法: bash daily_check.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔍 TrustAgency 日常系统检查${NC}"
echo -e "${BLUE}║  ${NC}$(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo

# 进度计数
CHECK_NUM=1
TOTAL_CHECKS=10
PASSED=0
FAILED=0

# 函数: 打印检查标题
check_header() {
    echo -e "${BLUE}[$CHECK_NUM/$TOTAL_CHECKS]${NC} $1"
    ((CHECK_NUM++))
}

# 函数: 打印成功信息
pass() {
    echo -e "${GREEN}✅${NC} $1"
    ((PASSED++))
}

# 函数: 打印警告信息
warn() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

# 函数: 打印失败信息
fail() {
    echo -e "${RED}❌${NC} $1"
    ((FAILED++))
}

# ====================
# 检查 1: Git 状态
# ====================
check_header "检查 Git 状态"
if [[ -z $(git status -s) ]]; then
    pass "工作区干净"
else
    warn "有未提交的更改:"
    git status -s | head -3
fi
echo

# ====================
# 检查 2: 数据库完整性
# ====================
check_header "检查数据库完整性"
SECTIONS=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM sections" 2>/dev/null || echo "0")
CATEGORIES=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM categories" 2>/dev/null || echo "0")
PLATFORMS=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM platforms" 2>/dev/null || echo "0")
ARTICLES=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM articles" 2>/dev/null || echo "0")

echo "  📊 栏目: $SECTIONS | 分类: $CATEGORIES | 平台: $PLATFORMS | 文章: $ARTICLES"

if [[ "$SECTIONS" -eq 0 ]]; then
    fail "数据库可能损坏 (栏目数为0)"
    fail "建议恢复备份: cp backups/baseline_*.db trustagency.db"
else
    pass "数据库数据完整"
fi
echo

# ====================
# 检查 3: 后端进程
# ====================
check_header "检查后端服务状态"
if pgrep -f "uvicorn.*app.main" > /dev/null; then
    pass "后端已运行"
    # 检查响应
    RESPONSE=$(curl -s -m 2 http://localhost:8001/api/health 2>/dev/null || echo "")
    if [[ -n "$RESPONSE" ]]; then
        pass "后端响应正常"
    else
        warn "后端响应缓慢或无响应"
    fi
else
    warn "后端未运行"
    warn "  启动命令: bash start-backend-simple.sh"
fi
echo

# ====================
# 检查 4: 前端文件
# ====================
check_header "检查前端文件"
if [[ -f "backend/site/admin/index.html" ]]; then
    HTML_LINES=$(wc -l < backend/site/admin/index.html)
    echo "  📄 HTML 文件: $HTML_LINES 行"
    
    if [[ $HTML_LINES -gt 4000 ]]; then
        pass "HTML 文件大小正常"
    elif [[ $HTML_LINES -gt 2000 ]]; then
        warn "HTML 文件可能被优化过，检查功能是否完整"
    else
        fail "HTML 文件可能被损坏 (应该 > 4000 行)"
        fail "  恢复命令: git checkout backend/site/admin/index.html"
    fi
else
    fail "HTML 文件不存在"
fi
echo

# ====================
# 检查 5: 模块文件
# ====================
check_header "检查 JavaScript 模块"
MODULES_COUNT=$(find backend/site/admin/js -name "*.js" -type f 2>/dev/null | wc -l)
echo "  📦 模块文件数: $MODULES_COUNT"

if [[ $MODULES_COUNT -ge 10 ]]; then
    pass "模块文件完整"
else
    warn "模块数量较少 (应该 >= 10)"
fi

# 检查关键模块
CRITICAL_MODULES=("backend/site/admin/js/app.js" "backend/site/admin/js/modules/auth.js" "backend/site/admin/js/modules/ui.js")
for module in "${CRITICAL_MODULES[@]}"; do
    if [[ -f "$module" ]]; then
        pass "  ✓ $(basename $module)"
    else
        fail "  ✗ $(basename $module) 缺失"
    fi
done
echo

# ====================
# 检查 6: 系统资源
# ====================
check_header "检查系统资源占用"
MEM_TOTAL=$(vm_stat 2>/dev/null | grep "Pages free" | awk '{print $3}' | tr -d '.' | tr -d ',')
MEM_FREE=$((MEM_TOTAL / 256))  # 粗略转换为 MB

PS_MEM=$(ps aux | grep -E "Code|Chrome|python|uvicorn" | grep -v grep | awk '{sum+=$6} END {print int(sum/1024)}' || echo "0")
echo "  💾 相关进程内存: ~${PS_MEM} MB"

if [[ $PS_MEM -lt 300 ]]; then
    pass "系统内存占用正常"
elif [[ $PS_MEM -lt 500 ]]; then
    warn "系统内存占用偏高 (${PS_MEM} MB)"
else
    fail "系统内存占用过高 (${PS_MEM} MB)"
    fail "  建议: 关闭不必要的应用，或重启 VSCode"
fi

DISK_USAGE=$(du -sh . 2>/dev/null | cut -f1)
echo "  💿 项目磁盘占用: $DISK_USAGE"
pass "磁盘空间充足"
echo

# ====================
# 检查 7: 备份文件
# ====================
check_header "检查备份系统"
BACKUP_COUNT=$(ls backups/*.db 2>/dev/null | wc -l)
echo "  🗂️  备份文件数: $BACKUP_COUNT"

if [[ $BACKUP_COUNT -ge 3 ]]; then
    pass "备份充足"
else
    warn "备份文件不足"
    warn "  建议: cp trustagency.db backups/backup_\$(date +%Y%m%d_%H%M%S).db"
fi

# 检查最近备份
LATEST_BACKUP=$(ls -t backups/*.db 2>/dev/null | head -1)
if [[ -n "$LATEST_BACKUP" ]]; then
    BACKUP_AGE=$(( ($(date +%s) - $(stat -f%m "$LATEST_BACKUP")) / 86400 ))
    echo "  📅 最近备份: $BACKUP_AGE 天前"
    
    if [[ $BACKUP_AGE -gt 7 ]]; then
        warn "备份已超过 7 天"
    fi
fi
echo

# ====================
# 检查 8: 日志错误
# ====================
check_header "检查系统日志"
if [[ -f "/tmp/backend.log" ]]; then
    ERROR_COUNT=$(grep -i "error" /tmp/backend.log | wc -l)
    WARNING_COUNT=$(grep -i "warning" /tmp/backend.log | wc -l)
    echo "  📝 错误数: $ERROR_COUNT | 警告数: $WARNING_COUNT"
    
    if [[ $ERROR_COUNT -eq 0 ]]; then
        pass "日志中无错误"
    elif [[ $ERROR_COUNT -lt 5 ]]; then
        warn "日志中有少量错误"
    else
        fail "日志中有许多错误 ($ERROR_COUNT)"
        fail "  检查: tail -20 /tmp/backend.log | grep -i error"
    fi
else
    warn "后端日志文件不存在 (后端未运行)"
fi
echo

# ====================
# 检查 9: 最后提交
# ====================
check_header "检查最后提交"
LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s")
LAST_COMMIT_TIME=$(git log -1 --pretty=format:"%ai")
echo "  🔄 最后提交: $LAST_COMMIT"
echo "     时间: $LAST_COMMIT_TIME"

# 计算天数 (粗略)
# 提取日期部分（格式: 2025-11-23）并转换为时间戳
COMMIT_DATE=$(echo "$LAST_COMMIT_TIME" | cut -d' ' -f1)
LAST_COMMIT_TIMESTAMP=$(date -j -f "%Y-%m-%d" "$COMMIT_DATE" +%s 2>/dev/null || echo 0)
CURRENT_TIMESTAMP=$(date +%s)
if [[ $LAST_COMMIT_TIMESTAMP -gt 0 ]]; then
    DAYS_SINCE=$(( (CURRENT_TIMESTAMP - LAST_COMMIT_TIMESTAMP) / 86400 ))
    echo "     距今: $DAYS_SINCE 天前"
    
    if [[ $DAYS_SINCE -eq 0 ]]; then
        pass "代码已更新"
    elif [[ $DAYS_SINCE -le 3 ]]; then
        pass "代码近期已更新"
    else
        warn "代码已 $DAYS_SINCE 天未更新"
    fi
fi
echo

# ====================
# 检查 10: 依赖检查
# ====================
check_header "检查依赖"

# Python 依赖
if python3 -c "import fastapi" 2>/dev/null; then
    pass "FastAPI 已安装"
else
    fail "FastAPI 未安装"
fi

# 数据库驱动
if python3 -c "import sqlite3" 2>/dev/null; then
    pass "SQLite3 已安装"
else
    fail "SQLite3 未安装"
fi
echo

# ====================
# 最终汇总
# ====================
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📊 检查汇总${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}✅ 通过检查: $PASSED${NC}"
echo -e "${RED}❌ 失败项: $FAILED${NC}"

if [[ $FAILED -eq 0 ]]; then
    echo
    echo -e "${GREEN}🎉 系统状态良好，可以开始工作!${NC}"
    echo
    echo "💡 建议:"
    echo "   1. 确认后端已启动: bash start-backend-simple.sh"
    echo "   2. 打开浏览器访问: http://localhost:8001/admin/"
    echo "   3. 登录账号: admin / admin123"
    echo "   4. 开始开发工作"
    echo
    exit 0
else
    echo
    echo -e "${YELLOW}⚠️  发现问题，请先解决后再开始工作${NC}"
    echo
    echo "快速修复:"
    if [[ ! -f "backend/site/admin/index.html" ]] || [[ $(wc -l < backend/site/admin/index.html) -lt 2000 ]]; then
        echo "  1. 恢复前端: git checkout backend/site/admin/index.html"
    fi
    if [[ "$SECTIONS" -eq 0 ]]; then
        echo "  1. 恢复数据库: cp backups/baseline_*.db trustagency.db"
    fi
    if ! pgrep -f "uvicorn" > /dev/null; then
        echo "  2. 启动后端: bash start-backend-simple.sh"
    fi
    echo
    exit 1
fi
