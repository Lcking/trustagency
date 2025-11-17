# 数据整合任务 - 执行计划

**项目**: TrustAgency 前后端数据整合  
**日期**: 2025-11-12  
**目标**: 统一前后端数据，创建完整的用户体验演示，并总结优化点

---

## 📋 任务概述

### 目标
- ✅ 将前端 mock 数据迁移到后端数据库
- ✅ 在后端创建丰富的初始数据
- ✅ 前端调用后端 API 获取数据
- ✅ 模拟用户使用全流程 (查看、搜索、编辑、发布)
- ✅ 记录问题和改进点
- ✅ 总结优化建议

### 当前状态
- **前端**: 静态 HTML + 硬编码数据 (平台、文章、FAQ、知识库)
- **后端**: FastAPI + SQLAlchemy ORM，已有模型但数据不足
- **数据库**: SQLite (trustagency.db)
- **API**: 45+ 端点已定义，但未完全测试

---

## 📊 数据结构分析

### 前端现有数据

#### 1. 平台 (Platforms)
**HTML 硬编码位置**: `/site/index.html` L200-220

| 平台名 | 描述 | 杠杆 | 最低存款 | URL |
|--------|------|------|---------|-----|
| Alpha Leverage | 高杠杆、低费率 | 100x | $100 | /platforms/alpha-leverage/ |
| Beta Margin | 风险管理完善 | 50x | $500 | /platforms/beta-margin/ |
| Gamma Trader | 新手友好 | 75x | $200 | /platforms/gamma-trader/ |

**需要迁移的字段**: 名称、描述、杠杆倍数、最低存款、URL 等

#### 2. 文章 (Articles)
**HTML 位置**: `/site/` 各子目录 (wiki, guides, qa)

类型 1: 知识库文章 (Wiki)
- `what-is-leverage` - 什么是杠杆交易
- 内容: 基础概念、原理、风险等

类型 2: 指南文章 (Guides)
- 快速开始指南
- 交易指南
- 内容: 步骤、示例、最佳实践

类型 3: FAQ (常见问题)
- 位置: `/site/qa/`
- 内容: Q&A 对

**需要迁移的字段**: 标题、slug、内容、分类、标签、是否发布等

### 后端数据库模型

#### Article 模型 (/backend/app/models/article.py)
```python
- id: 主键
- title: 文章标题
- slug: URL 友好的标识符
- content: 文章内容 (Markdown)
- summary: 文章摘要
- section_id: 栏目 FK
- category_id: 分类 FK
- tags: 标签 (逗号分隔)
- author_id: 作者 FK (必需)
- platform_id: 平台 FK (可选)
- is_published: 是否发布
- is_featured: 是否置顶
- view_count: 浏览次数
- like_count: 点赞次数
- meta_description: SEO 描述
- created_at, updated_at, published_at: 时间戳
```

#### Platform 模型
```python
- id, name, slug, description, website
- max_leverage, min_deposit, fee_rate
- rating, is_active, is_featured, is_recommended
- founded_year, country, safety_rating, regulation_status
- features, pros, cons, rank
```

#### Section 模型 (栏目)
```python
- id, name, slug, description
- icon, color
- articles: 关联的文章
```

#### Category 模型 (分类)
```python
- id, name, slug, description
- articles: 关联的文章
```

---

## 🔄 数据迁移方案

### 第 1 步: 创建后端数据初始化脚本

**目标**: 将前端 mock 数据写入数据库

**脚本位置**: `/Users/ck/Desktop/Project/trustagency/backend/init_integration_data.py`

**需要创建的数据**:

1. **Admin User** (管理员)
   - 创建 1-2 个默认管理员账户
   - 用于发布文章、管理平台

2. **Sections** (栏目)
   - "知识库" (Wiki)
   - "指南" (Guides)
   - "FAQ" (常见问题)
   - "平台评测" (Platform Reviews)

3. **Categories** (分类)
   - "教育", "风险管理", "交易技巧", "平台评测", "新手入门" 等

4. **Platforms** (平台) - 从 init_sample_data.py 迁移
   - Alpha Leverage
   - Beta Margin
   - Gamma Trader

