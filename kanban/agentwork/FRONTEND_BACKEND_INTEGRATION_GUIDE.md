# 🔌 前后端集成指南与接口文档

**文档版本**: 1.0  
**创建日期**: 2025-11-06  
**适用范围**: trustagency 项目前后端集成

---

## 📋 当前前端需要的数据接口

### 1. 首页数据

#### 推荐平台卡片
**当前实现**: 硬编码的静态数据
```html
<!-- 当前在 site/index.html 中 -->
<div class="card">
  <h3>Alpha Leverage</h3>
  <p>高杠杆、低费率的专业交易平台</p>
  <a href="/platforms/alpha-leverage/">查看详情</a>
</div>
```

**需要的 API**:
```
GET /api/platforms?limit=3&sort=-rating
返回最高评分的 3 个平台
```

**预期响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "Alpha Leverage",
      "slug": "alpha-leverage",
      "description": "高杠杆、低费率的专业交易平台",
      "logo_url": "/images/alpha-logo.png",
      "rating": 4.8,
      "min_leverage": 1,
      "max_leverage": 100,
      "commission_rate": 0.001,
      "risk_level": "high"
    },
    // ... 更多平台
  ],
  "total": 3
}
```

#### 常见问题列表
**当前实现**: HTML 中的手风琴组件
```html
<button class="accordion">什么是股票杠杆交易？</button>
<div class="panel">
  <p>内容...</p>
</div>
```

**需要的 API**:
```
GET /api/articles?category=faq&limit=10
返回常见问题列表
```

**预期响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "title": "什么是股票杠杆交易？",
      "slug": "what-is-leverage",
      "content": "杠杆交易是...",
      "category": "faq",
      "view_count": 1500,
      "created_at": "2025-10-21T10:00:00Z"
    },
    // ... 更多问题
  ],
  "total": 10
}
```

### 2. 平台详情页 (site/platforms/*/index.html)

**当前实现**: 每个平台一个单独的 HTML 文件

**需要的 API**:
```
GET /api/platforms/:slug
返回指定平台的完整信息
```

**预期响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "Alpha Leverage",
    "slug": "alpha-leverage",
    "description": "...",
    "logo_url": "/images/alpha-logo.png",
    "website_url": "https://alphaleverage.com",
    "established_year": 2018,
    "regulated": true,
    "min_leverage": 1,
    "max_leverage": 100,
    "commission_rate": 0.001,
    "risk_level": "high",
    "rating": 4.8,
    "reviews_count": 245,
    "features": [
      "高流动性",
      "低手续费",
      "风险管理工具"
    ],
    "pros": ["优点1", "优点2"],
    "cons": ["缺点1", "缺点2"],
    "reviews": [
      {
        "id": 1,
        "user": { "id": 1, "username": "user123" },
        "rating": 5,
        "title": "很好的平台",
        "content": "...",
        "created_at": "2025-11-01T10:00:00Z"
      }
    ]
  }
}
```

### 3. 平台对比页

**当前实现**: 静态表格

**需要的 API**:
```
POST /api/compare
Body: {
  "platform_ids": [1, 2, 3]
}
返回多个平台的对比数据
```

**预期响应**:
```json
{
  "code": 200,
  "data": {
    "comparison_fields": [
      "min_leverage",
      "max_leverage",
      "commission_rate",
      "rating",
      "established_year",
      "regulated"
    ],
    "platforms": [
      {
        "id": 1,
        "name": "Alpha Leverage",
        "values": {
          "min_leverage": 1,
          "max_leverage": 100,
          "commission_rate": 0.001,
          "rating": 4.8,
          "established_year": 2018,
          "regulated": true
        }
      },
      // ... 其他平台
    ]
  }
}
```

### 4. 知识库/Wiki 页面

**当前实现**: 静态 HTML

**需要的 API**:
```
GET /api/articles?category=wiki
GET /api/articles/:slug
返回知识库文章
```

**预期响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "什么是杠杆交易",
    "slug": "what-is-leverage",
    "content": "<h2>什么是杠杆交易</h2><p>...</p>",
    "category": "wiki",
    "view_count": 3000,
    "author": "admin",
    "published": true,
    "created_at": "2025-10-21T10:00:00Z",
    "updated_at": "2025-11-01T10:00:00Z",
    "related_articles": [
      {
        "id": 2,
        "title": "杠杆交易风险",
        "slug": "leverage-risks"
      }
    ]
  }
}
```

