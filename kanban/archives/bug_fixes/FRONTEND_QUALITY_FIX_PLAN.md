# 🔧 Port 8001 前端质量修复计划

**修复目标**: 将硬编码数据改为 API 动态加载  
**预计时间**: 3-4 小时  
**难度**: 中等  

---

## 📋 修复清单

### 第 1 阶段: 准备工作 (30 分钟)

- [ ] 验证后端 API 是否正常运行
- [ ] 查看 API 响应格式
- [ ] 准备前端代码修改

### 第 2 阶段: Wiki 页面修复 (1 小时)

- [ ] 创建 API 数据加载函数
- [ ] 实现搜索功能
- [ ] 实现分类过滤
- [ ] 移除硬编码数据

### 第 3 阶段: QA 页面修复 (45 分钟)

- [ ] 从 API 加载 FAQ 数据
- [ ] 更新 UI 渲染逻辑
- [ ] 测试所有问题加载

### 第 4 阶段: 平台页面修复 (45 分钟)

- [ ] 验证字段完整性
- [ ] 添加缺失字段显示
- [ ] 优化平台卡片样式

### 第 5 阶段: 测试和验收 (45 分钟)

- [ ] 完整功能测试
- [ ] 性能检查
- [ ] 浏览器兼容性测试

---

## 🎯 API 检查

### 需要的 API 端点

```bash
# 获取所有文章
GET /api/articles

# 按关键词搜索
GET /api/articles/search/by-keyword?keyword=...

# 按栏目获取
GET /api/articles/by-section/{slug}

# 获取单篇文章
GET /api/articles/{id}
```

### 验证 API 是否工作

```bash
# 测试 API 1
curl http://localhost:8000/api/articles | python3 -m json.tool | head -50

# 测试 API 2
curl "http://localhost:8000/api/articles/search/by-keyword?keyword=leverage" | python3 -m json.tool

# 测试 API 3
curl http://localhost:8000/api/articles/by-section/qa | python3 -m json.tool
```

---

## 💻 代码修复方案

### 方案 A: Wiki 页面修复代码

**文件**: `/site/wiki/index.html`

**需要修改的部分** (大约在第 300-400 行):

```javascript
// ❌ 旧代码：硬编码数据
const wikiArticles = [
    {
        title: '什么是保证金追加...',
        // ... 全部硬编码
    },
    // ... 10-20 个文章
];

// ✅ 新代码：从 API 加载
async function loadWikiArticles() {
    try {
        // 1. 加载所有文章
        const response = await fetch('/api/articles?section=wiki');
        const articles = await response.json();
        
        // 2. 处理响应（可能是数组或对象）
        const articleList = Array.isArray(articles) ? articles : [articles];
        
        // 3. 渲染到页面
        renderWikiArticles(articleList);
    } catch (error) {
        console.error('加载 Wiki 文章失败:', error);
        // 显示错误提示
    }
}

// 搜索功能
async function searchArticles(keyword) {
    if (!keyword.trim()) {
        // 重新加载所有文章
        loadWikiArticles();
        return;
    }
    
    try {
        const response = await fetch(`/api/articles/search/by-keyword?keyword=${keyword}`);
        const results = await response.json();
        renderWikiArticles(results);
    } catch (error) {
        console.error('搜索失败:', error);
    }
}

// 渲染文章列表
function renderWikiArticles(articles) {
    const container = document.getElementById('articlesContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    articles.forEach(article => {
        const html = `
            <article class="card mb-3">
                <div class="card-body">
                    <h3 class="card-title">${article.title}</h3>
                    <p class="card-text">${article.content?.substring(0, 100)}...</p>
                    <a href="/article/${article.slug}" class="btn btn-primary btn-sm">
                        阅读全文
                    </a>
                </div>
            </article>
        `;
        container.innerHTML += html;
    });
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', () => {
    loadWikiArticles();
    
    // 绑定搜索
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchArticles(e.target.value);
        });
    }
});
```

---

### 方案 B: QA 页面修复代码

**文件**: `/site/qa/index.html`

**需要修改的部分** (FAQ 列表):

```javascript
// ❌ 旧代码：硬编码 10 个问题
<div class="accordion-item">
    <h2 class="accordion-header">
        <button class="accordion-button">
            什么是股票杠杆交易？
        </button>
    </h2>
    <div class="accordion-body">
        股票杠杆交易是指投资者向券商借入资金...
    </div>
</div>
// ... 重复 10 次

// ✅ 新代码：从 API 加载
<div id="faqContainer" class="accordion"></div>

<script>
async function loadFAQ() {
    try {
        // 加载 QA 栏目的文章
        const response = await fetch('/api/articles/by-section/qa');
        const articles = await response.json();
        const faqs = Array.isArray(articles) ? articles : [articles];
        
        renderFAQ(faqs);
    } catch (error) {
        console.error('加载 FAQ 失败:', error);
    }
}

function renderFAQ(faqs) {
    const container = document.getElementById('faqContainer');
    container.innerHTML = '';
    
    faqs.forEach((faq, index) => {
        const html = `
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" 
                            type="button" 
                            data-bs-toggle="collapse" 
                            data-bs-target="#faq${index}" 
                            aria-expanded="${index === 0}">
                        ${faq.title}
                    </button>
                </h2>
                <div id="faq${index}" 
                     class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                     data-bs-parent="#faqContainer">
                    <div class="accordion-body">
                        ${faq.content}
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += html;
    });
}

