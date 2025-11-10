# 📚 TrustAgency API 参考文档

**版本**: 1.0.0  
**基础URL**: http://localhost:8001  
**更新**: 2025-11-06

---

## 🎯 API 端点总览

**总端点数**: 30+  
**分类**: 5 个

### 快速导航

| 分类 | 端点数 | 状态 |
|------|--------|------|
| [认证](#认证) | 5 | ✅ |
| [平台](#平台管理) | 7 | ✅ |
| [文章](#文章管理) | 13 | ✅ |
| [管理后台](#管理后台) | 4 | ✅ NEW |
| [系统](#系统) | 1 | ✅ |

---

## 🔐 认证

基地址: `/api/admin`

### 注册
```http
POST /api/admin/register
Content-Type: application/json

{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password",
  "full_name": "Admin User"
}

响应 200:
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "is_active": true,
  "is_superadmin": false,
  "created_at": "2025-11-06T10:00:00",
  "last_login": null
}
```

### 登录
```http
POST /api/admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secure_password"
}

响应 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

### 获取当前用户
```http
GET /api/admin/me
Authorization: Bearer {token}

响应 200:
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "is_superadmin": true,
  "created_at": "2025-11-06T10:00:00",
  "last_login": "2025-11-06T17:00:00"
}
```

### 修改密码
```http
POST /api/admin/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "current_password",
  "new_password": "new_password"
}

响应 200: { "message": "密码已更新" }
```

### 登出
```http
POST /api/admin/logout
Authorization: Bearer {token}

响应 200: { "message": "已登出" }
```

---

## 🏢 平台管理

基地址: `/api/platforms`

### 获取所有平台
```http
GET /api/platforms?skip=0&limit=10&sort_by=rank&order=asc

查询参数:
- skip: 跳过数量 (default: 0)
- limit: 返回数量 (default: 10, max: 100)
- sort_by: 排序字段 (id, name, rating, rank, created_at)
- order: asc 或 desc
- search: 搜索关键词
- is_active: true/false
- is_featured: true/false

响应 200:
{
  "total": 50,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "name": "Binance",
      "rating": 4.8,
      "rank": 1,
      "is_regulated": true,
      "is_active": true,
      "is_featured": true,
      "created_at": "2025-11-06T10:00:00",
      "updated_at": "2025-11-06T15:00:00"
    }
  ]
}
```

### 创建平台
```http
POST /api/platforms
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Binance",
  "description": "Leading cryptocurrency exchange",
  "rating": 4.8,
  "min_leverage": 1,
  "max_leverage": 125,
  "commission_rate": 0.001,
  "is_regulated": true
}

响应 201: { "id": 1, ... }
```

### 更新平台
```http
PUT /api/platforms/{platform_id}
Authorization: Bearer {token}

{
  "rating": 4.9,
  "rank": 1,
  "is_featured": true
}

响应 200: { ... }
```

### 删除平台
```http
DELETE /api/platforms/{platform_id}
Authorization: Bearer {token}

响应 204: (无内容)
```

### 切换状态
```http
POST /api/platforms/{platform_id}/toggle-status
Authorization: Bearer {token}

响应 200: { "is_active": true }
```

### 切换精选状态
```http
POST /api/platforms/{platform_id}/toggle-featured
Authorization: Bearer {token}

响应 200: { "is_featured": true }
```

### 批量更新排名
```http
POST /api/platforms/bulk/update-ranks
Authorization: Bearer {token}
Content-Type: application/json

{
  "ranks": [
    { "platform_id": 1, "new_rank": 1 },
    { "platform_id": 2, "new_rank": 2 },
    { "platform_id": 3, "new_rank": 3 }
  ]
}

响应 200: { "updated_count": 3 }
```

### 获取受监管平台
```http
GET /api/platforms/regulated/list?limit=20

响应 200: { "items": [...] }
```

### 获取精选平台
```http
GET /api/platforms/featured/list?limit=10

响应 200: { "items": [...] }
```

---

## 📄 文章管理

基地址: `/api/articles`

### 获取所有文章
```http
GET /api/articles?skip=0&limit=10&category=review&sort_by=created_at&order=desc

查询参数:
- skip, limit: 分页
- category: review, guide, news
- search: 搜索标题/内容
- is_published: true/false
- platform_id: 按平台过滤
- author_id: 按作者过滤

响应 200:
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "title": "Bitcoin 2025 Investment Guide",
      "slug": "bitcoin-2025-investment-guide",
      "content": "...",
      "category": "guide",
      "is_published": true,
      "view_count": 1500,
      "like_count": 250,
      "created_at": "2025-11-05T10:00:00",
      "published_at": "2025-11-05T10:30:00"
    }
  ]
}
```

### 创建文章
```http
POST /api/articles
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Bitcoin Guide",
  "content": "Detailed content...",
  "category": "guide",
  "platform_id": 1,
  "tags": "bitcoin,crypto,guide"
}

响应 201: { "id": 1, "slug": "bitcoin-guide", ... }
```

### 更新文章
```http
PUT /api/articles/{article_id}
Authorization: Bearer {token}

{
  "title": "Updated Title",
  "content": "Updated content..."
}

响应 200: { ... }
```

### 删除文章
```http
DELETE /api/articles/{article_id}
Authorization: Bearer {token}

