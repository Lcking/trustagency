#!/bin/bash

# ============================================================
# TrustAgency 前后端一键启动脚本
# ============================================================

set -e

PROJECT_DIR="/Users/ck/Desktop/Project/trustagency"
BACKEND_DIR="$PROJECT_DIR/backend"
LOG_FILE="/tmp/trustagency_startup.log"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     TrustAgency 前后端一键启动脚本 v1.0              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查Python环境
echo -e "${YELLOW}[1/5] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
echo ""

# 检查依赖
echo -e "${YELLOW}[2/5] 检查依赖...${NC}"
cd "$BACKEND_DIR"
if ! python3 -c "import fastapi; import uvicorn; import sqlalchemy" 2>/dev/null; then
    echo -e "${YELLOW}⚙️  安装依赖...${NC}"
    pip install -q -r requirements.txt
fi
echo -e "${GREEN}✅ 依赖检查完成${NC}"
echo ""

# 检查端口
echo -e "${YELLOW}[3/5] 检查端口...${NC}"
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null; then
    echo -e "${YELLOW}⚠️  端口8001已被占用，正在清理...${NC}"
    kill $(lsof -t -i:8001) 2>/dev/null || true
    sleep 2
fi
echo -e "${GREEN}✅ 端口8001可用${NC}"
echo ""

# 启动后端
echo -e "${YELLOW}[4/5] 启动FastAPI后端服务...${NC}"
cd "$BACKEND_DIR"
nohup python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    > "$LOG_FILE" 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✅ 后端进程已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
echo -e "${YELLOW}[5/5] 等待后端启动完成...${NC}"
sleep 3

# 验证后端
MAX_RETRIES=10
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8001/api/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务已就绪${NC}"
        break
    fi
    RETRY=$((RETRY + 1))
    if [ $RETRY -eq $MAX_RETRIES ]; then
        echo -e "${RED}❌ 后端启动失败${NC}"
        echo -e "${RED}日志:${NC}"
        tail -20 "$LOG_FILE"
        exit 1
    fi
    sleep 1
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}      ✅ 系统启动成功！${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 显示访问信息
echo -e "${YELLOW}📋 系统访问信息:${NC}"
echo ""
echo -e "${GREEN}前端管理界面:${NC}      http://localhost:8001/admin/"
echo -e "${GREEN}API文档:${NC}          http://localhost:8001/api/docs"
echo -e "${GREEN}OpenAPI JSON:${NC}     http://localhost:8001/openapi.json"
echo ""
echo -e "${YELLOW}登录凭证:${NC}"
echo -e "  用户名: ${GREEN}admin${NC}"
echo -e "  密码: ${GREEN}admin123${NC}"
echo ""

# 显示系统状态
echo -e "${YELLOW}🔍 系统状态检查:${NC}"
echo ""

# 检查后端服务
if curl -s http://localhost:8001/api/sections > /dev/null 2>&1; then
    SECTION_COUNT=$(curl -s http://localhost:8001/api/sections | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
    echo -e "${GREEN}✅ 后端服务${NC}          http://localhost:8001"
    echo -e "   栏目数量: $SECTION_COUNT"
else
    echo -e "${RED}❌ 后端服务${NC}          无法连接"
fi

# 检查登录API
if curl -s -X POST http://localhost:8001/api/admin/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 认证系统${NC}          正常"
else
    echo -e "${YELLOW}⚠️  认证系统${NC}          需要检查"
fi

# 获取数据库统计
DB_FILE="$BACKEND_DIR/trustagency.db"
if [ -f "$DB_FILE" ]; then
    echo -e "${GREEN}✅ 数据库${NC}            存在 ($(ls -lh "$DB_FILE" | awk '{print $5}'))"
else
    echo -e "${YELLOW}⚠️  数据库${NC}            不存在"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}📚 快速命令:${NC}"
echo ""
echo "  # 查看服务状态"
echo "  ps aux | grep uvicorn"
echo ""
echo "  # 查看实时日志"
echo "  tail -f $LOG_FILE"
echo ""
echo "  # 停止服务"
echo "  kill $BACKEND_PID"
echo ""
echo "  # 运行验收测试"
echo "  bash $PROJECT_DIR/ACCEPTANCE_TEST.sh"
echo ""
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 打开浏览器 (macOS特定)
if command -v open &> /dev/null; then
    echo -e "${YELLOW}💻 正在打开浏览器...${NC}"
    sleep 2
    open "http://localhost:8001/admin/"
fi

echo ""
echo -e "${GREEN}🎉 TrustAgency系统已就绪！${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 保持进程运行
wait $BACKEND_PID
