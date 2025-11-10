# 平台字段条件显示/隐藏 - 技术可行性分析

**问题**: 只有在"验证栏目"时才需要关联平台，但目前无法动态显示/隐藏  
**分析日期**: 2025-11-08  
**分析状态**: ✅ 已完成  

---

## 1. 现状分析

### 1.1 后端数据模型

**文件**: `backend/app/models/article.py`

```python
class Article(Base):
    __tablename__ = "articles"
    
    # 字段关键部分:
    category = Column(String(100), index=True, nullable=False)      # 分类名称 (VARCHAR)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)  # ← 总是必填
```

**问题**: 
- ❌ `platform_id` 定义为 `nullable=False`，无法为 NULL
- ❌ 没有 `section` 或 `section_id` 字段来区分不同类型的文章
- ❌ 无法判断该文章是否属于"验证栏目"

### 1.2 前端表单结构

**文件**: `site/admin/index.html` (第 701-735 行)

```html
<!-- 原始表单字段 -->
<form id="articleForm" onsubmit="saveArticle(event)">
    <input type="text" id="articleTitle" required>
    <select id="articlePlatform" required></select>  <!-- ← 总是显示，总是必填 -->
    <input type="text" id="articleCategory" required>
    <textarea id="articleContent" required></textarea>
    <!-- 其他字段... -->
</form>
```

**问题**:
- ❌ `articlePlatform` 下拉框硬编码为 `required`
- ❌ 没有任何 JavaScript 逻辑来根据栏目改变显示状态
- ❌ 没有栏目选择字段（`articleSection`）

### 1.3 JavaScript 保存逻辑

**文件**: `site/admin/index.html` (第 1236-1310 行)

```javascript
async function saveArticle(e) {
    // ...
    const platformIdStr = document.getElementById('articlePlatform').value;
    if (!platformIdStr) {
        alert('请选择平台');  // ← 总是检查
        return;
    }
    
    const platformId = parseInt(platformIdStr);
    
    const articleData = {
        title: title,
        platform_id: platformId,  // ← 总是发送
        category: category,
        // ...
    };
    // ...
}
```

**问题**:
- ❌ 代码总是验证 `platform_id` 必填
- ❌ 总是在请求体中包含 `platform_id`
- ❌ 无条件逻辑

---

## 2. 为什么目前无法实现动态显示/隐藏

### 根本原因分析

| 层次 | 问题 | 原因 | 影响 |
|------|------|------|------|
| **数据模型** | 无 section 字段 | 旧设计没有栏目维度 | 无法判断何时需要平台 |
| **数据库** | platform_id 非空约束 | 当前架构假设所有文章必须关联平台 | 无法存储无平台文章 |
| **后端 API** | 无条件逻辑 | 路由总是要求 platform_id | 即使传递 null 也会验证失败 |
| **前端** | 无栏目选择 | 无法获知哪个栏目被选中 | 无法决定显示/隐藏 |
| **前端** | 无联动逻辑 | 没有事件监听器 | 即使有栏目字段也无法触发变化 |

### 2.1 技术障碍详解

#### 障碍 1: 缺少栏目维度

**现状**:
```
数据库: articles 表
┌─────────────────┬─────────────────┐
│ category        │ platform_id     │
│ (VARCHAR)       │ (NOT NULL)      │
├─────────────────┼─────────────────┤
│ "guides"        │ 1 (Binance)     │
│ "wiki"          │ 2 (Kraken)      │
│ "review"        │ 3 (Coinbase)    │
└─────────────────┴─────────────────┘
```

**问题**: 
- `category` 是文本，没有结构化定义
- 无法通过 category 名字判断该栏目是否需要平台
- 每次都需要硬编码 if/else 判断

