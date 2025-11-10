# Tiptap编辑器集成实现指南

## 第1阶段：基础集成 + 官方样式 (1天)

### 方案A: CDN方式（推荐 - 最快）

由于项目是Vanilla JS + CDN加载，**不需要npm构建**，直接用CDN引入Tiptap。

#### 步骤1: 在HTML头部添加CDN链接

```html
<!-- Tiptap 核心库和扩展 (CDN) -->
<link rel="stylesheet" href="https://unpkg.com/tiptap-default-styles@1.0.0/style.css">
<script src="https://unpkg.com/prosemirror-state"></script>
<script src="https://unpkg.com/prosemirror-view"></script>
<script src="https://unpkg.com/prosemirror-model"></script>
<script src="https://unpkg.com/prosemirror-transform"></script>
<script src="https://unpkg.com/prosemirror-collab"></script>
<script src="https://unpkg.com/prosemirror-commands"></script>
<script src="https://unpkg.com/prosemirror-schema-list"></script>
<script src="https://unpkg.com/@lezer/common"></script>
<script src="https://unpkg.com/@lezer/lr"></script>
<script src="https://unpkg.com/w3c-keyname"></script>
<script src="https://unpkg.com/tiptap/dist/tiptap.umd.js"></script>
<script src="https://unpkg.com/@tiptap/starter-kit/dist/starter-kit.umd.js"></script>
<script src="https://unpkg.com/@tiptap/extension-markdown/dist/markdown.umd.js"></script>
<script src="https://unpkg.com/@tiptap/extension-image/dist/image.umd.js"></script>
<script src="https://unpkg.com/@tiptap/extension-link/dist/link.umd.js"></script>
```

#### 步骤2: 创建编辑器容器

在文章管理表单中，**替换** `<textarea id="articleContent">` 为：

```html
<!-- 编辑器工具栏 -->
<div id="articleEditorToolbar" class="editor-toolbar">
    <!-- 工具栏按钮会通过JavaScript生成 -->
</div>

<!-- 编辑器容器 -->
<div id="articleEditor" class="editor-container"></div>

<!-- 隐藏字段存储HTML内容 -->
<input type="hidden" id="articleContent" />
```

#### 步骤3: 添加编辑器样式

在 `<style>` 标签中添加：

```css
/* Tiptap 编辑器样式 */
.editor-container {
    border: 1px solid #ddd;
    border-radius: 4px;
    min-height: 300px;
    padding: 10px;
    background: white;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.6;
}

.editor-toolbar {
    display: flex;
    gap: 5px;
    padding: 10px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    flex-wrap: wrap;
}

.editor-toolbar button {
    padding: 6px 12px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 3px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
}

.editor-toolbar button:hover {
    background: #f0f0f0;
    border-color: #999;
}

.editor-toolbar button.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.ProseMirror {
    outline: none;
    min-height: 280px;
}

.ProseMirror h1 {
    font-size: 24px;
    font-weight: bold;
    margin: 0.5em 0;
}

.ProseMirror h2 {
    font-size: 20px;
    font-weight: bold;
    margin: 0.4em 0;
}

.ProseMirror h3 {
    font-size: 18px;
    font-weight: bold;
    margin: 0.3em 0;
}

.ProseMirror h4,
.ProseMirror h5,
.ProseMirror h6 {
    font-size: 16px;
    font-weight: bold;
    margin: 0.3em 0;
}

.ProseMirror p {
    margin: 0.5em 0;
}

.ProseMirror ul,
.ProseMirror ol {
    padding-left: 2em;
    margin: 0.5em 0;
}

.ProseMirror li {
    margin: 0.25em 0;
}

.ProseMirror blockquote {
    border-left: 4px solid #ddd;
    padding-left: 1em;
    margin: 0.5em 0;
    color: #666;
}

.ProseMirror code {
    background: #f4f4f4;
    padding: 2px 4px;
    border-radius: 2px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}

.ProseMirror pre {
    background: #f4f4f4;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 0.5em 0;
}

.ProseMirror pre code {
    background: none;
    padding: 0;
    border-radius: 0;
}

.ProseMirror img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 0.5em 0;
}

.ProseMirror a {
    color: #667eea;
    text-decoration: none;
    cursor: pointer;
}

.ProseMirror a:hover {
    text-decoration: underline;
}
```

#### 步骤4: 编写编辑器初始化脚本

在HTML的 `<script>` 部分中添加以下代码（在加载完Tiptap CDN后）：

