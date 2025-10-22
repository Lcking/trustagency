# A-6：SEO 和 Schema 优化 - 实施计划

**状态**: 进行中 (2025-10-21)  
**任务目标**: 完整的 SEO 优化和结构化数据实施  
**预计时间**: 4 小时  
**质量目标**: 5/5 (Google Schema 验证、Lighthouse SEO 100)

---

## 📋 任务分解

### 子任务 1：增强 Schema 标记
**时间**: 1.5 小时  
**目标**: 为所有主要页面添加完整的 JSON-LD Schema

#### 1.1 首页 (index.html)
- [ ] 保留现有 WebSite + Organization Schema
- [ ] 添加 BreadcrumbList Schema
- [ ] 添加 FAQPage Schema (对常见问题部分)
- [ ] 添加 ItemList Schema (推荐平台)

#### 1.2 平台列表页 (platforms/index.html)
- [ ] 添加 BreadcrumbList Schema
- [ ] 为每个平台卡片添加 Product/Service Schema
- [ ] 添加平台的评分 (aggregateRating)

#### 1.3 对比页 (compare/index.html)
- [ ] 添加 BreadcrumbList Schema
- [ ] 为对比表添加 ComparisonTable Schema (或 Table 结构)
- [ ] 添加 FAQ Schema

#### 1.4 关于页 (about/index.html)
- [ ] 更新 Organization Schema (更详细的信息)
- [ ] 添加 BreadcrumbList Schema
- [ ] 添加 Person Schema (团队成员 - 如有)

#### 1.5 法律页 (legal/index.html)
- [ ] 添加 BreadcrumbList Schema
- [ ] 添加 WebPage Schema (文章类型)

#### 1.6 Wiki 文章 (wiki/*.html)
- [ ] 为每篇文章添加 Article/BlogPosting Schema
- [ ] 添加 BreadcrumbList Schema
- [ ] 添加 author, datePublished, dateModified

#### 1.7 Guides 页 (guides/*.html)
- [ ] 添加 HowTo Schema
- [ ] 添加 BreadcrumbList Schema

#### 1.8 FAQ 页 (qa/index.html)
- [ ] 为每个问答添加 QAPage Schema
- [ ] 添加 BreadcrumbList Schema

---

### 子任务 2：元标签优化
**时间**: 0.8 小时  
**目标**: 优化所有页面的元标签

#### 2.1 检查和更新
- [ ] Verify Open Graph 标签完整性
- [ ] 添加 og:image 标签 (所有页面)
- [ ] 优化 Meta Description (50-160 字符)
- [ ] 添加 Twitter 卡片标签
- [ ] 验证 Canonical 标签正确性

#### 2.2 新增标签
- [ ] 添加 theme-color meta 标签
- [ ] 添加 apple-touch-icon link
- [ ] 验证 charset 和 viewport 配置

---

### 子任务 3：robots.txt 和 sitemap 优化
**时间**: 0.4 小时  
**目标**: 优化爬虫配置和网站地图

#### 3.1 robots.txt 更新
- [x] robots.txt 已存在 (基础配置)
- [ ] 更新 domain URL (example.com → 实际域名)
- [ ] 验证 Sitemap URL 正确性
- [ ] 添加更多特定爬虫规则 (Bing, Baidu)

#### 3.2 sitemap.xml 更新
- [x] sitemap.xml 已存在 (基础配置)
- [ ] 更新所有 URL 的 lastmod 日期 (2025-10-21)
- [ ] 验证所有页面都已包含
- [ ] 添加 Wiki/Guides 所有文章页面 (当前缺失)
- [ ] 验证 XML 格式正确性

---

### 子任务 4：创建结构化数据验证文档
**时间**: 0.5 小时  
**目标**: 创建验证脚本和检查清单

#### 4.1 Schema 验证
- [ ] 创建 schema-validation.html (本地测试工具)
- [ ] 为每个页面提供 Google Schema 验证链接列表

#### 4.2 SEO 检查清单
- [ ] 创建 SEO_CHECKLIST.md
- [ ] 包含 Lighthouse 审计指标
- [ ] 包含 Google Search Console 配置步骤

---

### 子任务 5：本地验证和测试
**时间**: 0.8 小时  
**目标**: 验证所有优化的实际效果

#### 5.1 验证工具
- [ ] 使用 Google Schema Markup Validator
- [ ] 检查 Mobile-Friendly Test
- [ ] 运行 Lighthouse 审计

#### 5.2 测试清单
- [ ] 验证所有 Schema 有效
- [ ] 检查 Open Graph 预览
- [ ] 验证 Canonical 标签
- [ ] 测试 breadcrumb 显示

---

## 📊 当前状态

### ✅ 已完成
- robots.txt (基础配置)
- sitemap.xml (基础配置)
- 首页 JSON-LD Schema (WebSite + Organization)
- 基础 Meta 标签 (title, description, OG, Twitter)

### ⚠️ 需要改进
- BreadcrumbList Schema (所有页面缺失)
- Article/BlogPosting Schema (Wiki/Guides 缺失)
- 平台卡片的 Product Schema (缺失)
- og:image 标签 (所有页面缺失)
- FAQ Schema (需要改进)
- 实际域名替换 (目前使用 example.com)

### 📝 需要添加的页面
- Wiki 文章 (16 篇) - 需要 Article Schema
- Guides 文章 (10 篇) - 需要 HowTo Schema
- 平台详情页 (3 个) - 需要 Product Schema

---

## 🎯 实施顺序

1. **第 1 步**: 为所有主要页面添加 BreadcrumbList Schema
2. **第 2 步**: 为专业内容页面 (Wiki/Guides) 添加 Article/HowTo Schema
3. **第 3 步**: 优化 Meta 标签和 Open Graph
4. **第 4 步**: 更新 sitemap.xml (包含所有页面)
5. **第 5 步**: 本地验证和测试
6. **第 6 步**: 创建 SEO 检查清单和验证文档

---

## 📦 输出物清单

- [ ] 所有页面更新 (5+ pages with enhanced Schema)
- [ ] sitemap.xml (更新 - 包含 30+ 页面)
- [ ] SEO_CHECKLIST.md (验证清单)
- [ ] schema-validation.html (验证工具)
- [ ] SEO 审计报告 (Lighthouse + Schema 验证)

---

## 🔗 参考资源

- [Google Schema.org 文档](https://schema.org/)
- [Google Search Central](https://developers.google.com/search)
- [Schema Markup Validator](https://validator.schema.org/)
- [Lighthouse 文档](https://developers.google.com/web/tools/lighthouse)
