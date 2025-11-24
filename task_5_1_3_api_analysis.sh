#!/bin/bash

# ============================================================================
# Task 5.1.3: 后端 API 响应时间分析
# 用途: 分析所有 API 的响应时间，识别性能瓶颈
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║       Task 5.1.3: 后端 API 响应时间分析                              ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

API_URL="http://localhost:8001"
REPORT_FILE="API_PERFORMANCE_REPORT_$(date +%Y%m%d_%H%M%S).md"

# 测试 API 的函数
test_api() {
    local endpoint=$1
    local method=${2:-GET}
    local description=$3
    
    START=$(date +%s%N | cut -b1-13)
    
    if [ "$method" = "GET" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint")
    fi
    
    END=$(date +%s%N | cut -b1-13)
    DURATION=$((END - START))
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)
    
    # 检查响应大小
    BODY_SIZE=$(echo -n "$BODY" | wc -c)
    
    # 性能等级
    if [ $DURATION -lt 100 ]; then
        LEVEL="🟢 极快"
    elif [ $DURATION -lt 300 ]; then
        LEVEL="🟢 很快"
    elif [ $DURATION -lt 500 ]; then
        LEVEL="🟡 正常"
    else
        LEVEL="🔴 较慢"
    fi
    
    printf "%-50s | %5dms | %s | HTTP %s\n" "$description" "$DURATION" "$LEVEL" "$HTTP_CODE"
    
    echo "    → 响应大小: $(echo "scale=2; $BODY_SIZE / 1024" | bc)KB"
    
    echo "$endpoint|$DURATION|$HTTP_CODE|$BODY_SIZE"
}

echo "🔍 测试 API 响应时间..."
echo ""
echo "╔═════════════════════════════════════════════════════════════════════╗"
echo ""

# 保存测试结果
> /tmp/api_results.txt

# 核心 API 测试
echo "📋 核心功能 API"
test_api "/api/sections" GET "获取栏目列表" >> /tmp/api_results.txt
test_api "/api/categories" GET "获取分类列表" >> /tmp/api_results.txt
test_api "/api/platforms" GET "获取平台列表" >> /tmp/api_results.txt
echo ""

echo "📝 文章管理 API"
test_api "/api/articles?skip=0&limit=10" GET "获取文章列表" >> /tmp/api_results.txt
test_api "/api/articles?skip=0&limit=100" GET "获取文章列表(大量)" >> /tmp/api_results.txt
echo ""

echo "🤖 AI 任务 API"
test_api "/api/tasks?skip=0&limit=10" GET "获取任务列表" >> /tmp/api_results.txt
test_api "/api/tasks?status=PENDING" GET "获取待处理任务" >> /tmp/api_results.txt
echo ""

echo "⚙️ 系统 API"
test_api "/api/health" GET "健康检查" >> /tmp/api_results.txt
test_api "/api/admin/settings" GET "获取系统设置" >> /tmp/api_results.txt
echo ""

echo "╚═════════════════════════════════════════════════════════════════════╝"
echo ""

# 性能统计
echo "📊 性能统计..."
echo ""

# 计算平均响应时间
TOTAL_TIME=0
COUNT=0

while IFS='|' read -r endpoint duration http_code size; do
    if [ -n "$duration" ] && [ "$duration" != "0" ]; then
        TOTAL_TIME=$((TOTAL_TIME + duration))
        COUNT=$((COUNT + 1))
    fi
done < /tmp/api_results.txt

if [ $COUNT -gt 0 ]; then
    AVG_TIME=$((TOTAL_TIME / COUNT))
    echo "   • 测试 API 数: $COUNT"
    echo "   • 总响应时间: ${TOTAL_TIME}ms"
    echo "   • 平均响应时间: ${AVG_TIME}ms"
    echo "   • 状态: $([ $AVG_TIME -lt 500 ] && echo "✅ 优秀" || echo "⚠️ 需优化")"
else
    echo "   ❌ 无法收集数据"
fi

echo ""

# 生成详细报告
cat > "$REPORT_FILE" << EOF
# 📊 后端 API 响应时间分析报告 - Task 5.1.3

**生成时间**: $(date "+%Y-%m-%d %H:%M:%S")
**API 基础 URL**: $API_URL

---

## 📈 性能概览