```javascript
// 全局编辑器实例
let articleEditor = null;

// 初始化编辑器
function initArticleEditor(initialContent = '') {
    const container = document.getElementById('articleEditor');
    
    if (!container) return; // 如果容器不存在则跳过
    
    // 清空容器
    container.innerHTML = '';
    
    // 创建编辑器实例
    articleEditor = new window.Tiptap.Editor({
        element: container,
        extensions: [
            window.TiptapStarterKit.default,  // 基础功能包
            window.TiptapExtensionMarkdown.default,  // Markdown支持
            window.TiptapExtensionImage.default.configure({
                HTMLAttributes: {
                    class: 'editor-image',
                }
            }),
            window.TiptapExtensionLink.default.configure({
                openOnClick: false,
            }),
        ],
        content: initialContent || '<p>开始编辑文章内容...</p>',
    });
    
    // 生成工具栏按钮
    renderEditorToolbar();
}

// 渲染工具栏
function renderEditorToolbar() {
    if (!articleEditor) return;
    
    const toolbar = document.getElementById('articleEditorToolbar');
    if (!toolbar) return;
    
    toolbar.innerHTML = `
        <!-- 文本格式 -->
        <button onclick="toggleBold()" title="粗体 (Ctrl+B)">B</button>
        <button onclick="toggleItalic()" title="斜体 (Ctrl+I)">I</button>
        <button onclick="toggleStrike()" title="删除线">S</button>
        <button onclick="toggleCode()" title="代码">Code</button>
        
        <!-- 分隔符 -->
        <span style="margin: 0 5px; border-right: 1px solid #ccc;"></span>
        
        <!-- 列表 -->
        <button onclick="toggleBulletList()" title="无序列表">• 列表</button>
        <button onclick="toggleOrderedList()" title="有序列表">1. 列表</button>
        
        <!-- 分隔符 -->
        <span style="margin: 0 5px; border-right: 1px solid #ccc;"></span>
        
        <!-- 标题 -->
        <button onclick="setHeading(1)" title="标题1">H1</button>
        <button onclick="setHeading(2)" title="标题2">H2</button>
        <button onclick="setHeading(3)" title="标题3">H3</button>
        
        <!-- 分隔符 -->
        <span style="margin: 0 5px; border-right: 1px solid #ccc;"></span>
        
        <!-- 其他 -->
        <button onclick="toggleBlockquote()" title="引用">引用</button>
        <button onclick="insertCodeBlock()" title="代码块">代码块</button>
        <button onclick="insertImage()" title="插入图片">图片</button>
        <button onclick="insertLink()" title="插入链接">链接</button>
        
        <!-- 分隔符 -->
        <span style="margin: 0 5px; border-right: 1px solid #ccc;"></span>
        
        <!-- 撤销重做 -->
        <button onclick="undoEdit()" title="撤销">↶ 撤销</button>
        <button onclick="redoEdit()" title="重做">↷ 重做</button>
    `;
}

// 工具栏按钮处理函数
function toggleBold() {
    if (articleEditor) articleEditor.chain().focus().toggleBold().run();
}

function toggleItalic() {
    if (articleEditor) articleEditor.chain().focus().toggleItalic().run();
}

function toggleStrike() {
    if (articleEditor) articleEditor.chain().focus().toggleStrike().run();
}

function toggleCode() {
    if (articleEditor) articleEditor.chain().focus().toggleCode().run();
}

function toggleBulletList() {
    if (articleEditor) articleEditor.chain().focus().toggleBulletList().run();
}

function toggleOrderedList() {
    if (articleEditor) articleEditor.chain().focus().toggleOrderedList().run();
}

function setHeading(level) {
    if (articleEditor) articleEditor.chain().focus().toggleHeading({ level }).run();
}

function toggleBlockquote() {
    if (articleEditor) articleEditor.chain().focus().toggleBlockquote().run();
}

function insertCodeBlock() {
    if (articleEditor) articleEditor.chain().focus().toggleCodeBlock().run();
}

function insertImage() {
    const url = prompt('输入图片URL:');
    if (url && articleEditor) {
        articleEditor.chain().focus().setImage({ src: url }).run();
    }
}

function insertLink() {
    const url = prompt('输入链接URL:');
    if (url && articleEditor) {
        articleEditor.chain().focus().setLink({ href: url }).run();
    }
}

function undoEdit() {
    if (articleEditor) articleEditor.chain().focus().undo().run();
}

function redoEdit() {
    if (articleEditor) articleEditor.chain().focus().redo().run();
}

// 获取编辑器内容（HTML格式）
function getEditorContent() {
    if (!articleEditor) return '';
    return articleEditor.getHTML();
}

// 设置编辑器内容
function setEditorContent(html) {
    if (!articleEditor) {
        initArticleEditor(html);
    } else {
        articleEditor.commands.setContent(html);
    }
}

// 清空编辑器
function clearEditor() {
    if (articleEditor) {
        articleEditor.commands.clearContent();
    }
}
```

