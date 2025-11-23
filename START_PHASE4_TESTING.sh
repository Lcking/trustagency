#!/bin/bash
# ============================================================
# Phase 4 完整功能测试启动脚本
# ============================================================
# 
# 说明:
# 1. 这个脚本会启动后端服务和测试套件
# 2. 如果需要停止,按 Ctrl+C
# 3. 需要保证在项目根目录运行
# ============================================================

PROJECT_ROOT="/Users/ck/Desktop/Project/trustagency"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🚀 Phase 4 功能测试启动器${NC}"
echo -e "${BLUE}================================${NC}"

# 检查Python环境
echo -e "\n${YELLOW}✓ 环境检查${NC}"
python3 --version

# 检查后端文件
if [ ! -f "$PROJECT_ROOT/backend/app/main.py" ]; then
    echo -e "${RED}✗ 错误: 后端入口文件不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 后端入口文件存在${NC}"

# 进入后端目录
cd "$PROJECT_ROOT/backend" || exit 1

# 清理之前的Python进程 (可选)
echo -e "\n${YELLOW}✓ 清理之前的进程${NC}"
pkill -f "python.*app/main.py" 2>/dev/null || true

# 等待一下
sleep 1

# 启动后端服务
echo -e "\n${YELLOW}✓ 启动后端服务${NC}"
echo -e "${BLUE}命令: PYTHONPATH=. python3 app/main.py${NC}"
echo ""

PYTHONPATH=. python3 app/main.py &
BACKEND_PID=$!

# 等待服务启动
sleep 3

# 测试后端健康状态
echo -e "\n${YELLOW}✓ 健康检查${NC}"
HEALTH_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/admin/health" 2>/dev/null)
if [ -n "$HEALTH_RESPONSE" ]; then
    echo -e "${GREEN}✓ 后端健康检查通过${NC}"
    echo "响应: $HEALTH_RESPONSE"
else
    echo -e "${YELLOW}⚠ 健康检查暂未获得响应 (可能在启动中)${NC}"
fi

# 提示用户
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✓ 后端服务已启动${NC}"
echo -e "${BLUE}================================${NC}"

cat << 'EOF'

📝 后续测试步骤:

1️⃣ 浏览器打开前端:
   - 浏览器访问: http://localhost:8001/admin/
   - 应该看到登录页面

2️⃣ 测试登录:
   - 用户名: admin
   - 密码: admin123
   - 点击登录

3️⃣ 验证认证:
   - 登录后应显示主页
   - 检查token是否自动保存
   - 验证API调用是否带token

4️⃣ 测试模块化功能:
   - 浏览各个菜单部分
   - 检查section导航
   - 验证错误处理

5️⃣ 浏览器开发者工具检查:
   - 打开DevTools (F12)
   - 检查Console是否有错误
   - 验证Network请求是否正确

6️⃣ 停止服务:
   - 在终端按 Ctrl+C 停止服务

📊 测试页面:
   - 完整功能测试: http://localhost:8001/admin/test-phase4.html
   - 浏览器加载测试: http://localhost:8001/admin/test-browser-load.html

⚡ 快速测试命令:

登录测试:
curl -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

获取数据 (需要有效的token):
curl -X GET http://localhost:8001/api/admin/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

EOF

echo -e "\n${YELLOW}按 Ctrl+C 停止服务${NC}\n"

# 保持脚本运行
wait $BACKEND_PID
