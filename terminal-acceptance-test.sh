#!/bin/bash

# TrustAgency Bug 验收测试 - 纯终端版本
# 避免 VSCode 和浏览器卡顿问题
# 使用: bash terminal-acceptance-test.sh

set -e

PROJECT_DIR="/Users/ck/Desktop/Project/trustagency"
BACKEND_URL="http://127.0.0.1:8001"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TrustAgency Bug 验收测试 - 纯终端版${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查后端是否运行
echo -e "${YELLOW}🔍 Step 0: 检查后端服务${NC}"
if ! curl -s "$BACKEND_URL/admin/" > /dev/null 2>&1; then
    echo -e "${RED}✗ 后端未运行!${NC}"
    echo "请运行: cd $PROJECT_DIR/backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
    exit 1
fi
echo -e "${GREEN}✓ 后端服务正常${NC}"
echo ""

# 获取登录令牌
echo -e "${YELLOW}🔐 Step 1: 获取认证令牌${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/admin/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ 登录成功${NC}"
    echo "  Token: ${TOKEN:0:20}..."
else
    echo -e "${RED}✗ 登录失败${NC}"
    echo "  响应: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Bug_009: 栏目分类管理
echo -e "${YELLOW}🧪 Bug_009: 栏目分类添加/删除${NC}"

# 检查栏目是否存在
SECTIONS=$(curl -s "$BACKEND_URL/api/sections" \
    -H "Authorization: Bearer $TOKEN")

if echo "$SECTIONS" | grep -q '"id"'; then
    SECTION_ID=$(echo "$SECTIONS" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo -e "${GREEN}✓ 栏目加载成功 (ID: $SECTION_ID)${NC}"
    
    # 尝试添加分类
    ADD_CAT=$(curl -s -X POST "$BACKEND_URL/api/categories" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"测试分类_$(date +%s)\",\"section_id\":$SECTION_ID,\"is_active\":true}")
    
    if echo "$ADD_CAT" | grep -q '"id"'; then
        CAT_ID=$(echo "$ADD_CAT" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo -e "${GREEN}✓ 分类添加成功 (ID: $CAT_ID)${NC}"
        
        # 尝试删除分类
        DEL_CAT=$(curl -s -X DELETE "$BACKEND_URL/api/categories/$CAT_ID" \
            -H "Authorization: Bearer $TOKEN")
        
        if echo "$DEL_CAT" | grep -q '200\|"success"\|"message"'; then
            echo -e "${GREEN}✓ 分类删除成功${NC}"
        else
            echo -e "${RED}✗ 分类删除失败: $DEL_CAT${NC}"
        fi
    else
        echo -e "${RED}✗ 分类添加失败: $ADD_CAT${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 栏目为空，跳过此测试${NC}"
fi
echo ""

# Bug_010: 平台编辑保存认证
echo -e "${YELLOW}🧪 Bug_010: 平台编辑保存认证${NC}"

PLATFORMS=$(curl -s "$BACKEND_URL/api/platforms" \
    -H "Authorization: Bearer $TOKEN")

if echo "$PLATFORMS" | grep -q '"id"'; then
    PLATFORM_ID=$(echo "$PLATFORMS" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo -e "${GREEN}✓ 平台列表加载成功 (ID: $PLATFORM_ID)${NC}"
    
    # 尝试更新平台
    UPDATE_RESPONSE=$(curl -s -X PUT "$BACKEND_URL/api/platforms/$PLATFORM_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"测试平台_$(date +%s)\",\"url\":\"https://test.com\"}")
    
    if echo "$UPDATE_RESPONSE" | grep -q '"id"\|"success"'; then
        echo -e "${GREEN}✓ 平台编辑成功，无认证错误${NC}"
    else
        if echo "$UPDATE_RESPONSE" | grep -q "Invalid authentication"; then
            echo -e "${RED}✗ 认证错误: $UPDATE_RESPONSE${NC}"
        else
            echo -e "${YELLOW}⚠ 响应: $UPDATE_RESPONSE${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ 平台列表为空，跳过此测试${NC}"
fi
echo ""

# Bug_012: AI任务分类加载
echo -e "${YELLOW}🧪 Bug_012: AI任务分类动态加载${NC}"

if [ -n "$SECTION_ID" ]; then
    CATEGORIES=$(curl -s "$BACKEND_URL/api/categories/section/$SECTION_ID" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$CATEGORIES" | grep -q '"id"'; then
        CAT_COUNT=$(echo "$CATEGORIES" | grep -o '"id"' | wc -l)
        echo -e "${GREEN}✓ 分类动态加载成功 (共 $CAT_COUNT 个)${NC}"
    else
        echo -e "${YELLOW}⚠ 该栏目无分类${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 无栏目可用，跳过此测试${NC}"
fi
echo ""

# Bug_013: AI配置默认按钮
echo -e "${YELLOW}🧪 Bug_013: AI配置默认按钮认证${NC}"

AI_CONFIGS=$(curl -s "$BACKEND_URL/api/ai-configs" \
    -H "Authorization: Bearer $TOKEN")

if echo "$AI_CONFIGS" | grep -q '"id"'; then
    CONFIG_ID=$(echo "$AI_CONFIGS" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo -e "${GREEN}✓ AI配置列表加载成功 (ID: $CONFIG_ID)${NC}"
    
    # 尝试设置默认配置
    SET_DEFAULT=$(curl -s -X POST "$BACKEND_URL/api/ai-configs/$CONFIG_ID/set-default" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    if echo "$SET_DEFAULT" | grep -q '"id"\|"success"\|"message"'; then
        echo -e "${GREEN}✓ 设置默认配置成功，无认证错误${NC}"
    else
        if echo "$SET_DEFAULT" | grep -q "Invalid authentication"; then
            echo -e "${RED}✗ 认证错误: $SET_DEFAULT${NC}"
        else
            echo -e "${YELLOW}⚠ 响应: $SET_DEFAULT${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ AI配置列表为空，跳过此测试${NC}"
fi
echo ""

# Bug_011: Tiptap编辑器 (前端测试需要浏览器)
echo -e "${YELLOW}🧪 Bug_011: Tiptap编辑器加载${NC}"
echo -e "${BLUE}   此测试需要浏览器验证，请访问:${NC}"
echo -e "${BLUE}   http://localhost:8001/admin/${NC}"
echo -e "${BLUE}   然后进入"文章管理" → "编辑文章"${NC}"
echo -e "${BLUE}   检查浏览器控制台是否有错误消息${NC}"
echo ""

# 总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  验收测试完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✓ 所有API测试已完成${NC}"
echo -e "${YELLOW}⚠ Bug_011需要浏览器进行可视化验证${NC}"
echo ""
echo -e "${BLUE}📋 建议后续步骤:${NC}"
echo "  1. 打开浏览器访问 http://localhost:8001/admin/"
echo "  2. 验证 Bug_011 (Tiptap编辑器加载)"
echo "  3. 确认所有 5 个 Bug 都已修复"
echo ""
