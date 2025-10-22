# A-4 实施指南 - Wiki 和 Guides 文章创建

**状态**: 🟢 实施中  
**目标**: 创建 30+ 知识库文章  
**质量目标**: 5/5 ⭐⭐⭐⭐⭐

---

## 📘 第一部分: 开发环境设置

### 步骤 1: 创建目录结构

```bash
# Wiki 文章目录
mkdir -p site/wiki/what-is-leverage
mkdir -p site/wiki/margin-call
mkdir -p site/wiki/leverage-ratio
mkdir -p site/wiki/long-short
mkdir -p site/wiki/risk-metrics
mkdir -p site/wiki/position-sizing
mkdir -p site/wiki/stop-loss-takeprofit
mkdir -p site/wiki/diversification
mkdir -p site/wiki/risk-reward-ratio
mkdir -p site/wiki/technical-analysis
mkdir -p site/wiki/support-resistance
mkdir -p site/wiki/candlestick-patterns
mkdir -p site/wiki/fundamental-analysis
mkdir -p site/wiki/fee-structure
mkdir -p site/wiki/choosing-platform
mkdir -p site/wiki/platform-security

# Guides 文章目录
mkdir -p site/guides/quick-start
mkdir -p site/guides/open-account
mkdir -p site/guides/first-trade
mkdir -p site/guides/risk-settings
mkdir -p site/guides/stop-loss-setup
mkdir -p site/guides/day-trading
mkdir -p site/guides/swing-trading
mkdir -p site/guides/trend-trading
mkdir -p site/guides/common-mistakes
mkdir -p site/guides/best-practices
```

### 步骤 2: 验证基础文件

```bash
# 确认关键文件存在
ls site/index.html                    # ✓ 首页
ls site/wiki/index.html               # ✓ Wiki 首页
ls site/guides/index.html             # ✓ Guides 首页
ls assets/css/main.css                # ✓ CSS
ls assets/js/main.js                  # ✓ JavaScript
```

---

## 🎨 第二部分: Wiki 文章模板 (最终版本)

### 模板代码 (可复制)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="[文章简短描述，80-160 字]">
    <meta name="keywords" content="[关键词1, 关键词2, 关键词3]">
    <meta name="author" content="股票杠杆平台排行榜单">
    <meta property="og:title" content="[文章标题]">
    <meta property="og:description" content="[简短描述]">
    <meta property="og:url" content="https://example.com/wiki/[slug]/">
    <meta property="og:type" content="article">
    
    <title>[文章标题] - 股票杠杆平台排行榜单</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="../../assets/css/main.css">
    <link rel="stylesheet" href="../../assets/css/utilities.css">
    
    <!-- Schema.org 标记 -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": "[文章标题]",
        "description": "[简短描述]",
        "image": "https://example.com/images/article-image.jpg",
        "datePublished": "2025-10-21",
        "dateModified": "2025-10-21",
        "author": {
            "@type": "Organization",
            "name": "股票杠杆平台排行榜单"
        },
        "publisher": {
            "@type": "Organization",
            "name": "股票杠杆平台排行榜单",
            "logo": {
                "@type": "ImageObject",
                "url": "https://example.com/logo.png"
            }
        }
    }
    </script>
