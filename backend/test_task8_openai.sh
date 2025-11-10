#!/bin/bash

# Task 8 OpenAI 集成测试脚本

echo "🚀 Task 8 - OpenAI 集成测试"
echo ""

BACKEND_DIR="/Users/ck/Desktop/Project/trustagency/backend"
BASE_URL="http://127.0.0.1:8001/api"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "========== 环境检查 =========="

# 检查 .env 文件
echo "\n1️⃣  检查 OpenAI 配置:"
if grep -q "OPENAI_API_KEY" .env; then
    echo "   ✅ .env 文件中已配置 OPENAI_API_KEY"
    OPENAI_KEY=$(grep "OPENAI_API_KEY" .env | cut -d'=' -f2)
    if [[ "$OPENAI_KEY" == "sk-"* ]]; then
        echo "   ✅ API 密钥格式正确 (sk-...)"
    else
        echo "   ⚠️  API 密钥需要替换为真实的 OpenAI API 密钥"
    fi
else
    echo "   ⚠️  .env 文件中未找到 OPENAI_API_KEY"
fi

echo "\n2️⃣  检查依赖包:"
python -c "import openai; print('   ✅ openai 已安装')" 2>/dev/null || echo "   ❌ openai 未安装"

# 检查服务
echo "\n========== 服务状态检查 =========="

echo "\n3️⃣  Redis 状态:"
redis-cli ping > /dev/null 2>&1 && echo "   ✅ Redis 运行中" || echo "   ❌ Redis 未运行"

echo "\n4️⃣  Celery Worker 状态:"
ps aux | grep -q "[c]elery.*worker" && echo "   ✅ Worker 运行中" || echo "   ❌ Worker 未运行"

echo "\n5️⃣  FastAPI 后端状态:"
curl -s "$BASE_URL/health" | grep -q "ok" && echo "   ✅ 后端运行中" || echo "   ❌ 后端未运行"

echo "\n========== OpenAI 服务检查 =========="

echo "\n6️⃣  测试 OpenAI 服务连接:"
python << 'PYEOF'
try:
    from app.services.openai_service import OpenAIService
    health = OpenAIService.health_check()
    print(f"   状态: {health['status']}")
    print(f"   信息: {health['message']}")
    if 'model' in health:
        print(f"   模型: {health['model']}")
except Exception as e:
    print(f"   ❌ 错误: {e}")
PYEOF

echo "\n========== 任务生成测试 =========="

echo "\n7️⃣  测试 Celery 任务提交:"
python << 'PYEOF'
from app.tasks.ai_generation import generate_single_article
from app.celery_app import app

print("   📤 提交单篇文章生成任务...")
result = generate_single_article.apply_async(
    args=("Python 最佳实践", "guide"),
    queue='ai_generation'
)
print(f"   ✅ 任务已提交: {result.id}")
print(f"   📊 任务状态: {result.status}")
PYEOF

echo "\n========== 配置说明 =========="

echo "\n需要的配置步骤:"
echo ""
echo "1. 获取 OpenAI API 密钥:"
echo "   - 访问 https://platform.openai.com/api-keys"
echo "   - 创建新的 API 密钥"
echo ""
echo "2. 更新 .env 文件:"
echo "   OPENAI_API_KEY=sk-your-actual-key"
echo ""
echo "3. 检查模型可用性:"
echo "   - gpt-3.5-turbo (默认，成本低)"
echo "   - gpt-4 (更强大，成本高)"
echo "   - 在 .env 中设置 OPENAI_MODEL"
echo ""
echo "4. 配置生成参数:"
echo "   OPENAI_MAX_TOKENS=2000 (最多生成 token 数)"
echo "   OPENAI_TEMPERATURE=0.7 (创意度: 0-1)"
echo ""

echo "\n========== 完整功能流程 =========="

echo "\n实现的功能:"
echo "✅ OpenAI 服务类 (app/services/openai_service.py)"
echo "✅ 单篇文章生成任务"
echo "✅ 批量文章生成任务"
echo "✅ 异步执行和进度跟踪"
echo "✅ 错误处理和重试机制"
echo "✅ OpenAI 健康检查端点"
echo ""

echo "\n========== API 端点 =========="

echo "\n新增端点:"
echo "✅ GET /api/admin/openai-health - 检查 OpenAI 服务"
echo "✅ POST /api/tasks/generate-articles - 提交批量生成任务"
echo "✅ GET /api/tasks/{task_id}/progress - 查询生成进度"
echo ""

echo "========== 测试完成 =========="