#### 步骤5: 修改文章表单提交

修改 `saveArticle` 函数，将编辑器内容同步到隐藏字段：

```javascript
async function saveArticle(event) {
    event.preventDefault();
    
    // 同步编辑器内容到隐藏字段
    const articleContent = document.getElementById('articleContent');
    if (articleEditor) {
        articleContent.value = articleEditor.getHTML();
    }
    
    const formData = new FormData(document.getElementById('articleForm'));
    
    // ... 其他代码保持不变
}
```

#### 步骤6: 加载文章时初始化编辑器

修改 `showArticleForm` 函数：

```javascript
async function showArticleForm(articleId) {
    if (articleId) {
        // 编辑现有文章
        const response = await fetch(`${API_URL}/api/articles/${articleId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const article = await response.json();
            
            // 填充表单
            document.getElementById('articleTitle').value = article.title;
            document.getElementById('articleCategory').value = article.category;
            document.getElementById('articleSummary').value = article.summary || '';
            
            // 初始化编辑器并加载内容
            initArticleEditor(article.content);
            
            document.getElementById('articlePublished').checked = article.is_published;
            document.getElementById('articleFeatured').checked = article.is_featured;
            
            document.getElementById('articleForm').onsubmit = (e) => saveArticle(e, articleId);
        }
    } else {
        // 新建文章
        document.getElementById('articleForm').reset();
        initArticleEditor('');
        document.getElementById('articleForm').onsubmit = (e) => saveArticle(e);
    }
    
    document.getElementById('articleModal').style.display = 'flex';
}
```

---

## 第2阶段：图片上传 (1天)

### 后端实现

创建图片上传API端点：

**文件**: `/backend/app/routes/upload.py`

```python
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api", tags=["upload"])

# 上传目录
UPLOAD_DIR = "static/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    上传图片
    仅允许已认证用户上传
    """
    
    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 检查文件大小
    file_size = 0
    file_content = b""
    async for chunk in file.file:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="文件过大，最大允许5MB")
        file_content += chunk
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 返回文件URL
    url = f"/static/uploads/images/{filename}"
    
    return {
        "url": url,
        "filename": filename,
        "size": file_size
    }
```

### 前端集成

修改 `insertImage` 函数支持上传：

```javascript
async function insertImage() {
    // 创建文件输入
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // 显示上传提示
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '上传中...';
        btn.disabled = true;
        
        try {
            // 上传文件
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_URL}/api/upload/image`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                // 插入图片到编辑器
                if (articleEditor) {
                    articleEditor.chain().focus().setImage({ src: data.url }).run();
                }
            } else {
                alert('上传失败');
            }
        } catch (error) {
            alert('上传错误: ' + error.message);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    };
    
    input.click();
}
```

---

## 第3阶段：测试和优化 (0.5天)

### 测试清单

- [ ] 编辑器基本功能（加粗、斜体、列表等）
- [ ] 图片上传功能
- [ ] 链接插入功能
- [ ] 浏览器兼容性（Chrome、Firefox、Safari）
- [ ] 手机响应式适配
- [ ] 性能测试（大文档编辑）

---

## 快速开始

1. **更新HTML文件**
   - 添加CDN链接
   - 替换textarea为编辑器容器

2. **添加样式**
   - 复制上面的CSS代码

3. **添加JavaScript**
   - 复制编辑器初始化代码
   - 复制工具栏函数
   - 修改表单提交逻辑

4. **创建上传端点**
   - 在后端创建 `/api/upload/image` 端点

5. **测试验证**
   - 创建新文章，测试编辑功能
   - 测试图片上传

---

## 常见问题

### Q: 能否离线使用Tiptap？
A: CDN方式需要网络。可以考虑npm打包方案，但会增加复杂度。

### Q: 如何导出为Markdown？
A: 可以后续添加 `@tiptap/extension-markdown` 的导出功能。

### Q: 如何支持更多文件类型？
A: 在 `ALLOWED_EXTENSIONS` 和前端 `accept` 属性中添加。

