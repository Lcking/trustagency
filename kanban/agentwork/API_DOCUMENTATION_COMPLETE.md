# TrustAgency API 完整文档

**Version**: 1.0.0  
**Base URL**: `http://localhost:8001` (开发环境) / `https://api.trustagency.com` (生产环境)  
**API Prefix**: `/api`  
**Authentication**: Bearer Token (JWT)

---

## 📋 目录

1. [概览](#概览)
2. [认证](#认证)
3. [错误处理](#错误处理)
4. [平台管理 API](#平台管理-api)
5. [文章管理 API](#文章管理-api)
6. [任务管理 API](#任务管理-api)
7. [数据模型](#数据模型)
8. [HTTP 状态码](#http-状态码)

---

## 概览

### API 特性

✅ **RESTful 架构** - 遵循 REST 最佳实践  
✅ **JWT 认证** - 安全的 Bearer Token 认证  
✅ **分页支持** - 所有列表 API 均支持分页  
✅ **搜索过滤** - 丰富的搜索和过滤选项  
✅ **排序功能** - 灵活的多字段排序  
✅ **错误处理** - 统一的错误响应格式  
✅ **数据验证** - 使用 Pydantic 的严格数据验证  
✅ **健康检查** - 内置健康检查端点  

### 基础信息

```bash
# 获取 API 信息
GET /

# 响应示例
{
  "name": "TrustAgency API",
  "version": "1.0.0",
  "docs": "/api/docs"
}
```

### 健康检查

```bash
# 检查 API 运行状态
GET /api/health

# 响应示例
{
  "status": "ok",
  "message": "TrustAgency Backend is running"
}
```

---

## 认证

### 登录

获取访问令牌进行身份验证。

**Endpoint**: `POST /api/admin/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "your_secure_password"
}
```

**响应示例** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "is_active": true,
    "is_superadmin": true,
    "created_at": "2025-11-07T10:00:00",
    "last_login": "2025-11-07T18:30:00"
  }
}
```

**可能的错误**:
- `401 Unauthorized` - 用户名或密码错误
- `404 Not Found` - 用户不存在

---

### 使用认证令牌

所有需要认证的 API 请求都必须在 HTTP 头中包含 Bearer Token：

```bash
# 示例请求
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://api.trustagency.com/api/platforms
```

### Token 有效期

- **访问令牌有效期**: 24 小时
- **刷新策略**: 每次登录获取新 Token
- **过期处理**: 需要重新登录

---

## 错误处理

### 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "detail": "具体错误信息",
  "status_code": 400
}
```

### 常见错误代码

| 代码 | 含义 | 说明 |
|------|------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权或 Token 过期 |
| 403 | Forbidden | 无权访问资源 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器错误 |

### 错误示例

**验证错误** (422):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "input": "not-an-email"
    }
  ]
}
```

**认证错误** (401):
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

## 平台管理 API

### 获取平台列表

获取所有平台的列表，支持搜索、过滤和排序。

**Endpoint**: `GET /api/platforms`

**查询参数**:

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| skip | integer | 否 | 跳过的记录数 (默认 0) | 0 |
| limit | integer | 否 | 每页记录数 (1-100, 默认 10) | 20 |
| search | string | 否 | 搜索关键词 (名称、描述) | "binance" |
| sort_by | string | 否 | 排序字段 | "rank" |
| sort_order | string | 否 | 排序顺序: asc/desc | "asc" |
| is_active | boolean | 否 | 过滤活跃平台 | true |
| is_featured | boolean | 否 | 过滤精选平台 | true |

**排序字段选项**:
- `name` - 平台名称
- `rank` - 排名
- `rating` - 评分
- `commission_rate` - 手续费率
- `created_at` - 创建时间

**示例请求**:
```bash
# 获取排名前 20 的平台
GET /api/platforms?sort_by=rank&sort_order=asc&limit=20

# 搜索并获取精选平台
GET /api/platforms?search=binance&is_featured=true

# 分页查询
GET /api/platforms?skip=20&limit=10
```

**响应示例** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "name": "Binance",
      "description": "全球最大的加密货币交易所",
      "rating": 4.8,
      "rank": 1,
      "min_leverage": 1.0,
      "max_leverage": 125.0,
      "commission_rate": 0.001,
      "is_regulated": true,
      "logo_url": "https://...",
      "website_url": "https://binance.com",
      "is_active": true,
      "is_featured": true,
      "created_at": "2025-11-01T10:00:00",
      "updated_at": "2025-11-07T15:30:00"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```

---

### 获取单个平台

获取特定平台的详细信息。

**Endpoint**: `GET /api/platforms/{platform_id}`

**路径参数**:
- `platform_id` (integer, 必需) - 平台 ID

**示例请求**:
```bash
GET /api/platforms/1
```

**响应示例** (200 OK):
```json
{
  "id": 1,
  "name": "Binance",
  "description": "全球最大的加密货币交易所",
  "rating": 4.8,
  "rank": 1,
  "min_leverage": 1.0,
  "max_leverage": 125.0,
  "commission_rate": 0.001,
  "is_regulated": true,
  "logo_url": "https://...",
  "website_url": "https://binance.com",
  "is_active": true,
  "is_featured": true,
  "created_at": "2025-11-01T10:00:00",
  "updated_at": "2025-11-07T15:30:00"
}
```

**可能的错误**:
- `404 Not Found` - 平台不存在

---

### 创建平台

创建新平台 (仅管理员)。

**Endpoint**: `POST /api/platforms`

**认证**: 需要 Bearer Token

**请求体**:
```json
{
  "name": "Binance",
  "description": "全球最大的加密货币交易所",
  "rating": 4.8,
  "rank": 1,
  "min_leverage": 1.0,
  "max_leverage": 125.0,
  "commission_rate": 0.001,
  "is_regulated": true,
  "logo_url": "https://...",
  "website_url": "https://binance.com",
  "is_featured": true
}
```

**字段说明**:

| 字段 | 类型 | 必需 | 说明 | 验证 |
|------|------|------|------|------|
| name | string | ✓ | 平台名称 | 1-100 字符 |
| description | string | ✓ | 平台描述 | 最多 500 字符 |
| rating | float | ✓ | 评分 | 0-5 |
| rank | integer | ✓ | 排名 | >0 |
| min_leverage | float | ✓ | 最小杠杆 | >0 |
| max_leverage | float | ✓ | 最大杠杆 | >= min_leverage |
| commission_rate | float | ✓ | 手续费率 | 0-1 |
| is_regulated | boolean | ✓ | 是否受监管 | - |
| logo_url | string | ✓ | Logo URL | 有效 URL |
| website_url | string | ✓ | 官网 URL | 有效 URL |
| is_featured | boolean | 否 | 是否精选 | 默认 false |

**响应示例** (201 Created):
```json
{
  "id": 51,
  "name": "Binance",
  "description": "全球最大的加密货币交易所",
  "rating": 4.8,
  "rank": 1,
  "min_leverage": 1.0,
  "max_leverage": 125.0,
  "commission_rate": 0.001,
  "is_regulated": true,
  "logo_url": "https://...",
  "website_url": "https://binance.com",
  "is_active": true,
  "is_featured": true,
  "created_at": "2025-11-07T18:45:00",
  "updated_at": "2025-11-07T18:45:00"
}
```

---

### 更新平台

更新平台信息 (仅管理员)。

**Endpoint**: `PUT /api/platforms/{platform_id}`

**认证**: 需要 Bearer Token

**路径参数**:
- `platform_id` (integer, 必需) - 平台 ID

**请求体** (仅包含要更新的字段):
```json
{
  "rating": 4.9,
  "rank": 2,
  "is_featured": true
}
```

**响应示例** (200 OK):
```json
{
  "id": 1,
  "name": "Binance",
  "description": "全球最大的加密货币交易所",
  "rating": 4.9,
  "rank": 2,
  "min_leverage": 1.0,
  "max_leverage": 125.0,
  "commission_rate": 0.001,
  "is_regulated": true,
  "logo_url": "https://...",
  "website_url": "https://binance.com",
  "is_active": true,
  "is_featured": true,
  "created_at": "2025-11-01T10:00:00",
  "updated_at": "2025-11-07T19:00:00"
}
```

---

### 删除平台

删除平台 (仅管理员)。

**Endpoint**: `DELETE /api/platforms/{platform_id}`

**认证**: 需要 Bearer Token

**路径参数**:
- `platform_id` (integer, 必需) - 平台 ID

**响应**: 204 No Content

---

## 文章管理 API

### 获取文章列表

获取所有文章的列表，支持高级搜索、过滤和排序。

**Endpoint**: `GET /api/articles`

**查询参数**:

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| skip | integer | 否 | 跳过的记录数 (默认 0) | 0 |
| limit | integer | 否 | 每页记录数 (1-100, 默认 10) | 20 |
| search | string | 否 | 搜索关键词 | "bitcoin" |
| category | string | 否 | 分类过滤 | "交易指南" |
| platform_id | integer | 否 | 平台 ID 过滤 | 1 |
| author_id | integer | 否 | 作者 ID 过滤 | 5 |
| is_published | boolean | 否 | 发布状态过滤 | true |
| is_featured | boolean | 否 | 精选状态过滤 | true |
| sort_by | string | 否 | 排序字段 | "created_at" |
| sort_order | string | 否 | 排序顺序 | "desc" |

**排序字段选项**:
- `title` - 文章标题
- `created_at` - 创建时间
- `updated_at` - 更新时间
- `view_count` - 浏览数
- `like_count` - 点赞数

**示例请求**:
```bash
# 搜索 Bitcoin 相关文章
GET /api/articles?search=bitcoin&sort_by=like_count&sort_order=desc

# 获取已发布的文章
GET /api/articles?is_published=true&limit=20

# 按分类和平台过滤
GET /api/articles?category=交易指南&platform_id=1
```

**响应示例** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "title": "Bitcoin 初学者指南",
      "slug": "bitcoin-beginners-guide",
      "content": "这是一篇完整的 Bitcoin 介绍文章...",
      "summary": "快速了解 Bitcoin 的要点",
      "category": "教程",
      "tags": ["bitcoin", "加密货币", "初学者"],
      "platform_id": 1,
      "author_id": 1,
      "author": {
        "id": 1,
        "username": "admin",
        "full_name": "Admin User"
      },
      "meta_description": "Learn about Bitcoin",
      "meta_keywords": "bitcoin, cryptocurrency",
      "view_count": 1250,
      "like_count": 89,
      "is_published": true,
      "is_featured": true,
      "published_at": "2025-11-01T10:00:00",
      "created_at": "2025-10-30T08:00:00",
      "updated_at": "2025-11-07T15:30:00"
    }
  ],
  "total": 125,
  "skip": 0,
  "limit": 10
}
```

---

### 获取单个文章

获取特定文章的详细信息，自动增加浏览量。

**Endpoint**: `GET /api/articles/{article_id}`

**路径参数**:
- `article_id` (integer, 必需) - 文章 ID

**示例请求**:
```bash
GET /api/articles/1
```

**响应示例** (200 OK):
```json
{
  "id": 1,
  "title": "Bitcoin 初学者指南",
  "slug": "bitcoin-beginners-guide",
  "content": "这是一篇完整的 Bitcoin 介绍文章...",
  "summary": "快速了解 Bitcoin 的要点",
  "category": "教程",
  "tags": ["bitcoin", "加密货币", "初学者"],
  "platform_id": 1,
  "author_id": 1,
  "author": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  },
  "meta_description": "Learn about Bitcoin",
  "meta_keywords": "bitcoin, cryptocurrency",
  "view_count": 1251,
  "like_count": 89,
  "is_published": true,
  "is_featured": true,
  "published_at": "2025-11-01T10:00:00",
  "created_at": "2025-10-30T08:00:00",
  "updated_at": "2025-11-07T15:30:00"
}
```

---

### 创建文章

创建新文章 (仅管理员)。

**Endpoint**: `POST /api/articles?platform_id={platform_id}`

**认证**: 需要 Bearer Token

**查询参数**:
- `platform_id` (integer, 必需) - 所属平台 ID

**请求体**:
```json
{
  "title": "Bitcoin 初学者指南",
  "content": "这是一篇完整的 Bitcoin 介绍文章...",
  "summary": "快速了解 Bitcoin 的要点",
  "category": "教程",
  "tags": ["bitcoin", "加密货币", "初学者"],
  "meta_description": "Learn about Bitcoin",
  "meta_keywords": "bitcoin, cryptocurrency",
  "is_featured": true
}
```

**字段说明**:

| 字段 | 类型 | 必需 | 说明 | 验证 |
|------|------|------|------|------|
| title | string | ✓ | 文章标题 | 1-200 字符 |
| content | string | ✓ | 文章内容 | 最小 100 字符 |
| summary | string | ✓ | 文章摘要 | 最多 500 字符 |
| category | string | ✓ | 分类 | 1-50 字符 |
| tags | array | 否 | 标签列表 | 最多 10 个标签 |
| meta_description | string | 否 | SEO 描述 | 最多 160 字符 |
| meta_keywords | string | 否 | SEO 关键词 | 最多 100 字符 |
| is_featured | boolean | 否 | 是否精选 | 默认 false |

**响应示例** (201 Created):
```json
{
  "id": 126,
  "title": "Bitcoin 初学者指南",
  "slug": "bitcoin-beginners-guide",
  "content": "这是一篇完整的 Bitcoin 介绍文章...",
  "summary": "快速了解 Bitcoin 的要点",
  "category": "教程",
  "tags": ["bitcoin", "加密货币", "初学者"],
  "platform_id": 1,
  "author_id": 1,
  "author": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  },
  "meta_description": "Learn about Bitcoin",
  "meta_keywords": "bitcoin, cryptocurrency",
  "view_count": 0,
  "like_count": 0,
  "is_published": false,
  "is_featured": true,
  "published_at": null,
  "created_at": "2025-11-07T19:15:00",
  "updated_at": "2025-11-07T19:15:00"
}
```

---

### 更新文章

更新文章信息 (仅管理员)。

**Endpoint**: `PUT /api/articles/{article_id}`

**认证**: 需要 Bearer Token

**路径参数**:
- `article_id` (integer, 必需) - 文章 ID

**请求体** (仅包含要更新的字段):
```json
{
  "title": "Bitcoin 初学者指南 - 完整版",
  "is_featured": false,
  "tags": ["bitcoin", "加密货币", "初学者", "投资"]
}
```

**响应示例** (200 OK):
```json
{
  "id": 1,
  "title": "Bitcoin 初学者指南 - 完整版",
  "slug": "bitcoin-beginners-guide",
  "content": "这是一篇完整的 Bitcoin 介绍文章...",
  "summary": "快速了解 Bitcoin 的要点",
  "category": "教程",
  "tags": ["bitcoin", "加密货币", "初学者", "投资"],
  "platform_id": 1,
  "author_id": 1,
  "author": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  },
  "meta_description": "Learn about Bitcoin",
  "meta_keywords": "bitcoin, cryptocurrency",
  "view_count": 1251,
  "like_count": 89,
  "is_published": true,
  "is_featured": false,
  "published_at": "2025-11-01T10:00:00",
  "created_at": "2025-10-30T08:00:00",
  "updated_at": "2025-11-07T19:20:00"
}
```

---

### 发布文章

将文章发布到前台。

**Endpoint**: `POST /api/articles/{article_id}/publish`

**认证**: 需要 Bearer Token

**路径参数**:
- `article_id` (integer, 必需) - 文章 ID

**响应示例** (200 OK):
```json
{
  "id": 1,
  "title": "Bitcoin 初学者指南",
  "is_published": true,
  "published_at": "2025-11-07T19:25:00",
  "message": "文章已发布"
}
```

---

### 删除文章

删除文章 (仅管理员)。

**Endpoint**: `DELETE /api/articles/{article_id}`

**认证**: 需要 Bearer Token

**路径参数**:
- `article_id` (integer, 必需) - 文章 ID

**响应**: 204 No Content

---

## 任务管理 API

### 提交 AI 生成任务

提交文章批量生成任务。

**Endpoint**: `POST /api/tasks/generate`

**认证**: 需要 Bearer Token

**请求体**:
```json
{
  "titles": ["Python 入门指南", "FastAPI 最佳实践", "Docker 容器化"],
  "category": "guide",
  "batch_name": "November 2025 Batch"
}
```

**字段说明**:

| 字段 | 类型 | 必需 | 说明 | 验证 |
|------|------|------|------|------|
| titles | array | ✓ | 文章标题列表 | 1-100 个标题 |
| category | string | ✓ | 文章分类 | guide, news, tutorial |
| batch_name | string | 否 | 批次名称 | 最多 100 字符 |

**响应示例** (201 Created):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "celery_task_id": "abc123def456",
  "status": "pending",
  "message": "任务已提交，共 3 篇文章"
}
```

