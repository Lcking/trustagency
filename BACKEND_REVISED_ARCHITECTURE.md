# 🎯 后端架构重新设计 - 针对实际业务需求

**设计日期**: 2025-11-06  
**版本**: 2.0 (修订版 - 面向真实业务需求)  
**项目**: trustagency 股票杠杆平台管理系统

---

## 📋 核心业务需求分析

### 需求 1: 管理员模式 (无公众用户系统)
```
用户系统:
├─ 只需要: 单一管理员登录
├─ 不需要: 用户注册、评论系统、公众账户
└─ 功能: 文章、平台数据的增删改查

权限管理:
├─ 管理员: 完全访问
├─ 访客: 只读
└─ 无需: 分级权限、用户资料
```

### 需求 2: AI 内容生成系统 (核心创新功能)
```
编辑工作流:
1. 编辑批量输入文章标题
   ├─ 支持粘贴多行 (逗号、换行、制表符分隔)
   └─ 可预览输入列表

2. 配置 AI 参数
   ├─ 选择 AI 模型 (GPT-4, Claude, 本地模型等)
   ├─ 自定义系统提示词
   └─ 调整参数 (温度、长度等)

3. 指定发布目录
   ├─ 选择内容类型 (wiki, guide, faq)
   ├─ 标签和分类
   └─ SEO 元数据

4. 后台异步执行
   ├─ 批量生成文章
   ├─ 实时进度显示
   ├─ 完成提醒 (邮件/通知)
   └─ 失败重试机制

5. 内容审核和发布
   ├─ 生成内容预览
   ├─ 手动编辑调整
   ├─ 一键发布
   └─ 版本历史
```

### 需求 3: 数据管理系统
```
平台数据管理:
├─ 新增/编辑/删除平台
├─ 管理平台排名/评分
├─ 批量更新平台信息
└─ 导入/导出功能

内容管理:
├─ 编辑现有文章
├─ 删除旧文章
├─ 搜索和过滤
└─ 内容备份

前端数据展示:
├─ 从 Mock 数据 → 真实数据
├─ 实时更新
└─ 缓存管理
```

---

## 🏗️ 重新设计的技术栈

### 推荐方案: Python FastAPI + 任务队列

```
为什么选择 Python FastAPI?
✅ 专业数据处理能力 (数据分析、AI 集成)
✅ AI/LLM 集成生态最成熟
✅ 异步任务处理 (Celery)
✅ 快速开发、代码简洁
✅ 部署灵活 (支持多种服务器)
✅ 自动生成 API 文档
```

### 完整技术栈

| 组件 | 技术选择 | 用途 |
|------|---------|------|
| **后端框架** | FastAPI | 轻量、高性能、自动文档 |
| **数据库** | SQLite / PostgreSQL | 简单可靠、易备份 |
| **ORM** | SQLAlchemy | 数据映射、迁移管理 |
| **任务队列** | Celery + Redis | 异步处理 AI 任务 |
| **AI 集成** | LangChain / OpenAI SDK | AI 内容生成 |
| **认证** | JWT (仅管理员) | 单一登录 |
| **缓存** | Redis | 前端数据缓存 |
| **文件存储** | 本地文件系统 | 文章存储 |
| **日志** | Python logging | 错误追踪 |

---

## 📊 数据库设计 (简化版)

### 表结构

