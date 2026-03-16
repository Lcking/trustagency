# TrustAgency OpenClaw 对接文档

## 概述

本文档描述如何通过 OpenClaw 自动化平台与 TrustAgency 网站进行集成，实现定时数据同步等自动化任务。

---

## 站点架构

```
┌─────────────────────────────────────────────────────────────┐
│                    TrustAgency 架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────────┐│
│  │  Nginx   │────▶│  FastAPI │────▶│      SQLite DB       ││
│  │ (前端)   │     │  (后端)  │     │  (数据存储)          ││
│  └──────────┘     └──────────┘     └──────────────────────┘│
│                         │                                   │
│                         ▼                                   │
│                   ┌──────────┐     ┌──────────────────────┐│
│                   │  Celery  │────▶│     Tushare API      ││
│                   │ (异步任务)│     │  (外部数据源)        ││
│                   └──────────┘     └──────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  定时任务调度器  ──▶  HTTP 请求  ──▶  API 端点       │  │
│  │  (Cron 表达式)       (POST)          (/api/external) │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## API 端点

### 基础信息

| 属性 | 值 |
|------|-----|
| Base URL | `https://www.yycr.net` |
| API 前缀 | `/api/external` |
| 认证方式 | API Key (Header) |
| 内容类型 | `application/json` |

### 认证

所有 API 请求都需要在 Header 中携带 API Key：

```
X-API-Key: your-api-key-here
```

---

## 可用接口

### 1. 同步两融数据

**POST** `/api/external/tasks/sync-margin`

同步融资融券数据，从 Tushare API 获取最新数据并存入数据库。

#### 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| days | int | 3 | 同步最近 N 天的数据 (1-30) |
| force | bool | false | 是否强制重新同步已存在的数据 |

#### 请求示例

```json
{
  "days": 3,
  "force": false
}
```

或者不传参数使用默认值：

```bash
curl -X POST "https://www.yycr.net/api/external/tasks/sync-margin" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json"
```

#### 响应示例

```json
{
  "success": true,
  "summary_count": 1,
  "detail_count": 4311,
  "synced_dates": ["20260123", "20260122"],
  "skipped_dates": ["20260124"],
  "errors": [],
  "duration_ms": 5200,
  "timestamp": "2026-01-23T18:30:00.123456"
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | bool | 是否完全成功（无错误） |
| summary_count | int | 同步的汇总数据条数 |
| detail_count | int | 同步的明细数据条数 |
| synced_dates | array | 成功同步的日期列表 (YYYYMMDD) |
| skipped_dates | array | 跳过的日期（已有数据或无数据） |
| errors | array | 错误信息列表 |
| duration_ms | int | 执行耗时（毫秒） |
| timestamp | string | 执行时间 (ISO 8601) |

---

### 2. 获取两融数据状态

**GET** `/api/external/tasks/margin-status`

查询当前两融数据的状态。

#### 请求示例

```bash
curl -X GET "https://www.yycr.net/api/external/tasks/margin-status" \
  -H "X-API-Key: your-api-key"
```

#### 响应示例

```json
{
  "status": "ok",
  "summary": {
    "latest_date": "2026-01-22",
    "total_count": 30
  },
  "detail": {
    "latest_date": "2026-01-22",
    "total_count": 120000
  },
  "timestamp": "2026-01-23T18:30:00.123456"
}
```

---

### 3. 系统健康检查

**GET** `/api/external/health`

检查系统各组件的健康状态。

#### 请求示例

```bash
curl -X GET "https://www.yycr.net/api/external/health" \
  -H "X-API-Key: your-api-key"
```

#### 响应示例

```json
{
  "status": "healthy",
  "database": "healthy",
  "celery_worker": "healthy",
  "celery_beat": "check_logs",
  "margin_data_latest_date": "2026-01-22",
  "timestamp": "2026-01-23T18:30:00.123456"
}
```

---

### 4. Ping 测试

**GET** `/api/external/ping`

简单的连通性测试，无需认证。

#### 请求示例

```bash
curl -X GET "https://www.yycr.net/api/external/ping"
```

#### 响应示例

```json
{
  "status": "pong",
  "timestamp": "2026-01-23T18:30:00.123456"
}
```

---

## OpenClaw 配置指南

### 任务 1: 每日两融数据同步（17:30）

**触发器配置:**

```yaml
type: cron
expression: "30 17 * * *"
timezone: Asia/Shanghai
```

**动作配置:**

```yaml
type: http_request
method: POST
url: https://www.yycr.net/api/external/tasks/sync-margin
headers:
  X-API-Key: "{{secrets.TRUSTAGENCY_API_KEY}}"
  Content-Type: application/json
body:
  days: 3
  force: false
timeout: 120  # 秒
```

**成功条件:**

```yaml
success_condition:
  - response.status_code == 200
  - response.body.success == true
```

---

### 任务 2: 备用同步（18:30）

与任务 1 相同配置，只是触发时间改为 `30 18 * * *`。

---

### 任务 3: 定期健康检查

**触发器配置:**

```yaml
type: cron
expression: "0 */6 * * *"  # 每 6 小时
timezone: Asia/Shanghai
```

**动作配置:**

```yaml
type: http_request
method: GET
url: https://www.yycr.net/api/external/health
headers:
  X-API-Key: "{{secrets.TRUSTAGENCY_API_KEY}}"
timeout: 30
```

**告警条件:**

```yaml
alert_condition:
  - response.body.status != "healthy"
  - response.body.margin_data_latest_date < today - 3 days
```

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | API Key 无效或缺失 |
| 500 | 服务器内部错误 |

### 常见错误

**API Key 无效:**

```json
{
  "detail": "无效的 API Key"
}
```

**API Key 未配置（服务器端）:**

```json
{
  "detail": "API Key 未配置，请联系管理员"
}
```

---

## 数据说明

### Tushare 数据发布时间

- **融资融券汇总数据**: 每日 17:00-18:00 左右发布
- **融资融券明细数据**: 每日 17:00-19:00 左右发布（可能延迟）

### 同步策略

1. **17:30 第一次同步**: 尝试获取当天数据
2. **18:30 备用同步**: 如果 17:30 数据未发布，再次尝试
3. **多日同步**: 每次同步最近 3 天数据，确保不遗漏

### 非交易日处理

- 周末、节假日无新数据
- API 会返回 `synced_dates` 为空
- 这是正常情况，不视为错误

---

## 最佳实践

### 1. 重试策略

```yaml
retry:
  max_attempts: 3
  delay: 300  # 5 分钟后重试
  backoff: exponential
```

### 2. 超时设置

- 同步任务: 120 秒（数据量较大时需要时间）
- 健康检查: 30 秒
- Ping: 10 秒

### 3. 日志记录

建议记录每次任务的：
- 执行时间
- 响应内容（特别是 `synced_dates` 和 `errors`）
- 执行耗时

### 4. 监控告警

设置告警条件：
- 连续 3 次同步失败
- 数据超过 3 天未更新
- 健康检查状态异常

---

## 联系方式

如有问题，请联系站点管理员。

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-23 | 1.0.0 | 初始版本 |
