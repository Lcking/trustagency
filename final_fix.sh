#!/usr/bin/env bash
# 最终修复脚本 v2

echo "================================================"
echo "🔧 Admin 404 问题 - 最终修复脚本"
echo "================================================"

# 清理
echo "清理进程和缓存..."
pkill -9 -f "uvicorn\|celery" 2>/dev/null
sleep 1
find /Users/ck/Desktop/Project/trustagency/backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /Users/ck/Desktop/Project/trustagency/backend -name "*.pyc" -delete 2>/dev/null

# 验证文件
if [ ! -f "/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html" ]; then
    echo "❌ Admin 文件不存在!"
    exit 1
fi

# 启动
echo "启动后端..."
cd /Users/ck/Desktop/Project/trustagency/backend
source venv/bin/activate 2>/dev/null
python -m uvicorn app.main:app --port 8001 --reload
