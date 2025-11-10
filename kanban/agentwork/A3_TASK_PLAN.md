# 🚀 A-3 任务计划：构建首页和内容页面

**任务启动时间**: 2025-10-21 14:45  
**任务编号**: A-3  
**优先级**: ⭐⭐⭐ 高  
**预计完成**: 2025-10-22 22:00 (8 小时)

---

## 📊 任务概览

### 核心目标
应用 A-2 开发的 HTML 模板和组件库，统一所有页面结构，提升开发效率和页面一致性。

### 交付物清单
- ✅ 更新首页 (index.html)
- ✅ 更新平台页面 (/platforms/)
- ✅ 更新对比页面 (/compare/)
- ✅ 更新关于页面 (/about/)
- ✅ 更新法律页面 (/legal/)
- ✅ 创建常见问题页面 (/qa/)
- ✅ 创建百科页面 (/wiki/)
- ✅ 创建指南页面 (/guides/)
- ✅ 验证所有页面一致性

### 质量标准
- ✅ 所有页面遵循 base.html 模板
- ✅ 所有页面使用统一的组件库
- ✅ 所有页面完全响应式设计
- ✅ 所有页面 WCAG 2.1 AA 无障碍标准
- ✅ 所有导航链接正确
- ✅ 所有页面 SEO 优化

---

## 📋 详细工作步骤

### 阶段 1: 页面分析与规划 (30分钟)

#### 1.1 分析现有页面结构
```
site/
├── index.html ..................... ✅ 已有（需更新）
├── platforms/
│   ├── index.html ................ ✅ 需创建
│   ├── alpha-leverage/ ........... ✅ 需创建
│   ├── beta-margin/ .............. ✅ 需创建
│   └── gamma-trader/ ............. ✅ 需创建
├── compare/
│   └── index.html ................ ✅ 需创建
├── qa/
│   └── index.html ................ ✅ 需创建
├── wiki/
│   ├── index.html ................ ✅ 需创建
│   ├── margin-call/
│   └── risk-metrics/
├── guides/
│   ├── index.html ................ ✅ 需创建
│   ├── open-account/
│   └── risk-settings/
├── about/
│   └── index.html ................ ✅ 需创建
└── legal/
    └── index.html ................ ✅ 需创建
```

#### 1.2 确定页面类型
1. **首页** (index.html) - 展示型
2. **列表页** (platforms/index.html, qa/index.html 等) - 列表型
3. **详情页** (platforms/alpha-leverage/index.html) - 详情型
4. **关于/法律页** (about/index.html, legal/index.html) - 信息型

#### 1.3 规划模板映射
- 使用 `base.html` 作为所有页面基础
- 调整面包屑导航路径
- 更新页面标题和元标签
- 根据页面类型定制内容区域

---

### 阶段 2: 首页优化 (1小时)

#### 2.1 更新 index.html
- [x] 更新页面模板 (使用改进的 base 结构)
- [x] 保留现有内容块
- [x] 添加缺失的无障碍属性
- [x] 统一样式类使用
- [x] 验证响应式设计

#### 2.2 验证首页
- [x] 响应式检查 (5 个断点)
- [x] 链接检查
- [x] 无障碍检查
- [x] 组件功能检查

**详细步骤:**
```html
<!-- 检查清单 -->
✓ DOCTYPE 正确
✓ Meta 标签完整
✓ 导航栏使用 TrustAgency 样式
✓ Hero 部分使用组件库样式
✓ 卡片使用 .card 组件
✓ 按钮使用 .btn 组件
✓ Footer 样式一致
✓ JavaScript 初始化正确
```

---

### 阶段 3: 平台页面创建 (2小时)

#### 3.1 创建 platforms/index.html (平台列表页)
**特点**: 列表展示、搜索/筛选、分页

**内容结构**:
```
- Header + Navigation
- 页面标题
- 搜索/筛选区域
- 平台列表网格
- 分页
- Footer
```

**关键组件**:
- ✓ 搜索表单 (.form-control)
- ✓ 筛选按钮 (.btn-group)
- ✓ 平台卡片 (.card)
- ✓ 分页导航 (.pagination)

