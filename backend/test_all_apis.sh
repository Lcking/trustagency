#!/bin/bash
# 全面测试 API

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2Mzc3NTkxMn0.WvVYiPcovkBFYG8Pa38-E2nkzWGXvSjohNxRvr3Ojt8"

echo "=========================================="
echo "🧪 全面测试 API"
echo "=========================================="
echo ""

# 测试平台列表
echo "1️⃣  测试获取平台列表..."
curl -s http://localhost:8001/api/platforms | jq '.[] | {id, name, platform_type}' | head -20
echo ""

# 测试分类列表
echo "2️⃣  测试获取分类列表..."
curl -s http://localhost:8001/api/categories | jq '.[] | {id, name, section_id}' | head -10
echo ""

# 测试栏目列表
echo "3️⃣  测试获取栏目列表..."
curl -s http://localhost:8001/api/sections | jq '.[] | {id, name}'
echo ""

# 测试 AI 配置
echo "4️⃣  测试获取 AI 配置..."
curl -s http://localhost:8001/api/ai-configs | jq '.[] | {id, name, provider, is_active}' | head -10
echo ""

echo "=========================================="
echo "✅ 测试完成"
echo "=========================================="
