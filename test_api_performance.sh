#!/bin/bash

# ============================================================================
# Task 5.1.3 - 后端 API 响应时间分析工具
# 用途: 测试所有 API 端点的响应时间
# ============================================================================

echo "🔍 API 响应时间分析"
echo "=================================="
echo ""

API_BASE="http://localhost:8001"
WARN_THRESHOLD=500  # 毫秒
ERROR_THRESHOLD=1000  # 毫秒

# 测试的 API 端点
ENDPOINTS=(
    "/api/health"
    "/api/sections"
    "/api/categories"
    "/api/platforms"
    "/api/articles?skip=0&limit=5"
    "/api/tasks?skip=0&limit=5"
)

TOTAL=0
SLOW=0
SLOW_APIS=()

echo "测试 API 响应时间..."
echo ""

for endpoint in "${ENDPOINTS[@]}"; do
    START=$(date +%s%N | cut -b1-13)
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE$endpoint" 2>/dev/null)
    END=$(date +%s%N | cut -b1-13)
    
    TIME=$((END - START))
    ((TOTAL++))
    
    if [ "$RESPONSE" = "200" ]; then
        STATUS="✅"
        
        if [ $TIME -lt $WARN_THRESHOLD ]; then
            COLOR="\033[0;32m"  # 绿色
        elif [ $TIME -lt $ERROR_THRESHOLD ]; then
            COLOR="\033[1;33m"  # 黄色
            ((SLOW++))
            SLOW_APIS+=("$endpoint ($TIME ms)")
        else
            COLOR="\033[0;31m"  # 红色
            ((SLOW++))
            SLOW_APIS+=("$endpoint ($TIME ms)")
        fi
        
        echo -e "$STATUS ${COLOR}${endpoint}: ${TIME}ms\033[0m"
    else
        echo "❌ $endpoint: HTTP $RESPONSE (超时或错误)"
        ((SLOW++))
    fi
done

echo ""
echo "=================================="
echo "📊 性能统计"
echo "=================================="
echo "总请求数: $TOTAL"
echo "快速请求: $((TOTAL - SLOW)) (< 500ms)"
echo "缓慢请求: $SLOW (>= 500ms)"

if [ $SLOW -gt 0 ]; then
    echo ""
    echo "⚠️  缓慢的 API:"
    for api in "${SLOW_APIS[@]}"; do
        echo "   - $api"
    done
fi

echo ""
echo "✅ 分析完成"
echo ""
echo "建议:"
echo "  • 如果所有 API 都 < 500ms，性能良好 ✅"
echo "  • 如果有 API >= 500ms，需要优化"
echo "  • 可以考虑:"
echo "    1. 添加数据库索引"
echo "    2. 实现查询结果缓存"
echo "    3. 优化 SQL 查询"
