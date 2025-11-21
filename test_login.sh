#!/bin/bash
# 测试登录端点

echo "🔍 测试登录端点..."
echo ""

# 测试登录
echo "📨 发送登录请求:"
echo "用户名: admin"
echo "密码: admin123"
echo ""

curl -v -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>&1 | head -50

echo ""
echo "✅ 测试完成"