---

### 查询任务状态

获取任务的当前状态和进度。

**Endpoint**: `GET /api/tasks/{task_id}`

**认证**: 需要 Bearer Token

**路径参数**:
- `task_id` (string, 必需) - 任务 ID (UUID)

**示例请求**:
```bash
GET /api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**响应示例** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "batch_id": "batch_20251107_001",
  "status": "processing",
  "progress": 66,
  "celery_status": "active",
  "celery_task_id": "abc123def456",
  "total_count": 3,
  "completed_count": 2,
  "failed_count": 0,
  "error_message": null,
  "created_at": "2025-11-07T18:00:00",
  "started_at": "2025-11-07T18:05:00",
  "completed_at": null,
  "last_update": "2025-11-07T18:15:00"
}
```

**状态说明**:
- `pending` - 等待处理
- `processing` - 正在处理
- `completed` - 已完成
- `failed` - 失败
- `cancelled` - 已取消

---

### 获取任务进度

获取详细的实时进度信息。

**Endpoint**: `GET /api/tasks/{task_id}/progress`

**认证**: 需要 Bearer Token

**路径参数**:
- `task_id` (string, 必需) - 任务 ID

**响应示例** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 66,
  "current": 2,
  "total": 3,
  "status": "processing",
  "celery_status": "active",
  "last_update": "2025-11-07T18:15:00",
  "estimated_remaining_time": 120
}
```

---

### 取消任务

取消正在进行的任务。

**Endpoint**: `POST /api/tasks/{task_id}/cancel`

**认证**: 需要 Bearer Token

**路径参数**:
- `task_id` (string, 必需) - 任务 ID

**响应示例** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "任务已取消"
}
```

