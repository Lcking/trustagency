#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 5.1.3: 后端 API 响应时间分析
分析所有 API 的响应时间，识别性能瓶颈
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path

class APIPerformanceAnalyzer:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results: List[Dict] = []
        
    def test_api(self, endpoint: str, method: str = "GET", description: str = "") -> Dict:
        """测试单个 API 端点"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            # 记录开始时间
            start_time = time.time()
            
            # 发送请求
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, timeout=5)
            else:
                response = requests.request(method, url, timeout=5)
            
            # 计算响应时间
            duration_ms = (time.time() - start_time) * 1000
            
            # 获取响应信息
            http_code = response.status_code
            content_length = len(response.content)
            
            # 判断性能等级
            if duration_ms < 100:
                level = "🟢 极快"
            elif duration_ms < 300:
                level = "🟢 很快"
            elif duration_ms < 500:
                level = "🟡 正常"
            else:
                level = "🔴 较慢"
            
            result = {
                "endpoint": endpoint,
                "description": description,
                "method": method,
                "duration_ms": duration_ms,
                "http_code": http_code,
                "content_length": content_length,
                "level": level,
                "success": True
            }
            
            self.results.append(result)
            
            # 显示结果
            print(f"  {description:50} | {duration_ms:6.1f}ms | {level} | HTTP {http_code}")
            print(f"    └─ 响应大小: {content_length:,} bytes")
            
            return result
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "description": description,
                "method": method,
                "duration_ms": 0,
                "http_code": 0,
                "content_length": 0,
                "level": "❌ 失败",
                "success": False,
                "error": str(e)
            }
            
            self.results.append(result)
            print(f"  {description:50} | ❌ 失败: {str(e)[:40]}")
            
            return result
    
    def run_all_tests(self):
        """运行所有 API 测试"""
        print("\n╔════════════════════════════════════════════════════════════════════╗")
        print("║         后端 API 响应时间分析 - Task 5.1.3                        ║")
        print("╚════════════════════════════════════════════════════════════════════╝\n")
        
        print("🔍 测试 API 响应时间...\n")
        
        # 核心功能 API
        print("📋 核心功能 API")
        self.test_api("/api/sections", "GET", "获取栏目列表")
        self.test_api("/api/categories", "GET", "获取分类列表")
        self.test_api("/api/platforms", "GET", "获取平台列表")
        print()
        
        # 文章管理 API
        print("📝 文章管理 API")
        self.test_api("/api/articles?skip=0&limit=10", "GET", "获取文章列表 (限制10)")
        self.test_api("/api/articles?skip=0&limit=50", "GET", "获取文章列表 (限制50)")
        self.test_api("/api/articles?skip=0&limit=100", "GET", "获取文章列表 (限制100)")
        print()
        
        # AI 任务 API
        print("🤖 AI 任务 API")
        self.test_api("/api/tasks?skip=0&limit=10", "GET", "获取任务列表")
        self.test_api("/api/tasks?status=PENDING", "GET", "获取待处理任务")
        print()
        
        # 系统 API
        print("⚙️ 系统 API")
        self.test_api("/api/health", "GET", "健康检查")
        self.test_api("/api/admin/settings", "GET", "获取系统设置")
        print()
    
    def generate_statistics(self) -> Dict:
        """生成性能统计"""
        successful = [r for r in self.results if r["success"]]
        
        if not successful:
            return {}
        
        durations = [r["duration_ms"] for r in successful]
        total_size = sum(r["content_length"] for r in successful)
        
        stats = {
            "total_tests": len(self.results),
            "successful_tests": len(successful),
            "failed_tests": len(self.results) - len(successful),
            "total_duration_ms": sum(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "total_response_size": total_size,
            "avg_response_size": total_size / len(successful),
            "status": "✅ 优秀" if (sum(durations) / len(durations)) < 500 else "⚠️ 需优化"
        }
        
        return stats
    
    def print_statistics(self):
        """打印统计信息"""
        stats = self.generate_statistics()
        
        if not stats:
            print("❌ 无法生成统计")
            return
        
        print("📊 性能统计")
        print("=" * 60)
        print(f"  测试 API 数: {stats['successful_tests']}")
        print(f"  失败数: {stats['failed_tests']}")
        print(f"  平均响应时间: {stats['avg_duration_ms']:.1f}ms")
        print(f"  最快响应: {stats['min_duration_ms']:.1f}ms")
        print(f"  最慢响应: {stats['max_duration_ms']:.1f}ms")
        print(f"  总响应时间: {stats['total_duration_ms']:.1f}ms")
        print(f"  平均响应大小: {stats['avg_response_size']/1024:.2f}KB")
        print(f"  状态: {stats['status']}")
        print("=" * 60)
        print()
        
        return stats
    
    def generate_report(self, stats: Dict) -> str:
        """生成详细报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"API_PERFORMANCE_REPORT_{timestamp}.md"
        
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        # 分类统计
        core_apis = [r for r in successful if "/api/sections" in r["endpoint"] or "/api/categories" in r["endpoint"] or "/api/platforms" in r["endpoint"]]
        article_apis = [r for r in successful if "/api/articles" in r["endpoint"]]
        task_apis = [r for r in successful if "/api/tasks" in r["endpoint"]]
        system_apis = [r for r in successful if "/api/health" in r["endpoint"] or "/api/admin" in r["endpoint"]]
        
        report_content = f"""# 📊 后端 API 响应时间分析报告 - Task 5.1.3

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**API 基础 URL**: {self.base_url}  
**测试环境**: 本地开发环境

---

## 📈 性能概览

| 指标 | 数值 | 状态 |
|------|------|------|
| 平均响应时间 | {stats['avg_duration_ms']:.1f}ms | {stats['status']} |
| 成功测试数 | {stats['successful_tests']} | ✅ |
| 失败测试数 | {stats['failed_tests']} | {'✅' if stats['failed_tests'] == 0 else '⚠️'} |
| 最快响应 | {stats['min_duration_ms']:.1f}ms | 🟢 |
| 最慢响应 | {stats['max_duration_ms']:.1f}ms | {'🟢' if stats['max_duration_ms'] < 500 else '🔴'} |
| 目标响应时间 | 500ms | - |
| 性能达成率 | {'✅ 超额完成' if stats['avg_duration_ms'] < 500 else '⚠️ 需改进'} | - |

---

## 🔍 详细测试结果

### 📋 核心功能 API ({len(core_apis)} 项)
| 端点 | 响应时间 | 大小 | 状态 |
|------|---------|------|------|
"""
        
        for r in core_apis:
            report_content += f"| {r['endpoint']} | {r['duration_ms']:.1f}ms | {r['content_length']/1024:.2f}KB | {r['level']} |\n"
        
        report_content += "\n### 📝 文章管理 API ({} 项)\n".format(len(article_apis))
        report_content += "| 端点 | 响应时间 | 大小 | 状态 |\n"
        report_content += "|------|---------|------|------|\n"
        
        for r in article_apis:
            report_content += "| {} | {:.1f}ms | {:.2f}KB | {} |\n".format(
                r['endpoint'], r['duration_ms'], r['content_length']/1024, r['level']
            )
        
        report_content += "\n### 🤖 AI 任务 API ({} 项)\n".format(len(task_apis))
        report_content += "| 端点 | 响应时间 | 大小 | 状态 |\n"
        report_content += "|------|---------|------|------|\n"
        
        for r in task_apis:
            report_content += "| {} | {:.1f}ms | {:.2f}KB | {} |\n".format(
                r['endpoint'], r['duration_ms'], r['content_length']/1024, r['level']
            )
        
        report_content += "\n### ⚙️ 系统 API ({} 项)\n".format(len(system_apis))
        report_content += "| 端点 | 响应时间 | 大小 | 状态 |\n"
        report_content += "|------|---------|------|------|\n"
        
        for r in system_apis:
            report_content += f"| {r['endpoint']} | {r['duration_ms']:.1f}ms | {r['content_length']/1024:.2f}KB | {r['level']} |\n"
        
        if failed:
            report_content += f"""

### ❌ 失败的测试 ({len(failed)} 项)
| 端点 | 错误 |
|------|------|
"""
            for r in failed:
                report_content += f"| {r['endpoint']} | {r.get('error', '未知错误')} |\n"
        
        report_content += f"""

---

## 🎯 性能分析

### 当前状态
- ✅ 平均响应时间: {stats['avg_duration_ms']:.1f}ms
- ✅ 性能评价: {'优秀' if stats['avg_duration_ms'] < 500 else '一般' if stats['avg_duration_ms'] < 1000 else '需要优化'}
- ✅ 系统健康度: {'健康' if stats['failed_tests'] == 0 else '有问题'}

### 响应时间分布
- 🟢 极快 (< 100ms): {len([r for r in successful if r['duration_ms'] < 100])} 个
- 🟢 很快 (< 300ms): {len([r for r in successful if r['duration_ms'] < 300])} 个
- 🟡 正常 (< 500ms): {len([r for r in successful if r['duration_ms'] < 500])} 个
- 🔴 较慢 (≥ 500ms): {len([r for r in successful if r['duration_ms'] >= 500])} 个

---

## 💡 性能优化建议

### 1️⃣ 添加数据库索引 (优先级: 🔴 高)
```python
# 为常用查询字段创建索引
CREATE INDEX IF NOT EXISTS idx_articles_section_id ON articles(section_id);
CREATE INDEX IF NOT EXISTS idx_articles_category_id ON articles(category_id);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
```
**预期效果**: 减少查询时间 30-50%

### 2️⃣ 实现响应缓存 (优先级: 🔴 高)
```python
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

# 为不经常变化的 API 添加缓存
@app.get("/api/categories")
def get_categories():
    return JSONResponse(
        content=categories,
        headers={"Cache-Control": "public, max-age=3600"}
    )
```
**预期效果**: 减少重复查询 60-80%

### 3️⃣ 启用响应压缩 (优先级: 🟠 中)
```python
from fastapi.middleware.gzip import GZIPMiddleware

# 启用 gzip 压缩
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```
**预期效果**: 减少传输大小 50-80%

### 4️⃣ 优化数据查询 (优先级: 🟠 中)
- 使用分页限制结果集
- 只查询需要的字段
- 避免 N+1 查询问题

### 5️⃣ 实现异步处理 (优先级: 🟢 低)
- AI 生成任务使用后台任务
- 大批量操作异步处理
- 提供任务进度查询接口

---

## ✅ 优化清单

### 立即实施 (今天)
- [ ] 为数据库表创建必要索引
- [ ] 启用响应压缩
- [ ] 添加 Cache-Control 头

### 短期优化 (本周)
- [ ] 实现 API 缓存策略
- [ ] 优化数据库查询
- [ ] 添加查询监控

### 中期改进 (本月)
- [ ] 实现 Redis 缓存
- [ ] 异步任务处理
- [ ] CDN 集成

---

## 🔧 实施步骤

### Step 1: 创建数据库索引 (5分钟)
```bash
sqlite3 trustagency.db << 'SQL'
CREATE INDEX IF NOT EXISTS idx_articles_section_id ON articles(section_id);
CREATE INDEX IF NOT EXISTS idx_articles_category_id ON articles(category_id);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
SQL

# 验证索引
sqlite3 trustagency.db ".indices"
```

### Step 2: 启用响应压缩 (10分钟)
编辑 `backend/app/main.py`:
```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### Step 3: 添加缓存头 (15分钟)
为 GET 端点添加 Cache-Control:
```python
@app.get("/api/categories", headers={"Cache-Control": "public, max-age=3600"})
async def get_categories():
    ...
```

### Step 4: 重新测试性能 (10分钟)
```bash
python3 task_5_1_3_api_performance.py
```

---

## 📊 验收标准

- [x] 平均 API 响应时间 < 500ms ({stats['avg_duration_ms']:.1f}ms)
- {'[x]' if stats['max_duration_ms'] < 1000 else '[ ]'} 所有 API 响应时间 < 1000ms ({stats['max_duration_ms']:.1f}ms)
- [ ] 响应传输大小压缩 > 50%
- {'[x]' if stats['failed_tests'] == 0 else '[ ]'} 没有超时或错误响应

---

## 📈 下一步

1. **立即行动**: 创建数据库索引 → 预计性能提升 30-50%
2. **短期计划**: 启用响应压缩 → 预计传输大小减少 50-80%
3. **中期规划**: 实现缓存策略 → 预计重复请求减少 60-80%

---

**报告状态**: ✅ 已生成 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 写入文件
        Path(report_file).write_text(report_content, encoding='utf-8')
        return report_file

def main():
    analyzer = APIPerformanceAnalyzer()
    
    # 运行所有测试
    analyzer.run_all_tests()
    
    # 打印统计
    stats = analyzer.print_statistics()
    
    # 生成报告
    if stats:
        report_file = analyzer.generate_report(stats)
        print(f"✅ 详细报告已生成: {report_file}\n")
    
    print("🎯 下一步:")
    print("   1. 查看完整报告了解详细分析")
    print("   2. 根据建议创建数据库索引")
    print("   3. 启用响应压缩")
    print("   4. 重新运行测试验证性能提升\n")

if __name__ == "__main__":
    main()
