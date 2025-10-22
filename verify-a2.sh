#!/bin/bash

# 快速验证脚本 - 检查 A-2 任务的所有交付物
# Quick Verification Script - Check all deliverables for task A-2

set -e  # 任何错误都停止执行

echo "================================"
echo "A-2 任务交付物验证"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0

# 验证函数
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    fi
}

check_dir() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    fi
}

check_content() {
    local file=$1
    local content=$2
    local description=$3
    
    if grep -q "$content" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    fi
}

echo "== 1. 核心文件检查 =="
check_file "site/base.html" "base.html 模板文件"
check_file "site/assets/css/main.css" "main.css 样式表（扩展版）"
check_file "site/assets/css/utilities.css" "utilities.css 工具类库"
check_file "site/assets/js/main.js" "main.js 脚本（模块化版）"
check_file "site/components.html" "components.html 组件库演示"
echo ""

echo "== 2. 文档文件检查 =="
check_file "TEMPLATES_GUIDE.md" "TEMPLATES_GUIDE.md 参考指南"
check_file "A2_COMPLETION_SUMMARY.md" "A2_COMPLETION_SUMMARY.md 完成总结"
check_file "A2_VERIFICATION_CHECKLIST.md" "A2_VERIFICATION_CHECKLIST.md 验收清单"
check_file "kanban/issues/A-2.md" "kanban/issues/A-2.md 任务更新"
echo ""

echo "== 3. HTML 结构检查 =="
check_content "site/base.html" "<!DOCTYPE html>" "base.html: HTML5 DOCTYPE"
check_content "site/base.html" "id=\"main-content\"" "base.html: 主要内容区域"
check_content "site/base.html" "skip-to-content" "base.html: Skip-to-content 链接"
check_content "site/components.html" "class=\"card\"" "components.html: 卡片组件"
echo ""

echo "== 4. CSS 功能检查 =="
check_content "site/assets/css/main.css" "--primary-color" "main.css: CSS 变量"
check_content "site/assets/css/main.css" ".card" "main.css: 卡片样式"
check_content "site/assets/css/main.css" ".btn-primary" "main.css: 按钮样式"
check_content "site/assets/css/utilities.css" ".d-flex" "utilities.css: Flexbox 工具类"
check_content "site/assets/css/utilities.css" "user-select" "utilities.css: User-select 工具类"
echo ""

echo "== 5. JavaScript 功能检查 =="
check_content "site/assets/js/main.js" "window.TrustAgency" "main.js: TrustAgency 全局对象"
check_content "site/assets/js/main.js" "setupFocusIndicators" "main.js: 键盘导航指示"
check_content "site/assets/js/main.js" "announceToScreenReader" "main.js: 屏幕阅读器支持"
check_content "site/assets/js/main.js" "IntersectionObserver" "main.js: 图片懒加载"
echo ""

echo "== 6. 无障碍性检查 =="
check_content "site/base.html" "aria-label" "base.html: ARIA 标签"
check_content "site/assets/css/main.css" "skip-to-content" "main.css: Skip-to-content 样式"
check_content "site/assets/css/main.css" "focus-visible" "main.css: Focus 可见性"
check_content "site/assets/js/main.js" "aria-live" "main.js: Aria-live 支持"
echo ""

echo "== 7. 响应式设计检查 =="
check_content "site/assets/css/main.css" "@media" "main.css: 媒体查询"
check_content "site/assets/css/utilities.css" "@media" "utilities.css: 响应式工具类"
check_content "site/base.html" "viewport" "base.html: Viewport meta 标签"
echo ""

echo "== 8. 浏览器兼容性检查 =="
check_content "site/assets/css/utilities.css" "-webkit-user-select" "utilities.css: Safari 兼容性"
check_content "site/assets/js/main.js" "Element.prototype.closest" "main.js: IE 11 Polyfill"
echo ""

# 文件大小检查
echo "== 9. 文件大小检查 =="
echo -n "site/base.html: "
wc -l < "site/base.html" | xargs echo "行"

echo -n "site/assets/css/main.css: "
wc -l < "site/assets/css/main.css" | xargs echo "行"

echo -n "site/assets/css/utilities.css: "
wc -l < "site/assets/css/utilities.css" | xargs echo "行"

echo -n "site/assets/js/main.js: "
wc -l < "site/assets/js/main.js" | xargs echo "行"

echo ""

# 总结
echo "== 验证结果摘要 =="
echo -e "✅ 通过: ${GREEN}$PASSED${NC}"
echo -e "❌ 失败: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}所有检查通过！✅${NC}"
    echo -e "${GREEN}================================${NC}"
    exit 0
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}有 $FAILED 项检查失败❌${NC}"
    echo -e "${RED}================================${NC}"
    exit 1
fi
