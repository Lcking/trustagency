#!/bin/bash
# 自动保存脚本 - 每 30 分钟自动提交一次更改
# 用法: ./AUTO_SAVE_SCRIPT.sh 或在后台运行: nohup ./AUTO_SAVE_SCRIPT.sh &

WORK_DIR="/Users/ck/Desktop/Project/trustagency"
COMMIT_INTERVAL=1800  # 30 分钟（秒数）

cd "$WORK_DIR"

echo "🔄 自动保存进程已启动"
echo "工作目录: $WORK_DIR"
echo "保存间隔: $(($COMMIT_INTERVAL / 60)) 分钟"
echo "按 Ctrl+C 停止"

while true; do
    sleep $COMMIT_INTERVAL
    
    # 检查是否有未提交的更改
    if ! git diff-index --quiet HEAD --; then
        echo ""
        echo "📝 检测到更改，正在自动保存..."
        echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
        
        # 添加所有更改（除了未跟踪文件）
        git add -A
        
        # 提交
        COMMIT_MSG="auto: 自动保存进度 - $(date '+%Y%m%d-%H%M%S')"
        git commit -m "$COMMIT_MSG"
        
        if [ $? -eq 0 ]; then
            echo "✅ 自动保存成功"
            git log --oneline -1
        else
            echo "❌ 自动保存失败"
        fi
    else
        echo -n "✓ $(date '+%H:%M:%S') - 无新更改"
        echo ""
    fi
done
