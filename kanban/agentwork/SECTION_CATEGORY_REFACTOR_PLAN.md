# 栏目分类体系重构 - 完整规划文档

**文档创建时间**: 2025-11-08  
**优先级**: 🔴 高  
**预计工时**: 12-16小时  

---

## 一、需求梳理

### 1.1 问题诊断

**当前系统的缺陷**:
```
❌ 分类维度混乱
   - category 字段承载两个维度: 栏目(百科/指南) + 分类(风险管理/基础概念)
   - 导致数据模糊且难以维护

❌ 平台关联不灵活
   - 所有文章都有 platform_id，但只有"验证记录"栏目才需要
   - 导致其他栏目文章中的 platform_id 为 NULL，浪费空间

❌ AI生成链路不完整
   - 无法指定栏目
   - 无法指定分类层级
   - 缺少API端点和错误处理
   - 无法针对性生成不同栏目的内容
```

### 1.2 设计目标

**目标架构**:
1. 清晰的分层: 栏目 → 分类 → 文章
2. 灵活的平台关联: 仅验证栏目需要平台字段
3. 完整的AI生成流程: 栏目→分类→标题→生成

---

## 二、数据模型设计

### 2.1 新增表: Section (栏目)

```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- "常见问题", "百科", "指南", "验证记录"
    slug VARCHAR(100) UNIQUE NOT NULL,  -- "faq", "wiki", "guide", "review"
    description TEXT,
    icon VARCHAR(50),                    -- "❓", "📚", "📖", "✅"
    requires_platform BOOLEAN DEFAULT FALSE,  -- 只有 review=true
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**示例数据**:
```
1, "常见问题", "faq", "用户常见问题", "❓", false, 1, true
2, "百科", "wiki", "交易知识百科", "📚", false, 2, true
3, "指南", "guide", "交易操作指南", "📖", false, 3, true
4, "验证记录", "review", "平台验证报告", "✅", true, 4, true
```

### 2.2 改造表: Category (分类)

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    section_id INTEGER NOT NULL FOREIGN KEY,
    name VARCHAR(100) NOT NULL,  -- "基础概念", "风险管理"
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 复合唯一约束: 同栏目下分类名唯一
    UNIQUE (section_id, name)
);
```

**示例数据**:
```
-- 百科栏目的分类
1, 2, "基础概念", "basics", ..., 1
2, 2, "风险管理", "risk-management", ..., 2
3, 2, "交易工具", "trading-tools", ..., 3
4, 2, "市场分析", "market-analysis", ..., 4

-- 验证栏目的分类
5, 4, "曝光", "exposure", ..., 1
6, 4, "验证", "verification", ..., 2
```

### 2.3 改造表: Article (文章)

```sql
-- 原始字段保持，新增/修改:
ALTER TABLE articles ADD COLUMN section_id INTEGER FOREIGN KEY;
ALTER TABLE articles MODIFY COLUMN category VARCHAR(100) → category_id INTEGER FOREIGN KEY;
ALTER TABLE articles ADD COLUMN platform_id INTEGER FOREIGN KEY -- 保留，验证栏目时必填

-- 最终结构
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    
    -- 新的分类维度
    section_id INTEGER NOT NULL FOREIGN KEY,  -- 指向栏目
    category_id INTEGER NOT NULL FOREIGN KEY,  -- 指向该栏目下的分类
    platform_id INTEGER FOREIGN KEY,          -- 仅验证栏目时非NULL
    
    author_id INTEGER NOT NULL FOREIGN KEY,
    
    is_published BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    published_at DATETIME
);
```

### 2.4 改造表: AIGenerationTask (AI任务)

```sql
CREATE TABLE ai_generation_tasks (
    id INTEGER PRIMARY KEY,
    batch_id VARCHAR(36) UNIQUE NOT NULL,
    
    -- 目标配置
    section_id INTEGER NOT NULL FOREIGN KEY,
    category_id INTEGER NOT NULL FOREIGN KEY,
    platform_id INTEGER FOREIGN KEY,  -- 仅当 section="review" 时必填
    
    -- 生成参数
    titles TEXT NOT NULL,  -- JSON: ["title1", "title2", ...]
    model VARCHAR(50) NOT NULL,  -- "gpt-3.5-turbo", "gpt-4", ...
    temperature FLOAT DEFAULT 0.7,
    
    -- API配置
    api_endpoint VARCHAR(500),  -- POST 请求地址
    api_key VARCHAR(500),       -- 加密存储
    request_body TEXT,          -- 模板: {title: "{title}", ...}
    
    -- 执行状态
    status VARCHAR(20) DEFAULT "pending",  -- pending, processing, completed, failed
    progress INTEGER DEFAULT 0,  -- 0-100
    completed_count INTEGER DEFAULT 0,
    total_count INTEGER NOT NULL,
    error_message TEXT,         -- 失败原因
    
    creator_id INTEGER NOT NULL FOREIGN KEY,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME
);
```