</head>
<body>
    <a href="#main-content" class="skip-link">跳转到主要内容</a>
    
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="../../index.html">📊 平台排行</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="../../index.html">首页</a></li>
                    <li class="nav-item"><a class="nav-link" href="../../platforms/index.html">平台</a></li>
                    <li class="nav-item"><a class="nav-link" href="../../compare/index.html">对比</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="resourcesDropdown" role="button" data-bs-toggle="dropdown">
                            资源
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="resourcesDropdown">
                            <li><a class="dropdown-item" href="../../wiki/index.html">📚 百科知识</a></li>
                            <li><a class="dropdown-item" href="../../guides/index.html">📖 交易指南</a></li>
                            <li><a class="dropdown-item" href="../../qa/index.html">❓ 常见问题</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- 面包屑导航 -->
    <nav aria-label="breadcrumb" class="bg-light py-2 border-bottom">
        <div class="container">
            <ol class="breadcrumb mb-0">
                <li class="breadcrumb-item"><a href="../../index.html">首页</a></li>
                <li class="breadcrumb-item"><a href="../../wiki/index.html">百科</a></li>
                <li class="breadcrumb-item active">[文章标题]</li>
            </ol>
        </div>
    </nav>
    
    <!-- 主内容 -->
    <main id="main-content" class="py-5">
        <div class="container">
            <div class="row">
                <!-- 主文章 -->
                <article class="col-lg-8">
                    <header class="mb-4">
                        <h1>[文章标题]</h1>
                        <div class="article-meta text-muted small">
                            <time datetime="2025-10-21">📅 2025 年 10 月 21 日</time>
                            <span class="ms-3">👤 股票杠杆平台排行榜单</span>
                            <span class="ms-3">⏱️ 阅读时间: [X] 分钟</span>
                        </div>
                    </header>
                    
                    <!-- 文章摘要 -->
                    <div class="alert alert-info mb-4">
                        <h5 class="alert-heading">本文摘要</h5>
                        <p class="mb-0">[本文要点摘要，1-3 句，主要概括]</p>
                    </div>
                    
                    <!-- 内容部分 -->
                    <section id="section-1">
                        <h2>第一部分: [子标题]</h2>
                        <p>[正文内容...]</p>
                        <!-- 列表示例 -->
                        <ul>
                            <li>要点 1</li>
                            <li>要点 2</li>
                            <li>要点 3</li>
                        </ul>
                    </section>
                    
                    <section id="section-2">
                        <h2>第二部分: [子标题]</h2>
                        <p>[正文内容...]</p>
                        <!-- 表格示例 -->
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead class="table-light">
                                    <tr>
                                        <th>列 1</th>
                                        <th>列 2</th>
                                        <th>列 3</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>数据</td>
                                        <td>数据</td>
                                        <td>数据</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>
                    
                    <section id="section-3">
                        <h2>第三部分: [子标题]</h2>
                        <p>[正文内容...]</p>
                        <!-- 警告框 -->
                        <div class="alert alert-warning" role="alert">
                            ⚠️ <strong>重要提示:</strong> [警告或重要信息]
                        </div>
                    </section>
                    
                    <!-- 总结 -->
                    <section class="article-summary bg-light p-4 rounded mt-5 mb-5">
                        <h2>📌 总结</h2>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item bg-light">✓ 关键要点 1</li>
                            <li class="list-group-item bg-light">✓ 关键要点 2</li>
                            <li class="list-group-item bg-light">✓ 关键要点 3</li>
                        </ul>
                    </section>
                    
                    <!-- 下一步建议 -->
                    <section class="next-steps mb-5">
                        <h2>📚 下一步学习</h2>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">相关文章</h5>
                                        <a href="[related-article-1]" class="btn btn-sm btn-outline-primary">阅读更多 →</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">交易指南</h5>
                                        <a href="../../guides/[guide-slug]/" class="btn btn-sm btn-outline-primary">查看指南 →</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- 分页导航 -->
                    <nav class="article-pagination mt-5 pt-4 border-top" aria-label="Article navigation">
                        <div class="row">
                            <div class="col-md-6">
                                <a href="[previous-article]" class="btn btn-outline-secondary">← 上一篇文章</a>
                            </div>
                            <div class="col-md-6 text-end">
                                <a href="[next-article]" class="btn btn-outline-secondary">下一篇文章 →</a>
                            </div>
                        </div>
                    </nav>
                </article>
                
                <!-- 侧边栏 -->
                <aside class="col-lg-4">
                    <!-- 目录 -->
                    <div class="card mb-4">
                        <div class="card-header bg-primary text-white">
                            <h5 class="card-title mb-0">📖 本文目录</h5>
                        </div>
                        <div class="card-body">
                            <nav class="toc">
                                <ol class="list-unstyled">
                                    <li><a href="#section-1">第一部分</a></li>
                                    <li><a href="#section-2">第二部分</a></li>
                                    <li><a href="#section-3">第三部分</a></li>
                                    <li><a href="#section-summary">总结</a></li>
                                </ol>
                            </nav>
                        </div>
                    </div>
                    
                    <!-- 相关文章 -->
                    <div class="card mb-4">
                        <div class="card-header bg-info text-white">
                            <h5 class="card-title mb-0">🔗 相关文章</h5>
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">
                                <a href="[related-1]">相关文章标题 1</a>
                            </li>
                            <li class="list-group-item">
                                <a href="[related-2]">相关文章标题 2</a>
                            </li>
                            <li class="list-group-item">
                                <a href="[related-3]">相关文章标题 3</a>
                            </li>
                        </ul>
                    </div>
                    
                    <!-- 快速导航 -->
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5 class="card-title mb-0">🎯 快速导航</h5>
                        </div>
                        <div class="card-body">
                            <a href="../../platforms/index.html" class="btn btn-sm btn-outline-success d-block mb-2">查看平台</a>
                            <a href="../../compare/index.html" class="btn btn-sm btn-outline-success d-block mb-2">平台对比</a>
                            <a href="../../guides/index.html" class="btn btn-sm btn-outline-success d-block">交易指南</a>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="bg-dark text-white py-5 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-4">
                    <h5>关于我们</h5>
                    <p>提供专业的股票杠杆交易平台对比和教育资源。</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h5>快速链接</h5>
                    <ul class="list-unstyled">
                        <li><a href="../../index.html" class="text-white-50 text-decoration-none">首页</a></li>
                        <li><a href="../../platforms/index.html" class="text-white-50 text-decoration-none">平台列表</a></li>
                        <li><a href="../../wiki/index.html" class="text-white-50 text-decoration-none">百科知识</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>法律</h5>
                    <ul class="list-unstyled">
                        <li><a href="../../legal/index.html" class="text-white-50 text-decoration-none">法律声明</a></li>
                        <li><a href="../../about/index.html" class="text-white-50 text-decoration-none">关于我们</a></li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary">
            <div class="text-center">
                <p class="text-white-50 mb-0">&copy; 2025 股票杠杆平台排行榜单. 版权所有。</p>
            </div>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="../../assets/js/main.js" defer></script>