```sql
-- 1. 管理员用户表 (只有一个管理员)
CREATE TABLE admin_user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);

-- 2. 平台信息表
CREATE TABLE platforms (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  logo_url VARCHAR(255),
  website_url VARCHAR(255),
  min_leverage INT DEFAULT 1,
  max_leverage INT DEFAULT 100,
  commission_rate DECIMAL(5,4),
  risk_level ENUM('low','medium','high') DEFAULT 'medium',
  rating DECIMAL(3,2) DEFAULT 3.0,
  rank INT,  -- 排名
  established_year INT,
  regulated BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_rank (rank),
  KEY idx_rating (rating)
);

-- 3. 文章表
CREATE TABLE articles (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  slug VARCHAR(200) UNIQUE NOT NULL,
  title VARCHAR(200) NOT NULL,
  content LONGTEXT NOT NULL,
  category VARCHAR(50),  -- wiki, guide, faq
  status ENUM('draft','published','archived') DEFAULT 'draft',
  ai_generated BOOLEAN DEFAULT FALSE,  -- 是否 AI 生成
  ai_model VARCHAR(50),  -- 使用的 AI 模型
  ai_prompt TEXT,  -- 使用的 AI 提示词
  view_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  published_at TIMESTAMP,
  KEY idx_slug (slug),
  KEY idx_category (category),
  KEY idx_status (status)
);

-- 4. AI 生成任务表
CREATE TABLE ai_generation_tasks (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  task_id VARCHAR(100) UNIQUE NOT NULL,  -- Celery task ID
  status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
  titles TEXT NOT NULL,  -- JSON 格式的标题列表
  model VARCHAR(50),
  system_prompt TEXT,
  category VARCHAR(50),
  total_count INT,
  success_count INT DEFAULT 0,
  failed_count INT DEFAULT 0,
  error_message TEXT,
  created_article_ids TEXT,  -- 生成的文章 ID 列表 (JSON)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  KEY idx_task_id (task_id),
  KEY idx_status (status)
);

-- 5. 前端缓存表 (可选)
CREATE TABLE cache (
  key VARCHAR(100) PRIMARY KEY,
  value LONGTEXT NOT NULL,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎯 核心 API 端点设计

### 管理界面 API

#### 认证
```
POST /api/admin/login
  请求: {username, password}
  响应: {token, admin_info}

GET /api/admin/me
  响应: {admin 信息}

POST /api/admin/logout
```

#### 平台管理
```
GET /api/admin/platforms
  获取所有平台列表

POST /api/admin/platforms
  创建新平台
  请求: {name, slug, description, ...}

PUT /api/admin/platforms/:id
  编辑平台
  
DELETE /api/admin/platforms/:id
  删除平台

PATCH /api/admin/platforms/:id/rank
  更新平台排名
  请求: {rank}
```

#### 文章管理
```
GET /api/admin/articles
  获取所有文章

POST /api/admin/articles
  创建文章
  
PUT /api/admin/articles/:id
  编辑文章

DELETE /api/admin/articles/:id
  删除文章

PATCH /api/admin/articles/:id/status
  更新文章状态 (draft/published/archived)
```

#### AI 内容生成 (核心功能)
```
POST /api/admin/generate/preview
  预览 AI 生成 (不真正生成)
  请求: {
    titles: ["标题1", "标题2", ...],
    model: "gpt-4",
    system_prompt: "你是一个专业的...",
    category: "wiki"
  }
  响应: {preview_count, estimated_time}

POST /api/admin/generate/create
  开始批量生成
  请求: {
    titles,
    model,
    system_prompt,
    category,
    publish: false  // 生成后是否自动发布
  }
  响应: {task_id, status: "pending"}

GET /api/admin/generate/tasks/:task_id
  查询生成任务进度
  响应: {
    status: "processing",
    progress: 3/10,
    success_count: 3,
    failed_count: 0,
    error_message: null
  }

GET /api/admin/generate/tasks/:task_id/results
  获取生成结果
  响应: {
    articles: [{id, title, slug, status}, ...],
    failed_titles: ["标题3"]
  }

POST /api/admin/generate/tasks/:task_id/publish
  批量发布已生成的文章
  请求: {article_ids: [1, 2, 3]}
  响应: {published_count}
```

### 公开 API (供前端页面使用)

```
GET /api/platforms
  获取所有已发布的平台
  响应: [{id, name, slug, rating, rank, ...}]

GET /api/platforms/:slug
  获取单个平台详情

GET /api/articles
  获取文章列表 (按分类)
  查询: ?category=wiki&page=1&limit=10
  
GET /api/articles/:slug
  获取单篇文章

GET /api/statistics
  获取统计数据 (可选)
  响应: {total_articles, total_platforms, ...}
```

---

## 🚀 AI 内容生成模块设计

### 模块架构

```
前端管理界面
    ↓
FastAPI 后端
    ↓
    ├─ 验证 & 参数处理
    ├─ 创建 Celery 异步任务
    └─ 返回 task_id
    
        ↓
    
    Celery Worker (后台服务)
    ├─ 接收任务
    ├─ 循环处理标题列表
    │   ├─ 调用 LLM API (OpenAI/Claude/本地)
    │   ├─ 生成文章内容
    │   ├─ 保存到数据库
    │   └─ 更新进度
    ├─ 任务完成
    └─ 发送完成通知 (邮件/前端)

        ↓
        