**需要**:
```
数据库: articles 表  →  关联到 sections 表
┌─────────────┬─────────────┬──────────────────┐
│ section_id  │ category_id │ platform_id      │
│ (FK)        │ (FK)        │ (FK, NULLABLE)   │
├─────────────┼─────────────┼──────────────────┤
│ 2 (wiki)    │ 1           │ NULL             │
│ 4 (review)  │ 5           │ 3 (Coinbase)     │
└─────────────┴─────────────┴──────────────────┘

sections 表:
┌────┬──────────────┬──────────────────┐
│ id │ name         │ requires_platform│
├────┼──────────────┼──────────────────┤
│ 1  │ FAQ          │ false            │
│ 2  │ Wiki         │ false            │
│ 3  │ Guide        │ false            │
│ 4  │ Review       │ true             │
└────┴──────────────┴──────────────────┘
```

#### 障碍 2: 数据库非空约束

**现状**:
```sql
-- 现有约束
ALTER TABLE articles ALTER COLUMN platform_id SET NOT NULL;
```

**问题**: 
- 无法为 NULL，所以无法存储"无平台文章"
- 即使前端允许不选平台，后端也会拒绝

**需要**:
```sql
-- 新约束
ALTER TABLE articles ALTER COLUMN platform_id DROP NOT NULL;

-- 添加检查约束
ALTER TABLE articles ADD CONSTRAINT check_platform_requirement
  CHECK (
    -- 如果是验证栏目，必须有平台
    (SELECT requires_platform FROM sections WHERE id=section_id) = true 
    THEN platform_id IS NOT NULL
    ELSE TRUE
  );
```

#### 障碍 3: 后端 API 没有条件逻辑

**现状** (`backend/app/routes/articles.py`):
```python
@router.post("/api/articles")
async def create_article(
    article_data: ArticleCreate,  # 包含 platform_id 必填
    current_user: AdminUser = Depends(get_current_user),
):
    # 直接使用 platform_id，无任何检查
    article = Article(
        title=article_data.title,
        platform_id=article_data.platform_id,  # ← 总是必填
        # ...
    )
```

**问题**:
- `ArticleCreate` Schema 要求 `platform_id: int` (必填)
- 无条件逻辑判断该文章是否真的需要 platform_id
- 错误消息对用户不友好

**需要**:
```python
@router.post("/api/articles")
async def create_article(
    article_data: ArticleCreateV2,  # 包含 section_id, category_id
    current_user: AdminUser = Depends(get_current_user),
):
    # 获取栏目信息
    section = db.query(Section).filter(Section.id == article_data.section_id).first()
    
    # 条件检查
    if section.requires_platform:
        if not article_data.platform_id:
            raise HTTPException(400, "此栏目需要关联平台")
    else:
        # 不需要平台，设为 NULL
        article_data.platform_id = None
    
    article = Article(**article_data.model_dump())
```

#### 障碍 4: 前端没有栏目选择和联动逻辑

**现状**:
```html
<!-- 只有平台选择 -->
<select id="articlePlatform" required></select>

<!-- 没有栏目选择 -->
<!-- 没有栏目→分类联动 -->
<!-- 没有栏目→平台显示/隐藏逻辑 -->
```

**问题**:
- 没有 `<select id="articleSection">` 元素
- 没有 JavaScript 事件监听（`onchange`）
- 没有 show/hide 函数

**需要**:
```html
<!-- 新增栏目选择 -->
<select id="articleSection" onchange="onSectionChanged()"></select>

<!-- 条件显示的平台字段 -->
<div id="platformFieldGroup" style="display: none;">
    <select id="articlePlatform"></select>
</div>

<script>
function onSectionChanged() {
    const sectionId = document.getElementById('articleSection').value;
    
    // 获取栏目信息（包括 requires_platform）
    fetch(`${API_URL}/api/sections/${sectionId}`)
        .then(r => r.json())
        .then(section => {
            const fieldGroup = document.getElementById('platformFieldGroup');
            const field = document.getElementById('articlePlatform');
            
            if (section.requires_platform) {
                fieldGroup.style.display = 'block';
                field.required = true;
            } else {
                fieldGroup.style.display = 'none';
                field.required = false;
                field.value = '';  // 清空选择
            }
        });
}
</script>
```

---

## 3. 实现方案对比

### 方案 A: 最小化方案 (1-2 小时)

**目标**: 快速实现平台字段的条件显示/隐藏，**仅在前端**，不修改后端

**步骤**:

1. 在前端表单添加栏目选择
   ```html
   <select id="articleSection" onchange="onSectionChanged()"></select>
   ```

