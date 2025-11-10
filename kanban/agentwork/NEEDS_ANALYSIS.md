# 需求分析和实现计划

## 当前真实状态

### 1️⃣ Emoji 一致性问题
**现状:**
- 菜单项: 只有"⚙️ 系统设置"有 emoji
- 其他菜单项：无 emoji（仪表板、平台管理、文章管理、AI任务、AI配置）
- 仪表板内的"🔧 系统状态"有 emoji，但其他内容标题没有

**需求:** 
- 要么全部加 emoji，要么一个都不加
- 保持整体风格一致

---

### 2️⃣ 栏目管理缺失

**现状:**
- ❌ 没有栏目管理菜单项
- ❌ 没有栏目管理页面
- ❌ 无法新增/编辑/删除栏目
- ❌ 批量生成任务中栏目只能选择，无法管理
- ❌ 文章管理中分类是文本输入，无法预先定义

**问题链:**
1. 在 AI 任务中选择栏目后，分类无法选择（只显示已有文章的分类）
2. 在文章管理新增文章时，分类是文本输入框，无法选择
3. 无法动态新增栏目

**需求:**
- 新增栏目管理菜单
- 实现栏目的 CRUD 操作
- 在栏目中管理分类（每个栏目可以有多个分类）
- 修复分类选择逻辑

---

### 3️⃣ 内容编辑器状态

**现状:**
- ✅ Tiptap 编辑器已集成（见第 948-949 行）
- ✅ 有编辑器样式（第 595-695 行）
- ✅ 有编辑器初始化函数

**问题:**
- 编辑器可能没有完全功能化
- 需要验证是否支持 markdown
- 需要验证图片上传和链接功能

**需求:**
- 评估编辑器的完整性
- 确保支持 markdown
- 确保支持图片上传
- 确保支持链接添加和格式调整

---

## 实现优先级

### 优先级 1（必须）: Emoji 一致性
- 简单快速的修改
- 影响用户界面
- **预计时间:** 15 分钟

### 优先级 2（关键）: 栏目管理
- 影响整个内容管理流程
- 需要新增菜单、页面、API 端点、数据库关系
- **预计时间:** 1-2 小时

### 优先级 3（评估）: 编辑器完整性
- 需要先验证现状
- 可能需要修改或升级
- **预计时间:** 30 分钟评估 + 1-2 小时实现（如需升级）

---

## 技术分析

### 1. Emoji 一致性修改

**选项 A: 移除所有 emoji**
```html
<!-- 从 -->
<li><a href="#" onclick="showSection('settings')" class="menu-item" data-section="settings">⚙️ 系统设置</a></li>
<!-- 改为 -->
<li><a href="#" onclick="showSection('settings')" class="menu-item" data-section="settings">系统设置</a></li>
```

**选项 B: 为所有菜单项添加 emoji**
```html
<li><a href="#" onclick="showSection('dashboard')" class="menu-item active" data-section="dashboard">📊 仪表板</a></li>
<li><a href="#" onclick="showSection('platforms')" class="menu-item" data-section="platforms">🌐 平台管理</a></li>
<li><a href="#" onclick="showSection('articles')" class="menu-item" data-section="articles">📝 文章管理</a></li>
<li><a href="#" onclick="showSection('tasks')" class="menu-item" data-section="tasks">⚙️ AI任务</a></li>
<li><a href="#" onclick="showSection('ai-configs')" class="menu-item" data-section="ai-configs">🤖 AI配置</a></li>
<li><a href="#" onclick="showSection('settings')" class="menu-item" data-section="settings">⚙️ 系统设置</a></li>
```

**建议:** 选项 B（加 emoji）更现代化，符合当前设计风格

---

### 2. 栏目管理实现

**需要做的:**

#### 后端部分
1. ✅ 栏目 API 已存在 (`/api/sections`)，可能需要扩展
2. 创建/获取分类列表 API
3. 为分类添加数据库表和模型

#### 前端部分
1. 新增菜单项: "栏目管理"
2. 新增栏目管理页面，包含:
   - 栏目列表
   - 新增/编辑栏目表单
   - 分类管理（每个栏目的分类列表）
3. 修改文章管理表单:
   - 分类改为下拉菜单（从该栏目的分类列表动态加载）
4. 修改批量生成表单:
   - 分类改为下拉菜单

#### 数据库部分
1. 可能需要创建 `categories` 表或在 `Section` 模型中添加分类字段
2. 建立 Article 与 Category 的关系

---

### 3. 编辑器完整性评估

**需要检查的:**
- [ ] Tiptap 编辑器是否已完全初始化
- [ ] 是否支持所有必需的格式（标题、加粗、斜体等）
- [ ] 是否支持图片上传
- [ ] 是否支持链接插入
- [ ] 是否支持列表、代码块等
- [ ] 是否支持 markdown 导入/导出

**潜在问题:**
- 编辑器可能是骨架代码，需要完成实现
- 可能需要添加 markdown 插件
- 可能需要配置文件上传到服务器

---

## 建议方案

### 立即执行（第 1 步）
1. ✅ 修复 emoji 一致性
2. ✅ 选择全部加 emoji 的方案

### 然后执行（第 2 步）
1. ✅ 实现栏目管理功能
2. ✅ 创建菜单和页面
3. ✅ 修复分类选择逻辑

### 评估并根据需要实现（第 3 步）
1. ⏸️ 检查编辑器现状
2. ⏸️ 根据评估结果决定是否需要升级

---

## 下一步

**请确认:**
1. Emoji 方案偏好？（移除还是全加）
2. 栏目分类的数据结构应该如何？
   - 选项 A: 在 Section 表中添加 categories JSON 字段
   - 选项 B: 创建单独的 Category 表，与 Section 有 1:N 关系
3. 编辑器是否需要完整的 markdown 支持？

我已准备好立即开始实现！
