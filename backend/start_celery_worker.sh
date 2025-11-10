#!/bin/bash

# Celery Worker 启动脚本
# 用于运行异步任务处理

# 设置环境变量
BACKEND_DIR="/Users/ck/Desktop/Project/trustagency/backend"
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# 启动 Celery Worker
# 参数说明:
# -A: 指定 Celery 应用 (app.celery_app)
# worker: 启动 worker 模式
# --loglevel: 日志级别 (info)
# --concurrency: 并发工作进程数 (4)
# --pool: 工作池类型 (prefork 对 macOS 友好)
# --autoscale: 自动扩展 (不超过8个进程)

cd "$BACKEND_DIR"

# 创建日志目录
mkdir -p /tmp/celery_logs

# 启动 Worker
nohup celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --pool=prefork \
    --autoscale=8,4 \
    --time-limit=30m \
    --soft-time-limit=25m \
    --logfile=/tmp/celery_logs/worker.log \
    --pidfile=/tmp/celery_worker.pid \
    > /tmp/celery_logs/worker_output.log 2>&1 &

echo "✅ Celery Worker 已启动"
echo "   PID: $(cat /tmp/celery_worker.pid 2>/dev/null || echo 'unknown')"
echo "   日志: /tmp/celery_logs/worker.log"

# 显示启动信息
sleep 1
tail -n 5 /tmp/celery_logs/worker.log
