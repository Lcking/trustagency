# 📱 前端集成指南 - Mock 数据 → 真实 API

**文档**: 前端从 Mock 数据迁移到真实后端 API 的完整指南  
**目标**: 替换所有硬编码的 Mock 数据为动态 API 调用  
**优先级**: 后端完成后的第一步  

---

## 📊 现状分析

### Mock 数据当前位置

#### 1. 首页平台卡片 (`site/index.html`)
```html
<!-- 当前: 硬编码 3 个平台 -->
<div class="row">
  <div class="col-md-4">
    <div class="card platform-card">
      <h3>Alpha Leverage</h3>
      <p>Rating: 4.8/5</p>
      <!-- ... 硬编码内容 ... -->
    </div>
  </div>
  <!-- 重复 2 次 -->
</div>
```

#### 2. 知识库分类 (`site/wiki/index.html`)
```html
<!-- 当前: 硬编码文章列表 -->
<div class="articles-list">
  <div class="article-item">
    <h4>什么是杠杆交易</h4>
    <!-- ... 硬编码内容 ... -->
  </div>
</div>
```

#### 3. 平台详情页 (`site/platforms/[name]/index.html`)
```html
<!-- 当前: 完全硬编码的平台数据 -->
```

---

## 🔄 迁移步骤

### Step 1: 创建 API 客户端模块

创建 `site/assets/js/api.js`:

```javascript
/**
 * TrustAgency API 客户端
 * 处理所有与后端的通信
 */

class TrustAgencyAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.token = null;
    this.loadToken();
  }

  // ==================== 认证 ====================

  async login(username, password) {
    /**
     * 管理员登录 (仅用于管理页面)
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) throw new Error('Login failed');

      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('admin_token', this.token);
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout() {
    /**
     * 登出
     */
    this.token = null;
    localStorage.removeItem('admin_token');
  }

  loadToken() {
    /**
     * 从 localStorage 加载保存的 token
     */
    this.token = localStorage.getItem('admin_token');
  }

  getAuthHeader() {
    /**
     * 获取认证头
     */
    if (!this.token) return {};
    return { 'Authorization': `Bearer ${this.token}` };
  }

  // ==================== 平台相关 API ====================

  async getPlatforms() {
    /**
     * 获取所有平台 (公开 API)
     * 返回: [{id, name, slug, rating, rank, ...}, ...]
     */
    try {
      const response = await fetch(`${this.baseURL}/platforms`);
      if (!response.ok) throw new Error('Failed to fetch platforms');
      return await response.json();
    } catch (error) {
      console.error('Error fetching platforms:', error);
      return [];
    }
  }

  async getPlatform(platformId) {
    /**
     * 获取单个平台详情
     */
    try {
      const response = await fetch(`${this.baseURL}/platforms/${platformId}`);
      if (!response.ok) throw new Error('Failed to fetch platform');
      return await response.json();
    } catch (error) {
      console.error('Error fetching platform:', error);
      return null;
    }
  }

  async createPlatform(platformData) {
    /**
     * 创建平台 (管理员 API)
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/platforms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeader()
        },
        body: JSON.stringify(platformData)
      });

      if (!response.ok) throw new Error('Failed to create platform');
      return await response.json();
    } catch (error) {
      console.error('Error creating platform:', error);
      throw error;
    }
  }

  async updatePlatform(platformId, platformData) {
    /**
     * 更新平台 (管理员 API)
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/platforms/${platformId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeader()
        },
        body: JSON.stringify(platformData)
      });

      if (!response.ok) throw new Error('Failed to update platform');
      return await response.json();
    } catch (error) {
      console.error('Error updating platform:', error);
      throw error;
    }
  }

  async deletePlatform(platformId) {
    /**
     * 删除平台 (管理员 API)
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/platforms/${platformId}`, {
        method: 'DELETE',
        headers: this.getAuthHeader()
      });

      if (!response.ok) throw new Error('Failed to delete platform');
      return await response.json();
    } catch (error) {
      console.error('Error deleting platform:', error);
      throw error;
    }
  }

  // ==================== 文章相关 API ====================

  async getArticles(category = null, page = 1, limit = 10) {
    /**
     * 获取文章列表 (公开 API)
     * 参数: category (wiki|guide|faq), page, limit
     * 返回: [{id, title, slug, category, status, ...}, ...]
     */
    try {
      let url = `${this.baseURL}/articles?page=${page}&limit=${limit}`;
      if (category) url += `&category=${category}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch articles');
      return await response.json();
    } catch (error) {
      console.error('Error fetching articles:', error);
      return [];
    }
  }

  async getArticle(slug) {
    /**
     * 获取单篇文章详情
     */
    try {
      const response = await fetch(`${this.baseURL}/articles/${slug}`);
      if (!response.ok) throw new Error('Failed to fetch article');
      return await response.json();
    } catch (error) {
      console.error('Error fetching article:', error);
      return null;
    }
  }

  async createArticle(articleData) {
    /**
     * 创建文章 (管理员 API)
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/articles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeader()
        },
        body: JSON.stringify(articleData)
      });

      if (!response.ok) throw new Error('Failed to create article');
      return await response.json();
    } catch (error) {
      console.error('Error creating article:', error);
      throw error;
    }
  }

  // ==================== AI 生成相关 API ====================

  async startGeneration(titles, model, systemPrompt, category) {
    /**
     * 开始 AI 文章生成任务
     * 返回: {task_id, status}
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/generate/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeader()
        },
        body: JSON.stringify({
          titles,
          model,
          system_prompt: systemPrompt,
          category
        })
      });

      if (!response.ok) throw new Error('Failed to start generation');
      return await response.json();
    } catch (error) {
      console.error('Error starting generation:', error);
      throw error;
    }
  }

  async getGenerationProgress(taskId) {
    /**
     * 获取生成任务进度
     * 返回: {status, progress, success_count, failed_count, ...}
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/generate/tasks/${taskId}`, {
        headers: this.getAuthHeader()
      });

      if (!response.ok) throw new Error('Failed to fetch progress');
      return await response.json();
    } catch (error) {
      console.error('Error fetching progress:', error);
      throw error;
    }
  }

  async getGenerationResults(taskId) {
    /**
     * 获取生成结果
     */
    try {
      const response = await fetch(`${this.baseURL}/admin/generate/tasks/${taskId}/results`, {
        headers: this.getAuthHeader()
      });

      if (!response.ok) throw new Error('Failed to fetch results');
      return await response.json();
    } catch (error) {
      console.error('Error fetching results:', error);
      throw error;
    }
  }
}