---

## 三、后端API设计

### 3.1 栏目管理 API

```
GET    /api/sections              - 获取所有栏目
GET    /api/sections/{id}         - 获取栏目详情
POST   /api/sections              - 创建栏目
PUT    /api/sections/{id}         - 更新栏目
DELETE /api/sections/{id}         - 删除栏目
```

**请求/响应示例**:

创建栏目:
```json
POST /api/sections
{
    "name": "验证记录",
    "slug": "review",
    "description": "平台验证报告",
    "icon": "✅",
    "requires_platform": true,
    "sort_order": 4
}

Response 201:
{
    "id": 4,
    "name": "验证记录",
    "slug": "review",
    "requires_platform": true,
    ...
}
```

### 3.2 分类管理 API

```
GET    /api/categories                    - 获取所有分类
GET    /api/categories/by-section/{id}   - 按栏目获取分类
GET    /api/categories/{id}              - 获取分类详情
POST   /api/categories                   - 创建分类
PUT    /api/categories/{id}              - 更新分类
DELETE /api/categories/{id}              - 删除分类
```

**请求示例**:

按栏目获取分类:
```json
GET /api/categories/by-section/2

Response 200:
{
    "data": [
        {"id": 1, "name": "基础概念", "section_id": 2, ...},
        {"id": 2, "name": "风险管理", "section_id": 2, ...}
    ],
    "total": 2
}
```

### 3.3 文章管理 API (改造)

```
GET    /api/articles?section_id=2&category_id=1
POST   /api/articles
PUT    /api/articles/{id}
DELETE /api/articles/{id}
```

创建文章 (新):
```json
POST /api/articles
{
    "title": "Bitcoin基础介绍",
    "section_id": 2,           // 百科
    "category_id": 1,          // 基础概念
    "platform_id": null,       // 只有section_id=4(验证)时必填
    "content": "...",
    "summary": "...",
    "is_featured": false
}
```

创建验证文章 (新):
```json
POST /api/articles
{
    "title": "Binance 平台验证报告",
    "section_id": 4,           // 验证记录
    "category_id": 5,          // 曝光或验证
    "platform_id": 1,          // 必填！
    "content": "...",
    "summary": "..."
}
```

### 3.4 AI 生成任务 API (完整重构)

```
GET    /api/tasks                        - 获取任务列表
GET    /api/tasks/{batch_id}             - 获取任务详情
POST   /api/tasks/generate-articles      - 创建生成任务
POST   /api/tasks/{batch_id}/retry       - 重试失败的任务
DELETE /api/tasks/{batch_id}             - 取消/删除任务
```

创建生成任务 (新):
```json
POST /api/tasks/generate-articles
{
    "section_id": 2,           // 百科
    "category_id": 1,          // 基础概念
    "platform_id": null,       // 如果 section_id=4，则必填
    "titles": ["Bitcoin基础", "以太坊介绍", "DeFi概念"],
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "api_endpoint": "https://api.openai.com/v1/chat/completions",
    "api_key": "sk-...",
    "request_body": {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "你是一个专业的金融写手"},
            {"role": "user", "content": "写一篇关于{title}的详细介绍，800-1000字"}
        ],
        "temperature": 0.7
    }
}

Response 201:
{
    "batch_id": "uuid-xxx",
    "status": "pending",
    "progress": 0,
    "total_count": 3,
    "created_at": "2025-11-08T..."
}
```

获取任务详情:
```json
GET /api/tasks/uuid-xxx

Response 200:
{
    "batch_id": "uuid-xxx",
    "section_id": 2,
    "category_id": 1,
    "titles": ["Bitcoin基础", "以太坊介绍", "DeFi概念"],
    "status": "processing",
    "progress": 33,
    "completed_count": 1,
    "total_count": 3,
    "error_message": null,
    "created_articles": [
        {"id": 123, "title": "Bitcoin基础", "status": "success"},
        {"id": 124, "title": "以太坊介绍", "status": "processing"},
        {"id": null, "title": "DeFi概念", "status": "pending"}
    ]
}
```

---

## 四、前端 UI 设计

### 4.1 栏目管理页面

```
┌─ 栏目管理 ────────────────────────┐
│ + 新增栏目                        │
├───────────────────────────────────┤
│ 栏目 | 别名 | 需要平台 | 操作    │
├───────────────────────────────────┤
│ 常见问题 | faq | ✗ | 编辑 删除  │
│ 百科 | wiki | ✗ | 编辑 删除     │
│ 指南 | guide | ✗ | 编辑 删除    │
│ 验证记录 | review | ✓ | 编辑 删除 │
└───────────────────────────────────┘
```

### 4.2 分类管理页面

