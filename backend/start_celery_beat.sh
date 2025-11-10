#!/bin/bash

# Celery Beat Scheduler 启动脚本
# 用于运行定时任务调度

# 设置环境变量
BACKEND_DIR="/Users/ck/Desktop/Project/trustagency/backend"
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# 启动 Celery Beat Scheduler
# 参数说明:
# -A: 指定 Celery 应用 (app.celery_app)
# beat: 启动 beat 调度器模式
# --loglevel: 日志级别 (info)
# --scheduler: 使用 RedBeat 以支持 Redis 持久化

cd "$BACKEND_DIR"

# 创建日志目录
mkdir -p /tmp/celery_logs

# 启动 Beat Scheduler
nohup celery -A app.celery_app beat \
    --loglevel=info \
    --scheduler=redbeat.RedBeatScheduler \
    --logfile=/tmp/celery_logs/beat.log \
    --pidfile=/tmp/celery_beat.pid \
    > /tmp/celery_logs/beat_output.log 2>&1 &

echo "✅ Celery Beat Scheduler 已启动"
echo "   PID: $(cat /tmp/celery_beat.pid 2>/dev/null || echo 'unknown')"
echo "   日志: /tmp/celery_logs/beat.log"

# 显示启动信息
sleep 1
tail -n 5 /tmp/celery_logs/beat.log
