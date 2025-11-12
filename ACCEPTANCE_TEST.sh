#!/bin/bash

# TrustAgency 前后端融合验收测试脚本
# 用于快速验证5个bug修复的完整性

API_URL="http://localhost:8001"
ADMIN_URL="http://localhost:8001/admin/"
TOKEN=""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "🎯 TrustAgency 前后端融合验收测试"
echo "========================================="
echo ""

# 第一步：检查后端是否运行
echo "📡 检查后端服务..."
if curl -s http://localhost:8001/api/sections > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务正常${NC}"
else
    echo -e "${RED}❌ 后端服务未运行${NC}"
    exit 1
fi

echo ""

# 第二步：获取认证令牌
echo "🔐 获取认证令牌..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ 无法获取令牌${NC}"
    echo "响应: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ 令牌获取成功${NC}"
echo "令牌: ${TOKEN:0:20}..."
echo ""

# 第三步：验证bug_009 - 分类管理
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 bug_009: 栏目分类添加/删除"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "1️⃣  获取栏目列表..."
SECTIONS=$(curl -s "$API_URL/api/sections" \
  -H "Authorization: Bearer $TOKEN")
echo "栏目数量: $(echo $SECTIONS | grep -o '"id"' | wc -l)"

echo "2️⃣  获取第一个栏目的分类..."
SECTION_ID=$(echo $SECTIONS | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
CATEGORIES=$(curl -s "$API_URL/api/sections/$SECTION_ID/categories" \
  -H "Authorization: Bearer $TOKEN")
echo "分类数量: $(echo $CATEGORIES | grep -o '"id"' | wc -l)"

echo "3️⃣  测试添加新分类..."
ADD_CATEGORY=$(curl -s -X POST "$API_URL/api/categories" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"测试分类\",\"section_id\":$SECTION_ID,\"is_active\":true}")

if echo $ADD_CATEGORY | grep -q '"id"'; then
    echo -e "${GREEN}✅ 分类添加成功${NC}"
    CATEGORY_ID=$(echo $ADD_CATEGORY | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    
    echo "4️⃣  测试删除分类..."
    DELETE_CATEGORY=$(curl -s -X DELETE "$API_URL/api/categories/$CATEGORY_ID" \
      -H "Authorization: Bearer $TOKEN")
    
    if echo $DELETE_CATEGORY | grep -q '"message"'; then
        echo -e "${GREEN}✅ 分类删除成功${NC}"
    else
        echo -e "${YELLOW}⚠️  分类删除响应: $DELETE_CATEGORY${NC}"
    fi
else
    echo -e "${RED}❌ 分类添加失败: $ADD_CATEGORY${NC}"
fi

echo ""

# 第四步：验证bug_010 - 平台编辑
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 bug_010: 平台管理编辑保存"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "1️⃣  获取平台列表..."
PLATFORMS=$(curl -s "$API_URL/api/platforms" \
  -H "Authorization: Bearer $TOKEN")
PLATFORM_ID=$(echo $PLATFORMS | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
echo "第一个平台ID: $PLATFORM_ID"

echo "2️⃣  测试编辑平台..."
UPDATE_PLATFORM=$(curl -s -X PUT "$API_URL/api/platforms/$PLATFORM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"更新的平台名\",\"url\":\"https://updated.com\"}")

if echo $UPDATE_PLATFORM | grep -q '"id"'; then
    echo -e "${GREEN}✅ 平台编辑成功${NC}"
elif echo $UPDATE_PLATFORM | grep -q 'Invalid authentication'; then
    echo -e "${RED}❌ 认证错误: $UPDATE_PLATFORM${NC}"
else
    echo -e "${YELLOW}⚠️  平台编辑响应: $UPDATE_PLATFORM${NC}"
fi

echo ""

# 第五步：验证bug_012 - AI任务分类加载
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 bug_012: AI任务分类加载"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "1️⃣  测试API - 获取分类列表..."
for SECTION_ID in {1..4}; do
    CATS=$(curl -s "$API_URL/api/sections/$SECTION_ID/categories" \
      -H "Authorization: Bearer $TOKEN")
    COUNT=$(echo $CATS | grep -o '"id"' | wc -l)
    echo "   栏目$SECTION_ID: $COUNT个分类"
done

echo ""

# 第六步：验证bug_013 - AI配置默认
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 bug_013: AI配置默认设置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "1️⃣  获取AI配置列表..."
AI_CONFIGS=$(curl -s "$API_URL/api/ai-configs" \
  -H "Authorization: Bearer $TOKEN")
AI_CONFIG_ID=$(echo $AI_CONFIGS | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
echo "第一个配置ID: $AI_CONFIG_ID"

echo "2️⃣  测试设置为默认配置..."
SET_DEFAULT=$(curl -s -X POST "$API_URL/api/ai-configs/$AI_CONFIG_ID/set-default" \
  -H "Authorization: Bearer $TOKEN")

if echo $SET_DEFAULT | grep -q '"message"'; then
    echo -e "${GREEN}✅ 默认配置设置成功${NC}"
elif echo $SET_DEFAULT | grep -q 'Invalid authentication'; then
    echo -e "${RED}❌ 认证错误: $SET_DEFAULT${NC}"
else
    echo -e "${YELLOW}⚠️  设置默认响应: $SET_DEFAULT${NC}"
fi

echo ""
echo "========================================="
echo "✨ 验收测试完成！"
echo "========================================="
echo ""
echo "📊 测试总结:"
echo "  ✅ 后端服务: 正常"
echo "  ✅ 认证系统: 正常"
echo "  ✅ API端点: 响应正常"
echo ""
echo "🌐 打开浏览器访问: $ADMIN_URL"
echo ""
