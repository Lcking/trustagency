# API 使用指南

**版本**: 1.0.0  
**最后更新**: 2025-11-12  
**维护者**: Backend Team

---

## 📚 目录

1. [基础知识](#基础知识)
2. [认证](#认证)
3. [常见操作](#常见操作)
4. [错误处理](#错误处理)
5. [最佳实践](#最佳实践)
6. [常见问题](#常见问题)

---

## 基础知识

### API 基础 URL

**本地开发**:
```
http://localhost:8001/api
```

**生产环境**:
```
https://api.trustagency.com/api
```

### 主要特性

| 特性 | 说明 |
|-----|------|
| **认证** | JWT Bearer Token |
| **数据格式** | JSON |
| **分页** | skip/limit 模式 |
| **排序** | sort_by/sort_order 参数 |
| **搜索** | 全文搜索支持 |
| **速率限制** | 每分钟 60 请求 (后续实现) |

### 响应格式

所有 API 响应都遵循以下格式：

**成功响应 (2xx)**:
```json
{
  "data": { /* 业务数据 */ },
  "timestamp": "2025-11-12T10:30:00",
  "request_id": "req_abc123def456"
}
```

**错误响应 (4xx/5xx)**:
```json
{
  "detail": "错误描述",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

---

## 认证

### 获取 Token

使用用户名和密码登录：

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

### 使用 Token

在请求头中添加 Authorization：

```bash
curl -X GET http://localhost:8001/api/articles \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Token 过期

Token 默认有效期为 24 小时。过期后可以：

1. **重新登录**获取新的 token
2. **使用刷新端点** (后续实现):
   ```bash
   curl -X POST http://localhost:8001/api/auth/refresh \
     -H "Authorization: Bearer OLD_TOKEN"
   ```

---

## 常见操作

### 1. 创建文章

```bash
curl -X POST http://localhost:8001/api/articles \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "深度学习入门",
    "slug": "deep-learning-intro",
    "content": "<h1>深度学习</h1><p>深度学习是...</p>",
    "summary": "这是一篇关于深度学习的入门文章",
    "category_id": 1,
    "platform_id": 1,
    "is_published": false
  }'
```

**响应 (201)**:
```json
{
  "id": 42,
  "title": "深度学习入门",
  "slug": "deep-learning-intro",
  "created_at": "2025-11-12T11:00:00",
  "author_id": 1
}
```

### 2. 搜索文章

获取包含特定关键词的文章：

```bash
# 按标题和内容搜索
curl -X GET "http://localhost:8001/api/articles?search=python&limit=20" \
  -H "Authorization: Bearer TOKEN"

# 按分类过滤
curl -X GET "http://localhost:8001/api/articles?category_id=5&sort_by=like_count&sort_order=desc" \
  -H "Authorization: Bearer TOKEN"
```

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "title": "Python 完全指南",
      "slug": "python-guide",
      "summary": "...",
      "view_count": 1250,
      "like_count": 85
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

### 3. 发布文章

将草稿文章发布：

```bash
curl -X PATCH http://localhost:8001/api/articles/42/publish \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"
```

**响应**:
```json
{
  "id": 42,
  "is_published": true,
  "published_at": "2025-11-12T12:00:00"
}
```

### 4. 上传图片

```bash
curl -X POST http://localhost:8001/api/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@/path/to/image.jpg"
```

**响应**:
```json
{
  "filename": "image-2025-11-12-abc123.jpg",
  "url": "/static/uploads/image-2025-11-12-abc123.jpg",
  "size": 245632,
  "mime_type": "image/jpeg"
}
```

### 5. 获取分类列表

```bash
curl -X GET "http://localhost:8001/api/categories?section_id=1" \
  -H "Authorization: Bearer TOKEN"
```

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "编程语言",
      "slug": "programming-languages",
      "section_id": 1,
      "article_count": 25
    },
    {
      "id": 2,
      "name": "框架和库",
      "slug": "frameworks",
      "section_id": 1,
      "article_count": 18
    }
  ],
  "total": 8
}
```

---

## 错误处理

### 常见错误

| 状态码 | 错误代码 | 说明 | 处理方式 |
|--------|---------|------|--------|
| 400 | VALIDATION_ERROR | 请求参数无效 | 检查参数格式 |
| 401 | UNAUTHORIZED | 未认证 | 提供有效 token |
| 403 | FORBIDDEN | 权限不足 | 使用有权限的账户 |
| 404 | NOT_FOUND | 资源不存在 | 检查 ID 是否正确 |
| 409 | CONFLICT | 资源冲突 (如重复 slug) | 修改冲突字段 |
| 422 | UNPROCESSABLE_ENTITY | 业务逻辑错误 | 检查业务规则 |
| 500 | INTERNAL_ERROR | 服务器错误 | 稍后重试或联系支持 |

### 错误响应示例

**400 - 验证错误**:
```json
{
  "detail": "1 validation error for Request body",
  "error_code": "VALIDATION_ERROR",
  "status_code": 400
}
```

**401 - 认证失败**:
```json
{
  "detail": "Invalid credentials",
  "error_code": "UNAUTHORIZED",
  "status_code": 401
}
```

**404 - 资源不存在**:
```json
{
  "detail": "Article not found",
  "error_code": "NOT_FOUND",
  "status_code": 404
}
```

**409 - Slug 已存在**:
```json
{
  "detail": "Article with this slug already exists",
  "error_code": "CONFLICT",
  "status_code": 409
}
```

---

## 最佳实践

### 1. 错误处理

始终检查响应状态码：

```python
import requests

def call_api(method, endpoint, **kwargs):
    """安全的 API 调用包装"""
    response = requests.request(method, endpoint, **kwargs)
    
    if response.status_code >= 400:
        error_data = response.json()
        raise Exception(f"API Error: {error_data['detail']}")
    
    return response.json()
```

### 2. Token 管理

安全地存储和使用 token：

```python
# 存储 token（在生产环境应使用更安全的方式）
import json

class TokenManager:
    def __init__(self, token_file='.token'):
        self.token_file = token_file
    
    def save_token(self, token_data):
        """保存 token"""
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)
    
    def get_token(self):
        """获取有效的 token"""
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                # 检查 token 是否过期
                if self.is_expired(token_data):
                    return self.refresh_token(token_data)
                return token_data['access_token']
        except FileNotFoundError:
            return None
    
    def is_expired(self, token_data):
        """检查 token 是否过期"""
        from datetime import datetime, timedelta
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        return datetime.now() > expires_at
    
    def refresh_token(self, token_data):
        """刷新 token"""
        # 实现刷新逻辑
        pass
```

### 3. 分页处理

正确处理分页数据：

```python
def get_all_articles(api_url, token):
    """获取所有文章（自动分页）"""
    articles = []
    skip = 0
    limit = 50  # 每次获取 50 条
    
    while True:
        response = requests.get(
            f"{api_url}/articles",
            params={'skip': skip, 'limit': limit},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.json()
        articles.extend(data['data'])
        
        # 检查是否还有更多数据
        if len(data['data']) < limit:
            break
        
        skip += limit
    
    return articles
```

### 4. 批量操作

进行批量操作时，控制并发：

```python
import asyncio
import aiohttp

async def upload_multiple_files(files, api_url, token):
    """异步上传多个文件"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for file in files:
            task = upload_file(session, file, api_url, token)
            tasks.append(task)
        
        # 限制并发数
        return await asyncio.gather(*tasks)

async def upload_file(session, file, api_url, token):
    """上传单个文件"""
    with open(file, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('file', f, filename=file)
        
        async with session.post(
            f"{api_url}/upload",
            data=data,
            headers={'Authorization': f'Bearer {token}'}
        ) as resp:
            return await resp.json()
```

### 5. 缓存策略

使用缓存减少 API 调用：

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedAPIClient:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.token = token
        self.cache = {}
        self.cache_ttl = {}
    
    def get_categories(self, section_id=None):
        """获取分类（使用缓存）"""
        cache_key = f"categories_{section_id}"
        
        # 检查缓存是否有效
        if cache_key in self.cache:
            if datetime.now() < self.cache_ttl[cache_key]:
                return self.cache[cache_key]
        
        # 从 API 获取
        response = requests.get(
            f"{self.api_url}/categories",
            params={'section_id': section_id},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        data = response.json()
        
        # 缓存 1 小时
        self.cache[cache_key] = data
        self.cache_ttl[cache_key] = datetime.now() + timedelta(hours=1)
        
        return data
```

---

## 常见问题

### Q1: 如何获取所有已发布的文章？

```bash
curl -X GET "http://localhost:8001/api/articles?is_published=true&limit=100" \
  -H "Authorization: Bearer TOKEN"
```

### Q2: 如何按热度排序文章？

```bash
curl -X GET "http://localhost:8001/api/articles?sort_by=like_count&sort_order=desc" \
  -H "Authorization: Bearer TOKEN"
```

### Q3: Slug 有什么要求？

- 长度: 3-50 个字符
- 字符: 只能包含小写字母、数字、连字符 (-)
- 格式: `article-title-123`

### Q4: Token 过期了怎么办？

使用 token 会收到 401 错误，此时需要重新登录获取新 token。

### Q5: 如何处理大文件上传？

- 单个文件最大 10MB
- 可以使用 `/api/upload/multiple` 批量上传
- 对于超大文件，需要分片上传 (待实现)

### Q6: API 有速率限制吗？

目前没有实现速率限制，后续版本会添加。建议不要频繁查询同一数据，使用缓存。

### Q7: 支持 CORS 吗？

是的，支持 CORS。允许的来源配置在环境变量中。

### Q8: 如何调试 API？

访问 Swagger UI: `http://localhost:8001/api/docs`
或 ReDoc: `http://localhost:8001/api/redoc`

---

## 📞 获取帮助

- **文档**: 查看 [API 审计报告](./API_AUDIT.md)
- **示例**: 查看 [Postman 集合](./TrustAgency_API.postman_collection.json)
- **支持**: 联系开发团队或提交 Issue

---

**版本**: 1.0.0  
**最后更新**: 2025-11-12