| 指标 | 数值 | 状态 |
|------|------|------|
| 平均响应时间 | ${AVG_TIME}ms | $([ $AVG_TIME -lt 500 ] && echo "✅ 优秀" || echo "⚠️ 需优化") |
| 测试 API 数 | $COUNT | - |
| 总响应时间 | ${TOTAL_TIME}ms | - |
| 目标响应时间 | 500ms | - |

---

## 🔍 详细测试结果

### 核心功能 API
- 获取栏目列表: [待收集]
- 获取分类列表: [待收集]
- 获取平台列表: [待收集]

### 文章管理 API
- 获取文章列表: [待收集]
- 获取文章列表(大量): [待收集]

### AI 任务 API
- 获取任务列表: [待收集]
- 获取待处理任务: [待收集]

### 系统 API
- 健康检查: [待收集]
- 获取系统设置: [待收集]

---

## 🎯 性能优化建议

### 1️⃣ 添加查询缓存 (优先级: 🔴 高)
\`\`\`python
# 在 backend/app/main.py 中添加缓存中间件

from functools import lru_cache
from datetime import datetime, timedelta

# 实现简单的 API 缓存
cache = {}
cache_ttl = timedelta(minutes=5)

def get_cached_or_fetch(key, fetch_fn):
    if key in cache:
        value, expires_at = cache[key]
        if datetime.now() < expires_at:
            return value
    
    value = fetch_fn()
    cache[key] = (value, datetime.now() + cache_ttl)
    return value
\`\`\`

**预期效果**: 减少数据库查询 50-70%

### 2️⃣ 添加数据库索引 (优先级: 🔴 高)
\`\`\`sql
-- 为常用查询字段创建索引
CREATE INDEX idx_articles_section_id ON articles(section_id);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
\`\`\`

**预期效果**: 减少查询时间 30-50%

### 3️⃣ 实现分页查询 (优先级: 🟠 中)
- 默认 limit: 50 (当前: 100)
- 最大 limit: 1000
- 显示总数信息

**预期效果**: 减少内存占用，提升响应速度

### 4️⃣ 异步处理长操作 (优先级: 🟠 中)
- AI 生成任务使用异步 Celery
- 大批量操作使用后台任务
- 提供任务进度查询接口

**预期效果**: 改善用户体验，提升系统吞吐量

### 5️⃣ 响应压缩 (优先级: 🟢 低)
\`\`\`python
# 在 FastAPI 中启用 gzip 压缩
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
\`\`\`

**预期效果**: 减少传输大小 50-80%

---

## ✅ 优化清单

### 立即实施 (本周)
- [ ] 创建必要的数据库索引
- [ ] 添加简单的查询缓存
- [ ] 启用响应压缩

### 短期优化 (本月)
- [ ] 实现 Redis 缓存
- [ ] 优化数据库查询
- [ ] 添加异步任务处理

### 长期规划 (下月)
- [ ] 实现 CDN 缓存策略
- [ ] 优化数据库架构
- [ ] 分库分表处理大数据量

---

## 🔧 实施步骤

### Step 1: 添加数据库索引 (10分钟)
\`\`\`bash
sqlite3 trustagency.db << 'SQL'
CREATE INDEX IF NOT EXISTS idx_articles_section_id ON articles(section_id);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
SQL
\`\`\`

### Step 2: 验证索引 (5分钟)
\`\`\`bash
sqlite3 trustagency.db ".indices"
\`\`\`

### Step 3: 性能对比测试 (15分钟)
重新运行 API 测试，对比优化前后的性能

---

## 📊 验收标准

- [ ] 平均 API 响应时间 < 500ms
- [ ] 所有 API 响应时间 < 1000ms
- [ ] 响应传输大小压缩 > 50%
- [ ] 没有超时或错误响应

---

## 📝 参考资源

- [FastAPI 性能优化](https://fastapi.tiangolo.com/deployment/concepts/)
- [SQLite 查询优化](https://www.sqlite.org/optoverview.html)
- [Python 缓存最佳实践](https://docs.python.org/3/library/functools.html#functools.lru_cache)

---

**状态**: 📝 等待实施

EOF

echo "✅ 详细报告已生成: $REPORT_FILE"
echo ""
echo "📍 立即改进:"
echo "   1. 为 articles 表创建索引"
echo "   2. 为 tasks 表创建索引"
echo "   3. 启用 gzip 响应压缩"
echo ""
echo "🎯 目标: 所有 API 响应 < 500ms"
echo ""
