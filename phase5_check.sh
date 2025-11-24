#!/bin/bash

# ============================================================================
# Phase 5 系统检查脚本
# 用途: 快速诊断系统状态，验证性能指标
# 使用: bash phase5_check.sh
# ============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║             Phase 5 系统检查脚本 - 性能诊断和验收                     ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查项计数
PASSED=0
FAILED=0

# ============================================================================
# 检查函数
# ============================================================================

check_git_status() {
    echo "${BLUE}📌 Git 状态检查${NC}"
    
    BRANCH=$(git branch --show-current)
    if [[ $BRANCH == "refactor/admin-panel-phase5" ]]; then
        echo "  ✅ 分支正确: $BRANCH"
        ((PASSED++))
    else
        echo "  ❌ 分支错误: $BRANCH (应该是 refactor/admin-panel-phase5)"
        ((FAILED++))
    fi
    echo ""
}

check_backend_status() {
    echo "${BLUE}🔧 后端服务检查${NC}"
    
    # 检查进程
    if pgrep -f "python3.*main.py" > /dev/null; then
        echo "  ✅ 后端进程运行中"
        ((PASSED++))
    else
        echo "  ❌ 后端进程未运行"
        echo "     建议: python3 backend/main.py &"
        ((FAILED++))
    fi
    
    # 检查 API 可用性
    if timeout 2 curl -s http://localhost:8001/api/sections > /dev/null 2>&1; then
        echo "  ✅ 后端 API 可用 (localhost:8001)"
        ((PASSED++))
    else
        echo "  ❌ 后端 API 不可用"
        ((FAILED++))
    fi
    
    # 检查健康检查端点 (Phase 5 新增)
    if timeout 2 curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "  ✅ 健康检查端点可用"
        ((PASSED++))
    else
        echo "  ⚠️  健康检查端点不可用 (Phase 5 新增，暂可忽略)"
    fi
    echo ""
}

