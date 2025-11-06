# 🚀 快速开始指南 - 后端开发

**目标**: 在 1 周内完成后端核心功能  
**难度**: 中等  
**先修**: Python 基础、FastAPI 入门、REST API 概念  

---

## 📋 前置条件检查

运行以下命令确保环境就绪:

```bash
# 检查 Python 版本
python3 --version  # 应该是 3.9+

# 检查 pip
pip3 --version

# 检查 Git
git --version
```

---

## ⚡ 极速 5 分钟起步

### 1️⃣ 初始化项目

```bash
# 在项目根目录
cd /Users/ck/Desktop/Project/trustagency

# 创建后端目录
mkdir backend
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 复制依赖文件 (从 IMPLEMENTATION_GUIDE.md 获取)
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
openai==1.3.0
celery==5.3.4
redis==5.0.0
pytest==7.4.3
EOF

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 创建最小化的后端框架

```bash
# 创建目录结构
mkdir -p app/{models,schemas,routes,services,tasks,utils}
mkdir tests migrations

# 创建必要文件
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py
```

### 3️⃣ 创建 `app/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "TrustAgency Backend"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./trustagency.db"
    
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str = ""  # 添加你的 API key
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### 4️⃣ 创建 `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "TrustAgency Backend API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
```

### 5️⃣ 运行!

```bash
python app/main.py
```

访问: http://localhost:8001/docs ✅

---

## 🏗️ 周计划 (7 天)

### Day 1: 数据库 + 认证 (8 小时)

**目标**: 能够登录

**任务**:
1. [ ] 创建数据库模型 (AdminUser, Platform, Article, Task)
2. [ ] 创建认证端点 (`POST /api/admin/login`)
3. [ ] 测试登录

**代码模板**:

```python
# app/models/admin.py
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# app/routes/admin.py
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/login")
async def login(username: str, password: str, db: Session):
    # 查询管理员
    # 验证密码
    # 返回 token
    pass
```

**检查**:
```bash
curl -X POST "http://localhost:8001/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 应该返回: {"access_token": "...", "token_type": "bearer"}
```

---

### Day 2: 平台 API (6 小时)

**目标**: 能够 CRUD 平台

**任务**:
1. [ ] `GET /api/platforms` - 获取所有平台
2. [ ] `POST /api/admin/platforms` - 创建平台
3. [ ] `PUT /api/admin/platforms/:id` - 编辑平台
4. [ ] `DELETE /api/admin/platforms/:id` - 删除平台
5. [ ] 测试所有端点

**快速测试**:
```bash
# 获取所有平台
curl "http://localhost:8001/api/platforms"

# 创建平台 (需要 token)
curl -X POST "http://localhost:8001/api/admin/platforms" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Platform",
    "slug": "test-platform",
    "rating": 4.5
  }'
```

---

### Day 3: 文章 API (6 小时)

**目标**: 能够管理文章

**任务**:
1. [ ] `GET /api/articles` - 获取文章列表
2. [ ] `GET /api/articles/:slug` - 获取单篇文章
3. [ ] `POST /api/admin/articles` - 创建文章
4. [ ] 支持按分类过滤
5. [ ] 测试

---

### Day 4: AI 生成系统第 1 部分 (8 小时)

**目标**: 能够提交生成任务

**任务**:
1. [ ] 配置 Celery + Redis
2. [ ] 创建 AI 服务 (`app/services/ai_service.py`)
3. [ ] 创建异步任务 (`app/tasks/generation.py`)
4. [ ] `POST /api/admin/generate/create` - 开始生成

**启动 Celery Worker**:
```bash
# 终端 1: Redis
redis-server

# 终端 2: Celery Worker
celery -A app.celery_app worker --loglevel=info

# 终端 3: FastAPI
python app/main.py
```

---

### Day 5: AI 生成系统第 2 部分 (6 小时)

**目标**: 能够查询生成进度和结果

**任务**:
1. [ ] `GET /api/admin/generate/tasks/:task_id` - 查询进度
2. [ ] `GET /api/admin/generate/tasks/:task_id/results` - 获取结果
3. [ ] 实时进度更新
4. [ ] 错误处理和重试

---

### Day 6: 前端集成 (6 小时)

**目标**: 前端显示真实数据

**任务**:
1. [ ] 创建 `site/assets/js/api.js`
2. [ ] 更新 `site/index.html` 加载真实平台
3. [ ] 更新知识库页面
4. [ ] 测试所有页面

---

### Day 7: 测试和优化 (4 小时)

**目标**: 系统稳定可靠

**任务**:
1. [ ] 编写单元测试
2. [ ] 性能优化
3. [ ] 错误处理完善
4. [ ] 文档完成

**测试命令**:
```bash
pytest tests/
```

---

## 🎯 最小化 MVP 路线图

如果时间紧张，按这个优先级:

### Week 1 必做 (优先级 P0)

```
Day 1-2: 
✅ 数据库 + 管理员认证
✅ 平台 API (CRUD)

