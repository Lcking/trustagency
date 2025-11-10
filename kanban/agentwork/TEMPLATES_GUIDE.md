# HTML 模板和组件库快速参考

## 项目结构

```
trustagency/
├── site/
│   ├── index.html                    # 首页
│   ├── base.html                     # 基础模板（参考用）
│   ├── components.html               # 组件库演示页面
│   ├── platforms/
│   │   ├── index.html                # 平台列表
│   │   └── alpha-leverage/
│   │       └── index.html            # 平台详情
│   ├── qa/
│   │   └── index.html                # FAQ 页面
│   ├── compare/
│   │   └── index.html                # 平台对比
│   ├── about/
│   │   └── index.html                # 关于页面
│   ├── legal/
│   │   └── index.html                # 法律声明
│   ├── wiki/                         # Wiki 页面
│   ├── guides/                       # 指南页面
│   ├── assets/
│   │   ├── css/
│   │   │   ├── main.css             # 主样式表（480+ 行）
│   │   │   └── utilities.css        # 工具类样式表
│   │   └── js/
│   │       └── main.js              # 主脚本（模块化）
│   ├── robots.txt
│   └── sitemap.xml
├── kanban/                           # Kanban 任务管理
├── nginx/                            # Nginx 配置
├── Dockerfile                        # Docker 镜像定义
├── docker-compose.build.yml          # Docker Compose 配置
├── README.md                         # 项目文档
├── CHECKLIST.md                      # 验收清单
└── agentwork.md                      # 项目进度
```

## 主要文件说明

### `site/base.html`
基础模板文件，包含所有页面应该遵循的标准结构：
- HTML5 DOCTYPE 和 meta 标签（SEO、响应式、兼容性）
- Skip-to-content 无障碍链接
- 响应式导航栏（带 dropdown 菜单）
- 面包屑导航占位
- 主要内容区域（id="main-content"）
- 完整的页脚
- Bootstrap 5 CDN 和自定义脚本加载

**使用方法**：复制 base.html 的结构到新页面，修改主要内容区域和 meta 标签。

### `site/assets/css/main.css`
主样式表（480+ 行），包含：
- CSS 变量定义（颜色、阴影等）
- 页面基础样式
- 组件样式：
  - 导航栏和下拉菜单
  - 面包屑导航
  - Hero 部分
  - 卡片（标准、推荐、成功、警告、危险）
  - 按钮（所有尺寸和状态）
  - 表单元素
  - 表格
  - 手风琴
  - 警告框和徽章
- 无障碍性样式：
  - Skip-to-content 链接
  - Focus 可见性
  - Keyboard navigation 指示器
  - Screen reader only 文本
- 响应式设计（Mobile-first）
- 打印样式

**主要 CSS 变量**：
```css
--primary-color: #0d6efd
--secondary-color: #6c757d
--success-color: #198754
--danger-color: #dc3545
--warning-color: #ffc107
--info-color: #0dcaf0
--light-color: #f8f9fa
--dark-color: #212529
```

**常用组件类**：
- `.card` - 标准卡片
- `.card-featured` - 推荐卡片（带"推荐"标签）
- `.card-success`、`.card-warning`、`.card-danger` - 带颜色指示的卡片
- `.btn-primary`、`.btn-outline-primary` - 按钮样式
- `.alert`、`.alert-primary` 等 - 警告框
- `.badge`、`.badge-primary` 等 - 徽章

### `site/assets/css/utilities.css`
工具类样式表（50+ 个工具类）：
- Display 工具类：`.d-flex`、`.d-grid`、`.d-none` 等
- Flexbox 工具类：`.flex-column`、`.justify-content-center` 等
- 尺寸工具类：`.w-25`、`.w-50`、`.h-100` 等
- 文本工具类：`.text-uppercase`、`.fw-bold` 等
- 背景工具类：`.bg-cover`、`.bg-center` 等
- 响应式工具类：`.d-sm-none`、`.text-md-center` 等
- 动画类：`.fade-in`、`.slide-in-up`、`.pulse` 等

### `site/assets/js/main.js`
主脚本文件（模块化结构）：

**全局对象**：`window.TrustAgency`

**配置**：
```javascript
TrustAgency.config = {
    debug: false,
    lang: 'zh-CN'
}
```

**主要函数**：
- `TrustAgency.init()` - 初始化所有功能
- `TrustAgency.initializeAccessibility()` - 初始化无障碍功能
- `TrustAgency.setupFocusIndicators()` - 键盘导航指示
- `TrustAgency.setupSkipToContent()` - Skip-to-content 功能
- `TrustAgency.setupAriaLive()` - 屏幕阅读器支持
- `TrustAgency.announceToScreenReader(message)` - 向屏幕阅读器发送消息
- `TrustAgency.initializeFormValidation()` - 表单验证
- `TrustAgency.initializeSmoothScroll()` - 平滑滚动
- `TrustAgency.initializeLazyLoad()` - 图片懒加载
- `TrustAgency.setupSearch()` - 搜索功能
- `TrustAgency.setupDarkModeToggle()` - 深色模式切换
- `TrustAgency.log(message, level)` - 调试日志

**自动初始化**：
页面加载时自动执行 `TrustAgency.init()`，初始化所有功能。

### `site/components.html`
组件库演示页面，展示所有可用的组件和样式：
- 卡片组件（5 种样式）
- 按钮（颜色、尺寸、样式）
- 警告框（5 种类型）
- 徽章（5 种颜色）
- 数据表格
- 手风琴
- 表单
- 面包屑导航
- 文本样式
- 工具类

