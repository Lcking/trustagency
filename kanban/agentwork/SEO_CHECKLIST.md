# SEO 检查清单与验收标准

**更新日期**: 2025-10-21  
**项目**: 股票杠杆平台排行榜单  
**状态**: 进行中

---

## 📋 Schema 标记验收清单

### BreadcrumbList Schema
- [x] 首页 (`/`) - BreadcrumbList 已添加
- [x] 平台列表 (`/platforms/`) - BreadcrumbList 已添加
- [x] 对比页 (`/compare/`) - BreadcrumbList 已添加
- [x] 关于页 (`/about/`) - BreadcrumbList 已添加
- [x] 法律页 (`/legal/`) - BreadcrumbList 已添加
- [x] FAQ 页 (`/qa/`) - BreadcrumbList 已添加
- [x] Wiki 索引 (`/wiki/`) - BreadcrumbList 已添加 (包含在页面)
- [x] Wiki 文章示例 (`/wiki/what-is-leverage/`) - BreadcrumbList 已添加
- [x] Guides 索引 (`/guides/`) - BreadcrumbList 已添加 (包含在页面)
- [x] Guides 文章示例 (`/guides/quick-start/`) - BreadcrumbList 已添加

### 页面特定 Schema
- [x] 首页 - WebSite + Organization + FAQPage Schema
- [x] 平台列表 - ItemList Schema
- [x] Wiki 索引 - CollectionPage Schema
- [x] Wiki 文章 - NewsArticle Schema
- [x] Guides 索引 - CollectionPage Schema
- [x] Guides 文章 - HowTo Schema
- [x] FAQ 页 - FAQPage Schema
- [x] 法律页 - WebPage Schema

### 平台详情页 Schema
- [ ] `/platforms/alpha-leverage/` - Product Schema (需要)
- [ ] `/platforms/beta-margin/` - Product Schema (需要)
- [ ] `/platforms/gamma-trader/` - Product Schema (需要)

---

## 🎯 元标签验收清单

### 基础元标签
- [x] `<title>` - 所有页面都有
- [x] `<meta name="description">` - 所有页面都有
- [x] `<meta name="keywords">` - 所有页面都有
- [x] `<meta name="robots">` - 所有页面都有
- [x] `<link rel="canonical">` - 所有页面都有
- [x] `<meta charset="UTF-8">` - 所有页面都有
- [x] `<meta name="viewport">` - 所有页面都有

### Open Graph 标签
- [x] 首页 - og:title, og:description, og:type, og:url
- [x] 平台列表 - og:title, og:description, og:type, og:url
- [x] 对比页 - og:title, og:description, og:type, og:url
- [x] FAQ 页 - og:title, og:description, og:type, og:url
- [x] 关于页 - og:title, og:description, og:type, og:url
- [x] 法律页 - (缺少 OG 标签 - 可选)
- [ ] og:image - 所有页面 (推荐)
- [ ] og:locale - 所有页面 (已在首页)

### Twitter 卡片标签
- [x] 首页 - twitter:card, twitter:title, twitter:description, twitter:url
- [ ] 其他页面 - Twitter 标签 (建议添加)

---

## 📍 Sitemap 验收

- [x] robots.txt 存在且有效
  - [x] User-agent 规则正确
  - [x] Sitemap 指向正确
  - [x] Crawl-delay 设置合理
  - [ ] 域名更新到实际地址 (当前: example.com)

- [x] sitemap.xml 已更新
  - [x] 包含所有主要页面 (13 个)
  - [x] 所有 URL 都有 `<lastmod>` 日期 (2025-10-21)
  - [x] 所有 URL 都有 `<priority>` 值
  - [x] 所有 URL 都有 `<changefreq>`
  - [x] XML 格式有效
  - [ ] 域名更新到实际地址 (当前: example.com)

---

## 🔍 SEO 性能指标

### Lighthouse SEO 审计
**目标**: 100/100

运行命令检查:
```bash
# 本地检查 (需要在浏览器中运行)
# Chrome DevTools > Lighthouse > SEO 标签页
```

检查清单:
- [ ] 所有 Lighthouse SEO 指标为绿色 ✅
- [ ] Mobile-Friendly (响应式设计)
- [ ] 可爬虫性 (无 robots 阻止)
- [ ] 页面使用 HTTPS
- [ ] 所有链接都有有效的 href 属性
- [ ] 所有页面都有元 description

### Schema 验证
**工具**: Google Schema Markup Validator  
**网址**: https://validator.schema.org/

