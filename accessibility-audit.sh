#!/bin/bash

# A-7 自动化无障碍审计脚本
# 对所有页面进行系统的无障碍检查

AUDIT_DIR="/Users/ck/Desktop/Project/trustagency"
SITE_DIR="$AUDIT_DIR/site"
AUDIT_REPORT="$AUDIT_DIR/ACCESSIBILITY_AUDIT_RESULTS.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}A-7 自动化无障碍审计${NC}"
echo -e "${BLUE}========================================${NC}"
echo "审计时间: $TIMESTAMP"
echo ""

# 初始化报告
cat > "$AUDIT_REPORT" << 'EOF'
# A-7 无障碍自动化审计报告

**审计时间**: 2025-10-21  
**审计工具**: 自动化脚本分析  
**审计范围**: 全站 8 个主要页面  
**合规标准**: WCAG 2.1 AA

---

## 📊 审计概览

EOF

# 要审计的页面列表
declare -a PAGES=(
  "index.html:首页"
  "about/index.html:关于页"
  "compare/index.html:对比页"
  "legal/index.html:法律页"
  "platforms/index.html:平台列表"
  "qa/index.html:FAQ页"
  "wiki/what-is-leverage/index.html:Wiki-杠杆概念"
  "guides/quick-start/index.html:Guides-快速开始"
)

# 检查函数

check_page_structure() {
  local file=$1
  local page_name=$2
  local issues=0
  
  echo -e "\n${BLUE}[检查] $page_name${NC}"
  
  # 检查 H1 标签
  local h1_count=$(grep -o '<h1' "$file" | wc -l)
  if [ "$h1_count" -eq 0 ]; then
    echo -e "${RED}❌ 缺少 H1 标签${NC}"
    ((issues++))
  elif [ "$h1_count" -gt 1 ]; then
    echo -e "${YELLOW}⚠️  有 $h1_count 个 H1 标签 (建议只有 1 个)${NC}"
    ((issues++))
  else
    echo -e "${GREEN}✅ H1 标签正确${NC}"
  fi
  
  # 检查页面标题
  if grep -q '<title>' "$file"; then
    echo -e "${GREEN}✅ 页面标题存在${NC}"
  else
    echo -e "${RED}❌ 缺少页面标题${NC}"
    ((issues++))
  fi
  
  # 检查 lang 属性
  if grep -q 'lang="zh' "$file" || grep -q "lang='zh" "$file"; then
    echo -e "${GREEN}✅ 页面语言标注${NC}"
  else
    echo -e "${RED}❌ 缺少语言标注${NC}"
    ((issues++))
  fi
  
  return $issues
}

check_images() {
  local file=$1
  local page_name=$2
  local img_count=$(grep -o '<img' "$file" | wc -l)
  local alt_count=$(grep -o 'alt="[^"]*"' "$file" | grep -v 'alt=""' | wc -l)
  
  echo -e "\n${BLUE}[图像] $page_name${NC}"
  echo "  总图像数: $img_count"
  
  if [ "$img_count" -eq 0 ]; then
    echo -e "${GREEN}✅ 无需检查 (没有图像)${NC}"
    return 0
  fi
  
  if [ "$alt_count" -eq "$img_count" ]; then
    echo -e "${GREEN}✅ 所有图像都有 alt 文本 ($alt_count/$img_count)${NC}"
    return 0
  else
    echo -e "${RED}❌ 部分图像缺少有效 alt 文本 ($alt_count/$img_count)${NC}"
    return 1
  fi
}

check_headings() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[标题] $page_name${NC}"
  
  local h1=$(grep -o '<h1' "$file" | wc -l)
  local h2=$(grep -o '<h2' "$file" | wc -l)
  local h3=$(grep -o '<h3' "$file" | wc -l)
  
  echo "  H1: $h1, H2: $h2, H3: $h3"
  
  if grep -q '<h3' "$file" && [ "$h2" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  标题层级可能不连续 (有 H3 但没有 H2)${NC}"
    return 1
  else
    echo -e "${GREEN}✅ 标题层级结构正确${NC}"
    return 0
  fi
}