Day 3-4:
✅ 文章 API (CRUD)
✅ 前端集成 (动态加载)

Day 5:
✅ 测试和修复
```

### Week 2 可做 (优先级 P1)

```
✅ AI 内容生成系统
✅ 缓存优化
✅ 监控和日志
```

---

## 🔧 常见问题

### Q: 如何添加管理员账户?

```python
# 在 app/main.py 中添加
from app.models import AdminUser
from app.utils.security import hash_password

def init_admin(db: Session):
    admin = db.query(AdminUser).filter(
        AdminUser.username == "admin"
    ).first()
    
    if not admin:
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@example.com"
        )
        db.add(admin)
        db.commit()

# 在应用启动时调用
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    init_admin(db)
    db.close()
```

### Q: 如何处理 CORS 错误?

```python
# 在 app/main.py 中配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # 前端地址
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q: 如何测试 API?

```bash
# 使用 Postman (UI)
# 或用命令行:
curl -X GET "http://localhost:8001/api/platforms"

# 或用 Python:
import requests
response = requests.get("http://localhost:8001/api/platforms")
print(response.json())
```

### Q: 如何部署到生产?

```bash
# 1. 使用 Gunicorn
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# 2. 或用 Docker
docker-compose up

# 3. 前面用 Nginx 反向代理
```

---

## 📊 完整的文件清单

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              ← 主应用
│   ├── config.py            ← 配置
│   ├── database.py          ← 数据库连接
│   ├── celery_app.py        ← Celery 配置
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── admin.py         ← 管理员模型
│   │   ├── platform.py      ← 平台模型
│   │   ├── article.py       ← 文章模型
│   │   └── task.py          ← 任务模型
│   │
│   ├── schemas/
│   │   ├── admin.py         ← 数据验证
│   │   ├── platform.py
│   │   ├── article.py
│   │   └── generation.py
│   │
│   ├── routes/
│   │   ├── admin.py         ← 认证端点
│   │   ├── platforms.py     ← 平台端点
│   │   ├── articles.py      ← 文章端点
│   │   └── generation.py    ← 生成端点
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── platform_service.py
│   │   ├── article_service.py
│   │   └── ai_service.py    ← AI 集成
│   │
│   ├── tasks/
│   │   └── generation.py    ← Celery 任务
│   │
│   └── utils/
│       ├── security.py      ← JWT, 密码
│       ├── auth_dependencies.py
│       └── cache.py
│
├── tests/                   ← 单元测试
│   ├── test_admin.py
│   ├── test_platforms.py
│   ├── test_articles.py
│   └── test_generation.py
│
├── migrations/              ← 数据库迁移
├── requirements.txt
├── .env                     ← 本地配置
├── .env.example             ← 示例配置
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## ✨ 辅助工具

### VSCode 插件推荐

```
- Python (Microsoft)
- Pylance (类型检查)
- REST Client (API 测试)
- SQLite (数据库浏览)
```

### 有用的命令

```bash
# 启动 FastAPI 开发服务器
python -m uvicorn app.main:app --reload

# 查看自动生成的 API 文档
# http://localhost:8001/docs

# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app

# 检查代码质量
flake8 app/
black app/  # 格式化代码
```

---

## 🎓 学习资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 教程](https://docs.sqlalchemy.org/)
- [Celery 文档](https://docs.celeryproject.io/)
- [OpenAI API 文档](https://platform.openai.com/docs/)

---

## ⏱️ 时间预估

| 任务 | 耗时 | 优先级 |
|------|------|--------|
| 数据库 + 认证 | 8h | P0 |
| 平台 API | 6h | P0 |
| 文章 API | 6h | P0 |
| 前端集成 | 6h | P0 |
| AI 生成 (基础) | 8h | P1 |
| AI 生成 (完整) | 6h | P1 |
| 测试和优化 | 6h | P1 |
| **总计** | **46h** | - |

**1-2 周完成所有核心功能** 🚀

---

## 🎯 成功标志

当你完成以下内容时，说明后端已经就绪:

- ✅ 可以登录获取 JWT token
- ✅ 可以 CRUD 平台和文章
- ✅ 前端页面显示真实数据
- ✅ 可以提交 AI 生成任务
- ✅ 可以查询生成进度
- ✅ 生成的文章保存到数据库
- ✅ 所有 API 有文档
- ✅ 基础错误处理完整
- ✅ 通过测试检查

---

**现在准备好开始了吗?** 🚀

建议下一步:
1. 看 IMPLEMENTATION_GUIDE.md 获得详细代码
2. 按照周计划一步步做
3. 有问题随时问我!

**Good luck! 💪**
