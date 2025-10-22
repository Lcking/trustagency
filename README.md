# 股票杠杆平台排行榜单 - 项目文档

**项目名称**: 股票杠杆平台排行榜单  
**项目类型**: 静态 SEO/GEO 友好网站  
**技术栈**: HTML5 + Bootstrap 5 + Nginx + Docker  
**开始日期**: 2025-10-21  
**更新日期**: 2025-10-16  

---

## 📋 目录

1. [项目概述](#项目概述)
2. [快速开始](#快速开始)
3. [项目结构](#项目结构)
4. [本地开发](#本地开发)
5. [Docker 部署](#docker-部署)
6. [性能指标](#性能指标)
7. [可访问性](#可访问性)
8. [SEO 与结构化数据](#seo-与结构化数据)
9. [故障排查](#故障排查)
10. [常见问题](#常见问题)

---

## 项目概述

股票杠杆平台排行榜单是一个完整的静态网站项目，专注于：

- ✅ **移动端优先** - 响应式设计，支持所有设备
- ✅ **SEO 友好** - 结构化数据（JSON-LD）、robots.txt、sitemap.xml
- ✅ **无障碍访问** - WCAG 2.1 AA 标准、ARIA 标签
- ✅ **高性能** - 优化的 Nginx 配置、智能缓存策略
- ✅ **容器化** - Docker + Docker Compose，一键部署
- ✅ **安全性** - CSP、HSTS、安全头等安全措施

### 核心特性

| 特性 | 描述 |
|------|------|
| 📱 响应式设计 | 375px、768px、1200px 完美适配 |
| 🔍 SEO 优化 | 完整的 Schema.org 结构化数据 |
| ♿ 无障碍 | Lighthouse 无障碍评分 ≥ 90 |
| ⚡ 性能 | LCP ≤ 2.5s，CLS ≈ 0 |
| 🐳 容器化 | Nginx Alpine 镜像，~42MB |
| 🔒 安全 | 多重安全头，CSP 策略 |

---

## 快速开始

### 前置要求

- Docker Desktop（[官方下载](https://www.docker.com/products/docker-desktop)）
- Docker Compose（通常包含在 Docker Desktop 中）
- bash shell（macOS/Linux 原生；Windows 用户可用 WSL 或 Git Bash）

### 本地运行（5 分钟）

#### 方式 1：使用 Docker Compose（推荐）

```bash
# 1. 进入项目目录
cd /path/to/trustagency

# 2. 构建并启动容器
docker compose -f docker-compose.build.yml up -d --build

# 3. 打开浏览器访问
# 本地地址: http://localhost/
# 或: http://localhost:8080/ (如果 80 端口被占用)

# 4. 查看容器状态
docker ps

# 5. 查看 Nginx 日志
docker logs trustagency-web

# 6. 停止容器
docker compose -f docker-compose.build.yml down
```

#### 方式 2：使用部署脚本

```bash
# 构建并部署
bash deploy.sh local

# 查看部署日志
cat deploy.log

# 更新代码
bash update.sh local
```

#### 方式 3：本地预览（仅限文件查看）

如不想使用 Docker，可直接用浏览器打开：

```bash
open site/index.html  # macOS
# 或在浏览器中输入: file:///path/to/trustagency/site/index.html
```

**注意**：本地打开 HTML 文件无法正确测试缓存头、CSP、CORS 等网络功能。

---

## 项目结构

```
trustagency/
├── site/                           # 静态网站根目录
│   ├── index.html                  # 首页
│   ├── robots.txt                  # SEO - 爬虫指令
│   ├── sitemap.xml                 # SEO - 网站地图
│   ├── assets/
│   │   ├── css/
│   │   │   └── main.css            # 自定义样式
│   │   ├── js/
│   │   │   └── main.js             # 最小化 JavaScript（无框架）
│   │   └── images/                 # 图片资源
│   ├── platforms/                  # 平台列表页
│   │   ├── index.html              # 平台汇总
│   │   ├── alpha-leverage/
│   │   │   └── index.html          # Alpha Leverage 详情
│   │   ├── beta-margin/
│   │   │   └── index.html          # Beta Margin 详情
│   │   └── gamma-trader/
│   │       └── index.html          # Gamma Trader 详情
│   ├── qa/                         # 常见问题
│   │   └── index.html              # FAQ 页面（≥10 条）
│   ├── wiki/                       # 知识库
│   │   ├── margin-call/
│   │   │   └── index.html          # 保证金追加
│   │   └── risk-metrics/
│   │       └── index.html          # 风险指标
│   ├── guides/                     # 使用指南
│   │   ├── open-account/
│   │   │   └── index.html          # 开户指南
│   │   └── risk-settings/
│   │       └── index.html          # 风险设置指南
│   ├── compare/                    # 平台对比
│   │   └── index.html              # 对比表
│   ├── about/                      # 关于我们
│   │   └── index.html
│   └── legal/                      # 法律声明
│       └── index.html
├── nginx/                          # Nginx 配置
│   ├── default.conf                # 主配置文件
│   └── logs/                       # 日志目录（Docker 挂载）
├── kanban/                         # Kanban 看板系统
│   ├── board.md                    # 看板主文件
│   └── issues/                     # 任务详细描述
│       ├── A-1.md ... A-11.md     # 各个任务文件
├── Dockerfile                      # Docker 镜像定义
├── docker-compose.build.yml        # Docker Compose 配置
├── deploy.sh                       # 部署脚本
├── update.sh                       # 更新脚本
├── README.md                       # 本文档
├── CHECKLIST.md                    # 验收清单
└── agentwork.md                    # 项目进度归档
```

---

## 本地开发

### 编辑页面

所有 HTML 页面都在 `site/` 目录中。修改后直接保存，然后刷新浏览器：

```bash
# 编辑首页
vi site/index.html

# 编辑 CSS
vi site/assets/css/main.css

# 编辑 JavaScript
vi site/assets/js/main.js
```

### 更新容器内容

如修改了 HTML、CSS、JS 等静态文件，需要重启或更新容器：

```bash
# 方式 1：使用 update 脚本（推荐）
bash update.sh local

# 方式 2：手动重启容器
docker compose -f docker-compose.build.yml restart

# 方式 3：完全重新构建
docker compose -f docker-compose.build.yml down --remove-orphans
docker compose -f docker-compose.build.yml up -d --build
```

### 常用开发命令

```bash
# 查看容器日志（实时）
docker logs -f trustagency-web

# 进入容器调试
docker exec -it trustagency-web /bin/sh

# 检查 Nginx 配置
docker exec trustagency-web nginx -t

# 查看容器资源使用
docker stats trustagency-web

# 验证页面（使用 curl）
curl -I http://localhost/
curl http://localhost/robots.txt
```

---

## Docker 部署

### 本地 Docker 部署

#### 快速部署

```bash
bash deploy.sh local
```

#### 手动部署

```bash
cd /path/to/trustagency
docker compose -f docker-compose.build.yml up -d --build --remove-orphans
```

#### 验证部署

```bash
# 检查容器运行状态
docker ps -a | grep trustagency

# 检查容器健康状态
docker ps --filter "name=trustagency-web" --format "{{.Status}}"

# 访问首页
curl http://localhost/
```

### 生产服务器部署

#### 使用部署脚本

```bash
bash deploy.sh prod --host user@example.com
```

#### 手动部署到服务器

```bash
# 1. 上传项目文件
scp -r /path/to/trustagency user@example.com:~/

# 2. SSH 连接到服务器
ssh user@example.com

# 3. 在服务器上运行
cd ~/trustagency
docker compose -f docker-compose.build.yml up -d --build --remove-orphans

# 4. 配置反向代理（Nginx/Apache）
# 指向 http://localhost:80 或配置的端口
```

### Docker 端口配置

默认配置使用端口 80。如 80 端口被占用，可修改 `docker-compose.build.yml`：

```yaml
ports:
  - "8080:80"  # 将本地 8080 映射到容器 80
```

然后访问 `http://localhost:8080/`

---

## 性能指标

### Core Web Vitals (CWV) 目标

| 指标 | 移动 4G | 桌面 | 目标 |
|------|--------|------|------|
| **LCP** (Largest Contentful Paint) | ≤ 4.0s | ≤ 2.5s | ✅ 绿色 |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.1 | ≈ 0 |
| **FID** (First Input Delay) | ≤ 100ms | ≤ 100ms | ✅ 绿色 |

### Lighthouse 评分目标

| 类别 | 目标分数 |
|------|---------|
| 性能 (Performance) | ≥ 85 |
| 无障碍 (Accessibility) | ≥ 90 |
| SEO | ≥ 90 |
| 最佳实践 (Best Practices) | ≥ 85 |

### 性能优化清单

- ✅ 压缩资源（Gzip）
- ✅ 缓存策略（HTML/CSS/JS/Images）
- ✅ 移动端优先
- ✅ 最小化 JavaScript（无框架）
- ✅ 内联关键 CSS
- ✅ 图片优化（使用 WebP、适当大小）
- ✅ 删除未使用的 CSS/JS
- ✅ 异步加载非关键资源

### 运行性能测试

```bash
# 使用 Lighthouse 测试（需要 Chrome/Chromium）
lighthouse http://localhost/ --view

# 使用 curl 检查响应头
curl -I http://localhost/

# 检查缓存头
curl -I http://localhost/assets/css/main.css

# 检查压缩
curl -I -H "Accept-Encoding: gzip" http://localhost/
```

---

## 可访问性

### WCAG 2.1 AA 合规性

本项目遵循 WCAG 2.1 AA 标准：

- ✅ 键盘导航完全可用（Tab、Enter、Escape）
- ✅ 屏幕阅读器支持（NVDA、JAWS、VoiceOver）
- ✅ 颜色对比度达到 AA 标准
- ✅ 语义 HTML（header, nav, main, article, section, footer）
- ✅ ARIA 标签（role, aria-label, aria-describedby）
- ✅ 图片 Alt 文本
- ✅ 表单标签关联

### 测试工具

```bash
# axe DevTools (Chrome 扩展)
# 访问 Chrome Web Store 安装

# Lighthouse 无障碍检查
lighthouse http://localhost/ --view

# NVDA 屏幕阅读器测试
# 下载: https://www.nvaccess.org/download/
```

---

## SEO 与结构化数据

### 页面 Schema 类型

| 页面 | Schema 类型 | 说明 |
|------|-----------|------|
| 首页 | WebSite, Organization, SearchAction | 站点整体信息 |
| 平台详情 | SoftwareApplication, BreadcrumbList, AggregateRating | 软件应用详情 |
| FAQ | FAQPage | 常见问题集合 |
| 百科/文章 | Article, TechArticle | 文章内容 |
| 指南 | HowTo | 逐步说明 |
| 对比 | ItemList | 项目列表 |

### SEO 检查清单

- ✅ robots.txt：允许爬虫；包含 Sitemap URL
- ✅ sitemap.xml：包含所有页面；包含优先级、更新频率
- ✅ Meta 标签：title、description、keywords
- ✅ Open Graph：og:title、og:description、og:image
- ✅ Twitter 卡片：twitter:card、twitter:title
- ✅ Canonical 标签：避免重复内容
- ✅ 结构化数据：JSON-LD 格式，通过 Google 测试

### 验证 Schema

```bash
# Google 结构化数据测试
# https://search.google.com/test/rich-results

# Schema.org 验证
# https://schema.org/

# 使用 curl 查看 HTML
curl http://localhost/ | grep -A 5 "application/ld+json"
```

---

## 故障排查

### 容器无法启动

```bash
# 1. 查看 Docker 构建日志
docker compose -f docker-compose.build.yml up

# 2. 查看容器错误
docker logs trustagency-web

# 3. 检查 Nginx 配置
docker exec trustagency-web nginx -t

# 4. 重建镜像
docker compose -f docker-compose.build.yml down --remove-orphans -v
docker compose -f docker-compose.build.yml up -d --build
```

### 页面返回 404

```bash
# 1. 检查文件是否存在
ls -la site/index.html

# 2. 进入容器检查文件挂载
docker exec trustagency-web ls -la /usr/share/nginx/html/

# 3. 检查 Nginx 日志
docker logs trustagency-web | grep 404
```

### 缓存问题

```bash
# 清除浏览器缓存（浏览器开发者工具 → Application → Clear Storage）
# 或使用 curl 检查
curl -i -H "Cache-Control: no-cache" http://localhost/

# 重启容器
docker compose -f docker-compose.build.yml restart
```

### 端口被占用

```bash
# 检查谁占用了 80 端口
lsof -i :80

# 方式 1：修改 docker-compose.yml 中的端口
# ports:
#   - "8080:80"

# 方式 2：停止占用进程
sudo kill -9 <PID>

# 方式 3：使用不同的 Docker Compose 文件
docker compose -f docker-compose.build.yml -p trustagency-alt up -d
```

---

## 常见问题

### Q: 如何修改页面内容？

**A**: 所有页面都在 `site/` 目录中，直接编辑 HTML 文件即可。修改后运行 `bash update.sh local` 更新容器。

### Q: 如何添加新页面？

**A**: 
1. 在 `site/` 中创建新的 HTML 文件或目录
2. 在导航栏 (`index.html`) 中添加链接
3. 更新 `robots.txt` 和 `sitemap.xml`
4. 添加适当的 Schema.org 结构化数据
5. 运行 `bash update.sh local` 更新容器

### Q: 如何更改 logo 和品牌信息？

**A**: 编辑以下文件中的相应内容：
- `site/index.html` 和其他 HTML 页面中的品牌名称
- `site/assets/images/` 中添加 logo 文件
- `nginx/default.conf` 中的缓存策略（如需要）

### Q: Docker 镜像多大？

**A**: 基于 `nginx:alpine` 的镜像约 **42-50 MB**（包括 Nginx 和静态文件）。

### Q: 如何在生产环境中使用？

**A**: 
1. 使用 `bash deploy.sh prod --host user@example.com` 自动部署
2. 或手动上传文件后运行 `docker compose -f docker-compose.build.yml up -d`
3. 配置反向代理（Nginx/Apache）指向容器
4. 配置 SSL 证书（Let's Encrypt）
5. 配置域名解析

### Q: 如何监控容器健康状态？

**A**: 
```bash
# 查看容器状态
docker ps --filter "name=trustagency-web"

# 查看详细健康状态
docker ps --filter "name=trustagency-web" --format "{{.Status}}"

# 查看日志
docker logs trustagency-web

# 使用 health check
docker inspect trustagency-web | grep -A 5 "Health"
```

### Q: 如何备份网站？

**A**: 
```bash
# 备份整个项目
tar -czf trustagency-backup-$(date +%Y%m%d).tar.gz /path/to/trustagency/

# 备份只是网站内容
tar -czf trustagency-site-$(date +%Y%m%d).tar.gz /path/to/trustagency/site/
```

---

## 支持与贡献

对于问题、建议或贡献，请联系：

📧 **Email**: support@example.com  
🌐 **Website**: https://example.com/  

---

## 许可证

© 2025 股票杠杆平台排行榜单。版权所有。

本网站仅供信息参考，不提供交易通道，不构成投资建议或引导。  
请遵守当地法律法规。

---

**最后更新**: 2025-10-16  
**文档版本**: 1.0
