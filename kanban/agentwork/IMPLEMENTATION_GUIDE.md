# 🎯 AI 内容生成系统 - 实施步骤指南

**文档**: 详细的逐步实现指南  
**语言**: Python + FastAPI  
**任务队列**: Celery + Redis  
**主要功能**: 管理员 AI 批量文章生成  

---

## 📋 第一阶段: 项目初始化 (2-3 小时)

### Step 1.1: 创建项目结构

```bash
# 在项目根目录创建后端文件夹
mkdir -p trustagency-backend
cd trustagency-backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 创建项目目录结构
mkdir -p app/{models,schemas,routes,services,tasks,utils}
mkdir -p tests
mkdir -p migrations

# 创建初始文件
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py
```

### Step 1.2: 安装依赖

创建 `requirements.txt`:

```
# Core
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
# 选择一个:
# sqlite (开发用)
# psycopg2-binary (PostgreSQL)

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Async Tasks
celery==5.3.4
redis==5.0.0

# AI Integration
openai==1.3.0
# langchain==0.1.0 (可选)

# API Documentation
pydantic-settings==2.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.0
```

安装:
```bash
pip install -r requirements.txt
```

### Step 1.3: 创建配置文件

`app/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "TrustAgency Backend"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./trustagency.db"
    # 或 PostgreSQL: "postgresql://user:password@localhost/trustagency"
    
    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change_me_in_production"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 24 小时
    
    # Redis 配置 (用于 Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### Step 1.4: 创建 `.env` 文件

```bash
DEBUG=True
DATABASE_URL=sqlite:///./trustagency.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123  # 改成强密码

SECRET_KEY=your-super-secret-key-change-in-production
OPENAI_API_KEY=sk-...  # 添加你的 OpenAI 密钥

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
```

---

## 📚 第二阶段: 数据库设置 (2-3 小时)

### Step 2.1: 数据库连接

`app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# 创建数据库引擎
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 2.2: 创建 SQLAlchemy 模型

`app/models/admin.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
from datetime import datetime

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
```

`app/models/platform.py`:

```python
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Enum, DateTime, func
from app.database import Base
from datetime import datetime
import enum

class Platform(Base):
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    logo_url = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    min_leverage = Column(Integer, default=1)
    max_leverage = Column(Integer, default=100)
    commission_rate = Column(Float, default=0.0)
    rating = Column(Float, default=3.0, index=True)
    rank = Column(Integer, nullable=True, index=True)
    established_year = Column(Integer, nullable=True)
    regulated = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
```

`app/models/article.py`:

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, DateTime, func
from app.database import Base
from datetime import datetime
import enum

class ArticleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    category = Column(String, index=True)  # wiki, guide, faq
    status = Column(Enum(ArticleStatus), default=ArticleStatus.draft, index=True)
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String, nullable=True)
    ai_prompt = Column(Text, nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
```

`app/models/task.py`:

```python
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, func
from app.database import Base
from datetime import datetime
import enum

class TaskStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class AIGenerationTask(Base):
    __tablename__ = "ai_generation_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)  # Celery task ID
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, index=True)
    titles = Column(Text)  # JSON 格式
    model = Column(String)
    system_prompt = Column(Text)
    category = Column(String)
    total_count = Column(Integer)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_article_ids = Column(Text, nullable=True)  # JSON 格式
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
```

### Step 2.3: 创建所有模型的 `__init__.py`

`app/models/__init__.py`:

```python
from app.models.admin import AdminUser
from app.models.platform import Platform
from app.models.article import Article, ArticleStatus
from app.models.task import AIGenerationTask, TaskStatus

__all__ = [
    "AdminUser",
    "Platform",
    "Article",
    "ArticleStatus",
    "AIGenerationTask",
    "TaskStatus"
]
```

### Step 2.4: 初始化数据库

`app/database.py` (添加初始化函数):

```python
from app.models import Base  # 导入所有模型

def init_db():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)