// 全局 API 实例
const api = new TrustAgencyAPI();
```

### Step 2: 更新首页平台卡片

修改 `site/index.html`:

```html
<!-- 替换前: 硬编码卡片 -->
<!-- <div class="row">
  <div class="col-md-4">
    <div class="card platform-card">
      <h3>Alpha Leverage</h3>
      ...
    </div>
  </div>
  ...
</div> -->

<!-- 替换后: 动态渲染 -->
<div class="row" id="platforms-container">
  <!-- 由 JavaScript 填充 -->
</div>

<script>
async function loadPlatforms() {
  const platforms = await api.getPlatforms();
  
  // 取前 3 个平台显示
  const topPlatforms = platforms.slice(0, 3);
  
  const container = document.getElementById('platforms-container');
  container.innerHTML = topPlatforms.map(platform => `
    <div class="col-md-4">
      <div class="card platform-card">
        <img src="${platform.logo_url || '/assets/images/placeholder.png'}" class="card-img-top" />
        <div class="card-body">
          <h3 class="card-title">${platform.name}</h3>
          <p class="card-text">${platform.description}</p>
          <div class="platform-meta">
            <span class="badge badge-primary">Rating: ${platform.rating}/5</span>
            <span class="badge badge-info">Rank #${platform.rank}</span>
          </div>
          <div class="platform-details">
            <p>Leverage: ${platform.min_leverage}x - ${platform.max_leverage}x</p>
            <p>Commission: ${platform.commission_rate}%</p>
          </div>
          <a href="/platforms/${platform.slug}/" class="btn btn-primary">详情</a>
        </div>
      </div>
    </div>
  `).join('');
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', loadPlatforms);
</script>
```

### Step 3: 更新知识库页面

修改 `site/wiki/index.html`:

```html
<!-- 替换前: 硬编码文章列表 -->

<!-- 替换后: 动态加载 -->
<div class="wiki-content">
  <h2>知识库</h2>
  
  <!-- 分类选项卡 -->
  <ul class="nav nav-tabs">
    <li class="nav-item">
      <a class="nav-link active" href="#" data-category="wiki">Wiki</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="#" data-category="guide">指南</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="#" data-category="faq">常见问题</a>
    </li>
  </ul>
  
  <!-- 文章列表容器 -->
  <div class="articles-list" id="articles-container">
    <!-- 由 JavaScript 填充 -->
  </div>
  
  <!-- 分页 -->
  <nav aria-label="Page navigation" id="pagination">
    <!-- 由 JavaScript 填充 -->
  </nav>
</div>

<script>
let currentCategory = 'wiki';
let currentPage = 1;

async function loadArticles() {
  const articles = await api.getArticles(currentCategory, currentPage, 10);
  
  const container = document.getElementById('articles-container');
  
  if (articles.length === 0) {
    container.innerHTML = '<p>暂无文章</p>';
    return;
  }
  
  container.innerHTML = articles.map(article => `
    <div class="article-item">
      <h4>
        <a href="/articles/${article.slug}/">${article.title}</a>
      </h4>
      <p class="article-meta">
        分类: <span class="category-badge">${article.category}</span>
        ${article.ai_generated ? '<span class="badge badge-info">AI生成</span>' : ''}
      </p>
      <p class="article-preview">${article.content.substring(0, 200)}...</p>
      <a href="/articles/${article.slug}/">阅读全文 →</a>
    </div>
  `).join('');
}

// 分类标签点击事件
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    
    // 更新активную вкладку
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    e.target.classList.add('active');
    
    // 加载新分类
    currentCategory = e.target.dataset.category;
    currentPage = 1;
    loadArticles();
  });
});