</body>
</html>
```

---

## 🎯 第三部分: Guides 文章模板 (最终版本)

### 模板代码 (可复制)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="[指南描述，80-160 字]">
    <meta name="keywords" content="[关键词1, 关键词2, 关键词3]">
    <meta name="author" content="股票杠杆平台排行榜单">
    <meta property="og:title" content="[指南标题]">
    <meta property="og:description" content="[简短描述]">
    <meta property="og:url" content="https://example.com/guides/[slug]/">
    <meta property="og:type" content="article">
    
    <title>[指南标题] - 股票杠杆平台排行榜单</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="../../assets/css/main.css">
    <link rel="stylesheet" href="../../assets/css/utilities.css">
    
    <!-- Schema.org 标记 -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "[指南标题]",
        "description": "[简短描述]",
        "step": [
            {
                "@type": "HowToStep",
                "text": "[步骤 1 描述]"
            },
            {
                "@type": "HowToStep",
                "text": "[步骤 2 描述]"
            }
        ]
    }
    </script>
</head>
<body>
    <a href="#main-content" class="skip-link">跳转到主要内容</a>
    
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="../../index.html">📊 平台排行</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="../../index.html">首页</a></li>
                    <li class="nav-item"><a class="nav-link" href="../../platforms/index.html">平台</a></li>
                    <li class="nav-item"><a class="nav-link" href="../../compare/index.html">对比</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="resourcesDropdown" role="button" data-bs-toggle="dropdown">
                            资源
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="resourcesDropdown">
                            <li><a class="dropdown-item" href="../../wiki/index.html">📚 百科知识</a></li>
                            <li><a class="dropdown-item" href="../../guides/index.html">📖 交易指南</a></li>
                            <li><a class="dropdown-item" href="../../qa/index.html">❓ 常见问题</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- 面包屑导航 -->
    <nav aria-label="breadcrumb" class="bg-light py-2 border-bottom">
        <div class="container">
            <ol class="breadcrumb mb-0">
                <li class="breadcrumb-item"><a href="../../index.html">首页</a></li>
                <li class="breadcrumb-item"><a href="../../guides/index.html">指南</a></li>
                <li class="breadcrumb-item active">[指南标题]</li>
            </ol>
        </div>
    </nav>
    
    <!-- 主内容 -->
    <main id="main-content" class="py-5">
        <div class="container">
            <div class="row">
                <!-- 主指南 -->
                <article class="col-lg-8">
                    <header class="mb-4">
                        <h1>[指南标题]</h1>
                        <div class="article-meta text-muted small">
                            <time datetime="2025-10-21">📅 2025 年 10 月 21 日</time>
                            <span class="ms-3">👤 股票杠杆平台排行榜单</span>
                            <span class="ms-3">⏱️ 预计时间: [X] 分钟</span>
                        </div>
                    </header>
                    
                    <!-- 指南简介 -->
                    <div class="alert alert-success mb-4">
                        <h5 class="alert-heading">🎯 本指南将教你:</h5>
                        <p class="mb-0">[指南主要成果描述]</p>
                    </div>
                    
                    <!-- 前置要求 -->
                    <div class="card mb-4 border-warning">
                        <div class="card-header bg-light">
                            <h5 class="card-title mb-0">✅ 前置要求</h5>
                        </div>
                        <div class="card-body">
                            <ul class="mb-0">
                                <li>要求 1</li>
                                <li>要求 2</li>
                                <li>要求 3</li>
                            </ul>
                        </div>
                    </div>
                    
                    <!-- 步骤 1 -->
                    <section class="step-section mb-4">
                        <h2>📍 步骤 1: [步骤标题]</h2>
                        <p>[步骤描述和背景信息...]</p>
                        <ol>
                            <li>具体操作 1</li>
                            <li>具体操作 2</li>
                            <li>具体操作 3</li>
                        </ol>
                        <div class="alert alert-info">
                            💡 <strong>提示:</strong> [相关提示]
                        </div>
                    </section>
                    
                    <!-- 步骤 2 -->
                    <section class="step-section mb-4">
                        <h2>📍 步骤 2: [步骤标题]</h2>
                        <p>[步骤描述...]</p>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead class="table-light">
                                    <tr>
                                        <th>参数</th>
                                        <th>说明</th>
                                        <th>示例</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>参数 1</td>
                                        <td>说明</td>
                                        <td>示例值</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>
                    
                    <!-- 步骤 3 -->
                    <section class="step-section mb-4">
                        <h2>📍 步骤 3: [步骤标题]</h2>
                        <p>[步骤描述...]</p>
                        <div class="alert alert-warning">
                            ⚠️ <strong>重要:</strong> [重要提醒]
                        </div>
                    </section>
                    
                    <!-- 常见问题 -->
                    <section class="faq-section mb-5 p-4 bg-light rounded">
                        <h2>❓ 常见问题</h2>
                        <div class="accordion" id="faqAccordion">
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                        问题 1 是什么?
                                    </button>
                                </h2>
                                <div id="faq1" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                    <div class="accordion-body">
                                        [答案内容...]
                                    </div>
                                </div>
                            </div>
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                        问题 2 是什么?
                                    </button>
                                </h2>
                                <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                    <div class="accordion-body">
                                        [答案内容...]
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    <!-- 成功检查 -->
                    <section class="success-checklist mb-5">
                        <h2>✅ 成功检查清单</h2>
                        <div class="list-group">
                            <label class="list-group-item">
                                <input class="form-check-input" type="checkbox" disabled> 检查点 1
                            </label>
                            <label class="list-group-item">
                                <input class="form-check-input" type="checkbox" disabled> 检查点 2
                            </label>
                            <label class="list-group-item">
                                <input class="form-check-input" type="checkbox" disabled> 检查点 3
                            </label>
                        </div>
                    </section>
                    
                    <!-- 下一步 -->
                    <section class="next-steps mb-5 p-4 bg-info bg-opacity-10 rounded">
                        <h2>🚀 下一步</h2>
                        <p>[建议下一步行动...]</p>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <a href="[next-guide]" class="btn btn-primary btn-sm">进阶指南 →</a>
                            </div>
                            <div class="col-md-6">
                                <a href="../../platforms/index.html" class="btn btn-outline-primary btn-sm">选择平台 →</a>
                            </div>
                        </div>
                    </section>
                    
                    <!-- 分页导航 -->
                    <nav class="guide-pagination mt-5 pt-4 border-top" aria-label="Guide navigation">
                        <div class="row">
                            <div class="col-md-6">
                                <a href="[previous-guide]" class="btn btn-outline-secondary">← 上一个指南</a>
                            </div>
                            <div class="col-md-6 text-end">
                                <a href="[next-guide]" class="btn btn-outline-secondary">下一个指南 →</a>
                            </div>
                        </div>
                    </nav>
                </article>
                
                <!-- 侧边栏 -->
                <aside class="col-lg-4">
                    <!-- 快速概览 -->
                    <div class="card mb-4 border-info">
                        <div class="card-header bg-info text-white">
                            <h5 class="card-title mb-0">⚡ 快速概览</h5>
                        </div>
                        <div class="card-body">
                            <dl class="row">
                                <dt class="col-sm-6">预计时间:</dt>
                                <dd class="col-sm-6">[X] 分钟</dd>
                                
                                <dt class="col-sm-6">难度:</dt>
                                <dd class="col-sm-6">初级 / 中级 / 高级</dd>
                                
                                <dt class="col-sm-6">所需账户:</dt>
                                <dd class="col-sm-6">活跃账户</dd>
                            </dl>
                        </div>
                    </div>
                    
                    <!-- 步骤导航 -->
                    <div class="card mb-4">
                        <div class="card-header bg-primary text-white">
                            <h5 class="card-title mb-0">📍 步骤导航</h5>
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item"><a href="#step-1">步骤 1: [标题]</a></li>
                            <li class="list-group-item"><a href="#step-2">步骤 2: [标题]</a></li>
                            <li class="list-group-item"><a href="#step-3">步骤 3: [标题]</a></li>
                        </ul>
                    </div>
                    
                    <!-- 专家提示 -->
                    <div class="card mb-4">
                        <div class="card-header bg-success text-white">
                            <h5 class="card-title mb-0">💡 专家提示</h5>
                        </div>
                        <div class="card-body">
                            <p class="small mb-0">[1-2 句专家建议]</p>
                        </div>
                    </div>
                    
                    <!-- 相关资源 -->
                    <div class="card">
                        <div class="card-header bg-secondary text-white">
                            <h5 class="card-title mb-0">📚 相关资源</h5>
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">
                                <a href="[related-1]">相关文章 1</a>
                            </li>
                            <li class="list-group-item">
                                <a href="[related-2]">相关文章 2</a>
                            </li>
                        </ul>
                    </div>
                </aside>
            </div>
        </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="bg-dark text-white py-5 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-4">
                    <h5>关于我们</h5>
                    <p>提供专业的股票杠杆交易平台对比和教育资源。</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h5>快速链接</h5>
                    <ul class="list-unstyled">
                        <li><a href="../../index.html" class="text-white-50 text-decoration-none">首页</a></li>
                        <li><a href="../../platforms/index.html" class="text-white-50 text-decoration-none">平台列表</a></li>
                        <li><a href="../../guides/index.html" class="text-white-50 text-decoration-none">交易指南</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>法律</h5>
                    <ul class="list-unstyled">
                        <li><a href="../../legal/index.html" class="text-white-50 text-decoration-none">法律声明</a></li>
                        <li><a href="../../about/index.html" class="text-white-50 text-decoration-none">关于我们</a></li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary">
            <div class="text-center">
                <p class="text-white-50 mb-0">&copy; 2025 股票杠杆平台排行榜单. 版权所有。</p>
            </div>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="../../assets/js/main.js" defer></script>
</body>
</html>
```