5. **Articles** (文章) - 从前端静态 HTML 提取
   - 知识库文章 (Wiki 类)
   - 指南文章 (Guides 类)
   - FAQ 文章 (FAQ 类)

### 第 2 步: 修改前端页面调用 API

**目标**: 将 HTML 硬编码数据改为动态加载

**需要修改的文件**:
- `/site/index.html` - 首页平台列表
- `/site/platforms/index.html` - 平台列表页
- `/site/wiki/index.html` - 知识库首页
- `/site/guides/index.html` - 指南首页
- `/site/qa/index.html` - FAQ 首页

**修改方式**:
1. 添加 JavaScript 客户端库 (axios + interceptors)
2. 页面加载时调用后端 API 获取数据
3. 动态渲染 HTML

**涉及的 API 端点**:
```
GET /api/platforms - 获取平台列表
GET /api/articles?section_id=1 - 获取某栏目文章
GET /api/articles/{id} - 获取单篇文章
GET /api/articles?category_id=1 - 按分类筛选
```

### 第 3 步: 运行系统端到端测试

**启动流程**:
```bash
# 1. 启动后端
cd /backend && python -m uvicorn app.main:app --reload --port 8001

# 2. 启动前端 (nginx 或简单 HTTP 服务)
# 可选方案: 使用 Python SimpleHTTPServer 或 nginx

# 3. 导入 Postman 集合进行 API 测试
# 4. 使用浏览器访问前端，验证数据加载
```

### 第 4 步: 模拟用户体验

**用户场景 1: 浏览者**
- [ ] 访问首页 → 查看平台排行榜
- [ ] 点击平台卡片 → 查看平台详情
- [ ] 点击"查看评测文章" → 阅读评测内容
- [ ] 搜索文章 → 查找相关内容
- [ ] 点击相关文章链接 → 浏览相关内容

**用户场景 2: 编辑者 (管理员)**
- [ ] 登录后台管理系统
- [ ] 创建新文章 → 输入标题、内容、分类
- [ ] 编辑已有文章 → 修改内容、更新分类
- [ ] 发布/取消发布文章
- [ ] 添加/编辑平台
- [ ] 查看文章统计 (浏览次数、点赞)

**用户场景 3: 搜索和筛选**
- [ ] 按分类筛选文章
- [ ] 按栏目筛选文章
- [ ] 按关键词搜索
- [ ] 按发布时间排序
- [ ] 查看热门文章

---

## 🎯 具体执行步骤

### Step 1: 数据库初始化 (30 分钟)

**1.1 创建 `/backend/init_integration_data.py`**
```python
# 包含以下内容:
# 1. 创建 Admin User
# 2. 创建 Sections (知识库、指南、FAQ、评测)
# 3. 创建 Categories (教育、风险、技巧、平台、入门)
# 4. 导入 Platforms 数据
# 5. 导入 Articles 数据 (从前端 HTML 提取)
```

**1.2 执行初始化**
```bash
cd /backend
python init_integration_data.py
```

**1.3 验证数据**
```bash
# 使用 sqlite3 cli 或 Postman 验证数据已正确导入
```

### Step 2: 前端 API 集成 (2-3 小时)

**2.1 复制 API 客户端库到前端**
- 复制 `/backend/app/services/api_client.py` 逻辑到前端
- 创建 `/site/assets/js/api-client.js`

**2.2 创建页面加载脚本**
- `/site/assets/js/load-platforms.js` - 首页平台加载
- `/site/assets/js/load-articles.js` - 文章列表加载
- `/site/assets/js/load-categories.js` - 分类加载

**2.3 修改 HTML 模板**
- 替换硬编码数据为动态加载
- 添加加载动画和错误处理

### Step 3: 系统测试 (1-2 小时)

**3.1 启动系统**
```bash
# 终端 1: 后端
cd /backend && python -m uvicorn app.main:app --reload --port 8001

# 终端 2: 前端 (如需要)
cd /site && python -m http.server 8000
```