// 页面加载时加载首个分类
document.addEventListener('DOMContentLoaded', loadArticles);
</script>
```

### Step 4: 更新平台详情页

创建动态平台详情模板 `site/platforms/platform-detail-template.html`:

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title id="page-title">平台详情</title>
  <!-- ... head 内容 ... -->
</head>
<body>
  <!-- 导航栏 (从 index.html 复制) -->
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <!-- ... 导航内容 ... -->
  </nav>

  <!-- 平台详情 -->
  <div class="container mt-5">
    <div class="platform-detail" id="platform-detail">
      <!-- 由 JavaScript 填充 -->
    </div>
  </div>

  <!-- 页脚 (从 index.html 复制) -->
  <footer>
    <!-- ... 页脚内容 ... -->
  </footer>

  <script src="/assets/js/api.js"></script>
  <script>
    async function loadPlatformDetail() {
      // 从 URL 获取平台 slug
      const pathParts = window.location.pathname.split('/');
      const platformSlug = pathParts[2]; // /platforms/{slug}/
      
      const platforms = await api.getPlatforms();
      const platform = platforms.find(p => p.slug === platformSlug);
      
      if (!platform) {
        document.getElementById('platform-detail').innerHTML = 
          '<div class="alert alert-danger">平台未找到</div>';
        return;
      }
      
      // 更新页面标题
      document.title = `${platform.name} - TrustAgency`;
      document.getElementById('page-title').textContent = platform.name;
      
      // 填充平台详情
      const container = document.getElementById('platform-detail');
      container.innerHTML = `
        <div class="row">
          <div class="col-md-8">
            <h1>${platform.name}</h1>
            <p class="lead">${platform.description}</p>
            
            <div class="platform-stats">
              <div class="stat-card">
                <h5>评分</h5>
                <p class="stat-value">${platform.rating} / 5.0</p>
              </div>
              <div class="stat-card">
                <h5>排名</h5>
                <p class="stat-value">#${platform.rank}</p>
              </div>
              <div class="stat-card">
                <h5>杠杆倍数</h5>
                <p class="stat-value">${platform.min_leverage}x - ${platform.max_leverage}x</p>
              </div>
              <div class="stat-card">
                <h5>佣金</h5>
                <p class="stat-value">${platform.commission_rate}%</p>
              </div>
            </div>
            
            <div class="platform-info">
              <h3>平台信息</h3>
              <ul>
                <li>建立年份: ${platform.established_year || 'N/A'}</li>
                <li>监管状态: ${platform.regulated ? '已监管 ✓' : '未监管'}</li>
                <li>官方网站: <a href="${platform.website_url}" target="_blank">${platform.website_url}</a></li>
              </ul>
            </div>
            
            <div class="platform-features">
              <h3>主要特性</h3>
              <!-- 可以从数据库扩展字段 -->
              <ul>
                <li>专业的交易平台</li>
                <li>实时市场数据</li>
                <li>24/7 客户支持</li>
              </ul>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="platform-sidebar">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">快速开户</h5>
                  <a href="${platform.website_url}" class="btn btn-primary btn-block" target="_blank">
                    访问官网
                  </a>
                </div>
              </div>
              
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">相关文章</h5>
                  <div id="related-articles"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
      
      // 加载相关文章
      loadRelatedArticles(platform.name);
    }
    
    async function loadRelatedArticles(platformName) {
      const articles = await api.getArticles();
      const related = articles.filter(a => 
        a.title.includes(platformName) || 
        a.content.includes(platformName)
      ).slice(0, 3);
      
      const container = document.getElementById('related-articles');
      if (related.length === 0) {
        container.innerHTML = '<p>暂无相关文章</p>';
        return;
      }
      
      container.innerHTML = related.map(article => `
        <div class="related-article">
          <a href="/articles/${article.slug}/">${article.title}</a>
        </div>
      `).join('');
    }
    
    // 加载
    document.addEventListener('DOMContentLoaded', loadPlatformDetail);
  </script>
