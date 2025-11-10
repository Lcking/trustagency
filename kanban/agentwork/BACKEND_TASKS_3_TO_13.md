# 后端开发 Task 3-13 详细规范

**项目**: TrustAgency 管理系统  
**文档**: Task 3 ~ Task 13 的完整实现规范  

---

## 🎯 Task 3: 管理员认证系统实现

### 目标
实现管理员登录、JWT 认证、密码加密、权限验证。

### 3.1 安全工具模块 (`app/utils/security.py`)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import os

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# HTTP Bearer 认证
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """获取当前用户（中间件）"""
    token = credentials.credentials
    payload = verify_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username
```

### 3.2 认证服务 (`app/services/auth_service.py`)

```python
from sqlalchemy.orm import Session
from app.models.admin_user import AdminUser
from app.schemas.admin import AdminCreate, AdminLogin
from app.utils.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status

class AuthService:
    @staticmethod
    def create_admin_user(db: Session, admin_create: AdminCreate) -> AdminUser:
        """创建管理员"""
        # 检查用户是否存在
        existing_user = db.query(AdminUser).filter(
            AdminUser.username == admin_create.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # 创建新用户
        hashed_password = hash_password(admin_create.password)
        admin_user = AdminUser(
            username=admin_create.username,
            email=admin_create.email,
            full_name=admin_create.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user
    
    @staticmethod
    def authenticate_user(db: Session, login: AdminLogin) -> AdminUser:
        """验证用户并返回 token"""
        user = db.query(AdminUser).filter(
            AdminUser.username == login.username
        ).first()
        
        if not user or not verify_password(login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is inactive"
            )
        
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> AdminUser:
        """根据用户名获取用户"""
        return db.query(AdminUser).filter(AdminUser.username == username).first()
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """改变密码"""
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid old password")
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        return True
```

### 3.3 认证路由 (`app/routes/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.admin import AdminLogin, AdminCreate, AdminResponse
from app.services.auth_service import AuthService
from app.utils.security import create_access_token, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/api/admin", tags=["auth"])

@router.post("/login", response_model=dict)
async def login(login: AdminLogin, db: Session = Depends(get_db)):
    """管理员登录"""
    user = AuthService.authenticate_user(db, login)
    
    # 创建 token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=1440)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.get("/me", response_model=AdminResponse)
async def get_me(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    user = AuthService.get_user_by_username(db, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=AdminResponse)
async def register(admin_create: AdminCreate, db: Session = Depends(get_db)):
    """创建新管理员（仅超级管理员可用）"""
    user = AuthService.create_admin_user(db, admin_create)
    return user

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """改变密码"""
    user = AuthService.get_user_by_username(db, current_user)
    AuthService.change_password(db, user.id, old_password, new_password)
    return {"detail": "Password changed successfully"}
```

### 3.4 初始化脚本 (`app/init_db.py`)

```python
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.admin_user import AdminUser
from app.models.platform import Platform
from app.models.article import Article
from app.models.ai_task import AIGenerationTask
from app.utils.security import hash_password
from app.models import Base

def init_db():
    """初始化数据库，创建表和默认管理员"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否存在默认管理员
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            # 创建默认管理员
            admin = AdminUser(
                username="admin",
                email="admin@trustagency.com",
                full_name="Administrator",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_superadmin=True
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员创建成功 (admin / admin123)")
        else:
            print("✅ 管理员已存在")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
```

### 测试用例 (Task 3)

```yaml
测试 3.1: 密码加密和验证
  步骤:
    1. hash_password("test123")
    2. verify_password("test123", hashed)
    3. verify_password("wrong", hashed)
  验证:
    - hash 和原密码不同
    - 正确密码验证成功
    - 错误密码验证失败
  预期: ✅ 密码安全系统正常

测试 3.2: Token 创建和验证
  步骤:
    1. create_access_token({"sub": "admin"})
    2. verify_token(token)
    3. verify_token(invalid_token)
  验证:
    - Token 生成成功
    - Token 验证成功返回 payload
    - 无效 token 抛出异常
  预期: ✅ JWT 系统正常

测试 3.3: 用户创建
  步骤:
    1. POST /api/admin/register
       {username: "test", email: "test@test.com", password: "pass123"}
    2. 检查响应
    3. 重复创建相同用户名
  验证:
    - 第一个请求返回 200 + 用户信息
    - 第二个请求返回 400 错误
  预期: ✅ 用户创建系统正常

测试 3.4: 用户登录
  步骤:
    1. POST /api/admin/login {username: "admin", password: "admin123"}
    2. 检查响应中的 token
    3. 使用 token GET /api/admin/me
  验证:
    - 登录成功返回 access_token
    - Token 有效可获取用户信息
  预期: ✅ 登录系统正常

测试 3.5: 密码改变
  步骤:
    1. 登录获取 token
    2. POST /api/admin/change-password {old: "admin123", new: "newpass123"}
    3. 尝试用新密码登录
  验证:
    - 改密码成功
    - 新密码可用于登录
    - 旧密码无法登录
  预期: ✅ 密码改变系统正常
```

---

## 🎯 Task 4: 平台管理 API 实现

### 4.1 平台服务 (`app/services/platform_service.py`)

```python
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate
from fastapi import HTTPException, status
from typing import List, Optional

class PlatformService:
    @staticmethod
    def create_platform(db: Session, platform_create: PlatformCreate) -> Platform:
        """创建平台"""
        # 检查名称唯一性
        existing = db.query(Platform).filter(
            Platform.name == platform_create.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform name already exists"
            )
        
        platform = Platform(**platform_create.dict())
        db.add(platform)
        db.commit()
        db.refresh(platform)
        return platform
    
    @staticmethod
    def get_platforms(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "rank",
        order: str = "asc"
    ) -> tuple[List[Platform], int]:
        """获取平台列表（支持搜索、分页、排序）"""
        query = db.query(Platform).filter(Platform.is_active == True)
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    Platform.name.ilike(f"%{search}%"),
                    Platform.description.ilike(f"%{search}%")
                )
            )
        
        # 排序
        if sort_by == "rank":
            sort_column = Platform.rank
        elif sort_by == "rating":
            sort_column = Platform.rating
        elif sort_by == "commission":
            sort_column = Platform.commission_rate
        else:
            sort_column = Platform.created_at
        
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        total = query.count()
        platforms = query.offset(skip).limit(limit).all()
        return platforms, total
    
    @staticmethod
    def get_platform(db: Session, platform_id: int) -> Platform:
        """获取单个平台"""
        platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        return platform
    
    @staticmethod
    def update_platform(
        db: Session,
        platform_id: int,
        platform_update: PlatformUpdate
    ) -> Platform:
        """更新平台"""
        platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        
        update_data = platform_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(platform, field, value)
        
        db.commit()
        db.refresh(platform)
        return platform
    
    @staticmethod
    def delete_platform(db: Session, platform_id: int) -> bool:
        """删除平台"""
        platform = db.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        
        db.delete(platform)
        db.commit()
        return True
    
    @staticmethod
    def bulk_update_ranks(db: Session, rank_data: dict) -> bool:
        """批量更新排名（格式: {platform_id: rank}）"""
        for platform_id, rank in rank_data.items():
            platform = db.query(Platform).filter(Platform.id == int(platform_id)).first()
            if platform:
                platform.rank = rank
        db.commit()
        return True
```

### 4.2 平台路由 (`app/routes/platforms.py`)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.platform import PlatformCreate, PlatformUpdate, PlatformResponse
from app.services.platform_service import PlatformService
from app.utils.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/platforms", tags=["platforms"])

@router.get("", response_model=dict)
async def list_platforms(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    sort_by: str = Query("rank"),
    order: str = Query("asc"),
    db: Session = Depends(get_db)
):
    """获取平台列表"""
    platforms, total = PlatformService.get_platforms(
        db, skip, limit, search, sort_by, order
    )
    return {
        "data": platforms,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("", response_model=PlatformResponse)
async def create_platform(
    platform_create: PlatformCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建平台"""
    return PlatformService.create_platform(db, platform_create)

@router.get("/{platform_id}", response_model=PlatformResponse)
async def get_platform(platform_id: int, db: Session = Depends(get_db)):
    """获取单个平台"""
    return PlatformService.get_platform(db, platform_id)

@router.put("/{platform_id}", response_model=PlatformResponse)
async def update_platform(
    platform_id: int,
    platform_update: PlatformUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新平台"""
    return PlatformService.update_platform(db, platform_id, platform_update)

@router.delete("/{platform_id}")
async def delete_platform(
    platform_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除平台"""
    PlatformService.delete_platform(db, platform_id)
    return {"detail": "Platform deleted successfully"}

@router.post("/bulk-rank")
async def bulk_update_ranks(
    rank_data: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量更新排名"""
    PlatformService.bulk_update_ranks(db, rank_data)
    return {"detail": "Ranks updated successfully"}
```

### 测试用例 (Task 4)

```yaml
测试 4.1: 创建平台
  步骤:
    1. POST /api/platforms {name: "AlphaLeverage", rating: 4.8}
    2. 验证响应
    3. 重复创建相同名称
  验证:
    - 第一个成功返回平台信息
    - 第二个返回 400 错误
  预期: ✅ 平台创建正常

测试 4.2: 获取平台列表
  步骤:
    1. POST 创建 3 个平台
    2. GET /api/platforms
    3. GET /api/platforms?search=Alpha
    4. GET /api/platforms?sort_by=rating&order=desc
  验证:
    - 返回分页数据
    - 搜索功能正常
    - 排序功能正常
  预期: ✅ 列表查询正常

测试 4.3: 获取单个平台
  步骤:
    1. 创建平台获取 ID
    2. GET /api/platforms/{id}
    3. GET /api/platforms/999 (不存在)
  验证:
    - 存在的 ID 返回平台信息
    - 不存在的 ID 返回 404
  预期: ✅ 单个查询正常

测试 4.4: 更新平台
  步骤:
    1. 创建平台
    2. PUT /api/platforms/{id} {rank: 1, rating: 4.9}
    3. GET 验证更新
  验证:
    - 更新成功
    - 新数据已保存
  预期: ✅ 更新功能正常

测试 4.5: 删除平台
  步骤:
    1. 创建平台
    2. DELETE /api/platforms/{id}
    3. GET 验证删除
  验证:
    - 删除成功
    - 平台从列表消失
  预期: ✅ 删除功能正常

测试 4.6: 批量更新排名
  步骤:
    1. 创建 5 个平台
    2. POST /api/platforms/bulk-rank {1: 3, 2: 1, 3: 2, 4: 5, 5: 4}
    3. 检查更新
  验证:
    - 所有平台排名更新正确
  预期: ✅ 批量更新正常
```

---

## 🎯 Task 5: 文章管理 API 实现

### 5.1 文章服务 (`app/services/article_service.py`)

```python
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.article import Article
from app.models.admin_user import AdminUser
from app.schemas.article import ArticleCreate, ArticleUpdate
from fastapi import HTTPException, status
from typing import List, Optional
import slugify

class ArticleService:
    @staticmethod
    def _generate_slug(title: str) -> str:
        """生成 URL 友好的 slug"""
        base_slug = slugify.slugify(title, to_lower=True)
        return base_slug
    
    @staticmethod
    def create_article(
        db: Session,
        article_create: ArticleCreate,
        author_id: int
    ) -> Article:
        """创建文章"""
        # 生成 slug
        slug = ArticleService._generate_slug(article_create.title)
        
        # 检查 slug 唯一性
        existing = db.query(Article).filter(Article.slug == slug).first()
        if existing:
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        article = Article(
            **article_create.dict(),
            author_id=author_id,
            slug=slug
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        return article
    
    @staticmethod
    def get_articles(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        platform_id: Optional[int] = None,
        is_published: Optional[bool] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> tuple[List[Article], int]:
        """获取文章列表"""
        query = db.query(Article)
        
        # 过滤
        if search:
            query = query.filter(
                or_(
                    Article.title.ilike(f"%{search}%"),
                    Article.content.ilike(f"%{search}%")
                )
            )
        if category:
            query = query.filter(Article.category == category)
        if platform_id:
            query = query.filter(Article.platform_id == platform_id)
        if is_published is not None:
            query = query.filter(Article.is_published == is_published)
        
        # 排序
        if sort_by == "views":
            sort_column = Article.view_count
        elif sort_by == "likes":
            sort_column = Article.like_count
        else:
            sort_column = Article.created_at
        
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        total = query.count()
        articles = query.offset(skip).limit(limit).all()
        return articles, total
    
    @staticmethod
    def get_article(db: Session, article_id: int) -> Article:
        """获取单个文章"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    
    @staticmethod
    def update_article(
        db: Session,
        article_id: int,
        article_update: ArticleUpdate,
        author_id: int
    ) -> Article:
        """更新文章"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 检查权限
        if article.author_id != author_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        update_data = article_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)
        
        db.commit()
        db.refresh(article)
        return article
    
    @staticmethod
    def delete_article(db: Session, article_id: int, author_id: int) -> bool:
        """删除文章"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if article.author_id != author_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        db.delete(article)
        db.commit()
        return True
    
    @staticmethod
    def publish_article(db: Session, article_id: int, author_id: int) -> Article:
        """发布文章"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if article.author_id != author_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        article.is_published = True
        article.published_at = datetime.utcnow()
        db.commit()
        db.refresh(article)
        return article
```

### 5.2 文章路由 (`app/routes/articles.py`)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from app.services.article_service import ArticleService
from app.utils.security import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/articles", tags=["articles"])

@router.get("", response_model=dict)
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    category: str = Query(None),
    platform_id: int = Query(None),
    is_published: bool = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    articles, total = ArticleService.get_articles(
        db, skip, limit, search, category, platform_id, is_published, sort_by, order
    )
    return {
        "data": articles,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("", response_model=ArticleResponse)
async def create_article(
    article_create: ArticleCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建文章"""
    user = AuthService.get_user_by_username(db, current_user)
    return ArticleService.create_article(db, article_create, user.id)

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取单个文章"""
    return ArticleService.get_article(db, article_id)

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新文章"""
    user = AuthService.get_user_by_username(db, current_user)
    return ArticleService.update_article(db, article_id, article_update, user.id)

@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文章"""
    user = AuthService.get_user_by_username(db, current_user)
    ArticleService.delete_article(db, article_id, user.id)
    return {"detail": "Article deleted successfully"}

@router.post("/{article_id}/publish")
async def publish_article(
    article_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布文章"""
    user = AuthService.get_user_by_username(db, current_user)
    ArticleService.publish_article(db, article_id, user.id)
    return {"detail": "Article published successfully"}
```

---

## 快速继续

由于文档长度限制，我将在实现 Task 1 时同时提供其他 Tasks 的代码模板。

**现在开始实现吗？选择:**

1. **立即开始 Task 1**（项目初始化和环境配置）
2. **继续查看 Task 6-13 的规范**（FastAPI Admin、Celery、测试、部署）