### 5. 指南页面

**当前实现**: 静态页面

**需要的 API**:
```
GET /api/articles?category=guide
GET /api/articles/:slug
返回指南文章
```

---

## 🔄 前端集成代码示例

### 示例 1：获取平台列表（首页）

```javascript
// 在 site/assets/js/main.js 中添加

class PlatformAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  async getPlatforms(options = {}) {
    const params = new URLSearchParams({
      limit: options.limit || 10,
      sort: options.sort || '-rating',
      ...options
    });
    
    const response = await fetch(`${this.baseURL}/platforms?${params}`);
    if (!response.ok) throw new Error('Failed to fetch platforms');
    return response.json();
  }

  async getPlatform(slug) {
    const response = await fetch(`${this.baseURL}/platforms/${slug}`);
    if (!response.ok) throw new Error('Platform not found');
    return response.json();
  }

  async comparePlatforms(platformIds) {
    const response = await fetch(`${this.baseURL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform_ids: platformIds })
    });
    if (!response.ok) throw new Error('Comparison failed');
    return response.json();
  }
}

// 使用示例
const api = new PlatformAPI();

// 在首页加载推荐平台
async function loadRecommendedPlatforms() {
  try {
    const result = await api.getPlatforms({ limit: 3 });
    const container = document.querySelector('.platforms-container');
    
    result.data.forEach(platform => {
      const card = createPlatformCard(platform);
      container.appendChild(card);
    });
  } catch (error) {
    console.error('Error loading platforms:', error);
  }
}

function createPlatformCard(platform) {
  const div = document.createElement('div');
  div.className = 'card';
  div.innerHTML = `
    <h3>${platform.name}</h3>
    <p>${platform.description}</p>
    <p>评分: ${platform.rating} / 5</p>
    <a href="/platforms/${platform.slug}/">查看详情</a>
  `;
  return div;
}

// 页面加载时调用
document.addEventListener('DOMContentLoaded', loadRecommendedPlatforms);
```

### 示例 2：提交评论

```javascript
// 用户评论表单

class ReviewAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  async submitReview(platformId, reviewData) {
    if (!this.token) {
      alert('请先登录');
      return;
    }

    const response = await fetch(
      `${this.baseURL}/platforms/${platformId}/reviews`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify(reviewData)
      }
    );

    if (!response.ok) throw new Error('Failed to submit review');
    return response.json();
  }

  async getReviews(platformId) {
    const response = await fetch(
      `${this.baseURL}/platforms/${platformId}/reviews`
    );
    if (!response.ok) throw new Error('Failed to fetch reviews');
    return response.json();
  }
}

// HTML 表单
const reviewForm = document.querySelector('#review-form');
const reviewAPI = new ReviewAPI();

reviewForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(reviewForm);
  const reviewData = {
    title: formData.get('title'),
    content: formData.get('content'),
    rating: parseInt(formData.get('rating'))
  };

  try {
    await reviewAPI.submitReview(platformId, reviewData);
    alert('评论提交成功');
    reviewForm.reset();
    // 刷新评论列表
    loadReviews();
  } catch (error) {
    alert('提交失败: ' + error.message);
  }
});
```

### 示例 3：用户认证

```javascript
// 用户登录/注册

class AuthAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) throw new Error('Login failed');
    
    const result = await response.json();
    localStorage.setItem('auth_token', result.data.token);
    localStorage.setItem('user', JSON.stringify(result.data.user));
    
    return result.data;
  }

  async register(username, email, password) {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    
    if (!response.ok) throw new Error('Registration failed');
    return response.json();
  }

  async logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  isLoggedIn() {
    return !!localStorage.getItem('auth_token');
  }
}
```

---

## 🛠️ 后端实现示例（Node.js + Express）

### 1. 平台路由

```javascript
// backend/src/routes/platforms.js
const express = require('express');
const router = express.Router();
const platformController = require('../controllers/platformController');