响应 204: (无内容)
```

### 发布文章
```http
POST /api/articles/{article_id}/publish
Authorization: Bearer {token}

响应 200: { "is_published": true, "published_at": "..." }
```

### 取消发布
```http
POST /api/articles/{article_id}/unpublish
Authorization: Bearer {token}

响应 200: { "is_published": false }
```

### 点赞
```http
POST /api/articles/{article_id}/like
Authorization: Bearer {token}

响应 200: { "like_count": 251 }
```

### 搜索文章
```http
GET /api/articles/search/by-keyword?keyword=bitcoin&skip=0&limit=10

响应 200: { "items": [...] }
```

### 获取热门文章
```http
GET /api/articles/trending/list?limit=10

响应 200: { "items": [...] }
```

### 获取精选文章
```http
GET /api/articles/featured/list?limit=10

响应 200: { "items": [...] }
```

### 按分类获取
```http
GET /api/articles/by-category/{category}?limit=10

响应 200: { "items": [...] }
```

### 按平台获取
```http
GET /api/articles/by-platform/{platform_id}?limit=10

响应 200: { "items": [...] }
```

### 按作者获取
```http
GET /api/articles/by-author/{author_id}?limit=10

响应 200: { "items": [...] }
```

---

## 📊 管理后台 ✨ (NEW in Task 6)

基地址: `/api/admin`

### 获取仪表板统计
```http
GET /api/admin/stats

响应 200:
{
  "platforms_count": 50,
  "articles_count": 100,
  "published_articles": 85,
  "active_tasks": 3,
  "total_views": 50000
}
```

### 获取平台列表（管理）
```http
GET /api/admin/platforms?skip=0&limit=10&search=binance&is_active=true

响应 200:
{
  "total": 50,
  "items": [...]
}
```

### 获取文章列表（管理）
```http
GET /api/admin/articles?skip=0&limit=10&search=bitcoin&category=guide

响应 200:
{
  "total": 100,
  "items": [...]
}
```

### 获取AI任务列表（管理）
```http
GET /api/admin/ai-tasks?skip=0&limit=10&status=pending

状态选项: pending, processing, completed, failed

响应 200:
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "batch_id": "batch_123",
      "batch_name": "Batch 1",
      "status": "processing",
      "progress": 45,
      "total_count": 10,
      "completed_count": 4,
      "failed_count": 1,
      "created_at": "2025-11-06T10:00:00"
    }
  ]
}
```

---

## 🏥 系统

### 健康检查
```http
GET /api/health

响应 200:
{
  "status": "ok",
  "message": "TrustAgency Backend is running"
}
```

---

## 🔗 API 文档

| 工具 | URL |
|------|-----|
| Swagger UI | http://localhost:8001/api/docs |
| ReDoc | http://localhost:8001/api/redoc |
| OpenAPI Schema | http://localhost:8001/api/openapi.json |

---

## 🔑 认证方式

所有需要认证的端点使用 **Bearer Token**:

```http
Authorization: Bearer <access_token>
```

Token 通过 `/api/admin/login` 获取，有效期: 24小时

---

## ⚠️ 错误响应

### 400 - 请求错误
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 - 未授权
```json
{
  "detail": "Not authenticated"
}
```

### 404 - 资源不存在
```json
{
  "detail": "Resource not found"
}
```

### 422 - 验证错误
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "Field is required",
      "type": "value_error"
    }
  ]
}
```

### 500 - 服务器错误
```json
{
  "detail": "Internal server error"
}
```

---

## 📈 分页说明

所有列表API都支持分页:

```
查询参数:
- skip: 跳过的记录数 (default: 0)
- limit: 返回的最大记录数 (default: 10, max: 100)

响应格式:
{
  "total": 总记录数,
  "skip": 跳过数,
  "limit": 限制数,
  "items": [...]
}
```

---

## 🔄 速率限制

当前未实现速率限制，建议：
- 每秒最多 100 个请求
- 批量操作使用 POST 端点

---

## 📝 更新日志

### v1.0.0 (2025-11-06)
- ✅ 认证系统完成
- ✅ 平台管理API完成
- ✅ 文章管理API完成
- ✅ 管理后台API完成 (NEW)
- ⏳ Celery异步任务队列 (即将推出)
- ⏳ AI内容生成 (即将推出)

---

## 💬 示例请求

### cURL
```bash
# 获取平台列表
curl -s http://localhost:8001/api/platforms | jq .

# 获取统计信息
curl -s http://localhost:8001/api/admin/stats | jq .

# 登录
curl -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq .
```

### Python
```python
import requests

# 获取统计
response = requests.get('http://localhost:8001/api/admin/stats')
print(response.json())

# 登录
auth = requests.post(
    'http://localhost:8001/api/admin/login',
    json={"username": "admin", "password": "password"}
).json()
```

### JavaScript
```javascript
// 获取统计
fetch('http://localhost:8001/api/admin/stats')
  .then(r => r.json())
  .then(data => console.log(data));

// 登录
fetch('http://localhost:8001/api/admin/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password' })
})
  .then(r => r.json())
  .then(data => console.log(data));
```

---

**最后更新**: 2025-11-06 17:50 UTC  
**维护者**: TrustAgency Team
