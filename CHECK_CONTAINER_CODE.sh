#!/bin/bash
# 在容器中测试 main.py 代码

echo "🔍 检查容器内的 main.py 文件..."
docker exec trustagency-backend cat /app/app/main.py | head -70

echo ""
echo "✅ 检查完成"