// 获取平台列表
router.get('/', platformController.getPlatforms);

// 获取单个平台
router.get('/:slug', platformController.getPlatform);

// 获取平台评论
router.get('/:id/reviews', platformController.getReviews);

// 提交评论
router.post('/:id/reviews', 
  authMiddleware, 
  platformController.submitReview
);

module.exports = router;
```

### 2. 平台控制器

```javascript
// backend/src/controllers/platformController.js

class PlatformController {
  async getPlatforms(req, res) {
    try {
      const limit = req.query.limit || 10;
      const sort = req.query.sort || '-rating';
      const riskLevel = req.query.risk;

      let query = 'SELECT * FROM platforms WHERE published = true';
      const params = [];

      // 风险等级筛选
      if (riskLevel) {
        query += ' AND risk_level = ?';
        params.push(riskLevel);
      }

      // 排序
      const sortField = sort.replace('-', '');
      const sortOrder = sort.startsWith('-') ? 'DESC' : 'ASC';
      query += ` ORDER BY ${sortField} ${sortOrder}`;

      // 分页
      query += ' LIMIT ?';
      params.push(parseInt(limit));

      const [platforms] = await db.query(query, params);

      res.json({
        code: 200,
        data: platforms,
        total: platforms.length
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }

  async getPlatform(req, res) {
    try {
      const { slug } = req.params;

      const [platforms] = await db.query(
        'SELECT * FROM platforms WHERE slug = ?',
        [slug]
      );

      if (platforms.length === 0) {
        return res.status(404).json({
          code: 404,
          message: 'Platform not found'
        });
      }

      res.json({
        code: 200,
        data: platforms[0]
      });
    } catch (error) {
      res.status(500).json({
        code: 500,
        message: error.message
      });
    }
  }
}

module.exports = new PlatformController();
```

### 3. 对比 API

```javascript
// backend/src/controllers/platformController.js (添加)

async comparePlatforms(req, res) {
  try {
    const { platform_ids } = req.body;

    if (!platform_ids || platform_ids.length === 0) {
      return res.status(400).json({
        code: 400,
        message: 'Platform IDs required'
      });
    }

    const placeholders = platform_ids.map(() => '?').join(',');
    const [platforms] = await db.query(
      `SELECT * FROM platforms WHERE id IN (${placeholders})`,
      platform_ids
    );

    res.json({
      code: 200,
      data: {
        comparison_fields: [
          'min_leverage',
          'max_leverage',
          'commission_rate',
          'rating',
          'established_year',
          'regulated'
        ],
        platforms: platforms.map(p => ({
          id: p.id,
          name: p.name,
          values: {
            min_leverage: p.min_leverage,
            max_leverage: p.max_leverage,
            commission_rate: p.commission_rate,
            rating: p.rating,
            established_year: p.established_year,
            regulated: p.regulated
          }
        }))
      }
    });
  } catch (error) {
    res.status(500).json({
      code: 500,
      message: error.message
    });
  }
}
```

---

## 📋 部署检查清单

### 后端部署前
- [ ] 所有 API 端点实现完成
- [ ] 数据库迁移脚本准备就绪
- [ ] 环境变量配置完成
- [ ] 错误处理完善
- [ ] 日志系统配置

### 前端集成
- [ ] API 调用代码集成
- [ ] 错误处理实现
- [ ] Loading 状态显示
- [ ] 用户反馈（提示/错误消息）
- [ ] 本地测试通过

### 发布前
- [ ] API 文档更新
- [ ] CORS 配置检查
- [ ] 速率限制配置
- [ ] 监控告警配置
- [ ] 备份策略确认

---

## 🔒 安全注意事项

### 前端
- [ ] 不在代码中存储敏感信息
- [ ] HTTPS 通信
- [ ] XSS 防护
- [ ] CSRF Token 验证

### 后端
- [ ] 输入验证和清理
- [ ] SQL 注入防护
- [ ] 认证和授权检查
- [ ] 敏感数据加密
- [ ] 日志记录

---

**准备好进行前后端集成了吗？** 🚀

遵循本指南的步骤，可以顺利完成前后端的对接！
