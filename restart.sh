#!/bin/bash
# 简单的重启脚本

cd /Users/ck/Desktop/Project/trustagency

# 完全停止
docker-compose down

# 启动
docker-compose up -d

# 等待
sleep 20

# 测试
curl -s http://localhost:8001/admin/ | head -5