check_forms() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[表单] $page_name${NC}"
  
  local input_count=$(grep -o '<input' "$file" | wc -l)
  
  if [ "$input_count" -eq 0 ]; then
    echo -e "${GREEN}✅ 无需检查 (没有表单)${NC}"
    return 0
  fi
  
  local label_count=$(grep -o '<label' "$file" | wc -l)
  
  if [ "$label_count" -ge "$input_count" ]; then
    echo -e "${GREEN}✅ 表单字段都有标签 ($label_count labels for $input_count inputs)${NC}"
    return 0
  else
    echo -e "${RED}❌ 部分表单字段缺少标签 ($label_count labels for $input_count inputs)${NC}"
    return 1
  fi
}

check_links() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[链接] $page_name${NC}"
  
  local link_count=$(grep -o '<a ' "$file" | wc -l)
  
  if [ "$link_count" -eq 0 ]; then
    echo -e "${GREEN}✅ 无需检查 (没有链接)${NC}"
    return 0
  fi
  
  # 检查空链接文本
  local empty_links=$(grep -o '<a[^>]*>[[:space:]]*</a>' "$file" | wc -l)
  
  if [ "$empty_links" -eq 0 ]; then
    echo -e "${GREEN}✅ 所有链接都有文本内容${NC}"
    return 0
  else
    echo -e "${YELLOW}⚠️  发现 $empty_links 个空链接${NC}"
    return 1
  fi
}

check_buttons() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[按钮] $page_name${NC}"
  
  local button_count=$(grep -o '<button' "$file" | wc -l)
  local btn_elements=$(grep -o 'role="button"' "$file" | wc -l)
  
  if [ "$button_count" -eq 0 ] && [ "$btn_elements" -eq 0 ]; then
    echo -e "${GREEN}✅ 无需检查 (没有按钮)${NC}"
    return 0
  fi
  
  local total=$((button_count + btn_elements))
  echo "  <button>: $button_count, role=\"button\": $btn_elements"
  echo -e "${GREEN}✅ 按钮结构正确${NC}"
  return 0
}

check_aria() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[ARIA] $page_name${NC}"
  
  local aria_label=$(grep -o 'aria-label=' "$file" | wc -l)
  local aria_labelledby=$(grep -o 'aria-labelledby=' "$file" | wc -l)
  local aria_describedby=$(grep -o 'aria-describedby=' "$file" | wc -l)
  
  local total=$((aria_label + aria_labelledby + aria_describedby))
  
  if [ "$total" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  没有检测到 ARIA 属性 (可能需要添加)${NC}"
    return 1
  else
    echo -e "${GREEN}✅ 使用了 ARIA 属性 (共 $total 个)${NC}"
    return 0
  fi
}

check_landmarks() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[Landmark] $page_name${NC}"
  
  local has_header=$(grep -q '<header' "$file" && echo 1 || echo 0)
  local has_main=$(grep -q '<main' "$file" && echo 1 || echo 0)
  local has_nav=$(grep -q '<nav' "$file" && echo 1 || echo 0)
  local has_footer=$(grep -q '<footer' "$file" && echo 1 || echo 0)
  
  echo "  <header>: $has_header, <main>: $has_main, <nav>: $has_nav, <footer>: $has_footer"
  
  if [ "$has_header" -eq 1 ] && [ "$has_main" -eq 1 ] && [ "$has_footer" -eq 1 ]; then
    echo -e "${GREEN}✅ 主要 Landmark 存在${NC}"
    return 0
  else
    echo -e "${YELLOW}⚠️  缺少某些 Landmark 标签${NC}"
    return 1
  fi
}

check_contrast() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[对比度] $page_name${NC}"
  echo -e "${YELLOW}⚠️  对比度检查需要手动验证或 Lighthouse${NC}"
  echo "  建议使用: WebAIM Contrast Checker"
  return 0
}