2. 添加硬编码的栏目配置
   ```javascript
   const SECTIONS = {
       1: { name: "FAQ", requires_platform: false },
       2: { name: "Wiki", requires_platform: false },
       3: { name: "Guide", requires_platform: false },
       4: { name: "Review", requires_platform: true }
   };
   ```

3. 实现切换逻辑
   ```javascript
   function onSectionChanged() {
       const sectionId = document.getElementById('articleSection').value;
       const section = SECTIONS[sectionId];
       const fieldGroup = document.getElementById('platformFieldGroup');
       
       if (section.requires_platform) {
           fieldGroup.style.display = 'block';
       } else {
           fieldGroup.style.display = 'none';
       }
   }
   ```

**优点** ✅:
- 不需要修改数据库
- 不需要修改后端
- 前端改动最小
- 快速实现

**缺点** ❌:
- 栏目配置硬编码在前端
- 数据不一致（前端定义 vs 数据库定义）
- 后端仍然要求 platform_id（数据不一致）
- 即使前端不发送 platform_id，后端也会校验失败
- **无法真正保存无平台文章**
- 技术债务（短期可行，长期不可维护）

**实现复杂度**: ⭐ (非常简单)  
**可维护性**: 👎 (差)  
**数据一致性**: ❌ (无法保证)  

---

### 方案 B: 中等方案 (4-6 小时)

**目标**: 实现完整的条件逻辑，包括**前端 + 后端改造**，但不修改数据库架构

**步骤**:

1. **前端**: 同方案 A，添加栏目选择和条件显示

2. **后端 Schema 改造** (`backend/app/schemas/article.py`)
   ```python
   class ArticleCreateV2(BaseModel):
       title: str
       section_id: int  # 新增
       category_id: int  # 改为 FK 而非 VARCHAR
       content: str
       platform_id: Optional[int] = None  # ← 改为可选
       # ... 其他字段
   ```

3. **后端 Route 改造** (`backend/app/routes/articles.py`)
   ```python
   @router.post("/api/articles")
   async def create_article(
       article_data: ArticleCreateV2,
       current_user: AdminUser = Depends(get_current_user),
   ):
       # 根据 section_id 判断是否需要 platform_id
       section = db.query(Section).filter(...).first()
       
       if section.requires_platform and not article_data.platform_id:
           raise HTTPException(400, "此栏目需要关联平台")
       
       if not section.requires_platform:
           article_data.platform_id = None
       
       # 创建文章...
   ```

4. **后端 Model 改造** (需要数据库迁移)
   ```python
   class Article(Base):
       # 新增字段
       section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
       # 改造现有字段
       category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
       # 改为可选
       platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=True)
   ```

5. **数据库迁移**
   - 创建 `sections` 表
   - 修改 `articles` 表结构
   - 数据迁移脚本

**优点** ✅:
- 前后端一致
- 数据完整性有保证
- 可以真正保存无平台文章
- 为后续的完整重构做准备

**缺点** ❌:
- 需要修改数据库表结构
- 需要数据迁移
- 实现复杂度中等
- 可能影响现有数据

**实现复杂度**: ⭐⭐⭐ (中等)  
**可维护性**: 👍 (好)  
**数据一致性**: ✅ (有保证)  

---

### 方案 C: 完整重构方案 (12-16 小时)

**目标**: 实现完整的栏目→分类→文章三层结构，包括 AI 任务系统完整改造

**这就是 `SECTION_CATEGORY_REFACTOR_PLAN.md` 中的 A-15 系列任务**

**步骤** (10 个主要任务):
1. A-15.1: 数据库完整设计
2. A-15.2: 栏目管理 API
3. A-15.3: 分类管理 API
4. A-15.4: 文章 API 改造
5. A-15.5: AI 任务 API 完整重构
6. A-15.6-A-15.9: 前端 UI 完整重构
7. A-15.10: 集成测试

**优点** ✅:
- 完全解决问题
- 架构清晰
- 扩展性好
- 为未来的功能准备

**缺点** ❌:
- 实现工作量大
- 涉及面广（前后端数据库）
- 需要充分测试
- 可能有较多风险

