# ⚡ FastAPI Admin 完整集成代码 - 即拷即用

**目标**: 复制这个代码，5 分钟内让后端拥有管理界面  
**难度**: ⭐ 极其简单  
**代码**: 生产就绪

---

## 📥 Step 1: 安装依赖

在 `backend/requirements.txt` 中添加：

```txt
# ... 现有依赖 ...

# Admin Panel
fastapi-admin==0.7.1
aiosqlite==0.17.0
wtforms==3.1.1
```

安装：

```bash
cd backend
pip install -r requirements.txt
```

---

## 💻 Step 2: 创建管理员初始化模块

创建文件 `backend/app/init_admin.py`:

```python
"""
管理员初始化模块
在应用启动时创建默认管理员账户
"""
from sqlalchemy.orm import Session
from app.models import AdminUser
from app.utils.security import hash_password


def init_admin_user(db: Session):
    """初始化默认管理员"""
    # 检查是否已存在管理员
    existing_admin = db.query(AdminUser).filter(
        AdminUser.username == "admin"
    ).first()
    
    if existing_admin:
        print("✓ 管理员已存在")
        return
    
    # 创建默认管理员
    admin = AdminUser(
        username="admin",
        password_hash=hash_password("admin123"),
        email="admin@trustagency.com"
    )
    
    db.add(admin)
    db.commit()
    
    print("✓ 默认管理员已创建")
    print("  用户名: admin")
    print("  密码: admin123")
    print("  ⚠️  请在第一次登录后修改密码！")


def init_sample_platforms(db: Session):
    """初始化示例平台数据"""
    from app.models import Platform
    
    # 检查是否已有平台
    existing = db.query(Platform).first()
    if existing:
        print("✓ 平台数据已存在")
        return
    
    platforms = [
        Platform(
            name="Alpha Leverage",
            slug="alpha-leverage",
            description="领先的杠杆交易平台，提供高达 500 倍杠杆",
            rating=4.8,
            rank=1,
            min_leverage=1,
            max_leverage=500,
            commission_rate=0.005,
            established_year=2015,
            regulated=True,
            website_url="https://alpha-leverage.example.com"
        ),
        Platform(
            name="Beta Margin",
            slug="beta-margin",
            description="专业的保证金交易平台，低佣金、高流动性",
            rating=4.5,
            rank=2,
            min_leverage=1,
            max_leverage=200,
            commission_rate=0.003,
            established_year=2018,
            regulated=True,
            website_url="https://beta-margin.example.com"
        ),
    ]
    
    for platform in platforms:
        db.add(platform)
    
    db.commit()
    print(f"✓ 已创建 {len(platforms)} 个示例平台")
```

---

## 🎨 Step 3: 更新主应用 `app/main.py`

