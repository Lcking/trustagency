# 后端开发任务详细拆分与测试用例

**项目**: TrustAgency 管理系统  
**开始时间**: 2025-11-06  
**总工作量**: ~30-35 小时  
**预计完成**: 2025-11-13 到 2025-11-15

---

## 📋 任务概览

```
Task 1:  后端项目初始化和环境配置        [1h]
Task 2:  数据库和 SQLAlchemy 模型设计    [2h]
Task 3:  管理员认证系统实现              [2.5h]
Task 4:  平台管理 API 实现               [4h]
Task 5:  文章管理 API 实现               [4h]
Task 6:  FastAPI Admin 后台集成          [1.5h]
Task 7:  Celery + Redis 任务队列配置     [1.5h]
Task 8:  OpenAI 集成和文章生成功能       [4h]
Task 9:  后端单元测试编写               [3h]
Task 10: 前端 API 客户端实现和测试       [3h]
Task 11: 端到端集成测试                 [2h]
Task 12: Docker 部署和生产优化           [2h]
Task 13: 文档完成和项目交付             [1.5h]
──────────────────────────────
总计: 31.5 小时
```

---

## 🎯 Task 1: 后端项目初始化和环境配置

### 目标
创建 FastAPI 项目结构、Python 虚拟环境、安装依赖、配置 .env 文件。

### 子任务

#### 1.1 创建项目目录结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用主文件
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/
│   │   ├── __init__.py
│   │   ├── admin_user.py       # 管理员模型
│   │   ├── platform.py         # 平台模型
│   │   ├── article.py          # 文章模型
│   │   └── ai_task.py          # AI 任务模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── admin.py            # 管理员 Schema
│   │   ├── platform.py         # 平台 Schema
│   │   ├── article.py          # 文章 Schema
│   │   └── ai_task.py          # 任务 Schema
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # 认证路由
│   │   ├── platforms.py        # 平台路由
│   │   ├── articles.py         # 文章路由
│   │   └── ai_tasks.py         # AI 任务路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # 认证服务
│   │   ├── platform_service.py # 平台业务逻辑
│   │   ├── article_service.py  # 文章业务逻辑
│   │   └── ai_service.py       # AI 生成服务
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT 和密码工具
│   │   └── exceptions.py       # 自定义异常
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py  # 认证中间件
│   └── admin/
│       ├── __init__.py
│       └── init_admin.py       # FastAPI Admin 配置
├── migrations/                 # 数据库迁移（Alembic）
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest 配置
│   ├── test_auth.py
│   ├── test_platforms.py
│   ├── test_articles.py
│   └── test_ai_tasks.py
├── .env.example
├── .env                        # 环境变量（Git 忽略）
├── .gitignore
├── requirements.txt            # 依赖列表
├── pyproject.toml              # 项目配置
├── alembic.ini                 # 数据库迁移配置
├── docker-compose.yml          # Docker Compose 配置
├── Dockerfile                  # Docker 镜像配置
└── README.md                   # 项目说明
```

#### 1.2 创建 Python 虚拟环境
```bash
cd /Users/ck/Desktop/Project/trustagency/backend
python3 -m venv venv
source venv/bin/activate
```

#### 1.3 安装依赖

```bash
pip install --upgrade pip
```

**核心依赖** (`requirements.txt`):
```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9  # PostgreSQL
sqlite==3.44.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
PyJWT==2.8.1

# Admin Panel
fastapi-admin==0.3.3
sqlmodel==0.0.14

# Task Queue
celery==5.3.4
redis==5.0.1

# AI Integration
openai==1.3.5
requests==2.31.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Development
black==23.12.0
flake8==6.1.0
mypy==1.7.1
```

#### 1.4 创建 .env 配置文件

```env
# FastAPI
ENVIRONMENT=development
DEBUG=True
API_TITLE=TrustAgency API
API_VERSION=1.0.0
API_DESCRIPTION=Admin CMS with AI Content Generation

# Database
DATABASE_URL=sqlite:///./trustagency.db
# 生产环境:
# DATABASE_URL=postgresql://user:password@localhost:5432/trustagency_prod

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# Admin
ADMIN_EMAIL=admin@trustagency.com
ADMIN_PASSWORD=admin123  # 生产环境应该改强密码