document.addEventListener('DOMContentLoaded', loadFAQ);
</script>
```

---

### 方案 C: 平台页面修复代码

**文件**: `/site/platforms/index.html`

**需要检查的部分**:

```javascript
// 检查平台数据是否完整
async function loadPlatforms() {
    try {
        const response = await fetch('/api/articles?section=platforms');
        const platforms = await response.json();
        const platformList = Array.isArray(platforms) ? platforms : [platforms];
        
        renderPlatforms(platformList);
    } catch (error) {
        console.error('加载平台失败:', error);
    }
}

function renderPlatforms(platforms) {
    const container = document.getElementById('platformsContainer');
    container.innerHTML = '';
    
    platforms.forEach(platform => {
        // ✅ 确保显示所有重要字段
        const html = `
            <div class="card platform-card">
                <div class="card-body">
                    <h3>${platform.name}</h3>
                    
                    <!-- 核心数据 -->
                    <div class="platform-info">
                        <p><strong>最小杠杆:</strong> ${platform.min_leverage}x</p>
                        <p><strong>最大杠杆:</strong> ${platform.max_leverage}x</p>
                        <p><strong>手续费:</strong> ${(platform.commission * 100).toFixed(2)}%</p>
                        <p><strong>账户类型:</strong> ${platform.account_type}</p>
                    </div>
                    
                    <!-- CTA 按钮 -->
                    <a href="${platform.link}" class="btn btn-primary" target="_blank">
                        立即开户
                    </a>
                </div>
            </div>
        `;
        container.innerHTML += html;
    });
}

document.addEventListener('DOMContentLoaded', loadPlatforms);
</script>
```

---

## 🚀 快速实施步骤

### 步骤 1: 备份原文件

```bash
cd /Users/ck/Desktop/Project/trustagency/site
cp wiki/index.html wiki/index.html.bak
cp qa/index.html qa/index.html.bak
cp platforms/index.html platforms/index.html.bak
```

### 步骤 2: 修改文件

根据上面的方案修改每个页面

### 步骤 3: 测试 API

```bash
# 启动后端（如果未启动）
cd /Users/ck/Desktop/Project/trustagency/backend
python -m uvicorn app.main:app --port 8000

# 测试 API
curl http://localhost:8000/api/articles/by-section/qa
```

### 步骤 4: 重新加载前端

```bash
# 前端已在 8001 运行，刷新浏览器即可
# http://localhost:8001/qa/
# http://localhost:8001/wiki/
```

### 步骤 5: 测试功能

- [ ] 搜索是否工作
- [ ] 分类是否工作
- [ ] 所有链接是否有效
- [ ] 页面加载速度如何

---

## ⚠️ 可能的问题和解决方案

### 问题 1: API 返回空数组

**原因**: 数据库中没有相应栏目的文章

**解决方案**:
```bash
# 检查数据库中是否有数据
cd /Users/ck/Desktop/Project/trustagency
sqlite3 trustagency.db "SELECT COUNT(*) FROM articles WHERE section_id = 2;" # 2 = qa

# 如果为 0，重新初始化数据
python -c "from backend.app.database import init_db; init_db()"
```

### 问题 2: 搜索无结果

**原因**: 搜索 API 可能需要调整

**解决方案**:
```javascript
// 添加调试日志
async function searchArticles(keyword) {
    console.log('搜索:', keyword);
    const response = await fetch(`/api/articles/search/by-keyword?keyword=${keyword}`);
    const data = await response.json();
    console.log('搜索结果:', data);
    // ...
}
```

### 问题 3: CORS 错误

**原因**: 前后端跨域问题

**解决方案**: 在后端添加 CORS 配置

---

## ✅ 验收标准

修复完成后检查:

```
[ ] Wiki 页面
    [x] 文章列表正常加载
    [x] 搜索功能工作
    [x] 分类过滤工作
    [x] 所有链接有效

[ ] QA 页面
    [x] FAQ 从数据库加载
    [x] 所有问题正常显示
    [x] 手风琴效果工作

[ ] 平台页面
    [x] 所有字段显示
    [x] CTA 按钮有效
    [x] 平台信息完整

[ ] 整体
    [x] 没有硬编码数据
    [x] 所有页面响应快速
    [x] 错误处理优雅
    [x] 可维护性提高
```

---

## 📞 需要帮助？

如果您需要我直接修改代码，请告诉我:

1. **您是否想我立即修复所有文件？** (是/否)
2. **您想要快速修复还是完整重构？** (快速/完整)
3. **您想先测试 API 吗？** (是/否)

我可以立即为您制作完整的修复代码！ 🔧
