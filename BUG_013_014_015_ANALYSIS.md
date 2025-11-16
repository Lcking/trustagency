# Bug013、bug014、bug015 诊断与修复方案

## 当前状态确认

### 后端API数据
- ✅ 文章API存在：`GET /api/articles` 返回 `[{..., section_name: "常见问题", category_name: "账户问题", ...}]`
- ✅ 文章公开链接路由存在：`GET /article/{slug}` 

### 前端页面结构
- `GET /` → `/site/index.html` (首页)
- `GET /qa/` → `/site/qa/index.html` (FAQ静态页面，内容硬编码)
- `GET /platforms/` → `/site/platforms/index.html` (平台列表，动态加载)
- `GET /compare/` → `/site/compare/index.html` (对比页面，动态加载)
- `GET /article/{slug}` → 后端路由，返回HTML （但目前返回500）

---

## Bug013 详细分析

### 问题描述
后端新增的"账户问题"分类文章对应不上前端页面：
- 后端链接：`http://localhost:8000/article/ce-shi-ce-shi-ce-shi` 
- 前端期望：`http://localhost:8000/qa/`

### 根本原因
**架构不一致问题**：
1. 前端的 `/qa/` 是一个静态HTML页面，内容完全硬编码
2. 后端新增的文章应该动态地集成到 `/qa/` 或创建独立的 `/article/` 动态页面
3. 当前没有任何前端机制将后端文章显示在 `/qa/` 页面中

### 解决方案（三选一）

#### 方案A：将后端文章集成到 `/qa/` 页面（推荐）
- 修改 `/site/qa/index.html` 的动态加载逻辑
- 从后端 API 获取section="常见问题"的文章
- 与现有的硬编码FAQ混合显示

**优点**：
- 保持用户体验一致
- FAQ和用户文章在同一页面
- 无需改变URL结构

#### 方案B：独立的文章页面（当前实现）
- 后端 `/article/{slug}` 返回完整的HTML文章页面
- 前端在合适的地方添加链接指向这些文章

**问题**：
- 当前 `/article/{slug}` 返回500错误
- 需要修复后端Schema标签生成逻辑（已部分修复）

#### 方案C：混合方案
- 保留 `/qa/` 作为综合页面
- 在 `/article/` 下提供完整文章视图
- 两者都支持

---

## Bug014 详细分析

###问题描述
访问 `/article/ce-shi-ce-shi-ce-shi` 返回 500 Internal Server Error

### 根本原因定位
经过代码审查，问题在 `/backend/app/main.py` 的 `view_article` 函数中：

**原问题**（已修复）：
```python
# 这行有操作符优先级问题
"articleSection": article.category_name or article.section.name if article.section else "未分类",
```

**修复后**：
```python
article_section = article.category_name or (article.section.name if article.section else "未分类")
```

### 可能的其他问题
1. BeautifulSoup 导入问题或HTML解析失败
2. JSON序列化时包含非序列化的对象
3. 文件路径或编码问题

### 修复步骤已完成
✅ 已修复main.py中的Schema数据生成逻辑

### 验证方法
重启后端后访问：`http://localhost:8000/article/ce-shi-ce-shi-ce-shi`

预期结果：返回200 OK和完整的HTML文章页面

---

## Bug015 详细分析

### 问题描述
1. 后端百度平台标记为推荐（`is_recommended = True`）
2. 但前端不显示百度作为推荐平台
3. 保存平台时返回500错误

### 根本原因分析

#### 问题1：前端不显示百度为推荐
**原因**：前端可能没有逻辑来显示`is_recommended`字段的平台

**检查点**：
- 首页是否有"推荐平台"部分？
- 这个部分的数据源是什么？

**解决方案**：需要在前端添加`is_recommended`过滤逻辑

#### 问题2：保存平台返回500
**可能原因**：
1. 字段验证失败（某个必需字段为空）
2. 数据库约束冲突（唯一性或外键约束）
3. 文件上传失败（logo_url处理）
4. 权限问题（需要认证但未提供）

**调查步骤**：
1. 检查后端的平台保存端点 `/api/platforms`
2. 查看错误日志中的具体错误信息
3. 检查请求的payload是否有效

---

## 建议的修复优先级

### 立即修复（阻塞功能）
1. ✅ Bug014：修复 `/article/{slug}` 路由的500错误
2. 🔴 Bug015：调查平台保存的500错误

### 后续优化
3. 🟡 Bug013：设计和实现文章与FAQ的集成方案

---

## 测试验证清单

- [ ] 重启后端后访问 `/article/ce-shi-ce-shi-ce-shi` 正常（非500）
- [ ] 文章显示包含正确的标题、内容、分类信息
- [ ] Schema.org标签正确生成（检查源代码）
- [ ] 百度平台的保存操作返回200（非500）
- [ ] 如果百度标记为推荐，在首页显示
- [ ] `/qa/` 页面考虑集成后端文章数据

---

## 文件变更记录

### 已修改
- `/backend/app/main.py` - 修复Schema数据生成逻辑

### 待修改
- `/backend/app/routes/platforms.py` - 可能需要调查保存错误
- `/site/qa/index.html` - 考虑集成后端文章数据
- `/site/index.html` - 可能需要添加推荐平台逻辑