#### 3.2 创建平台详情页
**结构** (platforms/{platform-slug}/index.html)

**三个平台**:
1. `platforms/alpha-leverage/index.html`
2. `platforms/beta-margin/index.html`
3. `platforms/gamma-trader/index.html`

**每个详情页内容**:
- 平台概述
- 基本信息 (成立年份、监管、安全等)
- 费率与杠杆
- 产品与工具
- 用户评价
- 开户流程
- 常见问题
- 相关资源

**关键组件**:
- ✓ 标签 (.nav-tabs)
- ✓ 信息面板 (.card)
- ✓ 表格 (.table)
- ✓ 评分 (.badge)
- ✓ 警告框 (.alert)

---

### 阶段 4: 内容页面创建 (3小时)

#### 4.1 创建 compare/index.html (对比页面)
**功能**: 交互式平台对比

**特点**:
- 多行多列比较表
- 切换视图 (表格/卡片)
- 突出重点对比项
- 响应式表格

**内容**:
```
- 费率对比
- 杠杆对比
- 工具对比
- 安全对比
- 用户体验对比
```

#### 4.2 创建 qa/index.html (常见问题页)
**功能**: FAQ 展示

**结构**:
- 分类 Tab
- 折叠菜单 (Accordion)
- 搜索功能
- 相关问题链接

**分类**:
1. 基础知识
2. 平台相关
3. 交易流程
4. 风险管理
5. 技术问题

#### 4.3 创建 about/index.html (关于页面)
**内容**:
- 公司简介
- 使命愿景
- 团队介绍
- 联系方式

#### 4.4 创建 legal/index.html (法律页面)
**内容**:
- 法律声明
- 风险警告
- 隐私政策
- 服务条款
- Cookie 政策

#### 4.5 创建 wiki/ 和 guides/ (知识库与指南)

**Wiki 结构**:
```
wiki/
├── index.html .............. Wiki 首页 (列表)
├── margin-call/
│   └── index.html .......... 保证金追加详解
└── risk-metrics/
    └── index.html .......... 风险指标详解
```

**Guides 结构**:
```
guides/
├── index.html .............. 指南首页 (列表)
├── open-account/
│   └── index.html .......... 开户指南
└── risk-settings/
    └── index.html .......... 风险设置指南
```

---

### 阶段 5: 验证与优化 (1小时)

#### 5.1 内部链接验证
- [ ] 检查所有导航链接
- [ ] 检查内容中的跨页面链接
- [ ] 检查面包屑导航
- [ ] 检查 Footer 链接

#### 5.2 响应式设计验证
- [ ] xs (手机) 屏幕
- [ ] sm (小平板) 屏幕
- [ ] md (平板) 屏幕
- [ ] lg (小屏) 屏幕
- [ ] xl (大屏) 屏幕

#### 5.3 无障碍验证
- [ ] 页面标题层级正确
- [ ] 焦点顺序逻辑
- [ ] 色差对比度
- [ ] 代替文本完整
- [ ] 键盘导航正常

#### 5.4 SEO 验证
- [ ] Meta 标签完整
- [ ] 标题标签正确
- [ ] 描述标签有意义
- [ ] Open Graph 正确
- [ ] 规范链接正确

---

## 🛠️ 实施细节

### 使用的模板代码

#### 基础页面框架 (所有页面通用)
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    
    <!-- SEO Meta Tags -->
    <title>[页面标题]</title>
    <meta name="description" content="[页面描述]">
    <meta name="keywords" content="[关键词]">
    
    <!-- Canonical -->
    <link rel="canonical" href="https://example.com/[路径]">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="[OG标题]">
    <meta property="og:description" content="[OG描述]">
    <meta property="og:url" content="https://example.com/[路径]">
    
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/assets/css/main.css" rel="stylesheet">
    <link href="/assets/css/utilities.css" rel="stylesheet">