# 主程序中调用
# 从 app/main.py 中调用
```

---

## 🔐 第三阶段: 认证系统 (2-3 小时)

### Step 3.1: 创建安全工具

`app/utils/security.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证 JWT Token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

### Step 3.2: 创建认证依赖

`app/utils/auth_dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.utils.security import verify_token

security = HTTPBearer()

async def get_current_admin(credentials: HTTPAuthCredentials = Depends(security)):
    """获取当前管理员"""
    token = credentials.credentials
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return payload.get("sub")  # 返回管理员用户名
```

### Step 3.3: Pydantic 数据验证模型

`app/schemas/admin.py`:

```python
from pydantic import BaseModel
from datetime import datetime

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    username: str
    email: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### Step 3.4: 创建认证路由

`app/routes/admin.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser
from app.schemas.admin import AdminLogin, TokenResponse, AdminResponse
from app.utils.security import verify_password, hash_password, create_access_token
from app.utils.auth_dependencies import get_current_admin
from datetime import timedelta

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/login", response_model=TokenResponse)
async def login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """管理员登录"""
    # 从数据库查询管理员
    admin = db.query(AdminUser).filter(
        AdminUser.username == credentials.username
    ).first()
    
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # 创建 JWT Token
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=timedelta(minutes=1440)
    )
    
    return {"access_token": access_token}

@router.get("/me", response_model=AdminResponse)
async def get_admin_info(
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取管理员信息"""
    admin = db.query(AdminUser).filter(
        AdminUser.username == username
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return admin

@router.post("/logout")
async def logout(username: str = Depends(get_current_admin)):
    """登出 (可选，客户端删除 token 即可)"""
    return {"message": "Logged out successfully"}
```

---

## 🤖 第四阶段: AI 内容生成核心系统 (4-6 小时)

### Step 4.1: Celery 配置

`app/celery_app.py`:

```python
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "trustagency",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 分钟
)
```

### Step 4.2: AI 服务

`app/services/ai_service.py`:

```python
import json
from openai import OpenAI
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_article(
        self, 
        title: str, 
        system_prompt: str, 
        model: str = "gpt-4"
    ) -> str:
        """
        生成单篇文章
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"请为以下标题创建一篇高质量的文章:\n{title}"
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating article for '{title}': {str(e)}")
            raise

ai_service = AIService()
```

### Step 4.3: Celery 任务

`app/tasks/generation.py`:

```python
import json
import time
import logging
from celery import shared_task
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Article, AIGenerationTask, ArticleStatus, TaskStatus
from app.services.ai_service import ai_service
from app.database import Base
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    """将文本转换为 slug"""
    import re
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'-+', '-', slug).strip('-')

