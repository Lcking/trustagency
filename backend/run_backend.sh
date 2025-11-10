#!/bin/bash
# 后端启动和维护脚本 - 在后台运行

cd /Users/ck/Desktop/Project/trustagency/backend

# 设置日志文件
LOG_FILE="/tmp/trustagency_backend.log"

echo "🚀 启动 TrustAgency 后端服务器..." | tee $LOG_FILE
echo "日志文件: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# 设置环境并启动
PYTHONPATH=/Users/ck/Desktop/Project/trustagency/backend \
/Users/ck/Desktop/Project/trustagency/backend/venv/bin/python -m uvicorn app.main:app --reload --port 8001 \
  >> $LOG_FILE 2>&1 &

echo "✅ 后端进程已启动 (PID: $!)"
echo "📊 访问地址: http://localhost:8001"
echo "📖 API 文档: http://localhost:8001/api/docs"
echo "🔍 ReDoc: http://localhost:8001/api/redoc"
echo ""
echo "实时查看日志: tail -f $LOG_FILE"