前端收到通知 → 刷新 → 显示结果
```

### 实现细节

```python
# backend/tasks.py
from celery import Celery
from openai import OpenAI

celery_app = Celery('trustagency')

@celery_app.task(bind=True)
def generate_articles(self, task_id, titles, model, system_prompt, category):
    """
    异步生成文章
    """
    # 初始化任务状态
    update_task_status(task_id, 'processing')
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    success_count = 0
    failed_count = 0
    created_articles = []
    
    for i, title in enumerate(titles):
        try:
            # 调用 LLM
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请为以下标题创建一篇文章:\n{title}"}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 保存文章
            article = save_article(
                title=title,
                content=content,
                category=category,
                ai_model=model,
                ai_prompt=system_prompt
            )
            
            created_articles.append(article.id)
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to generate article for {title}: {str(e)}")
        
        # 更新进度
        progress = (i + 1) / len(titles)
        update_task_progress(task_id, progress, success_count, failed_count)
        
        # 避免 API 限流
        time.sleep(1)
    
    # 任务完成
    complete_task(task_id, created_articles)
    send_notification(f"文章生成完成: {success_count}/{len(titles)}")
```

---

## 📱 前端数据集成方案

### 从 Mock 数据到真实数据

#### 现状 (Mock)
```javascript
// site/assets/js/data.js
const platforms = [
  { id: 1, name: 'Alpha Leverage', rating: 4.8, ... },
  { id: 2, name: 'Beta Margin', rating: 4.5, ... }
];

const articles = {
  wiki: [
    { title: '什么是杠杆交易', slug: '...' }
  ]
};
```

#### 目标 (真实数据)
```javascript
// site/assets/js/api.js
class TrustAgencyAPI {
  async getPlatforms() {
    const response = await fetch('/api/platforms');
    return response.json();
  }
  
  async getArticles(category) {
    const response = await fetch(`/api/articles?category=${category}`);
    return response.json();
  }
}

// 页面加载时
document.addEventListener('DOMContentLoaded', async () => {
  const api = new TrustAgencyAPI();
  const platforms = await api.getPlatforms();
  renderPlatforms(platforms);
});
```

#### 缓存策略
```javascript
// 在 Redis 中缓存，减少数据库查询
GET /api/platforms (缓存 1 小时)
GET /api/articles (缓存 30 分钟)
GET /api/articles/:slug (缓存 24 小时)