---

## 🔄 第四部分: 开发流程

### 对于每篇 Wiki 文章:

1. **创建文件** - `site/wiki/[slug]/index.html`
2. **复制模板** - 使用上述 Wiki 模板代码
3. **填充内容** - 替换 `[...]` 占位符
4. **添加链接** - 填充相关文章链接 (指向其他 wiki/guides)
5. **验证链接** - 确保所有 href 正确
6. **测试响应** - 检查移动/平板/桌面视图
7. **检查可访问性** - 验证键盘导航、颜色对比等

### 对于每篇 Guides 文章:

1. **创建文件** - `site/guides/[slug]/index.html`
2. **复制模板** - 使用上述 Guides 模板代码
3. **编写步骤** - 通常 3-8 个有序步骤
4. **添加示例** - 表格/代码示例 (如适用)
5. **填充 FAQ** - 预见常见问题
6. **创建清单** - 成功检查点
7. **测试流程** - 按照步骤验证是否清晰

---

## 📋 质量控制清单

### 每个文件完成前:

- [ ] HTML5 有效 (无错误或警告)
- [ ] 所有链接有效 (无 404)
- [ ] 响应式设计工作正常 (3 个断点测试)
- [ ] 可访问性通过 (WAVE 或类似工具)
- [ ] 字数合理 (Wiki: 800-1500, Guides: 1000-2000)
- [ ] Schema 标记正确
- [ ] 面包屑导航正确
- [ ] 侧边栏内容相关
- [ ] 无拼写或语法错误

---

## 🚀 开始第一篇文章

**建议从以下开始:**

1. **Wiki**: "什么是杠杆交易?" (`what-is-leverage`)
   - 最基础的概念
   - 最容易引导读者
   - 可以设置模式

2. **Guides**: "5 分钟快速开始" (`quick-start`)
   - 最激励人心
   - 短小精悍
   - 可以快速完成

---

**准备好开始吗？** 🎯

*下一步: 创建目录，选择第一篇文章，然后开始编写！*