**访问方式**：打开 `http://localhost/components.html`（开发环境）

## 常见用法

### 使用基础模板创建新页面

1. 复制 `base.html` 的完整结构
2. 修改 `<title>` 和 meta 标签
3. 修改导航栏中的 aria-current="page" 指向当前页面
4. 在 `<main id="main-content">` 中添加页面内容

### 创建卡片组件

**标准卡片**：
```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title">标题</h5>
    </div>
    <div class="card-body">
        <p class="card-text">内容</p>
    </div>
    <div class="card-footer">
        <a href="#" class="btn btn-primary btn-sm">操作</a>
    </div>
</div>
```

**推荐卡片**：
```html
<div class="card card-featured">
    <!-- 内容 -->
</div>
```

### 使用表单验证

```html
<form>
    <div class="form-group mb-3">
        <label for="email" class="form-label">邮箱</label>
        <input type="email" class="form-control" id="email" required>
    </div>
    <button type="submit" class="btn btn-primary">提交</button>
</form>
```

表单自动验证将在提交时触发，使用 Bootstrap 的 `was-validated` 类。

### 向屏幕阅读器发送消息

```javascript
TrustAgency.announceToScreenReader('操作成功');
```

### 启用图片懒加载

在 `<img>` 标签中使用 `data-src` 替代 `src`：
```html
<img data-src="/image.jpg" alt="描述">
```

### 启用深色模式切换

添加一个按钮：
```html
<button id="dark-mode-toggle" aria-pressed="false">🌙</button>
```

然后调用：
```javascript
TrustAgency.setupDarkModeToggle();
```

## 响应式设计

### 断点
- 超小屏幕 (xs): < 576px (Mobile)
- 小屏幕 (sm): ≥ 576px
- 中等屏幕 (md): ≥ 768px (Tablet)
- 大屏幕 (lg): ≥ 992px (Desktop)
- 超大屏幕 (xl): ≥ 1200px (Large Desktop)

### 响应式工具类
```html
<!-- 在 md 断点及以上隐藏 -->
<div class="d-md-none">Mobile only</div>

<!-- 在 md 断点以下隐藏 -->
<div class="d-none d-md-block">Desktop only</div>

<!-- 响应式文本对齐 -->
<p class="text-center text-md-left">文本</p>
```

## 无障碍性 (Accessibility)

### ARIA 标签
所有交互元素必须有 ARIA 标签：
```html
<button aria-label="菜单">☰</button>
<nav aria-label="主导航">...</nav>
<form aria-label="搜索表单">...</form>
```

### 键盘导航
- Tab 键：切换焦点到下一个交互元素
- Shift+Tab：切换焦点到上一个交互元素
- Enter：激活按钮/链接
- Space：切换复选框/单选按钮
- 箭头键：在菜单中导航

### Skip-to-content 链接
自动包含在 base.html 中：
```html
<a href="#main-content" class="skip-to-content">跳转到主要内容</a>
```

## SEO 优化

### Meta 标签（必需）
```html
<meta name="title" content="...">
<meta name="description" content="...">
<meta name="keywords" content="...">
<meta name="robots" content="index, follow">
```

### Open Graph（推荐）
```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://example.com/">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
```

### JSON-LD Schema（推荐）
```html
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "...",
    "url": "https://example.com"
}
</script>
```

## 性能优化

### 图片优化
使用 `data-src` 进行懒加载：
```html
<img data-src="/image.jpg" alt="描述" width="300" height="200">
```

### CSS 加载优化
样式表通过 CDN 加载：
- Bootstrap 5：jsDelivr CDN
- 自定义样式：本地文件

### JavaScript 加载优化
- 所有脚本在 </body> 之前加载
- main.js 采用模块化结构，DOMContentLoaded 后初始化

## 浏览器兼容性

- Chrome / Edge：最新两个版本
- Firefox：最新两个版本
- Safari：最新两个版本
- iOS Safari：最新两个版本
- IE 11：基本支持（Polyfills 已包含）

## 构建和部署

### 本地开发
```bash
# 使用 Docker 本地运行
bash deploy.sh local

# 访问
http://localhost/
http://localhost/components.html  # 组件库演示
```

### 生产部署
```bash
# 部署到服务器
bash deploy.sh prod --host user@server.com
```

## 故障排除

### CSS 样式未加载
1. 检查浏览器控制台中是否有 404 错误
2. 确保 CDN 链接有效
3. 清除浏览器缓存（Ctrl+Shift+Delete）

### JavaScript 功能不工作
1. 检查浏览器控制台中是否有 JavaScript 错误
2. 确保 main.js 已加载
3. 在浏览器控制台检查 `TrustAgency` 对象是否存在
4. 启用调试模式：`TrustAgency.config.debug = true`

### 移动端显示问题
1. 检查 viewport meta 标签
2. 测试各种屏幕尺寸
3. 使用 Bootstrap 响应式工具类

## 相关资源

- Bootstrap 5 官方文档：https://getbootstrap.com/docs/5.0/
- Schema.org：https://schema.org/
- MDN Web Docs：https://developer.mozilla.org/
- Web 无障碍倡议 (WAI)：https://www.w3.org/WAI/

## 下一步

- 对所有页面应用 base.html 模板
- 完成响应式测试
- 完成键盘导航测试
- 优化性能（Lighthouse 评分 ≥ 90）
