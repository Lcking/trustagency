#!/bin/bash
# API 验证脚本

echo "🔍 测试后端API..."
echo ""

# 测试平台列表
echo "1️⃣  获取平台列表:"
echo "---"
curl -s http://localhost:8001/api/platforms | jq '.' 2>/dev/null || echo "无法连接或无法解析JSON"
echo ""

# 测试分类列表
echo "2️⃣  获取分类列表 (前5个):"
echo "---"
curl -s http://localhost:8001/api/categories | jq '.[0:5]' 2>/dev/null || echo "无法连接"
echo ""

# 测试栏目列表
echo "3️⃣  获取栏目列表:"
echo "---"
curl -s http://localhost:8001/api/sections | jq '.' 2>/dev/null || echo "无法连接"
echo ""

# 测试AI配置
echo "4️⃣  获取AI配置:"
echo "---"
curl -s http://localhost:8001/api/ai-configs | jq '.' 2>/dev/null || echo "无法连接"
echo ""

echo "✅ API 测试完成"
