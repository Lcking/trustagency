#!/bin/bash

# SEO Schema 验证脚本
# 检查所有页面的 Schema 标记和元标签

echo "🔍 开始 Schema 标记验证..."
echo "=================================="
echo ""

# 定义检查的页面
declare -a pages=(
    "/index.html"
    "/platforms/index.html"
    "/compare/index.html"
    "/about/index.html"
    "/legal/index.html"
    "/qa/index.html"
    "/wiki/index.html"
    "/wiki/what-is-leverage/index.html"
    "/guides/index.html"
    "/guides/quick-start/index.html"
)

# 基础路径
BASE_PATH="/Users/ck/Desktop/Project/trustagency/site"

# 统计变量
total_files=0
files_with_breadcrumb=0
files_with_og_image=0
files_with_canonical=0
files_with_description=0

# 检查每个文件
for page in "${pages[@]}"; do
    file="$BASE_PATH$page"
    
    if [ -f "$file" ]; then
        ((total_files++))
        echo "📄 检查: $page"
        
        # 检查 BreadcrumbList Schema
        if grep -q '"@type".*"BreadcrumbList"' "$file" 2>/dev/null; then
            echo "  ✅ BreadcrumbList Schema: 存在"
            ((files_with_breadcrumb++))
        else
            echo "  ⚠️  BreadcrumbList Schema: 缺失"
        fi
        
        # 检查 og:image
        if grep -q 'property="og:image"' "$file" 2>/dev/null; then
            echo "  ✅ og:image 标签: 存在"
            ((files_with_og_image++))
        else
            echo "  ⚠️  og:image 标签: 缺失"
        fi
        
        # 检查 Canonical
        if grep -q 'rel="canonical"' "$file" 2>/dev/null; then
            echo "  ✅ Canonical 标签: 存在"
            ((files_with_canonical++))
        else
            echo "  ❌ Canonical 标签: 缺失"
        fi
        
        # 检查 Meta Description
        if grep -q 'name="description"' "$file" 2>/dev/null; then
            echo "  ✅ Meta Description: 存在"
            ((files_with_description++))
        else
            echo "  ❌ Meta Description: 缺失"
        fi
        
        echo ""
    else
        echo "❌ 文件不存在: $file"
        echo ""
    fi
done

# 显示统计
echo "=================================="
echo "📊 验证统计:"
echo "  总检查文件数: $total_files"
echo "  ✅ BreadcrumbList 完成率: $files_with_breadcrumb/$total_files ($(( $files_with_breadcrumb * 100 / $total_files ))%)"
echo "  ✅ og:image 完成率: $files_with_og_image/$total_files ($(( $files_with_og_image * 100 / $total_files ))%)"
echo "  ✅ Canonical 完成率: $files_with_canonical/$total_files ($(( $files_with_canonical * 100 / $total_files ))%)"
echo "  ✅ Meta Description 完成率: $files_with_description/$total_files ($(( $files_with_description * 100 / $total_files ))%)"
echo ""

# 检查 Sitemap
echo "🗺️  Sitemap 检查:"
sitemap_file="$BASE_PATH/sitemap.xml"
if [ -f "$sitemap_file" ]; then
    url_count=$(grep -c "<url>" "$sitemap_file" 2>/dev/null)
    echo "  ✅ Sitemap 存在"
    echo "  📍 URL 条目数: $url_count"
    
    if grep -q "2025-10-21" "$sitemap_file" 2>/dev/null; then
        echo "  ✅ 日期已更新到: 2025-10-21"
    else
        echo "  ⚠️  Sitemap 日期可能过旧"
    fi
else
    echo "  ❌ Sitemap 不存在"
fi

echo ""
echo "🤖 robots.txt 检查:"
robots_file="$BASE_PATH/robots.txt"
if [ -f "$robots_file" ]; then
    echo "  ✅ robots.txt 存在"
    
    if grep -q "Sitemap:" "$robots_file" 2>/dev/null; then
        echo "  ✅ Sitemap 行存在"
    else
        echo "  ⚠️  Sitemap 行缺失"
    fi
else
    echo "  ❌ robots.txt 不存在"
fi

echo ""
echo "=================================="
echo "✨ 验证完成！"
echo ""
echo "下一步:"
echo "1. 检查上面的 ⚠️ 警告项"
echo "2. 运行 Lighthouse 审计: Chrome DevTools > Lighthouse > SEO"
echo "3. 验证 Schema: https://validator.schema.org/"
echo "4. 使用 schema-validation-tool.html 进行交互式验证"