# OpenAI
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Cors
CORS_ORIGINS=["http://localhost:8000", "http://localhost:8001"]
```

#### 1.5 创建 pyproject.toml

```toml
[project]
name = "trustagency-backend"
version = "1.0.0"
description = "Admin CMS with AI Content Generation"
requires-python = ">=3.9"
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "sqlalchemy==2.0.23",
    "alembic==1.13.0",
    "psycopg2-binary==2.9.9",
    "python-jose[cryptography]==3.3.0",
    "passlib[bcrypt]==1.7.4",
    "python-dotenv==1.0.0",
    "PyJWT==2.8.1",
    "fastapi-admin==0.3.3",
    "celery==5.3.4",
    "redis==5.0.1",
    "openai==1.3.5",
    "requests==2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
    "httpx==0.25.2",
    "black==23.12.0",
    "flake8==6.1.0",
    "mypy==1.7.1",
]

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100
target-version = ['py39']

[tool.mypy]
python_version = "3.9"
ignore_missing_imports = true
```

#### 1.6 创建 .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
logs/
*.log

# Redis
dump.rdb
```

### 测试用例 (Task 1)

```yaml
测试 1.1: 项目目录结构创建
  步骤:
    1. 创建 backend 目录
    2. 创建所有子目录
    3. 创建 __init__.py 文件
  验证:
    - 所有文件夹存在
    - 所有 __init__.py 存在
  预期: ✅ 目录结构完整

测试 1.2: 虚拟环境创建
  步骤:
    1. 创建 venv
    2. 激活 venv
    3. 查看 Python 版本
  验证:
    - python --version 返回 3.9+
    - pip list 返回 pip, setuptools, wheel
  预期: ✅ 虚拟环境创建成功

测试 1.3: 依赖安装
  步骤:
    1. pip install -r requirements.txt
    2. pip list | grep fastapi
    3. pip list | grep sqlalchemy
  验证:
    - fastapi 存在
    - sqlalchemy 存在
    - 所有依赖版本正确
  预期: ✅ 所有依赖安装成功

测试 1.4: .env 文件配置
  步骤:
    1. 创建 .env 文件
    2. 设置所有必要变量
    3. python -c "from dotenv import load_dotenv"
  验证:
    - 所有必要的键存在
    - 没有未设置的值
  预期: ✅ 配置文件完整
```

### 实现检查清单

- [ ] backend 目录创建
- [ ] 所有子目录创建
- [ ] Python 虚拟环境创建并激活
- [ ] requirements.txt 编写
- [ ] .env 文件创建
- [ ] pyproject.toml 创建
- [ ] .gitignore 创建
- [ ] 所有依赖安装成功
- [ ] import fastapi, sqlalchemy 测试通过
- [ ] 提交 Git: "feat: 初始化后端项目结构和环境配置"

---

## 🎯 Task 2: 数据库和 SQLAlchemy 模型设计

### 目标
创建 SQLAlchemy ORM 模型，包括管理员、平台、文章、AI 任务等。

### 数据模型设计

#### 2.1 AdminUser 模型
```python
# app/models/admin_user.py

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_superadmin = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # 关系
    articles = relationship("Article", back_populates="author")
    ai_tasks = relationship("AIGenerationTask", back_populates="creator")
```

#### 2.2 Platform 模型
```python
# app/models/platform.py

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

class Platform(Base):
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    rating = Column(Float, default=0.0, nullable=False)  # 0-5 star
    rank = Column(Integer, nullable=True, index=True)  # 排名
    
    # 交易相关
    min_leverage = Column(Float, default=1.0, nullable=False)
    max_leverage = Column(Float, default=100.0, nullable=False)
    commission_rate = Column(Float, default=0.0, nullable=False)  # 0.001 = 0.1%
    is_regulated = Column(Boolean, default=False)
    
    # 链接和媒体
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    articles = relationship("Article", back_populates="platform", cascade="all, delete-orphan")
```

#### 2.3 Article 模型
```python
# app/models/article.py

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # 分类和标签
    category = Column(String(100), index=True, nullable=False)  # review, guide, news
    tags = Column(String(500), nullable=True)  # 逗号分隔
    
    # 作者和平台
    author_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    
    # 发布状态
    is_published = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False)
    
    # SEO
    meta_description = Column(String(160), nullable=True)
    meta_keywords = Column(String(500), nullable=True)
    
    # 统计
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # 关系
    author = relationship("AdminUser", back_populates="articles")
    platform = relationship("Platform", back_populates="articles")
```