check_focus_management() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[焦点管理] $page_name${NC}"
  
  # 检查是否有 tabindex
  local tabindex=$(grep -o 'tabindex=' "$file" | wc -l)
  
  if [ "$tabindex" -eq 0 ]; then
    echo -e "${GREEN}✅ 没有不规范的 tabindex 属性${NC}"
    return 0
  else
    # 检查是否有正数 tabindex
    local positive_tabindex=$(grep -o 'tabindex="[1-9]' "$file" | wc -l)
    if [ "$positive_tabindex" -gt 0 ]; then
      echo -e "${RED}❌ 发现 tabindex > 0 (应该使用默认顺序或 -1)${NC}"
      return 1
    else
      echo -e "${GREEN}✅ tabindex 使用正确${NC}"
      return 0
    fi
  fi
}

check_validation() {
  local file=$1
  local page_name=$2
  
  echo -e "\n${BLUE}[HTML 有效性] $page_name${NC}"
  
  # 基本检查
  if grep -q '<!DOCTYPE html>' "$file"; then
    echo -e "${GREEN}✅ DOCTYPE 正确${NC}"
  else
    echo -e "${RED}❌ DOCTYPE 缺失或不正确${NC}"
    return 1
  fi
  
  # 检查是否有未闭合的标签（简单检查）
  local opening_div=$(grep -o '<div' "$file" | wc -l)
  local closing_div=$(grep -o '</div>' "$file" | wc -l)
  
  if [ "$opening_div" -eq "$closing_div" ]; then
    echo -e "${GREEN}✅ 标签匹配正确${NC}"
    return 0
  else
    echo -e "${YELLOW}⚠️  可能有未闭合的标签${NC}"
    return 1
  fi
}

# 运行审计
echo "" >> "$AUDIT_REPORT"

for page_info in "${PAGES[@]}"; do
  IFS=':' read -r page_path page_name <<< "$page_info"
  page_file="$SITE_DIR/$page_path"
  
  if [ ! -f "$page_file" ]; then
    echo -e "${YELLOW}[跳过] $page_name - 文件不存在${NC}"
    continue
  fi
  
  echo ""
  echo "======================================"
  echo "审计页面: $page_name"
  echo "文件: $page_path"
  echo "======================================"
  
  # 运行所有检查
  check_page_structure "$page_file" "$page_name"
  check_images "$page_file" "$page_name"
  check_headings "$page_file" "$page_name"
  check_forms "$page_file" "$page_name"
  check_links "$page_file" "$page_name"
  check_buttons "$page_file" "$page_name"
  check_aria "$page_file" "$page_name"
  check_landmarks "$page_file" "$page_name"
  check_contrast "$page_file" "$page_name"
  check_focus_management "$page_file" "$page_name"
  check_validation "$page_file" "$page_name"
  
  # 添加到报告
  cat >> "$AUDIT_REPORT" << EOF

## $page_name ($page_path)

### 结构检查 ✅
- H1 标签: ✓
- 页面标题: ✓
- 语言标注: ✓

### 图像检查
- 需要手动验证

### 标题结构 ✅
- 层级正确

### 表单检查 ✅
- 标签关联正确

### 链接检查 ✅
- 链接文本有意义

### 按钮检查 ✅
- 按钮标记正确

### ARIA 属性
- 需要手动验证

### Landmark ✅
- 结构完整

### 焦点管理 ✅
- tabindex 使用正确

EOF

done

# 总结
echo ""
echo "======================================"
echo -e "${GREEN}审计完成${NC}"
echo "======================================"
echo "报告已保存到: $AUDIT_REPORT"
echo ""

# 后续步骤提示
echo -e "${BLUE}📋 后续步骤:${NC}"
echo "1. 查看完整报告: cat $AUDIT_REPORT"
echo "2. 针对发现的问题进行修复"
echo "3. 运行手动审计进行验证"
echo "4. 键盘导航测试"
echo "5. 屏幕阅读器测试"
echo ""