@shared_task(bind=True)
def generate_articles_task(
    self,
    task_id: str,
    titles: list,
    model: str,
    system_prompt: str,
    category: str
):
    """
    异步生成多篇文章
    """
    db = SessionLocal()
    
    try:
        # 更新任务状态为处理中
        task = db.query(AIGenerationTask).filter(
            AIGenerationTask.task_id == task_id
        ).first()
        
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        task.status = TaskStatus.processing
        task.started_at = datetime.utcnow()
        db.commit()
        
        created_articles = []
        failed_titles = []
        
        for i, title in enumerate(titles):
            try:
                # 调用 AI 服务生成内容
                content = await ai_service.generate_article(
                    title=title,
                    system_prompt=system_prompt,
                    model=model
                )
                
                # 创建文章
                slug = slugify(title)
                # 确保 slug 唯一
                counter = 1
                original_slug = slug
                while db.query(Article).filter(Article.slug == slug).first():
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                article = Article(
                    title=title,
                    slug=slug,
                    content=content,
                    category=category,
                    status=ArticleStatus.draft,
                    ai_generated=True,
                    ai_model=model,
                    ai_prompt=system_prompt
                )
                
                db.add(article)
                db.commit()
                db.refresh(article)
                
                created_articles.append(article.id)
                task.success_count += 1
                
                logger.info(f"Generated article: {title}")
                
            except Exception as e:
                logger.error(f"Failed to generate article for '{title}': {str(e)}")
                failed_titles.append(title)
                task.failed_count += 1
            
            # 更新进度
            progress = (i + 1) / len(titles)
            task.total_count = len(titles)
            db.commit()
            
            # 输出进度到 Celery
            self.update_state(
                state='PROGRESS',
                meta={'current': i + 1, 'total': len(titles), 'status': 'Generating...'}
            )
            
            # 避免 API 限流
            time.sleep(2)
        
        # 任务完成
        task.status = TaskStatus.completed
        task.completed_at = datetime.utcnow()
        task.created_article_ids = json.dumps(created_articles)
        task.error_message = json.dumps(failed_titles) if failed_titles else None
        
        db.commit()
        
        logger.info(f"Task {task_id} completed: {task.success_count}/{len(titles)} articles generated")
        
        return {
            "task_id": task_id,
            "status": "completed",
            "success_count": task.success_count,
            "failed_count": task.failed_count,
            "created_articles": created_articles
        }
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        
        task = db.query(AIGenerationTask).filter(
            AIGenerationTask.task_id == task_id
        ).first()
        
        if task:
            task.status = TaskStatus.failed
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        db.close()
```

### Step 4.4: 生成功能的 API 路由

`app/routes/generation.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import json
import uuid
from datetime import datetime

from app.database import get_db
from app.models import AIGenerationTask, TaskStatus
from app.utils.auth_dependencies import get_current_admin
from app.tasks.generation import generate_articles_task

router = APIRouter(prefix="/api/admin", tags=["generation"])

class GenerationRequest(BaseModel):
    titles: list[str]  # ["标题1", "标题2", ...]
    model: str = "gpt-4"
    system_prompt: str
    category: str  # wiki, guide, faq
    publish: bool = False  # 是否自动发布

class GenerationResponse(BaseModel):
    task_id: str
    status: str

