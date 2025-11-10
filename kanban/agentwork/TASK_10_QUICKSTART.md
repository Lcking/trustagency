# Task 10 快速启动和测试指南

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 激活虚拟环境
source venv/bin/activate

# 启动FastAPI服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**验证**:
```bash
curl http://localhost:8001/api/health
# 应该返回: {"status":"ok","message":"TrustAgency Backend is running"}
```

### 2. 启动其他服务

```bash
# Redis (需要另一个终端)
redis-server

# Celery Worker (需要另一个终端)
cd backend
celery -A app.celery_app worker --loglevel=info

# Flower监控 (需要另一个终端)
celery -A app.celery_app flower
```

### 3. 前端访问

```bash
# 使用Python简单HTTP服务器（或任何静态服务器）
cd /Users/ck/Desktop/Project/trustagency/site
python -m http.server 8000

# 访问: http://localhost:8000/
```

---

## 🧪 测试检查清单

### API连接测试

```bash
# 1. 健康检查
curl -s http://localhost:8001/api/health | json_pp

# 2. 平台列表
curl -s "http://localhost:8001/api/platforms?limit=5" | json_pp

# 3. 文章列表  
curl -s "http://localhost:8001/api/articles?limit=5" | json_pp

# 4. 健康检查（来自网页）
curl -s -H "User-Agent: Browser" http://localhost:8001/api/health
```

### 浏览器控制台测试

打开浏览器开发者工具 (F12)，在控制台运行：

```javascript
// 1. 检查API客户端
console.log(apiClient);

// 2. 测试健康检查
await apiClient.healthCheck().then(r => console.log(r));

// 3. 获取平台列表
await apiClient.getPlatforms({ limit: 5 }).then(r => console.log(r));

// 4. 启用调试模式
localStorage.setItem('apiDebug', 'true');

// 5. 检查缓存
console.log(apiClient.cache);

// 6. 测试令牌管理
apiClient.setToken('test-token-123', 3600);
console.log(apiClient.getToken());

// 7. 清除缓存
apiClient.clearCache();
```

---

## 🔧 配置说明

### API基础URL

默认: `http://localhost:8001/api`

修改:
```javascript
// 在浏览器控制台
localStorage.setItem('apiBaseURL', 'http://your-api-url/api');
```

### 调试模式

```javascript
// 启用
localStorage.setItem('apiDebug', 'true');

// 禁用
localStorage.setItem('apiDebug', 'false');
```

---

## 📊 功能测试

### 平台管理模块

```html
<!-- 在任何包含以下HTML的页面测试 -->
<div id="platforms-container"></div>

<script>
// 自动初始化并加载平台
// 页面加载时会自动调用 PlatformManager.init()
</script>
```

**测试项**:
- [ ] 页面加载时显示加载动画
- [ ] 平台列表加载并显示
- [ ] 搜索功能工作
- [ ] 过滤器工作
- [ ] 排序功能工作
- [ ] 分页正常工作

### 文章管理模块

```html
<!-- 在任何包含以下HTML的页面测试 -->
<div id="articles-container"></div>

<script>
// 自动初始化并加载文章
// 页面加载时会自动调用 ArticleManager.init()
</script>
```

**测试项**:
- [ ] 页面加载时显示加载动画
- [ ] 文章列表加载并显示
- [ ] 搜索功能工作
- [ ] 分类过滤工作
- [ ] 排序功能工作
- [ ] 分页正常工作

### 认证管理模块

**测试项**:
- [ ] 页面加载时显示登录/注册按钮
- [ ] 点击登录按钮显示登录模态框
- [ ] 点击注册按钮显示注册模态框
- [ ] 填写表单并提交
- [ ] 成功登录后显示用户名
- [ ] 点击登出按钮清除状态

---

## 🐛 故障排除

### 问题1: CORS错误

```
Access to XMLHttpRequest at 'http://localhost:8001/api/...' 
from origin 'http://localhost:8000' has been blocked
```

**解决方案**:
- 后端已配置CORS，确保后端服务运行

### 问题2: 平台/文章列表为空

```
"未找到符合条件的平台"
```

**解决方案**:
- 需要向数据库添加示例数据
- 运行: `cd backend && python quick_init_data.py`
- 或使用API创建数据

