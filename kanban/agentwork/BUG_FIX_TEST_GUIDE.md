# 🧪 Bug 修复功能测试指南

## 📋 测试准备

### 环境确认
✅ 后端已启动：http://localhost:8001
✅ 虚拟环境：使用 backend/venv/
✅ 数据库：已初始化，包含默认数据

### 登录凭证
- 用户名：`admin`
- 密码：`newpassword123`
- 访问地址：http://localhost:8001/admin/

---

## 🔍 Bug 测试

### Bug_005: 新增栏目弹窗不居中

**问题描述**：新增栏目编辑弹窗显示在左边而非居中

**测试步骤**：
1. 打开 Admin 后台：http://localhost:8001/admin/
2. 在左侧栏找到 "内容管理" → "栏目管理"
3. 点击 "新增栏目" 按钮
4. 观察弹窗位置

**预期结果**：
- ✅ 弹窗应该**居中显示**在屏幕中央
- ✅ 弹窗背景半透明（遮挡底层）
- ✅ 弹窗包含表单字段：名称、Slug、描述等

**技术细节**：
- 修复方式：使用 CSS class `.modal.active` 而非直接 `style.display`
- 文件位置：backend/site/admin/index.html (lines 1512-1519)
- 相关函数：`showSectionForm()`, `closeSectionModal()`

**验证代码** (F12 Console)：
```javascript
// 点击"新增栏目"后在控制台检查
let modal = document.querySelector('.modal.active');
console.log('Modal存在:', !!modal);
console.log('Modal类名:', modal?.className);
console.log('Display:', window.getComputedStyle(modal)?.display);
```

---

### Bug_006: 分类列表加载失败

**问题描述**：点击栏目展开箭头时，分类列表加载失败，JSON解析错误

**错误信息**：
```
Unexpected token 'I', "Internal S"... at position 0
```

**测试步骤**：
1. 登录 Admin 后台
2. 找到 "常见问题" (FAQ) 栏目
3. 点击栏目右侧的**展开箭头** ↓
4. 观察分类列表是否加载

**预期结果**：
- ✅ 分类列表应该正常加载并显示
- ✅ 显示 5 个分类：基础知识、账户管理、交易问题、安全、其他
- ✅ 浏览器 Console 无错误信息

**技术细节**：
- 修复方式：添加 HTTP 响应状态检查，避免解析错误HTML
- 文件位置：backend/site/admin/index.html (lines 1465-1513)
- 相关函数：`loadSectionCategoriesWithArticles()`
- 改进点：
  ```javascript
  if (!articlesResponse.ok) throw Error(`HTTP ${articlesResponse.status}`);
  let articlesData = Array.isArray(...) ? ... : ...;
  ```

**验证代码** (F12 Console)：
```javascript
// 点击展开后检查
let categories = document.querySelectorAll('.category-item');
console.log('分类数量:', categories.length);
console.log('分类列表:', Array.from(categories).map(c => c.textContent));
```

---

### Bug_007: 编辑器加载失败

**问题描述**：创建新文章时，编辑器显示"加载失败，已切换到纯文本模式"

**错误原因**：Tiptap CDN 库未正确加载到全局作用域

**测试步骤**：
1. 登录 Admin 后台
2. 进入 "内容管理" → "文章管理"
3. 点击 "新增文章" 按钮
4. 观察编辑器加载状态

**预期结果**：
- ✅ 编辑器应该正常加载（不显示错误消息）
- ✅ 工具栏应该显示：Bold、Italic、Heading、Link、Image 等按钮
- ✅ 编辑区域应该可以输入文本
- ✅ F12 Console 显示：`[Tiptap] Editor initialized successfully`

**技术细节**：
- 修复方式：
  1. 改用 jsDelivr CDN（UMD 格式）替换 unpkg
  2. 重写编辑器初始化函数，多层fallback
  3. 改进错误日志和诊断
- 文件位置：backend/site/admin/index.html
  - CDN 脚本：lines 785-792
  - 初始化函数：lines 2843-2945
- CDN 更新：
  ```html
  <!-- 旧 -->
  <script src="https://unpkg.com/@tiptap/core@2.0.0"></script>
  
  <!-- 新 -->
  <script src="https://cdn.jsdelivr.net/npm/@tiptap/core@2.0.0/dist/index.umd.js"></script>
  ```