---

### 获取任务历史

获取当前用户的任务历史。

**Endpoint**: `GET /api/tasks/history`

**认证**: 需要 Bearer Token

**查询参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| skip | integer | 否 | 跳过的记录数 (默认 0) |
| limit | integer | 否 | 每页记录数 (默认 10) |
| status | string | 否 | 状态过滤 |

**响应示例** (200 OK):
```json
{
  "data": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "batch_id": "batch_20251107_001",
      "status": "completed",
      "progress": 100,
      "total_count": 3,
      "completed_count": 3,
      "failed_count": 0,
      "created_at": "2025-11-07T18:00:00",
      "completed_at": "2025-11-07T18:30:00"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 10
}
```

---

## 数据模型

### AdminUser (管理员)

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "is_active": true,
  "is_superadmin": true,
  "created_at": "2025-11-01T10:00:00",
  "last_login": "2025-11-07T18:30:00"
}
```

**字段说明**:
- `id` - 用户 ID
- `username` - 用户名 (唯一)
- `email` - 电子邮件 (唯一)
- `full_name` - 全名
- `is_active` - 是否活跃
- `is_superadmin` - 是否超级管理员
- `created_at` - 创建时间
- `last_login` - 最后登录时间

---

### Platform (平台)

```json
{
  "id": 1,
  "name": "Binance",
  "description": "全球最大的加密货币交易所",
  "rating": 4.8,
  "rank": 1,
  "min_leverage": 1.0,
  "max_leverage": 125.0,
  "commission_rate": 0.001,
  "is_regulated": true,
  "logo_url": "https://...",
  "website_url": "https://binance.com",
  "is_active": true,
  "is_featured": true,
  "created_at": "2025-11-01T10:00:00",
  "updated_at": "2025-11-07T15:30:00"
}
```

**字段说明**:
- `id` - 平台 ID
- `name` - 平台名称
- `description` - 平台描述
- `rating` - 评分 (0-5)
- `rank` - 排名
- `min_leverage` - 最小杠杆
- `max_leverage` - 最大杠杆
- `commission_rate` - 手续费率 (0-1)
- `is_regulated` - 是否受监管
- `logo_url` - Logo URL
- `website_url` - 官网 URL
- `is_active` - 是否活跃
- `is_featured` - 是否精选
- `created_at` - 创建时间
- `updated_at` - 更新时间

---

### Article (文章)

```json
{
  "id": 1,
  "title": "Bitcoin 初学者指南",
  "slug": "bitcoin-beginners-guide",
  "content": "这是一篇完整的 Bitcoin 介绍文章...",
  "summary": "快速了解 Bitcoin 的要点",
  "category": "教程",
  "tags": ["bitcoin", "加密货币", "初学者"],
  "platform_id": 1,
  "author_id": 1,
  "author": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  },
  "meta_description": "Learn about Bitcoin",
  "meta_keywords": "bitcoin, cryptocurrency",
  "view_count": 1251,
  "like_count": 89,
  "is_published": true,
  "is_featured": true,
  "published_at": "2025-11-01T10:00:00",
  "created_at": "2025-10-30T08:00:00",
  "updated_at": "2025-11-07T15:30:00"
}
```

**字段说明**:
- `id` - 文章 ID
- `title` - 文章标题
- `slug` - URL 友好的标识符
- `content` - 文章内容
- `summary` - 文章摘要
- `category` - 分类
- `tags` - 标签列表
- `platform_id` - 所属平台 ID
- `author_id` - 作者 ID
- `author` - 作者信息对象
- `meta_description` - SEO 描述
- `meta_keywords` - SEO 关键词
- `view_count` - 浏览数
- `like_count` - 点赞数
- `is_published` - 是否已发布
- `is_featured` - 是否精选
- `published_at` - 发布时间
- `created_at` - 创建时间
- `updated_at` - 更新时间

---

### AIGenerationTask (AI 生成任务)

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "batch_id": "batch_20251107_001",
  "status": "processing",
  "progress": 66,
  "celery_status": "active",
  "celery_task_id": "abc123def456",
  "total_count": 3,
  "completed_count": 2,
  "failed_count": 0,
  "error_message": null,
  "created_at": "2025-11-07T18:00:00",
  "started_at": "2025-11-07T18:05:00",
  "completed_at": null,
  "last_update": "2025-11-07T18:15:00"
}
```