**3.2 运行 Postman 测试**
- 导入 `/docs/Postman_Collection.json`
- 执行所有 API 测试用例
- 验证响应正确

**3.3 浏览器验证**
- 打开 http://localhost:8000/
- 检查首页数据加载
- 检查所有导航链接

### Step 4: 用户体验模拟 (2-3 小时)

#### 场景 A: 浏览者场景
```
1. 访问首页
   - 查看平台排行榜卡片
   - 验证是否从 API 加载
   - 检查卡片样式和数据一致性

2. 点击平台详情页
   - 查看平台完整信息
   - 检查相关评测文章
   - 验证文章内容加载

3. 浏览文章
   - 进入知识库页面
   - 查看文章列表
   - 点击阅读单篇文章
   - 检查文章内容、评论、相关推荐

4. 搜索功能
   - 使用搜索框查询关键词
   - 检查搜索结果准确性
   - 验证排序和分页
```

**记录**: 
- ✅ 页面加载时间
- ✅ 数据完整性
- ❌ 发现的 bug
- 💡 用户体验问题

#### 场景 B: 编辑者场景
```
1. 登录后台
   - 访问管理系统登录页
   - 输入用户名/密码登录
   - 验证 token 保存和自动刷新

2. 创建新文章
   - 打开"新建文章"表单
   - 填入标题、内容、分类、标签
   - 上传图片 (如支持)
   - 预览和发布

3. 编辑已有文章
   - 进入文章列表
   - 点击编辑某篇文章
   - 修改内容
   - 保存更改

4. 管理平台
   - 查看平台列表
   - 添加/编辑/删除平台
   - 调整平台排序

5. 查看统计
   - 查看文章浏览次数
   - 查看点赞数
   - 查看热门文章排行
```

**记录**:
- ✅ 操作是否顺畅
- ✅ 表单验证
- ✅ 错误提示
- ❌ 发现的 bug
- 💡 用户界面改进

### Step 5: 问题记录和总结 (1 小时)

**5.1 创建优化报告**
- 文件: `/Users/ck/Desktop/Project/trustagency/INTEGRATION_FEEDBACK.md`
- 内容:
  - 发现的 bug (分为严重/中等/轻微)
  - 性能问题 (加载时间、API 响应)
  - 用户体验改进建议
  - 功能缺失或不完整
  - 代码质量问题

**5.2 分类优化点**
- 🔴 **阻塞性问题** (必须修复)
- 🟡 **重要改进** (下个版本修复)
- 🟢 **改进建议** (优化方向)

**5.3 总结**
- 用户评价 (假设)
- 网站整体完成度评分
- 下阶段工作优先级

---

## 📅 时间规划

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| 1 | 数据库初始化 | 30 分钟 |
| 2 | 前端 API 集成 | 2-3 小时 |
| 3 | 系统测试 | 1-2 小时 |
| 4 | 用户体验模拟 | 2-3 小时 |
| 5 | 问题总结 | 1 小时 |
| **总计** | | **7-8 小时** |

---

## 📝 交付物

### 生成的文件
- [ ] `init_integration_data.py` - 数据初始化脚本
- [ ] `/site/assets/js/api-client.js` - 前端 API 客户端
- [ ] 修改的前端 HTML 文件 (集成 API 调用)
- [ ] `INTEGRATION_FEEDBACK.md` - 反馈和优化建议
- [ ] `OPTIMIZATION_PLAN.md` - 下阶段优化计划

### 验收标准
- ✅ 前后端数据一致
- ✅ 所有主要页面能加载动态数据
- ✅ 用户能完成浏览-搜索-阅读全流程
- ✅ 管理员能完成发布-编辑-管理全流程
- ✅ 性能指标: 首页加载 < 2 秒
- ✅ 记录所有发现的问题和改进建议

---

## 🔗 相关文件引用

- 后端模型: `/backend/app/models/`
- API 端点: `/backend/app/routes/`
- 前端: `/site/`
- 文档: `/docs/` (API_GUIDE.md, FRONTEND_API_SPEC.md)

---

**状态**: 准备就绪  
**开始时间**: 等待确认  
**负责人**: AI Assistant