更新时自动清除相关缓存:
POST /api/admin/platforms → 清除 /api/platforms 缓存
PUT /api/admin/articles/:id → 清除 /api/articles/* 缓存
```

#### 页面改动清单
```
site/index.html
├─ 动态加载推荐平台 (from API)
├─ 动态加载 FAQ (from API)
└─ 动态加载知识库 (from API)

site/platforms/index.html
└─ 动态加载平台列表

site/compare/index.html
└─ 动态加载对比数据

site/wiki/index.html
site/guides/index.html
site/qa/index.html
└─ 动态加载对应分类的文章
```

---

## 🏗️ 项目文件结构

```
trustagency-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接
│   │
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── admin.py
│   │   ├── platform.py
│   │   ├── article.py
│   │   └── task.py
│   │
│   ├── schemas/                # Pydantic 数据验证
│   │   ├── admin.py
│   │   ├── platform.py
│   │   ├── article.py
│   │   └── generation.py
│   │
│   ├── routes/                 # API 路由
│   │   ├── admin.py
│   │   ├── platforms.py
│   │   ├── articles.py
│   │   └── generation.py       # AI 生成路由
│   │
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── platform_service.py
│   │   ├── article_service.py
│   │   └── ai_service.py       # AI 集成
│   │
│   ├── tasks/                  # Celery 任务
│   │   └── generation.py       # 异步生成任务
│   │
│   └── utils/
│       ├── security.py         # JWT 认证
│       ├── cache.py            # 缓存管理
│       └── logger.py           # 日志
│
├── tests/
│   ├── test_admin.py
│   ├── test_platforms.py
│   ├── test_articles.py
│   └── test_generation.py
│
├── migrations/                 # 数据库迁移
├── docker-compose.yml          # Celery + Redis + DB
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ 简化的任务队列

### 为什么需要异步任务队列?

```
问题: 生成 100 篇文章需要 5-10 分钟
解决:
├─ 用户点击 "开始生成" 后立即返回
├─ 后台 Celery Worker 异步处理
├─ 用户可以关闭页面，任务继续运行
├─ 完成后发送通知或邮件
```

### 技术方案

```
FastAPI 应用
    ↓
    POST /api/admin/generate/create
    ↓
    创建任务 + Celery.delay()
    ↓
    立即返回 {task_id}
    ↓
前端轮询 GET /api/admin/generate/tasks/:task_id
    ↓
    Celery Worker 后台处理
    ├─ 调用 LLM
    ├─ 生成文章
    ├─ 存储数据库
    └─ 更新进度
```

---

## 📅 开发时间表 (修订版)

| Phase | 任务 | 耗时 | 优先级 |
|-------|------|------|--------|
| **1** | 项目初始化 + 数据库 | 4-6h | P0 |
| **2** | 管理员认证 | 3-4h | P0 |
| **3** | 平台管理 API | 6-8h | P1 |
| **4** | 文章管理 API | 6-8h | P1 |
| **5** | **AI 生成模块** | **12-16h** | **P0** |
| **6** | 前端集成 | 8-10h | P1 |
| **7** | 缓存 & 优化 | 4-6h | P2 |
| **8** | 部署 & 测试 | 4-6h | P2 |

**总计**: 48-64 小时 ≈ **1-2 周**

---

## 🔐 安全考虑

```
管理员认证:
├─ JWT Token (24 小时过期)
├─ 密码加密 (bcrypt)
└─ 刷新令牌机制

API 安全:
├─ 所有管理 API 需要认证
├─ 公开 API 无需认证
├─ 速率限制 (防 DDoS)
└─ CORS 配置

LLM 集成:
├─ API Key 存储在环境变量
├─ 请求日志 (审计)
├─ 成本控制 (配额管理)
└─ 内容审核 (可选)
```

---

## 🎯 立即行动计划

### Week 1: 核心基础 (48-64 小时)

```
Day 1-2: 项目初始化
├─ 创建 FastAPI 项目
├─ 配置数据库
└─ 创建数据表

Day 2-3: 管理员系统
├─ 实现登录
├─ JWT 认证
└─ 基础 CRUD

Day 3-5: AI 生成系统 (核心)
├─ Celery 配置
├─ LLM 集成
├─ 任务队列
└─ 进度追踪

Day 5-6: API 完善
├─ 所有端点实现
├─ 错误处理
└─ 文档生成

Day 6-7: 前端集成
├─ 更新前端代码
├─ 移除 Mock 数据
└─ 测试验证
```

---

## 💡 关键差异对比

| 需求 | 之前方案 | 现在方案 |
|------|---------|---------|
| **用户系统** | 完整用户体系 | 仅管理员 |
| **认证** | JWT + 用户 | JWT + 管理员 |
| **核心功能** | 平台对比 | **AI 内容生成** |
| **任务处理** | 同步 API | 异步队列 |
| **复杂度** | 高 | 中等 |
| **开发周期** | 2.5-3 周 | **1-2 周** |
| **维护成本** | 高 | 低 |

---

## ✨ 新方案的优势

```
✅ 更简洁: 无需复杂的用户权限系统
✅ 更强大: AI 驱动的内容生成
✅ 更高效: 异步任务处理
✅ 更快速: 1-2 周快速部署
✅ 更灵活: 易于扩展新的 AI 模型
✅ 更智能: 内容自动化生成 = 运营效率 ↑
```

---

## 🚀 下一步

### 确认清单

请确认以下方案:

- [ ] **后端框架**: Python FastAPI ✅
- [ ] **数据库**: SQLite / PostgreSQL ✅
- [ ] **任务队列**: Celery + Redis ✅
- [ ] **AI 集成**: OpenAI / Claude / 本地模型 ✅
- [ ] **管理员模式**: 单一登录 ✅
- [ ] **核心功能**: AI 内容生成 ✅

### 缺少的信息

需要确认:
1. **使用哪个 LLM?** (OpenAI GPT-4, Claude 3, 本地模型等)
2. **是否需要多个管理员?** (当前设计假设单一管理员)
3. **文章是否需要版本控制?** (草稿/发布/存档)
4. **生成任务完成后如何通知?** (邮件/前端通知)

---

**现在这是一个真正适合你业务的方案!** 🎯

核心优势: **简洁的管理系统 + 强大的 AI 内容生成能力**

准备好开始开发了吗？
