#!/bin/bash

# 🔍 完整系统诊断脚本 - 检查所有已验收的功能

echo "========================================="
echo "🔍 完整系统诊断检查"
echo "========================================="
echo ""

API_URL="${1:-http://localhost:8001}"
echo "📍 API Base URL: $API_URL"
echo ""

# 1. 检查首页路由
echo "1️⃣  检查首页路由 (/)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
echo "Response Preview:"
echo "$BODY" | head -20
echo ""

# 2. 检查管理后台
echo "2️⃣  检查管理后台 (/admin/)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/admin/")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if [[ $HTTP_CODE == "200" ]]; then
    echo "✅ 管理后台可访问"
    # 检查是否包含HTML标签
    if echo "$BODY" | grep -q "<html\|<body\|<head"; then
        echo "✅ 返回HTML内容"
    else
        echo "❌ 返回非HTML内容"
    fi
else
    echo "❌ 管理后台无法访问 (HTTP $HTTP_CODE)"
fi
echo ""

# 3. 检查栏目API
echo "3️⃣  检查栏目管理API (/api/sections)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/sections")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if [[ $HTTP_CODE == "200" ]]; then
    echo "✅ 栏目API可访问"
    # 计算栏目数
    SECTION_COUNT=$(echo "$BODY" | grep -o '"id"' | wc -l)
    echo "📊 栏目数量: $SECTION_COUNT"
    echo "Response Preview:"
    echo "$BODY" | head -5
else
    echo "❌ 栏目API无法访问 (HTTP $HTTP_CODE)"
fi
echo ""

# 4. 检查分类API
echo "4️⃣  检查分类API (/api/categories)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/categories")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if [[ $HTTP_CODE == "200" ]]; then
    echo "✅ 分类API可访问"
    CATEGORY_COUNT=$(echo "$BODY" | grep -o '"id"' | wc -l)
    echo "📊 分类总数: $CATEGORY_COUNT"
else
    echo "❌ 分类API无法访问 (HTTP $HTTP_CODE)"
fi
echo ""

# 5. 检查文章API - by-section (QA)
echo "5️⃣  检查QA文章API (/api/articles/by-section/faq)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/articles/by-section/faq")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if [[ $HTTP_CODE == "200" ]]; then
    echo "✅ QA文章API可访问"
    ARTICLE_COUNT=$(echo "$BODY" | grep -o '"id"' | wc -l)
    echo "📊 FAQ文章数: $ARTICLE_COUNT"
else
    echo "❌ QA文章API无法访问 (HTTP $HTTP_CODE)"
fi
echo ""

# 6. 检查平台API
echo "6️⃣  检查平台API (/api/platforms)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/platforms")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if [[ $HTTP_CODE == "200" ]]; then
    echo "✅ 平台API可访问"
    PLATFORM_COUNT=$(echo "$BODY" | grep -o '"id"' | wc -l)
    echo "📊 平台数量: $PLATFORM_COUNT"
else
    echo "❌ 平台API无法访问 (HTTP $HTTP_CODE)"
fi
echo ""

# 7. 检查Schema标签
echo "7️⃣  检查Schema标签生成 (/article/test-article)"
echo "---"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/article/test-article" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if echo "$BODY" | grep -q "schema.org\|@context\|@type"; then
    echo "✅ Schema标签存在"
else
    echo "⚠️  Schema标签可能不存在或这篇文章不存在"
fi
echo ""

# 8. 检查认证端点
echo "8️⃣  检查认证API (/api/admin/login)"
echo "---"
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' \
    -w "\n%{http_code}" \
    "$API_URL/api/admin/login")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "HTTP Code: $HTTP_CODE"
if [[ $HTTP_CODE == "200" ]]; then
    echo "✅ 认证API工作正常"
    TOKEN=$(echo "$BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    if [ ! -z "$TOKEN" ]; then
        echo "✅ 获得Token: ${TOKEN:0:20}..."
    fi
else
    echo "❌ 认证失败 (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
fi
echo ""

echo "========================================="
echo "✅ 诊断检查完成"
echo "========================================="