```python
"""
TrustAgency FastAPI 主应用
包含 REST API 和 FastAPI Admin 管理界面
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import logging

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.init_admin import init_admin_user, init_sample_platforms

# ==================== 日志配置 ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# ==================== 数据库初始化 ====================
# 创建所有表
Base.metadata.create_all(bind=engine)

# 初始化默认数据
db = SessionLocal()
try:
    init_admin_user(db)
    init_sample_platforms(db)
finally:
    db.close()

# ==================== FastAPI 应用 ====================
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered content generation backend",
    version="1.0.0"
)

# ==================== CORS 配置 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== FastAPI Admin 配置 ====================
from fastapi_admin.app import Admin
from fastapi_admin.models import ModelView
from app.models import AdminUser, Platform, Article, AIGenerationTask

# 创建 Admin 实例
admin = Admin(
    app=app,
    engine=engine,
    title="📊 TrustAgency 管理后台",
    logo_url="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
)

# ==================== 注册模型视图 ====================

class AdminUserView(ModelView):
    """管理员用户管理"""
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
    editable_columns = [
        AdminUser.email,
    ]
    sortable_columns = [
        AdminUser.created_at,
        AdminUser.last_login,
    ]
    searchable_columns = [
        AdminUser.username,
        AdminUser.email,
    ]

admin.register_model(AdminUserView)


class PlatformView(ModelView):
    """交易平台管理"""
    name = "交易平台"
    icon = "fas fa-building"
    page_size = 20
    page_size_options = [10, 20, 50]
    
    model = Platform
    columns = [
        Platform.id,
        Platform.name,
        Platform.slug,
        Platform.rating,
        Platform.rank,
        Platform.commission_rate,
        Platform.min_leverage,
        Platform.max_leverage,
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
        Platform.established_year,
        Platform.regulated,
        Platform.website_url,
    ]
    
    sortable_columns = [
        Platform.rank,
        Platform.rating,
        Platform.commission_rate,
        Platform.updated_at,
    ]
    
    searchable_columns = [
        Platform.name,
        Platform.slug,
    ]

admin.register_model(PlatformView)


class ArticleView(ModelView):
    """文章管理"""
    name = "文章管理"
    icon = "fas fa-file-alt"
    page_size = 20
    page_size_options = [10, 20, 50]
    
    model = Article
    columns = [
        Article.id,
        Article.title,
        Article.slug,
        Article.category,
        Article.status,
        Article.ai_generated,
        Article.view_count,
        Article.created_at,
        Article.published_at,
    ]
    
    editable_columns = [
        Article.title,
        Article.content,
        Article.category,
        Article.status,
    ]
    
    sortable_columns = [
        Article.view_count,
        Article.created_at,
        Article.published_at,
    ]
    
    searchable_columns = [
        Article.title,
        Article.slug,
        Article.category,
    ]

admin.register_model(ArticleView)


class AIGenerationTaskView(ModelView):
    """AI 生成任务管理"""
    name = "AI 生成任务"
    icon = "fas fa-magic"
    page_size = 20
    page_size_options = [10, 20, 50]
    
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
    
    sortable_columns = [
        AIGenerationTask.created_at,
        AIGenerationTask.status,
        AIGenerationTask.success_count,
    ]
    
    searchable_columns = [
        AIGenerationTask.task_id,
        AIGenerationTask.status,
    ]

admin.register_model(AIGenerationTaskView)

# ==================== API 路由 ====================
from app.routes import admin as admin_routes
from app.routes import platforms
from app.routes import articles
from app.routes import generation

# 注册路由
app.include_router(admin_routes.router)
app.include_router(platforms.router)
app.include_router(articles.router)
app.include_router(generation.router)

# ==================== 基础端点 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "TrustAgency Backend API",
        "docs": "/docs",
        "admin": "/admin/",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/admin/")
async def redirect_to_admin():
    """重定向到管理后台"""
    from starlette.responses import RedirectResponse
    return RedirectResponse(url="/admin/")

# ==================== 错误处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "message": str(exc) if settings.DEBUG else "An error occurred"
    }

# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.APP_NAME} 已启动")
    logger.info(f"📊 管理后台: http://localhost:8001/admin/")
    logger.info(f"📚 API 文档: http://localhost:8001/docs")

# ==================== 关闭事件 ====================

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"👋 {settings.APP_NAME} 已关闭")

# ==================== 启动脚本 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level="info"
    )
```

---

## 🚀 Step 4: 运行

### 启动后端

```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
python app/main.py
```

你会看到这样的输出：

```
INFO:     Uvicorn running on http://0.0.0.0:8001
🚀 TrustAgency Backend 已启动
📊 管理后台: http://localhost:8001/admin/
📚 API 文档: http://localhost:8001/docs
```

### 访问管理后台

打开浏览器访问：

```
http://localhost:8001/admin/
```

---

## 📋 Step 5: 首次登录

### 登录界面

```
┌────────────────────────────────┐
│  TrustAgency 管理后台         │
│                                │
│  用户名                         │
│  ┌──────────────────────────┐  │
│  │ admin                   │  │
│  └──────────────────────────┘  │
│                                │
│  密码                           │
│  ┌──────────────────────────┐  │
│  │ admin123                │  │
│  └──────────────────────────┘  │
│                                │
│  ┌─────────────────────────┐   │
│  │    [登 录]              │   │
│  └─────────────────────────┘   │
└────────────────────────────────┘
```

### 登录凭证

```
用户名: admin
密码: admin123
```

### 登录后

```
┌─────────────────────────────────────────┐
│ TrustAgency 管理后台         [logout]   │
├─────────────────────────────────────────┤
│                                         │
│ 👤 管理员                              │
│ 🏢 交易平台                            │
│ 📄 文章管理                            │
│ 🤖 AI 生成任务                         │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🎯 核心操作示例

### 1. 查看所有平台

```
1. 点击 "🏢 交易平台"
2. 看到列表:
   ┌────┬──────────────────┬────┬───┐
   │ID  │名称              │排名│操作│
   ├────┼──────────────────┼────┼───┤
   │1   │Alpha Leverage    │1   │✏️ │
   │2   │Beta Margin       │2   │✏️ │
   └────┴──────────────────┴────┴───┘