验证各页面:
- [ ] 首页 - 通过验证
- [ ] 平台列表 - 通过验证
- [ ] 对比页 - 通过验证
- [ ] FAQ 页 - 通过验证
- [ ] Wiki 索引 - 通过验证
- [ ] Wiki 文章示例 - 通过验证
- [ ] Guides 索引 - 通过验证
- [ ] Guides 文章示例 - 通过验证

---

## 📱 特殊标签与配置

### 推荐配置
- [ ] `<meta name="theme-color">` - 添加到所有页面
- [ ] `<link rel="apple-touch-icon">` - 添加到所有页面
- [ ] `<link rel="manifest">` - PWA manifest (可选)
- [ ] `<meta name="og:image">` - 所有社交媒体页面

### 国际化 (可选)
- [ ] `<html lang="zh-CN">` - 所有页面已有
- [ ] hreflang 标签 - 如果有多语言 (不适用)

---

## 🚀 Google Search Console 集成

### 操作步骤
1. [ ] 访问 https://search.google.com/search-console
2. [ ] 添加属性 (选择 URL 前缀)
3. [ ] 输入网站 URL: `https://example.com`
4. [ ] 验证所有权 (选择 HTML 标签方法)
5. [ ] 提交 sitemap.xml (`https://example.com/sitemap.xml`)
6. [ ] 提交 robots.txt (`https://example.com/robots.txt`)

### 验证任务
- [ ] 网站验证成功
- [ ] Sitemap 被接受
- [ ] robots.txt 被读取
- [ ] 检查覆盖率 (应该 100%)
- [ ] 检查提交网址 (应该 100%)

---

## 📊 关键 SEO 指标

### 页面指标 (每个页面)
| 指标 | 目标值 | 当前值 |
|------|-------|--------|
| Meta Description 长度 | 50-160 字符 | ✓ |
| Title 长度 | 30-60 字符 | ✓ |
| H1 标签数量 | 1 个 | ✓ |
| Canonical 标签 | 有效 | ✓ |
| BreadcrumbList Schema | 全部页面 | ✓ |
| Open Graph 标签 | 基础完整 | ✓ |

### 站点级指标
| 指标 | 状态 |
|------|------|
| Sitemap 包含页面数 | 13 个 ✓ |
| robots.txt 有效 | ✓ |
| 移动友好性 | ✓ |
| 无爬虫阻止 | ✓ |
| HTTPS | ✓ (本地) |

---

## 📝 待办事项

### 立即执行 (当前)
- [ ] 验证首页 Schema (Google Validator)
- [ ] 验证平台列表 Schema
- [ ] 验证 FAQ 页 Schema
- [ ] 验证 Wiki 文章 Schema
- [ ] 验证 Guides 文章 Schema

### 后续任务 (部署前)
- [ ] 替换所有 `example.com` 为实际域名
- [ ] 添加平台详情页 Product Schema
- [ ] 为所有页面添加 og:image
- [ ] 运行 Lighthouse SEO 审计
- [ ] 提交到 Google Search Console

### 维护任务 (定期)
- [ ] 每月检查 Search Console 数据
- [ ] 监测排名与流量
- [ ] 定期更新 lastmod 日期
- [ ] 添加新页面到 sitemap.xml
- [ ] 监测爬虫错误

---

## 🧪 本地测试步骤

### 1. Schema 验证
```bash
# 使用在线工具验证 Schema
# https://validator.schema.org/

# 或使用命令行工具
npm install -g schema-validator
schema-validator /Users/ck/Desktop/Project/trustagency/site/index.html
```

### 2. SEO 本地审计
```bash
# 安装 Lighthouse CLI
npm install -g @lhci/cli@latest

# 运行审计
lhci autorun --config=lighthouserc.json
```

### 3. 链接检查
```bash
# 检查所有链接是否有效
linkchecker http://localhost:8000/
```

---

## ✅ 完成标准

**任务完成条件**:
1. ✅ 所有主要页面都有 BreadcrumbList Schema
2. ✅ Sitemap 包含所有 13 个页面
3. ✅ 所有页面都有有效的元标签
4. ✅ robots.txt 配置正确
5. ⏳ Schema 在 Google Validator 中验证成功 (测试中)
6. ⏳ Lighthouse SEO 得分 100/100 (本地测试中)

---

## 📚 参考资源

- [Google Schema.org 文档](https://schema.org/)
- [Google 搜索中心指南](https://developers.google.com/search)
- [Schema Markup Validator](https://validator.schema.org/)
- [Lighthouse 审计](https://developers.google.com/web/tools/lighthouse)
- [Open Graph 协议](https://ogp.me/)
- [Twitter Card 标签](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/summary-card)

---

**下次更新**: 2025-10-21 (Schema 验证完成后)