#### 2.4 AIGenerationTask 模型
```python
# app/models/ai_task.py

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AIGenerationTask(Base):
    __tablename__ = "ai_generation_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 批次信息
    batch_id = Column(String(100), unique=True, index=True, nullable=False)
    batch_name = Column(String(255), nullable=True)
    
    # 输入和输出
    titles = Column(JSON, nullable=False)  # 标题列表
    generated_articles = Column(JSON, nullable=True)  # 生成的文章列表
    
    # 任务状态
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    progress = Column(Integer, default=0)  # 0-100
    total_count = Column(Integer, nullable=False)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # 错误跟踪
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # 创建者
    creator_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 关系
    creator = relationship("AdminUser", back_populates="ai_tasks")
```

### Schema 定义（Pydantic）

#### 2.5 AdminUser Schema
```python
# app/schemas/admin.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AdminBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminResponse(AdminBase):
    id: int
    is_active: bool
    is_superadmin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    username: str
    password: str
```

#### 2.6 Platform Schema
```python
# app/schemas/platform.py

from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class PlatformBase(BaseModel):
    name: str
    description: Optional[str] = None
    rating: Optional[float] = 0.0
    rank: Optional[int] = None
    min_leverage: float = 1.0
    max_leverage: float = 100.0
    commission_rate: float = 0.0
    is_regulated: bool = False
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_featured: bool = False

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    rank: Optional[int] = None
    min_leverage: Optional[float] = None
    max_leverage: Optional[float] = None
    commission_rate: Optional[float] = None
    is_regulated: Optional[bool] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None

class PlatformResponse(PlatformBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### 2.7 Article Schema
```python
# app/schemas/article.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    category: str  # review, guide, news
    tags: Optional[str] = None
    platform_id: int
    is_featured: bool = False
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    platform_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None

class ArticleResponse(ArticleBase):
    id: int
    slug: str
    author_id: int
    is_published: bool
    view_count: int
    like_count: int
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

#### 2.8 AI Task Schema
```python
# app/schemas/ai_task.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AITaskCreate(BaseModel):
    batch_name: Optional[str] = None
    titles: List[str]

class AITaskResponse(BaseModel):
    id: int
    batch_id: str
    batch_name: Optional[str] = None
    status: str
    progress: int
    total_count: int
    completed_count: int
    failed_count: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### 数据库迁移配置

#### 2.9 Alembic 初始化
```bash
alembic init migrations
```

#### 2.10 alembic.ini 配置
```ini
sqlalchemy.url = driver://user:password@localhost/dbname
```

### 测试用例 (Task 2)

```yaml
测试 2.1: 模型创建和导入
  步骤:
    1. 导入所有模型
    2. 检查模型属性
    3. 创建表
  验证:
    - from app.models import AdminUser, Platform, Article, AIGenerationTask
    - 所有模型有正确的列定义
  预期: ✅ 所有模型导入成功

测试 2.2: Schema 验证
  步骤:
    1. 创建 PlatformCreate 实例
    2. 验证字段类型
    3. 检查默认值
  验证:
    - platform = PlatformCreate(name="Test", rating=4.5)
    - platform.rating == 4.5
  预期: ✅ Schema 验证通过

测试 2.3: 数据库连接
  步骤:
    1. 创建数据库连接
    2. 创建所有表
    3. 查询表元数据
  验证:
    - engine = create_engine("sqlite:///test.db")
    - Base.metadata.create_all(engine)
    - 表创建成功
  预期: ✅ 数据库连接和表创建成功

测试 2.4: 模型关系
  步骤:
    1. 创建 AdminUser
    2. 创建相关的 Articles
    3. 检查反向关系
  验证:
    - user.articles 返回正确的列表
    - article.author 返回正确的用户
  预期: ✅ 模型关系正确
```

### 实现检查清单

- [ ] 所有模型文件创建 (admin_user, platform, article, ai_task)
- [ ] 所有 Schema 文件创建 (admin, platform, article, ai_task)
- [ ] database.py 数据库连接配置创建
- [ ] Alembic 迁移脚本初始化
- [ ] 所有模型导入测试通过
- [ ] Schema 验证测试通过
- [ ] 数据库连接测试通过
- [ ] 提交 Git: "feat: 创建 SQLAlchemy 模型和 Pydantic Schema"

---

## 🎯 Task 3-13 的详细规范

由于上下文限制，我将分段提供其他 Task 的详细规范。

**现在开始 Task 1: 后端项目初始化和环境配置**

你要开始吗？还是需要看完所有 Task 的规范后再开始？

