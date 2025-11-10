#!/bin/bash
# 诊断登录问题

echo "🔍 诊断登录问题"
echo "=================================="
echo ""

# 1. 检查后端容器日志
echo "1️⃣  查看后端容器日志（最后 30 行）"
echo "=================================="
docker-compose logs backend --tail=30

echo ""
echo "2️⃣  测试登录端点"
echo "=================================="
echo "发送 POST 请求到 /api/admin/login"
curl -v -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>&1 | head -50

echo ""
echo "3️⃣  检查管理员用户是否存在"
echo "=================================="
echo "连接到数据库检查..."
docker exec trustagency-db psql -U trustagency -d trustagency -c "SELECT * FROM admin_user LIMIT 5;"

echo ""
echo "✅ 诊断完成"