### 问题3: 令牌过期

```
Error: 登录已过期，请重新登录
```

**解决方案**:
- 自动刷新机制会处理
- 如需手动刷新: `await apiClient.refreshToken()`

### 问题4: 缓存问题

```
数据不更新
```

**解决方案**:
```javascript
// 清除所有缓存
apiClient.clearCache();

// 跳过缓存加载
await apiClient.getPlatforms({ skipCache: true });
```

---

## 📝 示例代码

### 获取平台列表

```javascript
const platforms = await apiClient.getPlatforms({
    page: 1,
    limit: 20,
    sort_by: 'rating'
});

console.log(platforms.data);      // 平台列表
console.log(platforms.total);     // 总数
console.log(platforms.skip);      // 跳过数
console.log(platforms.limit);     // 每页数量
```

### 搜索平台

```javascript
const results = await apiClient.searchPlatforms('Alpha', {
    minLeverage: 50,
    maxLeverage: 100
});

console.log(results.data);  // 搜索结果
```

### 用户登录

```javascript
const response = await apiClient.login('admin', 'password');

console.log(response.access_token);   // 访问令牌
console.log(response.refresh_token);  // 刷新令牌
console.log(response.user);           // 用户信息
```

### 获取当前用户

```javascript
const user = await apiClient.getCurrentUser();

console.log(user.id);
console.log(user.username);
console.log(user.email);
console.log(user.full_name);
```

### 创建文章

```javascript
const article = await apiClient.createArticle({
    title: '新文章',
    slug: 'new-article',
    summary: '摘要',
    content: '内容',
    category: 'education',
    is_featured: false
});

console.log(article.id);
```

---

## 📈 性能监控

### 查看API性能

```javascript
// 启用日志后，控制台会显示:
// [2025-11-06T...] API: Request: GET /api/platforms?limit=5
// [2025-11-06T...] API: Response success: 200 - GET:/api/platforms?limit=5

// 测量单次请求时间
console.time('api-call');
await apiClient.getPlatforms();
console.timeEnd('api-call');
```

### 缓存命中率

```javascript
// 查看缓存大小
console.log('缓存项数:', apiClient.cache.size);

// 查看缓存内容
console.log('缓存键:', Array.from(apiClient.cache.keys()));
```

---

## 🔍 调试技巧

### 1. 启用详细日志

```javascript
localStorage.setItem('apiDebug', 'true');

// 所有API调用将被日志记录
// 在浏览器控制台查看输出
```

### 2. 检查令牌

```javascript
// 查看当前令牌
console.log('Token:', apiClient.getToken());

// 查看令牌过期时间
console.log('Expires at:', localStorage.getItem('token_expires_at'));
```

### 3. 测试重试机制

```javascript
// 模拟网络错误
// 1. 停止后端服务
// 2. 尝试调用API
// 3. 观察自动重试（最多3次）
// 4. 启动后端服务
// 5. 查看是否自动恢复

await apiClient.getPlatforms();
```

### 4. 查看请求头

```javascript
// 在浏览器开发者工具 -> Network 标签
// 查看每个请求的 Authorization 头

// 应该看到类似:
// Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## ✅ 完整测试流程

1. **启动所有服务**
   ```bash
   # 终端1: 后端
   cd backend && python -m uvicorn app.main:app --port 8001
   
   # 终端2: Redis
   redis-server
   
   # 终端3: Celery
   cd backend && celery -A app.celery_app worker
   
   # 终端4: 前端
   cd site && python -m http.server 8000
   ```

2. **浏览器测试**
   - 打开 `http://localhost:8000`
   - 按F12打开开发者工具
   - 在控制台运行测试命令

3. **检查结果**
   - [ ] API连接成功
   - [ ] 缓存工作正常
   - [ ] 令牌管理正确
   - [ ] 所有功能模块可用

---

## 📞 支持

有问题? 检查以下:
1. 后端服务是否运行 (curl health endpoint)
2. CORS配置是否正确
3. 浏览器控制台是否有错误
4. 调试日志是否提供信息
5. 检查firewall/防火墙设置

---

**Happy Testing! 🚀**
