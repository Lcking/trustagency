#!/bin/bash
# 执行修复 - 复制粘贴到终端运行

cd /Users/ck/Desktop/Project/trustagency && \
docker-compose down && \
docker-compose up -d && \
sleep 20 && \
echo "=====================================" && \
echo "测试管理后台访问" && \
echo "=====================================" && \
curl -s http://localhost:8001/admin/ | head -20 && \
echo "" && \
echo "=====================================" && \
echo "测试完成！" && \
echo "=====================================" && \
echo "" && \
echo "✅ 如果看到 <!DOCTYPE html，修复成功！" && \
echo "❌ 如果看到 \"Admin page not found\"，可能需要等待重载（5-10秒后再试）" && \
echo ""
