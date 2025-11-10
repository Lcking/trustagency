# 方案 B 实施 - 测试和验证

**实施时间**: 2025-11-08  
**状态**: 🟡 实施中 - 待浏览器测试验证  

---

## ✅ 已完成的改造

### 1. 后端数据库 (✅ 完成)

**创建 sections 表**:
```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    requires_platform BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

**默认数据插入**:
- ID 1: 常见问题 (requires_platform=false)
- ID 2: 百科 (requires_platform=false)
- ID 3: 指南 (requires_platform=false)
- ID 4: 验证 (requires_platform=true) ← 需要关联平台

**改造 articles 表**:
- 新增: section_id (FK to sections)
- 新增: category_id (可选，保留 category VARCHAR 向后兼容)
- 改造: platform_id 从 NOT NULL → NULLABLE

### 2. 后端模型 (✅ 完成)

**新建**: `backend/app/models/section.py`
- Section SQLAlchemy 模型
- 与 Article 的关系定义

**改造**: `backend/app/models/article.py`
- 新增: section_id (FK)
- 新增: category_id (可选)
- 改造: platform_id (可选)
- 新增: section 关系

### 3. 后端 API Schema (✅ 完成)

**改造**: `backend/app/schemas/article.py`
- 新增: section_id (必填)
- 改造: platform_id (可选)
- 改造: category (可选，向后兼容)
- 新增: category_id (可选)

### 4. 后端 API 路由 (✅ 完成)

**改造**: `backend/app/routes/articles.py`
- POST /api/articles 添加条件逻辑:
  ```python
  if section.requires_platform:
      验证 platform_id 必填
  else:
      将 platform_id 设为 None
  ```

### 5. 后端服务层 (✅ 完成)

**改造**: `backend/app/services/article_service.py`
- create_article() 方法签名改变
- 移除 platform_id 参数
- 添加 section_id 参数
- 处理可选的 platform_id

### 6. 数据库初始化 (✅ 完成)

**改造**: `backend/app/init_db.py`
- 导入 Section 模型
- 创建 4 个默认栏目
- 初始化后端已执行 ✅

### 7. 前端表单 HTML (✅ 完成)

**改造**: `site/admin/index.html`
- 新增: 栏目选择下拉 (`#articleSection`)
- 新增: 条件显示的平台字段容器 (`#articlePlatformFieldGroup`)
- 改造: 平台字段默认隐藏

### 8. 前端 JavaScript (✅ 完成)

**新增函数**:
- `loadSectionsForArticle()` - 加载栏目列表
- `onArticleSectionChanged()` - 栏目切换时处理逻辑

**改造函数**:
- `showArticleForm()` - 添加栏目加载和联动触发
- `saveArticle()` - 新增 section_id 处理，条件平台验证

---

## 🧪 待测试的功能

### 测试 1: 创建百科文章 (不需要平台)

**步骤**:
1. 打开后台管理界面
2. 点击 "新增文章"
3. 填写:
   - 标题: "Bitcoin 介绍"
   - 栏目: "百科"
   - 分类: "基础概念"
   - 内容: "这是 Bitcoin 的介绍..."
4. **验证**: 平台字段应该**隐藏**不显示 ✓

**预期结果**:
```
✅ 平台字段隐藏
✅ 可以不选平台直接提交
✅ 文章成功创建 (HTTP 201)
✅ 文章列表显示 "Bitcoin 介绍 | 百科 | NULL | 草稿"
```

---

### 测试 2: 创建验证文章 (需要平台)

**步骤**:
1. 点击 "新增文章"
2. 填写:
   - 标题: "Binance 平台审查"
   - 栏目: "验证"
   - 分类: "平台审查"
   - 内容: "Binance 是一个领先的交易平台..."
3. **验证**: 平台字段应该**显示**且为必填 ✓
4. 选择平台: "AlphaLeverage"
5. 点击保存

**预期结果**:
```
✅ 平台字段显示
✅ 平台字段为必填
✅ 不选平台时提示错误
✅ 选择平台后成功创建 (HTTP 201)
✅ 文章列表显示 "Binance 平台审查 | 验证 | 1 (AlphaLeverage) | 草稿"
```

---

### 测试 3: 切换栏目时动态改变

**步骤**:
1. 点击 "新增文章"
2. 栏目选择 "百科" → 平台字段隐藏 ✓
3. 栏目切换为 "验证" → 平台字段显示 ✓
4. 栏目切换为 "指南" → 平台字段隐藏 ✓

**预期结果**:
```
✅ 切换栏目时，平台字段显示/隐藏动态变化
✅ 隐藏时清空已选择的平台值
```

---

### 测试 4: 编辑文章 (保持一致)

**步骤**:
1. 从文章列表中编辑已创建的文章
2. 验证栏目、分类、平台字段预填充正确
3. 修改内容后保存

**预期结果**:
```
✅ 编辑页面正确预填充所有字段
✅ 栏目改变时平台字段正确显示/隐藏
✅ 保存成功 (HTTP 200)
```

---

### 测试 5: 删除文章 (无改变)

**步骤**:
1. 从文章列表删除一篇文章

**预期结果**:
```
✅ 删除功能正常 (HTTP 204)
✅ 文章从列表移除
```

---

### 测试 6: 错误处理

**测试 6a: 验证栏目但不选平台**

**步骤**:
1. 创建文章，选择 "验证" 栏目
2. 不选择平台直接点保存

**预期结果**:
```
❌ 前端提示: "该栏目需要选择平台"
```

**测试 6b: 无效的 section_id**

**预期结果** (后端验证):
```
❌ 后端返回: HTTP 400 "栏目 ID xxx 不存在"
```

---

## 🔍 浏览器测试计划

### 环境准备
- [ ] 后端已启动 ✅
- [ ] 数据库已初始化 ✅
- [ ] 管理员用户已创建 ✅ (admin/admin123)
- [ ] 前端代码已更新 ✅

### 测试流程
1. [ ] 打开 http://localhost:8001/admin/
2. [ ] 登录 (admin/admin123)
3. [ ] 切换到 "文章" 标签
4. [ ] 执行 6 个测试用例
5. [ ] 检查浏览器控制台是否有错误
6. [ ] 检查网络请求是否正确

---

## 📊 预期结果总结

| 测试 | 栏目 | 平台字段 | 平台必填 | 创建状态 |
|------|------|---------|---------|---------|
| Test 1 | 百科 | 隐藏 | 否 | ✅ 201 |
| Test 2 | 验证 | 显示 | 是 | ✅ 201 |
| Test 3 | 指南 | 隐藏 | 否 | - |
| Test 4 | 混合 | 动态 | 动态 | ✅ 200 |
| Test 5 | - | - | - | ✅ 204 |
| Test 6a | 验证 | 显示 | 是 | ❌ 提示 |
| Test 6b | 无效 | - | - | ❌ 400 |

---

## 🎯 完成标准

✅ 所有 8 个实施任务完成  
✅ 后端服务启动正常  
✅ 数据库表创建成功  
✅ 前后端代码改造完毕  

⏳ **待验证**: 浏览器功能测试

---

**下一步**: 打开浏览器进行实际功能测试

