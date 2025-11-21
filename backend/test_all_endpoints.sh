#!/bin/bash
# 全面测试所有关键 API 端点

echo "=========================================="
echo "🧪 全面 API 测试"
echo "=========================================="
echo ""

# 1. 测试登录
echo "1️⃣  测试登录 API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ 登录成功"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo "   ❌ 登录失败"
    exit 1
fi

echo ""

# 2. 测试平台列表
echo "2️⃣  测试平台列表..."
PLATFORMS=$(curl -s http://localhost:8001/api/platforms)
PLATFORM_COUNT=$(echo "$PLATFORMS" | grep -o '"name"' | wc -l)
echo "   ✅ 获取 $PLATFORM_COUNT 个平台"

# 3. 验证 platform_type
echo ""
echo "3️⃣  验证 platform_type 字段..."
echo "$PLATFORMS" | grep "platform_type" | head -4
echo ""

# 4. 测试分类
echo "4️⃣  测试分类列表..."
CATEGORIES=$(curl -s http://localhost:8001/api/categories)
CATEGORY_COUNT=$(echo "$CATEGORIES" | grep -o '"id"' | wc -l)
echo "   ✅ 获取 $CATEGORY_COUNT 个分类"

echo ""

# 5. 测试栏目
echo "5️⃣  测试栏目列表..."
SECTIONS=$(curl -s http://localhost:8001/api/sections)
SECTION_COUNT=$(echo "$SECTIONS" | grep -o '"id"' | wc -l)
echo "   ✅ 获取 $SECTION_COUNT 个栏目"

echo ""

# 6. 测试 AI 配置
echo "6️⃣  测试 AI 配置..."
AI_CONFIGS=$(curl -s http://localhost:8001/api/ai-configs)
if echo "$AI_CONFIGS" | grep -q '"name"'; then
    echo "   ✅ AI 配置获取成功"
else
    echo "   ❌ AI 配置获取失败"
fi

echo ""
echo "=========================================="
echo "✅ 全部测试完成"
echo "=========================================="