```
┌─ 分类管理 ─────────────────────────────┐
│ 筛选栏目: [百科 ▼]  + 新增分类          │
├────────────────────────────────────────┤
│ 分类名 | 栏目 | 说明 | 操作            │
├────────────────────────────────────────┤
│ 基础概念 | 百科 | ... | 编辑 删除      │
│ 风险管理 | 百科 | ... | 编辑 删除      │
│ 交易工具 | 百科 | ... | 编辑 删除      │
│ 市场分析 | 百科 | ... | 编辑 删除      │
│ 曝光 | 验证记录 | ... | 编辑 删除      │
│ 验证 | 验证记录 | ... | 编辑 删除      │
└────────────────────────────────────────┘
```

### 4.3 文章管理页面 (改造)

```
新增文章表单:
┌─ 新增文章 ────────────────────┐
│ 标题: [____________]          │
│ 栏目: [百科 ▼]                │
│ 分类: [基础概念 ▼]            │
│ 平台: (隐藏-仅验证栏目显示)   │
│ 摘要: [____________]          │
│ 内容: [____________]          │
│       [保存] [取消]           │
└───────────────────────────────┘

当选择"验证记录"栏目时:
┌─ 新增文章 ────────────────────┐
│ 标题: [____________]          │
│ 栏目: [验证记录 ▼]            │
│ 分类: [曝光 ▼]                │
│ 平台: [Binance ▼] ← 显示！    │
│ 摘要: [____________]          │
│ 内容: [____________]          │
│       [保存] [取消]           │
└───────────────────────────────┘
```

### 4.4 AI任务页面 (完整重构)

```
┌─ AI 任务生成 ──────────────────────────┐
│ 栏目: [百科 ▼]                         │
│ 分类: [基础概念 ▼]                    │
│ 平台: (隐藏)                           │
│                                       │
│ 模型配置:                              │
│ ┌─ 模型: [gpt-3.5-turbo ▼] ────────┐ │
│ │ API端点: [https://api.openai...] │ │
│ │ API Key: [sk-***] 🔒             │ │
│ │ 温度: [0.7]                      │ │
│ └─────────────────────────────────┘ │
│                                       │
│ 批量标题 (一行一个):                   │
│ ┌───────────────────────────────────┐ │
│ │ Bitcoin基础介绍                    │ │
│ │ 以太坊是什么                      │ │
│ │ DeFi完全指南                      │ │
│ └───────────────────────────────────┘ │
│                                       │
│ [🚀 提交生成任务] [测试连接]         │
│                                       │
│ 任务历史:                              │
│ ┌───────────────────────────────────┐ │
│ │ 百科/基础概念 | 3篇 | 进行中 33%  │ │
│ │ 验证/曝光 | 2篇 | 已完成 ✓        │ │
│ │ 百科/风险管理 | 5篇 | 失败 ✗     │ │
│ └───────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

## 五、任务分解 (按优先级)

### Phase 1: 数据模型 (2-3h)
- [ ] 创建 `sections` 表
- [ ] 改造 `categories` 表(添加 section_id FK)
- [ ] 改造 `articles` 表(添加 section_id, category_id, platform_id)
- [ ] 改造 `ai_generation_tasks` 表(添加完整字段)
- [ ] 数据库迁移脚本

### Phase 2: 后端API (4-5h)
- [ ] 实现 Section CRUD endpoints
- [ ] 实现 Category CRUD endpoints (按 section 过滤)
- [ ] 改造 Article API (支持 section + category)
- [ ] 完整重构 AI task API (支持配置、错误处理)
- [ ] 添加数据验证 (platform_id 依赖逻辑)

### Phase 3: 前端UI (3-4h)
- [ ] 创建栏目管理页面
- [ ] 创建分类管理页面
- [ ] 改造文章管理表单 (动态显示/隐藏字段)
- [ ] 完整重构AI任务表单 (配置、测试、错误提示)
- [ ] 任务列表展示 (状态、进度、错误信息)

### Phase 4: 集成测试 (2-3h)
- [ ] E2E 测试流程
- [ ] 错误场景处理
- [ ] 文档更新

---

## 六、风险识别

| 风险 | 影响 | 缓解方案 |
|------|------|--------|
| 数据迁移复杂 | 高 | 创建迁移脚本，提前备份 |
| 现有数据兼容 | 中 | category 字段保留，逐步迁移 |
| API 破坏性变更 | 高 | 版本控制，前端同步更新 |

---

## 七、完成标准

✅ 所有表结构创建完成  
✅ 所有API端点可用  
✅ 前端UI完全改造  
✅ E2E 测试通过  
✅ 可以完整创建 百科→风险管理→AI生成 流程  
✅ 可以完整创建 验证→曝光→平台→AI生成 流程  
✅ 任务失败时显示错误信息  

---

**下一步**: 等待确认，然后开始 Phase 1 数据模型实现。