**实现复杂度**: ⭐⭐⭐⭐⭐ (复杂)  
**可维护性**: 👍👍👍 (优秀)  
**数据一致性**: ✅✅ (非常好)  

---

## 4. 建议方案

### 推荐: **方案 B (中等方案)** + **计划后续 A-15 重构**

**理由**:

1. **平衡点**: 
   - ✅ 短期内快速实现需求 (4-6 小时)
   - ✅ 建立正确的数据模型基础
   - ✅ 为后续完整重构做准备
   - ✅ 不过度工程化

2. **实现顺序**:
   - **第 1 阶段** (今天): 方案 B 实现
     - 创建 `sections` 表 (4 条记录)
     - 改造 `articles` 表 (新增字段)
     - 改造后端 API
     - 改造前端表单
     - 完成条件显示/隐藏功能
   
   - **第 2 阶段** (未来): 方案 C 完整重构 (A-15)
     - 基于方案 B 的基础继续
     - 添加 `categories` 表分层
     - 完整的 UI 改造
     - AI 任务系统重构

3. **风险控制**:
   - 方案 B 修改相对独立
   - 可以逐步迁移数据
   - 有回滚空间
   - 不影响现有功能（兼容处理）

---

## 5. 如果暂时搁置该功能...

### 现状保持

**前端**: 保持平台字段总是显示和必填  
**后端**: 保持 platform_id 总是必填  
**数据**: 所有文章都必须关联平台  

### 后续激活时的工作

1. **立即要做**: (方案 B)
   - [ ] 创建 `sections` 表 (基础数据)
   - [ ] 添加 `section_id` 字段到 `articles` 表
   - [ ] 改造后端 API 支持条件逻辑
   - [ ] 改造前端表单添加栏目选择
   - [ ] 实现 JavaScript 联动逻辑

2. **后续可以做**: (方案 C)
   - [ ] 完整的栏目/分类系统
   - [ ] AI 任务系统完整重构
   - [ ] 数据迁移工具

---

## 6. 技术栈变更概览

### 如果实施方案 B

#### 后端新增/改造文件:

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/models/section.py` | 新建 | Section 模型 |
| `backend/app/models/article.py` | 改造 | 新增 section_id, category_id, 改造 platform_id |
| `backend/app/schemas/article.py` | 改造 | ArticleCreateV2 (section_id, category_id) |
| `backend/app/routes/articles.py` | 改造 | 添加条件逻辑 |
| `backend/app/services/article_service.py` | 改造 | 条件创建逻辑 |
| `backend/migrations/001_add_sections.py` | 新建 | 数据库迁移脚本 |

#### 前端改造文件:

| 文件 | 改造内容 |
|------|---------|
| `site/admin/index.html` | 添加栏目选择, 添加 onSectionChanged() 函数, 条件显示平台字段 |

#### 数据库变更:

| 操作 | SQL |
|------|-----|
| 新建 sections 表 | `CREATE TABLE sections (...)` |
| 修改 articles 表 | `ALTER TABLE articles ADD COLUMN section_id INT` |
| 修改 articles 表 | `ALTER TABLE articles ALTER COLUMN platform_id DROP NOT NULL` |
| 修改 articles 表 | `ALTER TABLE articles ADD COLUMN category_id INT` |

---

## 7. 总结决策表

| 方案 | 时间 | 复杂度 | 一致性 | 推荐 | 备注 |
|------|------|--------|--------|------|------|
| **A** (最小化) | 1-2h | ⭐ | ❌ | 不推荐 | 快但不稳定 |
| **B** (中等) | 4-6h | ⭐⭐⭐ | ✅ | ✅ **推荐** | 平衡点 |
| **C** (完整) | 12-16h | ⭐⭐⭐⭐⭐ | ✅✅ | 稍后做 | 完整方案 |

---

**建议决策**: 
1. 👍 **立即推进**: 方案 B (中等方案)，预计 4-6 小时
2. 📅 **后续规划**: 方案 C (完整重构 A-15)，安排在方案 B 完成后

**下一步**: 等待确认是否要推进方案 B，还是暂时搁置。

