# 🎨 FastAPI 管理后台集成 - 快速方案

**目标**: 1-2 小时内有一个可用的管理界面  
**方案**: FastAPI-Admin 库 + SQLAlchemy + SQLite

---

## ⚡ 极速集成（1 小时）

### Step 1: 安装依赖

```bash
pip install fastapi-admin==0.7.1
pip install aiosqlite
pip install sqlalchemy-admin==0.1.0
```

### Step 2: 更新 `app/main.py`

在你的 FastAPI 应用中集成管理后台:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from fastapi_admin.depends import get_resources
from fastapi_admin.models import APIResponse
from fastapi_admin.app import Admin
from starlette.responses import RedirectResponse

from app.config import get_settings
from app.database import engine, Base
from app.models import AdminUser, Platform, Article, AIGenerationTask

settings = get_settings()

# 初始化数据库
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 管理后台集成 ====================

# 创建 Admin 实例
admin = Admin(
    app=app,
    engine=engine,
    title="TrustAgency 管理后台",
    logo_url="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
    favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
)

# 注册模型到管理后台
@admin.register_model
class AdminUserAdmin:
    name = "管理员"
    icon = "fas fa-users"
    page_size = 50
    page_size_options = [10, 50, 100]
    
    model = AdminUser
    
    columns = [
        AdminUser.id,
        AdminUser.username,
        AdminUser.email,
        AdminUser.created_at,
        AdminUser.last_login,
    ]
    
    # 可编辑的字段
    editable_columns = [
        AdminUser.email,
    ]

@admin.register_model
class PlatformAdmin:
    name = "交易平台"
    icon = "fas fa-building"
    page_size = 50
    
    model = Platform
    
    columns = [
        Platform.id,
        Platform.name,
        Platform.slug,
        Platform.rating,
        Platform.rank,
        Platform.commission_rate,
        Platform.regulated,
        Platform.updated_at,
    ]
    
    editable_columns = [
        Platform.name,
        Platform.description,
        Platform.rating,
        Platform.rank,
        Platform.commission_rate,
        Platform.min_leverage,
        Platform.max_leverage,
    ]
    
    # 搜索字段
    search_columns = [
        Platform.name,
        Platform.slug,
    ]
    
    # 排序字段
    order_columns = [
        (Platform.rank, "排名"),
        (Platform.rating, "评分"),
    ]

@admin.register_model
class ArticleAdmin:
    name = "文章管理"
    icon = "fas fa-file-alt"
    page_size = 20
    
    model = Article
    
    columns = [
        Article.id,
        Article.title,
        Article.slug,
        Article.category,
        Article.status,
        Article.ai_generated,
        Article.view_count,
        Article.published_at,
    ]
    
    editable_columns = [
        Article.title,
        Article.content,
        Article.category,
        Article.status,
    ]
    
    search_columns = [
        Article.title,
        Article.slug,
    ]
    
    order_columns = [
        (Article.view_count, "浏览数"),
        (Article.published_at, "发布时间"),
    ]

@admin.register_model
class AIGenerationTaskAdmin:
    name = "AI 生成任务"
    icon = "fas fa-magic"
    page_size = 20
    
    model = AIGenerationTask
    
    columns = [
        AIGenerationTask.id,
        AIGenerationTask.task_id,
        AIGenerationTask.status,
        AIGenerationTask.total_count,
        AIGenerationTask.success_count,
        AIGenerationTask.failed_count,
        AIGenerationTask.created_at,
        AIGenerationTask.completed_at,
    ]
    
    search_columns = [
        AIGenerationTask.task_id,
    ]
    
    order_columns = [
        (AIGenerationTask.created_at, "创建时间"),
        (AIGenerationTask.status, "状态"),
    ]

# ==================== 原有 API 路由 ====================

@app.get("/")
async def root():
    return {"message": "TrustAgency Backend API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/admin")
async def redirect_to_admin():
    """重定向到管理后台"""
    return RedirectResponse(url="/admin/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
```

### Step 3: 运行

```bash
python app/main.py
```

### Step 4: 访问

```
📊 管理后台: http://localhost:8001/admin
📚 API 文档: http://localhost:8001/docs
```

---

## 🎨 更专业的方案（6-8 小时）

如果想要一个**漂亮的专业后台**，我可以为你创建一个 React + TypeScript 的管理系统。

包括:
- ✅ 用户友好的界面
- ✅ 完整的 CRUD 操作
- ✅ AI 生成任务可视化
- ✅ 实时进度显示
- ✅ 数据统计仪表板
- ✅ 响应式设计

这需要额外 6-8 小时，但会有一个**专业级的管理后台**。

---

## 🤔 你的选择？

**A. 快速方案** (现在就用 FastAPI-Admin，1h)
- 优点: 快速出品，能立即使用
- 缺点: 界面一般，但功能完整

**B. 专业方案** (我给你开发完整的 React 后台，6-8h)
- 优点: 界面美观，用户友好
- 缺点: 多花一周时间

**C. 两个都要** (先快速方案应急，再开发专业方案)
- 优点: 现在就能用，逐步升级
- 缺点: 要做两次工作

**我的建议**: **先做 A，后期升级到 B**

---

你想要哪个方案？我现在就为你实现！