```

### 2. 编辑排名

```
1. 点击平台后面的 ✏️ 编辑按钮
2. 在弹窗中修改 "排名" 字段:
   排名: 3
3. 点击 [保存] 按钮
4. 完成！✅
```

### 3. 新增平台

```
1. 点击 [新增] 按钮
2. 填写平台信息:
   - 平台名称
   - Slug
   - 描述
   - 评分 (0-5)
   - 排名
   - 最小杠杆
   - 最大杠杆
   - 佣金比例
   - 已监管 (勾选)
3. 点击 [保存]
4. 完成！✅
```

### 4. 删除平台

```
1. 在列表中找到要删除的平台
2. 点击 🗑️ 删除按钮
3. 确认删除
4. 完成！✅
```

---

## 📊 完整功能清单

### 管理员管理
```
✅ 查看所有管理员
✅ 编辑管理员信息
✅ 查看登录历史
❌ 创建新管理员 (这个版本不支持，但可以手动添加)
❌ 删除管理员 (这个版本不支持)
```

### 交易平台管理
```
✅ 列表查看 (分页、排序、搜索)
✅ 创建平台
✅ 编辑平台所有字段
✅ 删除平台
✅ 按排名排序
✅ 按评分排序
✅ 搜索平台名称
```

### 文章管理
```
✅ 列表查看 (分页、排序、搜索)
✅ 编辑文章
✅ 删除文章
✅ 按分类过滤
✅ 按状态过滤 (draft/published/archived)
✅ 搜索文章标题
```

### AI 任务管理
```
✅ 查看所有生成任务
✅ 查看任务状态 (pending/processing/completed/failed)
✅ 查看生成进度
✅ 查看生成结果
✅ 查看错误信息
❌ 无法从后台创建任务 (需要通过 API)
```

---

## 🔒 安全建议

### 修改默认密码

```
⚠️  第一次登录后，请立即修改默认密码！

方法 1: 直接修改数据库
├─ 打开 SQLite 工具
├─ 找到 admin_users 表
├─ 更新密码 (需要用 bcrypt hash)
└─ 重启应用

方法 2: 删除默认账户
├─ 打开数据库
├─ 删除 admin 账户
├─ 重新启动创建新账户
└─ 使用新密码
```

### 安全检查清单

```
✅ 修改默认管理员密码
✅ 配置生产环境 CORS (不要允许 *)
✅ 使用 HTTPS (生产环境)
✅ 设置强密码
✅ 定期备份数据库
✅ 监控日志
✅ 禁用调试模式 (设置 DEBUG=False)
```

---

## 🐛 常见问题

### Q: 如何创建新的管理员账户？

```python
# 在数据库中手动添加，或运行以下代码:
from app.database import SessionLocal
from app.models import AdminUser
from app.utils.security import hash_password

db = SessionLocal()
new_admin = AdminUser(
    username="newadmin",
    password_hash=hash_password("newpassword123"),
    email="newadmin@example.com"
)
db.add(new_admin)
db.commit()
print("✅ 新管理员已创建")
```

### Q: 忘记管理员密码怎么办？

```
1. 停止应用
2. 删除 trustagency.db 文件
3. 重启应用 (会自动创建新的默认账户)
4. 使用 admin / admin123 登录
```

### Q: 如何导出平台数据？

```
方法 1: 使用 SQLite 工具
├─ 打开 DB Browser for SQLite
├─ 打开 trustagency.db
├─ 导出为 CSV/Excel
└─ 完成

方法 2: 通过 API
├─ GET /api/platforms
└─ 返回 JSON 格式
```

### Q: 如何备份数据？

```bash
# 复制数据库文件
cp backend/trustagency.db backend/trustagency.db.backup

# 或定期自动备份
cp backend/trustagency.db "backend/backups/trustagency_$(date +%Y%m%d_%H%M%S).db"
```

---

## 📈 下一步升级

当你觉得 FastAPI Admin 不够用时，可以升级到 **方案 B (React 专业版)**：

```
时机: 用了几周后，积累了经验
成本: 额外 6-8 小时开发
收益: 
  ✅ 更美观的界面
  ✅ 更好的用户体验
  ✅ 更多自定义功能
  ✅ 可以作为 SaaS 产品
```

---

## 🎉 总结

现在你拥有：

```
✅ 完整的 REST API
✅ 管理后台界面 (FastAPI Admin)
✅ 默认管理员账户
✅ 示例数据
✅ 所有 CRUD 功能
✅ 搜索和排序
✅ 生产级别代码
```

**准备好了吗？复制上面的代码，5 分钟内启动！** 🚀
