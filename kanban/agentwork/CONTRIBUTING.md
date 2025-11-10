# Contributing Guide - TrustAgency 贡献指南

**Version**: 1.0.0  
**更新日期**: 2025-11-07

---

## 📋 目录

1. [行为守则](#行为守则)
2. [开始贡献](#开始贡献)
3. [开发设置](#开发设置)
4. [编码规范](#编码规范)
5. [提交变更](#提交变更)
6. [代码审查流程](#代码审查流程)
7. [报告问题](#报告问题)
8. [文档贡献](#文档贡献)

---

## 行为守则

### 我们的承诺

在参与 TrustAgency 社区时，我们致力于提供一个友好、尊重和包容的环境。

### 预期行为

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 接受建设性的批评
- 关注社区最佳利益
- 对其他社区成员表现出同情心

### 不可接受的行为

- 使用带有性别歧视、年龄歧视等的语言
- 人身攻击
- 骚扰或欺凌
- 无端的冒犯
- 其他可能被合理认为在专业环境中不适当的行为

---

## 开始贡献

### 代码贡献流程

1. **Fork 仓库**
   ```bash
   # 访问 https://github.com/Lcking/trustagency
   # 点击 Fork 按钮
   ```

2. **克隆您的 Fork**
   ```bash
   git clone https://github.com/your-username/trustagency.git
   cd trustagency
   ```

3. **添加上游仓库**
   ```bash
   git remote add upstream https://github.com/Lcking/trustagency.git
   ```

4. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **提交变更**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 访问 GitHub
   - 点击 "New Pull Request"
   - 选择您的分支和 main 分支
   - 填写 PR 描述
   - 点击 "Create Pull Request"

---

## 开发设置

### 环境要求

```
Python: 3.10+
Node.js: 18+
PostgreSQL: 15+
Redis: 7+
Docker: 20.10+
Docker Compose: 2.0+
```

### 本地开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/Lcking/trustagency.git
cd trustagency

# 2. 创建虚拟环境 (后端)
cd backend
python3.10 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 设置环境变量
cp .env.example .env
# 编辑 .env，设置本地配置

# 5. 初始化数据库
python init_db.py

# 6. 启动后端
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 7. 在另一个终端，设置前端
cd ../site
npm install

# 8. 启动前端
npm run dev

# 9. 访问 http://localhost:8000
```

### 使用 Docker 开发

```bash
# 启动所有服务
./docker-start.sh

# 查看日志
docker-compose logs -f

# 进入后端容器
docker-compose exec backend bash

# 运行测试
docker-compose exec backend pytest
```

---

## 编码规范

### Python 代码风格

遵循 PEP 8 标准：

```python
# ✓ 好的示例
def calculate_total(items: List[Item]) -> float:
    """计算总价。
    
    Args:
        items: 商品列表
    
    Returns:
        总价
    """
    return sum(item.price for item in items)

# ✗ 不好的示例
def calculateTotal(items):
    return sum([item.price for item in items])
```

### 命名规范

```python
# 类名使用 PascalCase
class AdminUser:
    pass

# 函数和变量使用 snake_case
def get_user_by_id(user_id: int) -> AdminUser:
    pass

# 常量使用 UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100
```

### 导入顺序

```python
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
from fastapi import FastAPI
from sqlalchemy import create_engine
import numpy as np

# 3. 本地应用
from app.models import AdminUser
from app.database import get_db
```

### 类型注解

```python
# ✓ 使用类型注解
from typing import Optional, List

def get_articles(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
) -> List[Article]:
    pass

# ✗ 避免
def get_articles(skip=0, limit=10, search=None):
    pass
```

### 文档字符串

```python
def create_article(data: ArticleCreate) -> Article:
    """创建新文章。
    
    Args:
        data: 文章数据
    
    Returns:
        创建的文章
    
    Raises:
        ValueError: 如果标题为空
    """
    pass
```

### JavaScript/TypeScript 代码风格

```javascript
// ✓ 使用 const 和 let
const MAX_ITEMS = 100;
let count = 0;

// ✗ 避免使用 var
var items = [];

// ✓ 箭头函数
const handleClick = (e) => {
  console.log(e);
};

// ✓ 使用解构
const { name, email } = user;

// ✓ 模板字符串
const message = `Hello, ${name}!`;
```

---

## 提交变更

### 提交消息格式

遵循 Conventional Commits：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (type)

- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式（不影响代码运行）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 依赖、构建等

### 示例

```bash
# 新功能
git commit -m "feat(article): add AI generation feature"

# 修复
git commit -m "fix(auth): fix token validation issue"

# 文档
git commit -m "docs: update API documentation"

# 带描述的提交
git commit -m "feat(platform): add platform ranking

- Add ranking field to platform model
- Update API endpoints to support ranking
- Add ranking validation"
```

---

## 代码审查流程

### 审查标准

代码审查将检查以下内容：

- ✅ 代码是否遵循风格指南
- ✅ 是否有测试覆盖
- ✅ 是否更新了文档
- ✅ 是否有安全问题
- ✅ 是否与现有代码一致
- ✅ 性能是否可接受

### 审查反馈

- 建议性的反馈用 "nit:" 前缀
- 要求更改用 "blocker:" 前缀
- 问题用 "question:" 前缀

### 处理反馈

```bash
# 基于反馈进行修改
git add .
git commit -m "refactor: address code review feedback"

# 推送更新
git push origin feature/your-feature-name

# PR 会自动更新
```

---

## 报告问题

### 提交 Issue 时

1. **检查是否已存在类似 Issue**
   - 使用搜索功能

2. **选择合适的模板**
   - Bug Report
   - Feature Request
   - Documentation
   - Question

3. **提供详细信息**
   ```
   **描述问题**
   清晰描述问题
   
   **重现步骤**
   1. 打开...
   2. 点击...
   3. 看到问题...
   
   **预期行为**
   应该发生什么
   
   **实际行为**
   实际发生了什么
   
   **环境信息**
   - OS: [e.g. Ubuntu 22.04]
   - Python: [e.g. 3.10.2]
   - Browser: [e.g. Chrome 108]
   
   **附加信息**
   错误堆栈、日志等
   ```

---

## 文档贡献

### 文档位置

```
/docs/              - 用户文档
API_DOCUMENTATION_COMPLETE.md
USER_MANUAL.md
MAINTENANCE_GUIDE.md
DEPLOYMENT_AND_LAUNCH_GUIDE.md
```

### 文档风格指南

- 使用清晰、简洁的语言
- 使用示例
- 添加代码高亮
- 使用有意义的标题
- 保持一致的格式

### 文档示例

```markdown
# 功能标题

## 概览
简要说明功能

## 使用方法
1. 第一步
2. 第二步

## 示例
\`\`\`python
# 代码示例
\`\`\`

## 相关链接
- [相关主题](link)
```

---

## 测试

### 运行测试

```bash
# 后端单元测试
cd backend
pytest

# 特定测试文件
pytest tests/test_auth.py

# 带覆盖率报告
pytest --cov=app tests/

# 前端测试
cd ../site
npm test

# E2E 测试
npm run test:e2e
```

### 编写测试

```python
# tests/test_article.py
import pytest
from app.services.article_service import ArticleService
from app.schemas.article import ArticleCreate

def test_create_article(db):
    """测试创建文章"""
    data = ArticleCreate(
        title="Test Article",
        content="Test content",
        summary="Test summary",
        category="test"
    )
    
    article = ArticleService.create_article(db, data, author_id=1, platform_id=1)
    
    assert article.title == "Test Article"
    assert article.author_id == 1
```

---

## 许可证

本项目使用 MIT 许可证。通过贡献代码，您同意您的代码将在相同的许可证下发布。

---

## 常见问题

**Q: 如何获得提交权限？**  
A: 第一次提交通过审查后，维护者会考虑授予权限。

**Q: 多久会审查我的 PR？**  
A: 通常 1-3 个工作日内。

**Q: 我可以贡献什么？**  
A: 代码、文档、翻译、测试、设计等。

**Q: 如何与其他贡献者联系？**  
A: 通过 GitHub Discussions 或邮件 support@trustagency.com

---

感谢您的贡献！🎉