check_database_status() {
    echo "${BLUE}💾 数据库检查${NC}"
    
    DB_FILE="trustagency.db"
    
    if [ -f "$DB_FILE" ]; then
        echo "  ✅ 数据库文件存在"
        ((PASSED++))
        
        # 检查文件大小
        SIZE=$(du -h "$DB_FILE" | cut -f1)
        echo "  📊 数据库大小: $SIZE"
        
        # 检查表数据
        ARTICLE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM articles;" 2>/dev/null || echo "0")
        TASK_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM tasks;" 2>/dev/null || echo "0")
        
        echo "  📈 文章数: $ARTICLE_COUNT"
        echo "  📈 任务数: $TASK_COUNT"
        ((PASSED++))
    else
        echo "  ❌ 数据库文件不存在"
        ((FAILED++))
    fi
    
    # 检查备份
    if [ -d "backups" ]; then
        BACKUP_COUNT=$(ls -1 backups/*.db 2>/dev/null | wc -l)
        echo "  📦 备份文件数: $BACKUP_COUNT"
        if [ $BACKUP_COUNT -gt 0 ]; then
            echo "  ✅ 备份系统就位"
            ((PASSED++))
        fi
    else
        echo "  ⚠️  备份目录不存在"
    fi
    echo ""
}

check_frontend_status() {
    echo "${BLUE}🎨 前端文件检查${NC}"
    
    FRONTEND_FILE="backend/site/admin/index.html"
    
    if [ -f "$FRONTEND_FILE" ]; then
        echo "  ✅ 前端文件存在"
        ((PASSED++))
        
        # 检查文件大小
        SIZE=$(du -h "$FRONTEND_FILE" | cut -f1)
        LINES=$(wc -l < "$FRONTEND_FILE")
        echo "  📊 前端文件大小: $SIZE ($LINES 行)"
        
        # 检查是否 < 2000 行 (Phase 5 目标)
        if [ $LINES -lt 2000 ]; then
            echo "  ✅ HTML 文件 < 2000 行"
            ((PASSED++))
        elif [ $LINES -lt 3000 ]; then
            echo "  ⚠️  HTML 文件 > 2000 行 (目标: < 2000)"
        else
            echo "  ❌ HTML 文件过大 (> 3000 行)"
            ((FAILED++))
        fi
    else
        echo "  ❌ 前端文件不存在"
        ((FAILED++))
    fi
    
    # 检查 Phase 5 新增的模块文件
    if [ -f "backend/site/admin/js/monitoring.js" ]; then
        echo "  ✅ 监控模块存在"
        ((PASSED++))
    else
        echo "  ⚠️  监控模块不存在 (Phase 5 新增)"
    fi
    echo ""
}

check_phase5_files() {
    echo "${BLUE}📄 Phase 5 相关文件检查${NC}"
    
    FILES=(
        "PHASE5_KICKOFF.md"
        "PHASE5_PROGRESS.md"
        "phase5_check.sh"
    )
    
    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
            ((PASSED++))
        else
            echo "  ⚠️  $file (可选)"
        fi
    done
    echo ""
}

check_performance_indicators() {
    echo "${BLUE}⚡ 性能指标检查${NC}"
    
    # 测试首页加载时间 (需要后端运行)
    if pgrep -f "python3.*main.py" > /dev/null; then
        echo "  🔍 测试前端加载时间..."
        
        # 简单的性能测试 (实际应该使用浏览器开发者工具)
        START=$(date +%s%N | cut -b1-13)
        if timeout 5 curl -s http://localhost:8001/ > /dev/null 2>&1; then
            END=$(date +%s%N | cut -b1-13)
            LOAD_TIME=$((END - START))
            
            echo "  ⏱️  首页加载时间: ${LOAD_TIME}ms"
            
            if [ $LOAD_TIME -lt 3000 ]; then
                echo "  ✅ 性能良好 (< 3s)"
                ((PASSED++))
            else
                echo "  ⚠️  性能需优化 (> 3s)"
            fi
        fi
    else
        echo "  ⚠️  后端未运行，无法测试性能"
    fi
    
    # 检查系统资源
    echo ""
    echo "  📊 系统资源占用:"
    
    # 检查内存
    if command -v free > /dev/null; then
        MEM_USAGE=$(free -h | grep Mem | awk '{print $3"/"$2}')
        echo "     内存: $MEM_USAGE"
    fi
    
    # 检查磁盘
    if command -v df > /dev/null; then
        DISK_USAGE=$(df -h . | tail -1 | awk '{print $3"/"$2}')
        echo "     磁盘: $DISK_USAGE"
    fi
    
    ((PASSED++))
    echo ""
}

check_api_response_time() {
    echo "${BLUE}🚀 API 响应时间检查${NC}"
    
    if ! pgrep -f "python3.*main.py" > /dev/null; then
        echo "  ⚠️  后端未运行，跳过测试"
        echo ""
        return
    fi
    
    ENDPOINTS=(
        "/api/sections"
        "/api/categories"
        "/api/platforms"
        "/api/articles?skip=0&limit=10"
    )
    
    for endpoint in "${ENDPOINTS[@]}"; do
        START=$(date +%s%N | cut -b1-13)
        
        if timeout 5 curl -s http://localhost:8001$endpoint > /dev/null 2>&1; then
            END=$(date +%s%N | cut -b1-13)
            TIME=$((END - START))
            
            if [ $TIME -lt 500 ]; then
                echo "  ✅ $endpoint: ${TIME}ms"
                ((PASSED++))
            else
                echo "  ⚠️  $endpoint: ${TIME}ms (目标: < 500ms)"
            fi
        else
            echo "  ❌ $endpoint: 超时或失败"
            ((FAILED++))
        fi
    done
    echo ""
}

check_backup_system() {
    echo "${BLUE}🔄 备份系统检查${NC}"
    
    if [ -d "backups" ]; then
        LATEST_BACKUP=$(ls -t backups/*.db 2>/dev/null | head -1)
        
        if [ -n "$LATEST_BACKUP" ]; then
            MTIME=$(stat -f%m "$LATEST_BACKUP" 2>/dev/null || stat -c%Y "$LATEST_BACKUP" 2>/dev/null)
            NOW=$(date +%s)
            AGE=$(( (NOW - MTIME) / 3600 ))
            
            echo "  ✅ 最新备份: $(basename "$LATEST_BACKUP")"
            echo "  ⏰ 备份时间: ${AGE}小时前"
            
            if [ $AGE -lt 6 ]; then
                echo "  ✅ 备份及时"
                ((PASSED++))
            else
                echo "  ⚠️  备份过期 (应 < 6小时)"
            fi
        fi
    else
        echo "  ⚠️  备份系统未初始化"
    fi
    echo ""
}

# ============================================================================
# 主检查流程
# ============================================================================

main() {
    echo "📝 开始系统检查..."
    echo ""
    
    check_git_status
    check_backend_status
    check_database_status
    check_frontend_status
    check_phase5_files
    check_performance_indicators
    check_api_response_time
    check_backup_system
    
    # 总结
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                         检查总结                                      ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "✅ 通过检查: ${GREEN}$PASSED${NC}"
    echo "❌ 失败检查: ${RED}$FAILED${NC}"
    echo ""
    
    TOTAL=$((PASSED + FAILED))
    if [ $TOTAL -gt 0 ]; then
        PERCENTAGE=$((PASSED * 100 / TOTAL))
        echo "通过率: ${PERCENTAGE}%"
        echo ""
    fi
    
    if [ $FAILED -eq 0 ]; then
        echo "${GREEN}✨ 所有检查通过！系统已准备好进行 Phase 5${NC}"
    elif [ $FAILED -le 2 ]; then
        echo "${YELLOW}⚠️  有些项目需要注意，但不影响进行${NC}"
    else
        echo "${RED}❌ 有多个项目失败，建议先解决再继续${NC}"
    fi
    echo ""
    
    echo "📍 下一步建议:"
    echo "   1. 查看上面的检查结果，处理任何失败项"
    echo "   2. 运行: bash daily_check.sh (全面检查)"
    echo "   3. 打开 PHASE5_KICKOFF.md 了解详细任务"
    echo "   4. 开始任务 5.1 性能诊断"
    echo ""
}

# 运行主检查
main