@router.post("/generate/create", response_model=GenerationResponse)
async def create_generation_task(
    request: GenerationRequest,
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    开始 AI 内容生成任务
    """
    # 验证输入
    if not request.titles or len(request.titles) == 0:
        raise HTTPException(status_code=400, detail="No titles provided")
    
    if not request.system_prompt:
        raise HTTPException(status_code=400, detail="System prompt is required")
    
    # 创建任务记录
    task_id = str(uuid.uuid4())
    
    task = AIGenerationTask(
        task_id=task_id,
        status=TaskStatus.pending,
        titles=json.dumps(request.titles),
        model=request.model,
        system_prompt=request.system_prompt,
        category=request.category,
        total_count=len(request.titles)
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 提交 Celery 异步任务
    generate_articles_task.delay(
        task_id=task_id,
        titles=request.titles,
        model=request.model,
        system_prompt=request.system_prompt,
        category=request.category
    )
    
    return {
        "task_id": task_id,
        "status": "pending"
    }

@router.get("/generate/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取生成任务进度
    """
    task = db.query(AIGenerationTask).filter(
        AIGenerationTask.task_id == task_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "total_count": task.total_count,
        "success_count": task.success_count,
        "failed_count": task.failed_count,
        "progress": f"{task.success_count + task.failed_count}/{task.total_count}",
        "created_at": task.created_at
    }

@router.get("/generate/tasks/{task_id}/results")
async def get_task_results(
    task_id: str,
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取生成结果
    """
    task = db.query(AIGenerationTask).filter(
        AIGenerationTask.task_id == task_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    created_articles = []
    if task.created_article_ids:
        created_articles = json.loads(task.created_article_ids)
    
    failed_titles = []
    if task.error_message:
        failed_titles = json.loads(task.error_message)
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "success_count": task.success_count,
        "failed_count": task.failed_count,
        "created_articles": created_articles,
        "failed_titles": failed_titles
    }
```

---

## 📦 第五阶段: 其他 API 端点 (3-4 小时)

### Step 5.1: 平台管理

`app/routes/platforms.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Platform
from app.utils.auth_dependencies import get_current_admin

router = APIRouter(tags=["platforms"])

class PlatformCreate(BaseModel):
    name: str
    slug: str
    description: str
    # ... 其他字段

class PlatformResponse(PlatformCreate):
    id: int
    rating: float
    rank: int
    
    class Config:
        from_attributes = True

@router.get("/api/platforms", response_model=list[PlatformResponse])
async def list_platforms(db: Session = Depends(get_db)):
    """获取所有平台 (公开 API)"""
    platforms = db.query(Platform).order_by(Platform.rank).all()
    return platforms

@router.get("/api/platforms/{platform_id}", response_model=PlatformResponse)
async def get_platform(platform_id: int, db: Session = Depends(get_db)):
    """获取单个平台详情"""
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform

@router.post("/api/admin/platforms", response_model=PlatformResponse)
async def create_platform(
    platform: PlatformCreate,
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建平台 (管理员 API)"""
    new_platform = Platform(**platform.dict())
    db.add(new_platform)
    db.commit()
    db.refresh(new_platform)
    return new_platform

@router.put("/api/admin/platforms/{platform_id}", response_model=PlatformResponse)
async def update_platform(
    platform_id: int,
    platform: PlatformCreate,
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新平台"""
    db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not db_platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    for key, value in platform.dict().items():
        setattr(db_platform, key, value)
    
    db.commit()
    db.refresh(db_platform)
    return db_platform

@router.delete("/api/admin/platforms/{platform_id}")
async def delete_platform(
    platform_id: int,
    username: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除平台"""
    db_platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not db_platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    db.delete(db_platform)
    db.commit()
    return {"message": "Platform deleted"}
```

---

## 🚀 第六阶段: 主应用入口 (1-2 小时)

### Step 6.1: 创建 FastAPI 应用

`app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.routes import admin, platforms, articles, generation

settings = get_settings()

# 初始化数据库
init_db()

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered content generation backend",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(admin.router)
app.include_router(platforms.router)
app.include_router(articles.router)
app.include_router(generation.router)

@app.get("/")
async def root():
    return {
        "message": "TrustAgency Backend API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

---

## 🐳 Docker 配置

### Step 7.1: Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY . .

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 7.2: docker-compose.yml

```yaml
version: '3.8'

services:
  # FastAPI 应用
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/trustagency
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app

  # PostgreSQL 数据库
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: trustagency
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis (用于 Celery)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Celery Worker (后台任务)
  celery_worker:
    build: .
    command: celery -A app.tasks.generation worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/trustagency
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
      - backend

  # Celery Flower (监控)
  celery_flower:
    build: .
    command: celery -A app.tasks.generation flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
      - celery_worker

volumes:
  postgres_data:
```

---

## ▶️ 启动步骤

### 开发模式

```bash
# 终端 1: FastAPI 应用
source venv/bin/activate
cd trustagency-backend
python -m uvicorn app.main:app --reload

# 终端 2: Redis
redis-server

# 终端 3: Celery Worker
celery -A app.celery_app worker --loglevel=info

# 终端 4: Celery Flower (监控)
celery -A app.celery_app flower
```

### 访问:
- API: http://localhost:8000
- 文档: http://localhost:8000/docs
- Flower 监控: http://localhost:5555

### 生产模式

```bash
docker-compose up -d
```

---

## ✅ 测试检查清单

- [ ] 管理员可以登录
- [ ] 获取 JWT Token
- [ ] 获取管理员信息
- [ ] 创建平台
- [ ] 编辑平台
- [ ] 删除平台
- [ ] 创建 AI 生成任务
- [ ] 查询任务进度
- [ ] 获取生成的文章
- [ ] 发布文章
- [ ] 前端能获取真实平台数据
- [ ] 前端能显示真实文章

---

**现在你已经有了完整的实施步骤!** 🎉

下一步: 按照这个指南逐步实现，任何问题都可以问我！