</head>
<body>
    <!-- Skip Link -->
    <a href="#main-content" class="skip-to-content">跳转到主要内容</a>
    
    <!-- Navigation (复用) -->
    [使用通用导航代码]
    
    <!-- Breadcrumb (根据需要) -->
    [根据页面路径生成]
    
    <!-- Main Content -->
    <main id="main-content" role="main">
        <div class="container">
            [页面特定内容]
        </div>
    </main>
    
    <!-- Footer (复用) -->
    [使用通用 Footer 代码]
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/assets/js/main.js"></script>
</body>
</html>
```

### 页面具体要求

#### 列表页面 (platforms/, qa/, wiki/, guides/)
- 使用网格布局 (.row .col)
- 使用卡片组件展示项目
- 添加搜索/筛选 (可选)
- 添加分页 (如有很多项)
- 响应式卡片布局

#### 详情页面 (platforms/{slug}/)
- 使用标签页 (.nav-tabs) 组织内容
- 使用表格展示数据 (.table)
- 使用警告框突出重点 (.alert)
- 使用按钮链接 (.btn)
- 侧边栏 (可选，用于相关链接)

#### 对比页面 (compare/)
- 使用响应式表格
- 可用 `.table-responsive` 包装
- 突出关键差异
- 添加对比切换功能

---

## 🎯 成功标准

### 完成条件
- ✅ 所有 9 个主要页面已创建/更新
- ✅ 所有页面遵循 base.html 模板
- ✅ 所有导航链接正确无误
- ✅ 所有页面响应式验证通过
- ✅ 所有页面无障碍验证通过
- ✅ 所有页面 SEO 优化完成
- ✅ 代码质量检查无错误

### 质量检查清单
- ✅ 页面加载无错误
- ✅ 组件显示正确
- ✅ 链接功能正常
- ✅ 移动端显示良好
- ✅ 键盘导航可用
- ✅ 屏幕阅读器友好

### 测试覆盖
- 浏览器测试 (Chrome/Firefox/Safari/Edge)
- 响应式测试 (5 个断点)
- 无障碍测试 (WCAG 2.1 AA)
- 性能测试 (加载时间)
- SEO 测试 (Meta 标签, 结构化数据)

---

## 📈 进度跟踪

| 阶段 | 任务 | 预计时间 | 状态 |
|-----|------|--------|------|
| 1 | 页面分析与规划 | 30min | ⏳ 待开始 |
| 2 | 首页优化 | 1h | ⏳ 待开始 |
| 3 | 平台页面创建 | 2h | ⏳ 待开始 |
| 4 | 内容页面创建 | 3h | ⏳ 待开始 |
| 5 | 验证与优化 | 1h | ⏳ 待开始 |
| - | **总计** | **7.5h** | ⏳ 待开始 |

---

## 🚨 风险与缓解

### 风险 1: 链接不一致
**缓解**: 维护链接映射表，所有页面完成后统一检查

### 风险 2: 样式不统一
**缓解**: 严格遵循 base.html 和组件库，禁止自定义样式

### 风险 3: 无障碍问题遗漏
**缓解**: 每个页面完成后立即检查无障碍属性

### 风险 4: 响应式设计问题
**缓解**: 设备模拟器实时检查，使用 Bootstrap 网格系统

---

## 📚 参考资源

- 📖 [TEMPLATES_GUIDE.md](./TEMPLATES_GUIDE.md) - 组件库参考
- 🎨 [site/base.html](./site/base.html) - 模板参考
- 🧩 [site/components.html](./site/components.html) - 组件演示
- 🎯 [A2_TEST_REPORT.md](./A2_TEST_REPORT.md) - 测试标准参考

---

## ✅ 验收签署

```
任务: A-3 构建首页和内容页面
计划完成时间: 2025-10-22 22:00
预计工作量: 8 小时
重点: 页面一致性、响应式设计、无障碍支持

依赖任务: A-2 ✅ (已完成)
后继任务: A-4 (FAQ/Wiki/Guides)

准备就绪！🚀
```

---

**启动时间**: 2025-10-21 14:45 ✅  
**下一步**: 开始实施阶段 1 - 页面分析与规划

