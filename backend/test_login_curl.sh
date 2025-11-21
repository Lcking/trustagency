#!/bin/bash
# 测试登录API

echo "=========================================="
echo "🔐 测试登录 API"
echo "=========================================="
echo ""

ENDPOINT="http://localhost:8001/api/admin/login"

echo "📤 POST $ENDPOINT"
echo '📦 请求体: {"username":"admin","password":"admin123"}'
echo ""

curl -i -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  2>&1

echo ""
echo "=========================================="
