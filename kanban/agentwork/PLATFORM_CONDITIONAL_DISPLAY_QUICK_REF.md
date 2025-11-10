# 平台字段条件显示 - 快速参考

## 问题

❓ 只有在"验证栏目"时才需要关联平台，但目前无法动态显示/隐藏

---

## 答案

### 为什么无法实现？

缺少 4 个关键部分:

| 部分 | 缺失 | 后果 |
|------|------|------|
| 📊 数据模型 | 无 section (栏目) | 无法区分验证 vs 其他 |
| 🗄️ 数据库 | platform_id NOT NULL | 无法存储无平台文章 |
| 🔧 后端 | 无条件逻辑 | API 总是要求 platform_id |
| 🎨 前端 | 无栏目字段 + 无联动 | 无法动态改变显示 |

---

## 解决方案

### ⭐ 推荐: 方案 B (中等方案)

**工作**: 4-6 小时  
**难度**: 中等  
**收益**: 快速 + 正确 + 为后续准备  

**做什么**:
1. 创建 `sections` 表 (4 条记录)
2. 改造 `articles` 表 (新增字段)
3. 改造后端 API (添加条件逻辑)
4. 改造前端表单 (栏目选择 + JavaScript 联动)

**效果**:
```
百科栏目 → 平台字段隐藏 ✓
验证栏目 → 平台字段显示 + 必填 ✓
数据正确保存 ✓
```

### 其他方案

| 方案 | 时间 | 优点 | 缺点 | 推荐 |
|------|------|------|------|------|
| A (最小化) | 1-2h | 快速 | 数据不一致 | ❌ 否 |
| **B (中等)** | **4-6h** | **快速+正确** | 中等复杂度 | **✅ 是** |
| C (完整) | 12-16h | 架构最优 | 工作量大 | 📅 后续 |

---

## 决策流程

```
是否实现平台条件显示?
│
├─ 是 → 选择方案 B (4-6h)
│       └─ 立即开始
│
└─ 否 → 暂时搁置
        └─ 保持现状: 平台字段总是显示
```

---

## 方案 B 实现步骤

### Step 1: 数据库 (30 min)

```sql
-- 创建 sections 表
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    requires_platform BOOLEAN DEFAULT FALSE
);

-- 插入 4 个栏目
INSERT INTO sections VALUES
    (1, 'FAQ', FALSE),
    (2, 'Wiki', FALSE),
    (3, 'Guide', FALSE),
    (4, 'Review', TRUE);

-- 改造 articles 表
ALTER TABLE articles ADD COLUMN section_id INTEGER;
ALTER TABLE articles ADD COLUMN category_id INTEGER;
ALTER TABLE articles ALTER COLUMN platform_id DROP NOT NULL;
```

### Step 2: 后端 API (1-1.5 hours)

```python
# backend/app/schemas/article.py
class ArticleCreateV2(BaseModel):
    title: str
    section_id: int  # 新增
    category_id: int  # 新增
    content: str
    platform_id: Optional[int] = None  # 改为可选

# backend/app/routes/articles.py
@router.post("/api/articles")
async def create_article(article_data: ArticleCreateV2, ...):
    section = db.query(Section).get(article_data.section_id)
    
    # 条件逻辑
    if section.requires_platform and not article_data.platform_id:
        raise HTTPException(400, "此栏目需要关联平台")
    
    if not section.requires_platform:
        article_data.platform_id = None
    
    # 创建文章...
```

### Step 3: 前端 UI (1-1.5 hours)

```html
<!-- 添加栏目选择 -->
<select id="articleSection" onchange="onSectionChanged()"></select>

<!-- 条件显示的平台字段 -->
<div id="platformFieldGroup" style="display:none;">
    <select id="articlePlatform"></select>
</div>

<script>
function onSectionChanged() {
    const sectionId = document.getElementById('articleSection').value;
    
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
                field.value = '';
            }
        });
}
</script>
```

### Step 4: 测试 (1 hour)

- [ ] 创建百科文章（无平台）✓
- [ ] 创建验证文章（有平台）✓
- [ ] 切换栏目时平台字段正确显示/隐藏 ✓
- [ ] 编辑、删除正常 ✓

---

## 时间规划

| 任务 | 时间 | 状态 |
|------|------|------|
| 数据库改造 | 30min | 📋 |
| 后端改造 | 1-1.5h | 📋 |
| 前端改造 | 1-1.5h | 📋 |
| 测试 | 1h | 📋 |
| **合计** | **4-5h** | 📋 |

---

## 下一步

**选择 1**: 👍 立即开始方案 B
```
我会:
1. 改造数据库
2. 改造后端 API
3. 改造前端 UI
4. 进行测试

预计 4-6 小时完成
```

**选择 2**: 📅 暂时搁置
```
我会:
1. 保持现状
2. 记录需求
3. 后续激活时按方案 B 推进
```

**选择 3**: 📘 查看详细文档
```
查看:
- PLATFORM_CONDITIONAL_DISPLAY_ANALYSIS.md (完整分析)
- PLATFORM_CONDITIONAL_DISPLAY_DECISION.md (决策说明)
- PLATFORM_CONDITIONAL_DISPLAY_DECISION_TREE.md (决策树)
```

---

**等待您的决策！** 🚀

