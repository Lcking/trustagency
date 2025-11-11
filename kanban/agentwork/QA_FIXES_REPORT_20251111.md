# QA问题修复报告 - 2025年11月11日

## 概述
修复了4个用户报告的QA问题，涉及图片编辑功能、文章保存、弹窗大小和输入框宽度。

---

## 修复详情

### 1. 图片对齐功能不可用 ✅
**问题描述**：编辑器中的「图左」、「图中」、「图右」按钮无法使用

**根本原因**：
- `alignImage()` 函数使用了不正确的Tiptap API调用方式
- 原代码尝试使用 `chain()` 和 `updateAttributes()` 的组合，但对图片节点不生效

**修复方案**：
```javascript
// 修复前 (错误):
articleEditor.chain().focus().updateAttributes('image', { style }).run();

// 修复后 (正确):
const { $from } = articleEditor.state.selection;
const pos_node = $from.before($from.depth);
const node = articleEditor.state.doc.nodeAt(pos_node);
if (node && node.type.name === 'image') {
    articleEditor.commands.updateAttributes('image', { style: newStyle.trim() });
}
```

**测试状态**：✅ 已验证，图片对齐功能正常工作

---

### 2. 图片宽度设置不可用 ✅
**问题描述**：「图宽%」按钮无法设置图片宽度

**根本原因**：
- 同样是Tiptap API调用方式不正确
- 宽度百分比值处理有问题

**修复方案**：
```javascript
// 修复前 (错误):
const style = `max-width:100%;height:auto;display:block;width:${n}%;margin:8px auto;`;
articleEditor.chain().focus().updateAttributes('image', { style }).run();

// 修复后 (正确):
const currentAttrs = node.attrs;
let newStyle = (currentAttrs.style || '').replace(/width:\d+%?;?/g, '');
newStyle = `width:${n}%;${newStyle}`;
articleEditor.commands.updateAttributes('image', { 
    style: newStyle.trim() 
});
```

**测试状态**：✅ 已验证，可正确设置图片宽度

---

### 3. 文章保存失败（Internal Server Error） ✅
**问题描述**：点击保存后显示 "保存失败: Internal Server Error"

**根本原因**：
- `ArticleResponse` Pydantic Schema的 `@root_validator` 验证器配置错误
- 原代码在处理SQLAlchemy对象时尝试调用 `.get()` 方法
- Pydantic v2要求 `pre=False` 的验证器必须设置 `skip_on_failure=True`

**错误日志**：
```
AttributeError: 'Article' object has no attribute 'get'
PydanticUserError: If you use `@root_validator` with pre=False you MUST specify `skip_on_failure=True`
```

**修复方案**：
```python
# 修复前 (错误):
@root_validator(pre=True)
def _hydrate_category_name(cls, values):
    category_obj = values.get('category_obj')  # Article对象没有.get()方法
    ...

# 修复后 (正确):
@root_validator(pre=False, skip_on_failure=True)
def _populate_category_name(cls, values):
    if not values.get('category_name'):
        values['category_name'] = values.get('category')
    return values
```

**API测试结果**：
```bash
$ curl -X POST http://127.0.0.1:8001/api/articles \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"测试文章","section_id":1,"category_id":1,...}'

# 响应: 201 Created ✅
{
  "id": 12,
  "title": "测试文章",
  "is_published": false,
  "view_count": 0,
  ...
}
```

**测试状态**：✅ 已验证，文章保存成功

---

### 4. 新增文章弹窗太小 ✅
**问题描述**：新增文章的模态框尺寸太小，希望扩大30%

**修复方案**：
- 调整 `.modal-large` 样式
- 为文章模态框添加 `modal-large` 类

```css
/* 修复前 */
.modal-content.modal-large {
    max-width: 800px;
}

/* 修复后 */
.modal-content.modal-large {
    max-width: 1040px;      /* 800px * 1.3 = 1040px */
    max-height: 95vh;       /* 优化高度 */
}
```

```html
<!-- 修复前 -->
<div class="modal-content">

<!-- 修复后 -->
<div class="modal-content modal-large">
```

**尺寸对比**：
| 参数 | 修复前 | 修复后 | 增幅 |
|------|--------|--------|------|
| 宽度 | 800px | 1040px | +30% |
| 高度 | 90vh | 95vh | +5.6% |

**测试状态**：✅ 已验证，弹窗尺寸增大30%

---

### 5. 标题输入框宽度不统一 ✅
**问题描述**：标题输入框、摘要输入框、内容编辑器宽度不一致，需要协调

**根本原因**：
- 标题被放在了 `form-row`（两列布局）中，但只占用一列
- 摘要是直接在 `form-group`（全宽）中
- 内容编辑器也是全宽
- 这导致三个输入框宽度不对齐

**修复方案**：
```css
/* 新增全宽样式 */
.form-row.full-width {
    grid-template-columns: 1fr;
}
```

```html
<!-- 修复前 -->
<div class="form-row">
    <div class="form-group">
        <input type="text" id="articleTitle" />
    </div>
</div>

<!-- 修复后 -->
<div class="form-row full-width">
    <div class="form-group">
        <input type="text" id="articleTitle" />
    </div>
</div>
```

**布局验证**：
- ✅ 标题宽度 = 内容宽度 = 摘要宽度（都是100%）
- ✅ 栏目和分类保持两列布局
- ✅ 视觉层级清晰

**测试状态**：✅ 已验证，输入框宽度统一

---

## 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `/backend/site/admin/index.html` | 修复图片编辑函数；扩大弹窗；统一输入框宽度 |
| `/backend/app/schemas/article.py` | 修复验证器配置 |

---

## 验证清单

- [x] 图片对齐（左、中、右）功能可用
- [x] 图片宽度设置功能可用
- [x] 文章保存API返回201 Created
- [x] 弹窗宽度增大到1040px（比原来大30%）
- [x] 标题、摘要、内容输入框宽度对齐
- [x] 代码提交到Git

---

## 后端运行状态

- **FastAPI版本**：0.104.1
- **服务器地址**：http://127.0.0.1:8001
- **Admin地址**：http://127.0.0.1:8001/site/admin/
- **数据库状态**：✅ 正常
- **认证系统**：✅ 正常
- **文件上传**：✅ 正常

---

## 建议

1. **长期改进**：考虑将验证器迁移到Pydantic v2的 `@model_validator`
2. **编辑器改进**：考虑为图片编辑添加实时预览
3. **UI改进**：弹窗可考虑支持拖动调整大小
4. **测试覆盖**：建议添加图片编辑功能的单元测试

---

**修复日期**：2025年11月11日  
**Git Commit**：`167f1a9`  
**修复人**：GitHub Copilot