</body>
</html>
```

---

## 🔐 后端接口需求清单

后端需要提供以下 API 端点 (确认已实现):

### 公开 API (无需认证)

```
✅ GET  /api/platforms
✅ GET  /api/platforms/:id
✅ GET  /api/articles
✅ GET  /api/articles/:slug
✅ GET  /api/statistics (可选)
```

### 管理员 API (需要认证)

```
✅ POST   /api/admin/login
✅ GET    /api/admin/me
✅ POST   /api/admin/logout

✅ POST   /api/admin/platforms
✅ PUT    /api/admin/platforms/:id
✅ DELETE /api/admin/platforms/:id

✅ POST   /api/admin/articles
✅ PUT    /api/admin/articles/:id
✅ DELETE /api/admin/articles/:id

✅ POST   /api/admin/generate/create
✅ GET    /api/admin/generate/tasks/:task_id
✅ GET    /api/admin/generate/tasks/:task_id/results
```

---

## 🎨 页面迁移优先级

| 优先级 | 页面 | 数据源 | 复杂度 | 工作量 |
|-------|------|--------|--------|--------|
| P0 | index.html | 平台 | 低 | 1h |
| P0 | platforms/ | 平台 | 中 | 1.5h |
| P1 | wiki/ | 文章 (wiki) | 中 | 1h |
| P1 | guides/ | 文章 (guide) | 中 | 1h |
| P1 | qa/ | 文章 (faq) | 中 | 1h |
| P2 | compare/ | 平台对比 | 高 | 2h |
| P2 | 搜索功能 | 文章 + 平台 | 高 | 2h |

---

## ✅ 测试检查清单

```javascript
// 在浏览器控制台测试

// 1. 测试获取平台
await api.getPlatforms()
// 应该返回: [{id, name, slug, rating, ...}, ...]

// 2. 测试获取文章
await api.getArticles('wiki')
// 应该返回: [{id, title, slug, content, ...}, ...]

// 3. 测试单篇文章
await api.getArticle('some-article-slug')
// 应该返回: {id, title, slug, content, ...}

// 4. 测试登录 (仅管理页面)
await api.login('admin', 'password')
// 应该返回: {access_token, token_type}

// 5. 测试生成任务 (仅管理页面)
await api.startGeneration(
  ['标题1', '标题2'],
  'gpt-4',
  '你是专业编辑',
  'wiki'
)
// 应该返回: {task_id, status}
```

---

## 🚀 迁移时间表

| Phase | 任务 | 耗时 |
|-------|------|------|
| 1 | 创建 API 客户端 | 1h |
| 2 | 更新首页 | 1h |
| 3 | 更新知识库页面 | 3h |
| 4 | 更新平台详情 | 1.5h |
| 5 | 测试所有页面 | 1.5h |
| 6 | 优化和修复 | 1h |
| **总计** | | **8-9h** |

---

## 💡 关键配置

### 后端 CORS 配置

确保后端配置允许前端访问:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "https://yourdomain.com"  # 生产域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 前端 API 基础 URL

如果后端和前端在不同端口:

```javascript
// 开发环境
const api = new TrustAgencyAPI('http://localhost:8001/api');

// 生产环境
const api = new TrustAgencyAPI('/api');
```

---

## 🎯 后续优化

### 缓存策略

```javascript
// 添加本地缓存以减少 API 调用
class CachedAPI extends TrustAgencyAPI {
  constructor(baseURL) {
    super(baseURL);
    this.cache = new Map();
  }

  async getPlatforms() {
    const cacheKey = 'platforms';
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < 3600000) {
      return cached.data;  // 1 小时缓存
    }
    
    const data = await super.getPlatforms();
    this.cache.set(cacheKey, { data, timestamp: Date.now() });
    return data;
  }
}
```

### 错误处理

```javascript
// 添加更完善的错误处理
async function loadWithErrorHandling(fn) {
  try {
    return await fn();
  } catch (error) {
    console.error('API Error:', error);
    showErrorNotification('加载失败，请刷新重试');
    return null;
  }
}
```

### 加载状态

```javascript
// 添加加载指示器
async function loadArticles() {
  const container = document.getElementById('articles-container');
  container.innerHTML = '<p>加载中...</p>';
  
  const articles = await api.getArticles(currentCategory, currentPage);
  
  if (articles.length === 0) {
    container.innerHTML = '<p>暂无文章</p>';
    return;
  }
  
  container.innerHTML = /* ... */;
}
```

---

**现在你有了完整的前端集成计划！** 🎉

一旦后端完成，按照这个指南就能快速集成所有页面。