**字段说明**:
- `task_id` - 任务 UUID
- `batch_id` - 批次 ID
- `status` - 任务状态
- `progress` - 进度百分比 (0-100)
- `celery_status` - Celery 任务状态
- `celery_task_id` - Celery 任务 ID
- `total_count` - 总文章数
- `completed_count` - 已完成数
- `failed_count` - 失败数
- `error_message` - 错误信息
- `created_at` - 创建时间
- `started_at` - 开始时间
- `completed_at` - 完成时间
- `last_update` - 最后更新时间

---

## HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功或其他不需要返回体的成功操作 |
| 400 | Bad Request | 请求参数错误或验证失败 |
| 401 | Unauthorized | 未授权，需要登录或 Token 过期 |
| 403 | Forbidden | 无权访问该资源 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器错误 |

---

## 常见问题

### Q: 如何获取 API 文档?
**A**: 访问 `http://localhost:8001/api/docs` (Swagger UI) 或 `http://localhost:8001/api/redoc` (ReDoc)

### Q: Token 过期了怎么办?
**A**: 需要重新登录，获取新的 Token

### Q: 如何在请求中使用 Token?
**A**: 在 HTTP Header 中添加 `Authorization: Bearer YOUR_TOKEN`

### Q: 一次最多可以生成多少篇文章?
**A**: 一次最多 100 篇

### Q: 如何监控任务进度?
**A**: 使用 `/api/tasks/{task_id}/progress` 端点定时查询

### Q: 是否支持 CORS 跨域请求?
**A**: 是的，已配置 CORS，允许配置的源进行跨域请求

---

**更新日期**: 2025-11-07  
**API 版本**: 1.0.0  
**维护者**: TrustAgency Team

