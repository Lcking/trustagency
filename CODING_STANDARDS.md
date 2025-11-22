# TrustAgency 编码规范

**版本**：1.0  
**发布日期**：2025-11-21  
**状态**：强制执行  
**维护者**：开发团队

---

## 目录
1. [JavaScript/HTML 规范](#javascripthtml-规范)
2. [后端 Python 规范](#后端-python-规范)
3. [数据库规范](#数据库规范)
4. [Git 工作流规范](#git-工作流规范)
5. [测试规范](#测试规范)
6. [代码审查规范](#代码审查规范)

---

## JavaScript/HTML 规范

### 脚本块管理（严格规则）

**规则 1.1：脚本块数量限制**
- ✅ 允许：最多 2 个 `<script>` 标签
- ✅ 第一个：主脚本块（所有业务逻辑）
- ✅ 第二个：诊断脚本块（仅用于调试/监控）
- ❌ 禁止：在 HTML 元素内插入 `<script>` 标签
- ❌ 禁止：在页面中间多个位置插入 `<script>` 标签
- ❌ 禁止：使用 inline event handlers（如 `onclick="func()"`）

**反例（禁止）**：
```html
<!-- ❌ 错误：在div内插入脚本 -->
<div id="loginPage">
    <form>...</form>
    <script>
        function handleLogin() { ... }  // 不要这样做！
    </script>
</div>

<div id="mainPage">
    <script>
        function showSection() { ... }  // 不要这样做！
    </script>
</div>
```

**正例（规范）**：
```html
<!-- ✅ 正确：所有脚本集中在</body>前 -->
<body>
    <div id="loginPage">...</div>
    <div id="mainPage">...</div>
    
    <script>  <!-- 唯一的主脚本块 -->
        // 所有函数定义、初始化代码
        function handleLogin() { ... }
        function showSection() { ... }
        document.addEventListener('DOMContentLoaded', () => { ... });
    </script>
</body>
```

---

**规则 1.2：脚本块位置**
- ✅ 主脚本块：必须在 `</body>` 前
- ✅ 诊断脚本块：可以在主脚本块之后
- ❌ 禁止：在 `<head>` 中放置业务逻辑脚本
- ❌ 禁止：在 HTML 元素内放置脚本

**检查方法**：
```bash
# 检查脚本块数量
grep -c "<script>" backend/site/admin/index.html
# 应该输出：2

# 检查脚本块位置
grep -n "<script>" backend/site/admin/index.html
# 应该输出：
# 1347:<script>
# 4108:<script>
```

---

**规则 1.3：脚本块结构组织**

主脚本块必须按照以下顺序组织：

```javascript
<script>
// ========== 第1部分：全局变量定义 ==========
const API_BASE_URL = getAPIUrl();
const API_URL = `${API_BASE_URL}/api`;
let token = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');

// ========== 第2部分：工具函数 ==========
function getAPIUrl() { ... }
function getAuthHeaders() { ... }
async function authenticatedFetch(url, options) { ... }
function showNotification(message, type) { ... }
function hideNotification() { ... }

// ========== 第3部分：业务函数 ==========
// 按模块组织
// - 认证相关
async function handleLogin(username, password) { ... }
async function handleLogout() { ... }
// - UI展示相关  
function showLoginPage() { ... }
function showMainPage() { ... }
// - 数据加载相关
async function loadSections() { ... }
async function loadPlatforms() { ... }

// ========== 第4部分：DOM事件绑定 ==========
document.addEventListener('DOMContentLoaded', function() {
    // 初始化代码：检查登录状态、加载数据等
});

document.addEventListener('click', function(e) {
    // 事件委托：处理按钮点击、链接点击等
});

// ========== 第5部分：页面加载时的初始化 ==========
(function initPage() {
    // 页面初始化逻辑
})();

</script>
```

---

### HTML 结构规范

**规则 1.4：HTML 元素平衡**
- ✅ 每个 `<div>` 开标签必须有对应的 `</div>` 闭标签
- ✅ 修改 HTML 时必须检查平衡性
- ❌ 禁止：存在未闭合的标签
- ❌ 禁止：存在不匹配的标签对

**检查方法**：
```bash
# 检查开闭标签数量
echo "Open <div>: $(grep -o '<div' backend/site/admin/index.html | wc -l)"
echo "Close </div>: $(grep -o '</div>' backend/site/admin/index.html | wc -l)"
# 两个数字应该相同
```

---

**规则 1.5：HTML 修改位置**
- ✅ 新增 HTML 应该放在已有的容器内
- ✅ 应该使用语义化标签（`<section>`, `<article>`, `<form>` 等）
- ❌ 禁止：在脚本块附近插入大块 HTML
- ❌ 禁止：改变现有的主要 div 结构

---

**规则 1.6：事件处理**
- ✅ 使用 `addEventListener` 或 事件委托
- ✅ 在脚本块中定义所有事件处理函数
- ❌ 禁止：在 HTML 中使用 `onclick`, `onchange` 等 inline handlers

**反例**：
```html
<!-- ❌ 不要这样 -->
<button onclick="showSection('categories')">栏目</button>
<input type="text" onchange="validateForm()" />
```

**正例**：
```html
<!-- ✅ 要这样 -->
<button data-section="categories" class="section-btn">栏目</button>
<input type="text" class="form-input" data-field="email" />
```

```javascript
// 在脚本块中
document.addEventListener('click', function(e) {
    if (e.target.matches('.section-btn')) {
        const section = e.target.dataset.section;
        showSection(section);
    }
});
```

---

**规则 1.7：函数命名**
- ✅ 使用 camelCase 命名（`loadSections`, `handleLogin`）
- ✅ 函数名应该清晰表达功能（`showSection` 而不是 `show`）
- ✅ 异步函数使用 async/await（`async function loadData() { ... }`)
- ❌ 禁止：使用单字母变量名（除了循环计数器 `i`）
- ❌ 禁止：混合不同的命名风格

---

### API 调用规范

**规则 1.8：API URL 构造**
- ✅ 始终使用 `getAPIUrl()` 函数获取基础 URL
- ✅ 使用 `authenticatedFetch()` 进行鉴权请求
- ✅ 在请求中包含认证令牌（如果需要）
- ❌ 禁止：硬编码 API URL（如 `http://localhost:8001/api/...`）
- ❌ 禁止：直接使用 `fetch()` 而不添加鉴权头

**规范示例**：
```javascript
// ❌ 错误
async function loadData() {
    const response = await fetch('http://localhost:8001/api/sections');
    const data = await response.json();
}

// ✅ 正确
async function loadData() {
    const response = await authenticatedFetch(`${API_URL}/sections`);
    const data = await response.json();
}
```

---

### localStorage 使用规范

**规则 1.9：数据存储**
- ✅ 使用 `localStorage.setItem('token', value)` 存储
- ✅ 使用 `localStorage.getItem('token')` 读取
- ✅ JSON 数据必须使用 `JSON.stringify()` / `JSON.parse()`
- ✅ 定义常量管理 localStorage 的键名

**规范示例**：
```javascript
// 定义常量
const STORAGE_KEYS = {
    TOKEN: 'token',
    CURRENT_USER: 'currentUser',
    SETTINGS: 'appSettings'
};

// 存储
localStorage.setItem(STORAGE_KEYS.TOKEN, token);
localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify(user));

// 读取
const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
const user = JSON.parse(localStorage.getItem(STORAGE_KEYS.CURRENT_USER) || '{}');
```

---

## 后端 Python 规范

### 文件结构规范

**规则 2.1：项目结构**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── database.py       # 数据库配置和初始化
│   ├── models/           # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── section.py
│   │   ├── platform.py
│   │   └── website_settings.py
│   ├── routes/           # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── sections.py
│   │   └── website_settings.py
│   └── schemas/          # Pydantic 模式
│       ├── __init__.py
│       └── section.py
```

---

**规则 2.2：导入顺序**
- 第1组：Python 标准库（`import os`, `from datetime import datetime`）
- 第2组：第三方库（`from fastapi import FastAPI`, `from sqlalchemy import Column`）
- 第3组：本地应用（`from app.models import Section`）
- 各组之间用空行分隔

**规范示例**：
```python
# ✅ 正确的导入顺序
import os
from datetime import datetime

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Section, Platform
from app.routes import sections_router, platforms_router
```

---

### 函数/类命名规范

**规则 2.3：命名风格**
- ✅ 类名：PascalCase（`UserSettings`, `ArticleDetail`）
- ✅ 函数名：snake_case（`create_section`, `get_user_by_id`）
- ✅ 常量：UPPER_SNAKE_CASE（`DATABASE_URL`, `MAX_RETRIES`）
- ✅ 私有函数/变量：_leading_underscore（`_validate_input`, `_internal_state`）

---

### 数据库操作规范

**规则 2.4：ORM 使用**
- ✅ 使用 SQLAlchemy ORM（而不是原始 SQL）
- ✅ 使用 Pydantic 模式进行数据验证
- ✅ 使用依赖注入获取 DB Session（`Depends(get_db)`）
- ❌ 禁止：使用原始 SQL 字符串拼接
- ❌ 禁止：直接暴露数据库对象给前端

**规范示例**：
```python
# ❌ 错误：不使用ORM
@app.get("/sections")
def get_sections():
    query = f"SELECT * FROM sections WHERE platform_id = {platform_id}"
    # 直接执行SQL - 危险！

# ✅ 正确：使用ORM
@app.get("/sections")
def get_sections(platform_id: int, db: Session = Depends(get_db)):
    sections = db.query(Section).filter(
        Section.platform_id == platform_id
    ).all()
    return [SectionSchema.from_orm(s) for s in sections]
```

---

**规则 2.5：错误处理**
- ✅ 使用 try-except 捕获异常
- ✅ 返回 HTTP 错误码（400, 401, 404, 500 等）
- ✅ 在异常中包含有意义的错误信息
- ❌ 禁止：忽略异常
- ❌ 禁止：返回 500 错误而不记录日志

**规范示例**：
```python
# ✅ 正确的错误处理
@app.get("/sections/{section_id}")
def get_section(section_id: int, db: Session = Depends(get_db)):
    try:
        section = db.query(Section).filter(
            Section.id == section_id
        ).first()
        
        if not section:
            raise HTTPException(
                status_code=404,
                detail=f"Section {section_id} not found"
            )
        
        return section
    except Exception as e:
        logger.error(f"Error fetching section: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

---

### 日志规范

**规则 2.6：日志记录**
- ✅ 使用 Python 的 `logging` 模块
- ✅ 在关键操作处记录日志（创建、更新、删除）
- ✅ 在错误处记录 ERROR 级别日志
- ✅ 在调试时记录 DEBUG 级别日志
- ❌ 禁止：使用 `print()` 进行日志输出

**规范示例**：
```python
import logging

logger = logging.getLogger(__name__)

def create_section(section_data, db: Session):
    try:
        section = Section(**section_data)
        db.add(section)
        db.commit()
        logger.info(f"Created section: {section.id}")
        return section
    except Exception as e:
        logger.error(f"Failed to create section: {str(e)}")
        raise
```

---

## 数据库规范

### 规则 3.1：模型定义
- ✅ 每个模型都要有明确的 `__tablename__`
- ✅ 每个模型都要有 `id` 作为主键
- ✅ 每个模型都要有 `created_at` 和 `updated_at` 时间戳
- ✅ 使用有意义的列名和类型
- ❌ 禁止：模型没有主键
- ❌ 禁止：使用模糊的列名（如 `data`, `value1`, `value2`）

**规范示例**：
```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Section(Base):
    __tablename__ = 'sections'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow, nullable=False)
    
    # 关系定义
    platform = relationship("Platform", back_populates="sections")
```

---

### 规则 3.2：迁移和初始化
- ✅ 在 `database.py` 中集中管理所有初始化逻辑
- ✅ 在启动时检查表是否存在，不存在则创建
- ✅ 在初始化时添加默认数据
- ❌ 禁止：手动创建表或修改表结构而不更新模型

**规范示例**：
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Platform, Section

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """初始化数据库：创建表、添加默认数据"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 添加默认数据
    db = SessionLocal()
    
    # 检查是否已有数据
    if db.query(Platform).count() == 0:
        default_platforms = [
            Platform(name="Platform 1", ...),
            Platform(name="Platform 2", ...),
        ]
        db.add_all(default_platforms)
        db.commit()
    
    db.close()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Git 工作流规范

### 规则 4.1：分支管理
- `main`：生产分支，始终可运行，受保护
- `dev`：开发分支，集成所有功能
- `feature/xxx`：功能分支，从 `dev` 创建
- `bugfix/xxx`：修复分支，从 `dev` 创建
- `hotfix/xxx`：紧急修复，从 `main` 创建

**分支创建命令**：
```bash
# 创建功能分支
git checkout dev
git pull origin dev
git checkout -b feature/new-feature-name

# 创建修复分支
git checkout -b bugfix/issue-description

# 创建紧急修复
git checkout main
git checkout -b hotfix/critical-bug
```

---

### 规则 4.2：提交信息格式
遵循 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**（type）：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码风格调整（不影响功能）
- `refactor`: 代码重构
- `test`: 添加/修改测试
- `chore`: 构建、依赖等更新
- `perf`: 性能优化

**示例**：
```bash
# ✅ 正确
git commit -m "feat(admin): add website settings panel

- Add WebsiteSettings model
- Add API endpoints for settings management
- Add UI form for editing settings

Closes #123"

# ❌ 错误
git commit -m "update code"
git commit -m "fixed stuff"
git commit -m "新增功能"
```

---

### 规则 4.3：Pull Request 流程
- 从 `feature/xxx` 创建 PR 到 `dev`
- PR 标题遵循 commit 格式
- PR 描述必须包括：
  - 功能描述
  - 修改内容列表
  - 测试结果
  - 规范检查清单（见下一部分）

---

## 测试规范

### 规则 5.1：测试覆盖
- ✅ 所有 API 端点都要有集成测试
- ✅ 所有关键业务逻辑都要有单元测试
- ✅ 测试覆盖率 > 80%
- ❌ 禁止：合并没有测试的代码到 main

---

### 规则 5.2：集成测试
所有功能修改都必须通过完整集成测试。参见 `INTEGRATION_TESTS.md`

---

## 代码审查规范

### 规则 6.1：PR 审查清单

**提交者必须填写** 提交 PR 时：
- [ ] 代码遵循编码规范
- [ ] 脚本块数量验证（最多 2 个）
- [ ] HTML 标签平衡性检查（开闭相同）
- [ ] 已通过所有集成测试
- [ ] 没有 console 错误
- [ ] API 路由正确
- [ ] 数据库变更已文档化
- [ ] 提交信息格式正确

**审查者必须检查**：
- [ ] 代码是否遵循规范
- [ ] 是否有潜在的系统稳定性风险
- [ ] 是否有性能问题
- [ ] 测试覆盖是否充分
- [ ] 是否会影响其他功能

---

### 规则 6.2：代码审查标准
- 🟢 **APPROVED**：可以合并
- 🟡 **REQUEST CHANGES**：需要改进，不能合并
- 🔵 **COMMENT**：有建议但不阻止合并

---

## 新功能开发检查清单

在提交 PR 前，必须完成以下检查清单：

**开发阶段**：
- [ ] 功能已按需求实现
- [ ] 代码遵循编码规范
- [ ] 所有函数/变量命名规范
- [ ] 有适当的注释和文档

**脚本块检查**（前端）：
- [ ] 脚本块数量 <= 2 个
- [ ] 所有脚本块在 `</body>` 前
- [ ] 所有函数定义在脚本块内
- [ ] 没有 inline event handlers
- [ ] 没有在 HTML 元素内插入脚本

**HTML 检查**（前端）：
- [ ] div 开闭标签平衡
- [ ] 没有残留的调试代码
- [ ] 没有硬编码的 API URL

**API 检查**（前后端）：
- [ ] 使用 `authenticatedFetch()` 而不是 `fetch()`
- [ ] API URL 使用 `getAPIUrl()` 函数
- [ ] 错误处理完善
- [ ] 返回值格式一致

**数据库检查**（后端）：
- [ ] 新模型已添加到 `models/` 目录
- [ ] 已更新 `database.py` 初始化函数
- [ ] 数据库变更已记录
- [ ] 没有直接的 SQL 语句

**测试阶段**：
- [ ] 单元测试编写完成
- [ ] 集成测试通过
- [ ] 手动测试验证功能
- [ ] 检查浏览器 console 无错误
- [ ] 检查后端日志无异常
- [ ] 原有功能未被破坏

**最终检查**：
- [ ] Git commit 信息格式正确
- [ ] PR 描述完整
- [ ] 所有规范检查清单项目已完成

---

## 违规处理

**违规后果**：
1. 第一次：需要修改并重新审查
2. 第二次：需要团队审查和讨论
3. 第三次：暂时禁止 commit 权限

---

## 规范更新

本规范每个季度审查一次。如需更新规范，请在团队会议上讨论并形成共识。

---

**签名**：开发团队认可  
**最后更新**：2025-11-21
