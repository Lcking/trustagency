# 前后端集成修复方案

## 问题描述
后端新增的百科文章（wiki 栏目下的"市场分析"分类）与前端页面路由不匹配：

- **后端生成的链接**: `/article/{slug}` 或 `/static/article_view.html?id=1`
- **前端页面路由**: `/wiki/xxx/`、`/qa/xxx/`、`/guides/xxx/`

## 解决方案

### 1. 后端 API 改进 ✅
**文件**: `backend/app/routes/articles.py`

新增了 `/api/articles/by-section/{section_slug}` 端点，支持按栏目 slug 获取已发布的文章：

```
GET /api/articles/by-section/wiki?limit=100
GET /api/articles/by-section/faq?limit=50
GET /api/articles/by-section/guide?limit=100
GET /api/articles/by-section/review?limit=100
```

**好处**：
- 前端可以直接按栏目加载文章数据
- 统一了所有栏目的数据获取方式
- 支持分页（`skip` 和 `limit` 参数）

### 2. 前端页面改进

#### 2.1 Wiki 页面 (`site/wiki/index.html`) ✅
**改动**：
- 添加了 `loadWikiArticlesFromBackend()` 函数，从后端动态加载 wiki 文章
- 将文章链接改为 `/article/{slug}` 而不是 `/wiki/{slug}`
- 添加了分类颜色映射，使分类徽章与后端分类名称对应
- 保留了静态数据作为后备方案（防止后端不可用时出错）

**关键改动**：
```javascript
// 从后端加载文章
const backendArticles = await fetch(`/api/articles/by-section/wiki?limit=100`)
// 将文章链接指向后端路由
url: `/article/${article.slug}` // 而不是 `/wiki/{slug}`
```

#### 2.2 常见问题页面 (`site/qa/index.html`) ✅
**改动**：
- 更新了 API 端点从 `/api/articles/by-category/常见问题` 改为 `/api/articles/by-section/faq`
- 统一了 API 调用方式
- 文章链接已指向 `/article/{slug}`

#### 2.3 指南页面 (`site/guides/index.html`) ✅
**改动**：
- 添加了动态加载指南文章的脚本
- 支持从后端加载指南栏目的文章
- 保持默认内容作为后备

## 技术架构

### 数据流
```
后端数据库 (categories, articles)
        ↓
    后端 API 
        ├─ /api/categories/section/{id}  (获取分类)
        └─ /api/articles/by-section/{slug} (获取文章) ← NEW
        ↓
    前端 JavaScript
        ├─ Wiki 页面 (动态加载 wiki 文章)
        ├─ FAQ 页面 (动态加载 faq 文章)
        └─ Guides 页面 (动态加载 guide 文章)
        ↓
    用户浏览器
        └─ 统一使用 /article/{slug} 链接查看文章
```

## 栏目对应关系

| 前端页面 | 栏目 Slug | API 端点 | 数据源 |
|--------|---------|---------|-------|
| /wiki/ | wiki | `/api/articles/by-section/wiki` | 百科文章 |
| /qa/ | faq | `/api/articles/by-section/faq` | 常见问题文章 |
| /guides/ | guide | `/api/articles/by-section/guide` | 指南文章 |
| /platforms/ (review) | review | `/api/articles/by-section/review` | 平台评测文章 |

## 测试步骤

1. **启动后端服务**
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --port 8000
   ```

2. **验证后端 API**
   ```bash
   # 测试新端点
   curl http://localhost:8000/api/articles/by-section/wiki?limit=10
   ```

3. **在浏览器中验证**
   - 打开 http://localhost:8000/wiki/ - 应该显示动态加载的百科文章
   - 打开 http://localhost:8000/qa/ - 应该显示动态加载的常见问题
   - 点击任何文章卡片，应该导向 `/article/{slug}` 链接
   - 文章详情页面应该正确显示（使用后端的文章模板）

4. **在管理后台验证**
   - 登录 http://localhost:8000/admin
   - 在百科栏目下创建新文章
   - 验证前端 wiki 页面是否实时显示新文章

## 已发布的 API 端点

完整的文章 API 端点列表：

```
GET    /api/articles                           - 获取文章列表（支持分页、搜索、排序）
POST   /api/articles                           - 创建文章（需要认证）
GET    /api/articles/{article_id}              - 获取单篇文章
PUT    /api/articles/{article_id}              - 更新文章（需要认证）
DELETE /api/articles/{article_id}              - 删除文章（需要认证）
GET    /api/articles/by-section/{section_slug} - 按栏目获取文章 ← NEW
GET    /api/articles/by-category/{category}    - 按分类获取文章
GET    /api/articles/by-platform/{platform_id} - 按平台获取文章
GET    /api/articles/by-author/{author_id}     - 按作者获取文章
GET    /api/articles/featured/list             - 获取特色文章
GET    /api/articles/trending/list             - 获取热门文章
POST   /api/articles/{article_id}/publish      - 发布文章
POST   /api/articles/{article_id}/unpublish    - 取消发布
```

## 后续改进建议

1. **添加分类同步**
   - 在后端为每个栏目生成对应的 sitemap
   - 前端 FAQ/Wiki/Guides 页面的分类侧边栏可以动态加载

2. **优化搜索**
   - 实现全局搜索，同时搜索 wiki、faq、guides 的文章
   - 添加搜索结果的 SEO 优化

3. **缓存优化**
   - 后端为常访问的文章列表添加缓存
   - 前端 JavaScript 缓存加载的文章列表（localStorage）

4. **实时更新**
   - 考虑使用 WebSocket 实时推送新文章到前端
   - 或者使用 polling 定期检查新文章

## 已修复的问题

✅ **bug_001**: 后端文章与前端链接不匹配
- **原因**: 前端硬编码使用 `/wiki/{slug}` 路由，但后端生成 `/article/{slug}` 链接
- **修复**: 前端现在正确使用后端生成的 `/article/{slug}` 链接

✅ **内容同步问题**
- **原因**: 前端使用硬编码的文章列表，不能实时同步后端数据
- **修复**: 前端现在从后端 API 动态加载文章数据

✅ **栏目访问问题**
- **原因**: 后端有栏目和分类数据，但前端不能直接访问
- **修复**: 新增 `/api/articles/by-section/{slug}` 端点供前端使用

---

**修复时间**: 2025-11-16
**修复者**: GitHub Copilot
**状态**: ✅ 已完成
