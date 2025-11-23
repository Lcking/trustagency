#!/bin/bash
# Phase 4 快速恢复和验证指南
# 用于在系统卡顿后快速恢复工作

echo "========================================="
echo "    TrustAgency Phase 4 恢复指南"
echo "========================================="
echo ""

# 步骤1: 清理进程
echo "📋 步骤1: 清理系统进程..."
echo "   关闭Chrome浏览器..."
pkill -f "Chrome" 2>/dev/null || echo "   Chrome未运行"

echo "   关闭VSCode..."
pkill -f "Code" 2>/dev/null || echo "   VSCode未运行"

echo "   等待系统稳定..."
sleep 3

# 步骤2: 启动后端
echo ""
echo "🚀 步骤2: 启动后端服务..."
cd /Users/ck/Desktop/Project/trustagency/backend

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "   创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境并启动
source .venv/bin/activate
echo "   启动FastAPI服务 (端口 8001)..."
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/backend.log 2>&1 &

sleep 3

# 步骤3: 验证后端
echo ""
echo "✅ 步骤3: 验证后端服务..."
if curl -s http://127.0.0.1:8001/admin/ > /dev/null 2>&1; then
    echo "   ✓ 后端服务正常运行"
else
    echo "   ✗ 后端服务无响应"
    echo "   查看日志: tail -20 /tmp/backend.log"
fi

# 步骤4: 显示访问地址
echo ""
echo "🌐 步骤4: 访问应用..."
echo ""
echo "   后台地址: http://localhost:8001/admin/"
echo "   API文档:  http://localhost:8001/api/docs"
echo "   默认账号: admin"
echo "   默认密码: admin123"
echo ""

# 步骤5: 测试登录API
echo "🧪 步骤5: 测试登录API..."
echo ""
echo "   发送测试请求..."
response=$(curl -s -X POST http://127.0.0.1:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

if echo "$response" | grep -q "access_token"; then
    echo "   ✓ 登录API正常工作"
    echo "   返回Token: $(echo $response | cut -c1-50)..."
else
    echo "   ✗ 登录API返回错误"
    echo "   响应: $response"
fi

echo ""
echo "========================================="
echo "    恢复完成！"
echo "========================================="
echo ""
echo "💡 提示:"
echo "   1. 在浏览器中打开 http://localhost:8001/admin/"
echo "   2. 输入账号: admin"
echo "   3. 输入密码: admin123"
echo "   4. 点击登录"
echo ""
echo "📚 文档:"
echo "   - PHASE4_FINAL_SUMMARY.md (最终总结)"
echo "   - EMERGENCY_STATUS_REPORT.md (状态报告)"
echo "   - PHASE4_DEPLOYMENT_CHECKLIST.md (部署清单)"
echo ""
