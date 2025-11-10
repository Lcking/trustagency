#!/bin/bash

# Task 11 E2E 测试框架验证脚本
# 用途: 快速验证 Task 11 的所有文件和配置

echo "=================================="
echo "Task 11 E2E 测试框架验证"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
TOTAL=0
PASSED=0

# 检查函数
check_file() {
    local file=$1
    local name=$2
    ((TOTAL++))
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $name 存在"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $name 不存在"
    fi
}

check_dir() {
    local dir=$1
    local name=$2
    ((TOTAL++))
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC} $name 目录存在"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $name 目录不存在"
    fi
}

# 核心配置文件
echo "📦 核心配置文件检查:"
check_file "package.json" "package.json"
check_file "playwright.config.js" "playwright.config.js"
echo ""

# 测试文件
echo "🧪 测试文件检查:"
check_dir "tests/e2e" "E2E 测试目录"
check_file "tests/e2e/auth.spec.js" "认证测试"
check_file "tests/e2e/platforms.spec.js" "平台测试"
check_file "tests/e2e/articles.spec.js" "文章测试"
check_file "tests/e2e/error-scenarios.spec.js" "错误场景测试"
check_file "tests/e2e/performance.spec.js" "性能和安全测试"
echo ""

# 文档文件
echo "📚 文档文件检查:"
check_file "TASK_11_COMPLETION_REPORT.md" "完成报告"
check_file "TASK_11_QUICKSTART.md" "快速开始指南"
check_file "TASK_11_DELIVERY_CHECKLIST.md" "交付清单"
check_file "TASK_11_FINAL_SUMMARY.md" "最终总结"
check_file "PROJECT_PROGRESS_2025_11_06_v4.md" "项目进度报告"
echo ""

# 行数统计
echo "📊 代码行数统计:"
if [ -f "tests/e2e/auth.spec.js" ]; then
    TOTAL_LINES=$(wc -l tests/e2e/*.js package.json playwright.config.js 2>/dev/null | tail -1 | awk '{print $1}')
    echo -e "总代码行数: ${GREEN}$TOTAL_LINES${NC} 行"
    
    # 分文件统计
    echo ""
    echo "文件分解:"
    wc -l tests/e2e/*.js 2>/dev/null | grep -v total | while read lines file; do
        if [ $lines -gt 0 ]; then
            echo "  $(basename $file): $lines 行"
        fi
    done
fi
echo ""

# 测试用例数统计
echo "🧪 测试用例统计:"
if [ -f "tests/e2e/auth.spec.js" ]; then
    AUTH_TESTS=$(grep -c "test(" tests/e2e/auth.spec.js)
    PLATFORM_TESTS=$(grep -c "test(" tests/e2e/platforms.spec.js)
    ARTICLE_TESTS=$(grep -c "test(" tests/e2e/articles.spec.js)
    ERROR_TESTS=$(grep -c "test(" tests/e2e/error-scenarios.spec.js)
    PERF_TESTS=$(grep -c "test(" tests/e2e/performance.spec.js)
    TOTAL_TESTS=$((AUTH_TESTS + PLATFORM_TESTS + ARTICLE_TESTS + ERROR_TESTS + PERF_TESTS))
    
    echo "  认证测试: $AUTH_TESTS cases"
    echo "  平台测试: $PLATFORM_TESTS cases"
    echo "  文章测试: $ARTICLE_TESTS cases"
    echo "  错误测试: $ERROR_TESTS cases"
    echo "  性能测试: $PERF_TESTS cases"
    echo -e "  ${GREEN}总计: $TOTAL_TESTS cases${NC}"
fi
echo ""

# NPM 依赖检查
echo "📦 NPM 配置检查:"
if [ -f "package.json" ]; then
    if grep -q "@playwright/test" package.json; then
        echo -e "${GREEN}✅${NC} Playwright 依赖已配置"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} Playwright 依赖未配置"
    fi
    ((TOTAL++))
    
    if grep -q "\"test\":" package.json; then
        echo -e "${GREEN}✅${NC} npm test 脚本已配置"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} npm test 脚本未配置"
    fi
    ((TOTAL++))
fi
echo ""

# Playwright 配置检查
echo "⚙️  Playwright 配置检查:"
if [ -f "playwright.config.js" ]; then
    if grep -q "defineConfig" playwright.config.js; then
        echo -e "${GREEN}✅${NC} 配置已使用 defineConfig"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} 配置未使用 defineConfig"
    fi
    ((TOTAL++))
    
    if grep -q "devices" playwright.config.js; then
        echo -e "${GREEN}✅${NC} 多设备支持已配置"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} 多设备支持未配置"
    fi
    ((TOTAL++))
    
    if grep -q "webServer" playwright.config.js; then
        echo -e "${GREEN}✅${NC} Web 服务器自启动已配置"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} Web 服务器自启动未配置"
    fi
    ((TOTAL++))
fi
echo ""

# 最终总结
echo "=================================="
echo "验证总结"
echo "=================================="
PERCENTAGE=$((PASSED * 100 / TOTAL))
echo "通过检查: $PASSED / $TOTAL (${PERCENTAGE}%)"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}✅ 所有检查通过!${NC}"
    echo ""
    echo "下一步:"
    echo "1. npm install                 (安装依赖)"
    echo "2. npm run test:ui             (运行测试 - UI 模式)"
    echo "3. npm run report              (查看报告)"
else
    echo -e "${YELLOW}⚠️  有些检查失败,请检查上述错误${NC}"
fi
echo ""

# 快速开始提示
echo "=================================="
echo "快速命令"
echo "=================================="
echo "运行所有测试:"
echo "  npm test"
echo ""
echo "UI 模式 (推荐):"
echo "  npm run test:ui"
echo ""
echo "特定测试套件:"
echo "  npm run test:auth          # 认证测试"
echo "  npm run test:platforms     # 平台测试"
echo "  npm run test:articles      # 文章测试"
echo "  npm run test:errors        # 错误场景"
echo "  npm run test:performance   # 性能和安全"
echo ""
echo "查看报告:"
echo "  npm run report"
echo ""
