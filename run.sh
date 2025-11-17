#!/bin/bash
# 启动并验证系统

set -e

echo "🚀 启动 TrustAgency 系统"

# 启动后端
echo "后端启动中..."
cd /Users/ck/Desktop/Project/trustagency/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 4

# 启动前端  
echo "前端启动中..."
cd /Users/ck/Desktop/Project/trustagency/site
python3 -m http.server 8001 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 2

# 验证服务
echo ""
echo "✅ 服务启动完成"
echo "后端 PID: $BACKEND_PID"
echo "前端 PID: $FRONTEND_PID"

# 测试
echo ""
echo "🧪 测试 API..."
curl -s -o /dev/null -w "后端 API: HTTP %{http_code}\n" http://localhost:8000/api/articles?limit=1
curl -s -o /dev/null -w "前端首页: HTTP %{http_code}\n" http://localhost:8001/
curl -s -o /dev/null -w "文章详情 (Slug): HTTP %{http_code}\n" http://localhost:8001/article/faq-what-is-leverage

echo ""
echo "✅ 系统就绪！"
echo ""
echo "访问地址:"
echo "  首页: http://localhost:8001/"
echo "  QA 页面: http://localhost:8001/qa/" 
echo "  Wiki 页面: http://localhost:8001/wiki/"
echo "  文章详情: http://localhost:8001/article/faq-what-is-leverage"