**验证代码** (F12 Console)：
```javascript
// 创建新文章后检查
TiptapDiagnostics.check();

// 预期输出示例：
// {
//   "Tiptap加载": true,
//   "StartKit": true,
//   "编辑器容器": true,
//   "DOM就绪": true,
//   "总体状态": "✅ 正常"
// }

// 或检查编辑器对象
console.log('编辑器存在:', !!window.TiptapEditor);
console.log('Tiptap库:', window.Tiptap);
```

---

### Bug_008: 平台URL显示为null

**问题描述**：在平台管理页面，所有平台的 URL 显示为 null 而非网址

**测试步骤**：
1. 登录 Admin 后台
2. 进入 "平台管理"
3. 查看平台列表

**预期结果**：
- ✅ AlphaLeverage 应显示：https://alphaleverage.com
- ✅ BetaMargin 应显示：https://betamargin.com
- ✅ GammaTrader 应显示其对应的网址
- ✅ 不应该显示 null 或 undefined

**技术细节**：
- 根本原因：Platform 模型的字段是 `website_url`，但数据库中没有值
- 修复方式：更新 init_db.py，为默认平台添加 `website_url` 字段
- 文件位置：backend/app/init_db.py (lines 115-140)
- 修复代码：
  ```python
  platforms = [
      {
          "name": "AlphaLeverage",
          "website_url": "https://alphaleverage.com",  # ← 添加了这行
          "rating": 4.8,
          # ... 其他字段
      },
      # ...
  ]
  ```

**验证代码** (F12 Console)：
```javascript
// 检查页面上的 URL 显示
let urlCells = document.querySelectorAll('table tbody tr td:nth-child(2)');
console.log('平台 URLs:', Array.from(urlCells).map(cell => cell.textContent));

// 或检查API响应
fetch('http://localhost:8001/api/platforms')
  .then(r => r.json())
  .then(data => {
    console.log('平台数据:', data);
    data.forEach(p => console.log(`${p.name}: ${p.website_url}`));
  });
```

---

## 📊 测试清单

| Bug | 测试步骤 | 预期结果 | 实际结果 | 状态 |
|-----|--------|--------|--------|------|
| bug_005 | 点击新增栏目 | 弹窗居中显示 | | ⏳ |
| bug_006 | 展开栏目查看分类 | 分类列表加载成功 | | ⏳ |
| bug_007 | 创建新文章 | 编辑器正常加载，工具栏可见 | | ⏳ |
| bug_008 | 查看平台管理 | URL 显示为网址，非 null | | ⏳ |

---

## 🛠️ 故障排除

### 问题：无法访问 Admin 页面

```bash
# 检查后端是否运行
curl -s -I http://localhost:8001/admin/

# 预期：HTTP/1.1 200 OK
```

### 问题：编辑器仍显示加载失败

```javascript
// F12 Console 运行以诊断
TiptapDiagnostics.check();

// 或检查CDN是否加载
window.Tiptap ? console.log('✅ Tiptap库已加载') : console.log('❌ Tiptap库未加载');
```

### 问题：平台 URL 仍显示 null

```bash
# 重新初始化数据库
cd /Users/ck/Desktop/Project/trustagency/backend
./venv/bin/python -c "import sys; sys.path.insert(0, '.'); from app.init_db import init_db; init_db()"

# 然后重启后端
```

---

## 📝 测试记录

请将测试结果记录在下表：

### 测试执行记录

**测试日期**：___________
**测试人员**：___________

#### Bug_005 测试
- [ ] 弹窗出现
- [ ] 弹窗居中
- [ ] 表单可用
- [ ] 备注：___________

#### Bug_006 测试
- [ ] 展开成功
- [ ] 分类列表显示
- [ ] 无 Console 错误
- [ ] 备注：___________

#### Bug_007 测试
- [ ] 编辑器加载
- [ ] 工具栏可见
- [ ] 可以输入文本
- [ ] 无错误消息
- [ ] 备注：___________

#### Bug_008 测试
- [ ] URL 显示为网址
- [ ] 非 null/undefined
- [ ] 所有平台都有 URL
- [ ] 备注：___________

---

**生成时间**：2025-11-09
**文档版本**：1.0
