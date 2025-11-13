"""
FastAPI 应用主文件
"""
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import and_

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title=os.getenv("API_TITLE", "TrustAgency API"),
    description=os.getenv("API_DESCRIPTION", "Admin CMS with AI Content Generation"),
    version=os.getenv("API_VERSION", "1.0.0"),
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS 配置 - 允许所有来源（本地开发）
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost", "http://localhost:80", "http://localhost:8000", "http://localhost:8001"]')
if isinstance(cors_origins, str) and cors_origins.strip():
    import json
    try:
        cors_origins = json.loads(cors_origins)
    except json.JSONDecodeError:
        cors_origins = ["http://localhost:8001"]
else:
    cors_origins = ["http://localhost:8001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 IMPORTANT: 挂载静态文件必须在注册路由之前！
# StaticFiles 挂载必须最先执行，否则后续路由会拦截请求
import os
import sys

def get_backend_dir():
    """
    获取后端目录的绝对路径，支持多环境
    
    优先级顺序：
    1. 环境变量 BACKEND_DIR（推荐用于 Docker 和生产）
    2. __file__ 相对路径（本地开发和 Docker）
    3. 当前工作目录（作为备选）
    4. Docker 容器内的默认路径
    
    这种方法确保在各种环境下都能正确识别路径
    """
    candidates = [
        # 1. 环境变量（最高优先级）
        os.getenv("BACKEND_DIR"),
        # 2. 相对于当前文件的相对路径（最可靠）
        str(Path(__file__).parent.parent.resolve()),
        # 3. 当前工作目录
        os.getcwd(),
        # 4. Docker 容器内的默认路径
        "/app",
    ]
    
    for candidate in candidates:
        if candidate:
            try:
                path = Path(candidate).resolve()
                if path.exists():
                    return path
            except (OSError, ValueError):
                # 某些路径在当前环境中不可访问
                continue
    
    # 最后的保障：使用 __file__ 计算路径
    return Path(__file__).parent.parent.resolve()


# 获取后端目录
BACKEND_DIR = get_backend_dir()
ADMIN_DIR = BACKEND_DIR / "site" / "admin"

# 调试输出（仅在非生产环境）
if os.getenv("DEBUG", "False") == "True":
    print(f"[INIT] BACKEND_DIR: {BACKEND_DIR}", file=sys.stderr)
    print(f"[INIT] ADMIN_DIR: {ADMIN_DIR}", file=sys.stderr)
    print(f"[INIT] ADMIN_DIR exists: {ADMIN_DIR.exists()}", file=sys.stderr)

# 挂载通用静态文件夹（用于上传的图片等）
static_path = BACKEND_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 🔥 导入所有数据库模型，确保 SQLAlchemy 可以识别所有表
# 这必须在路由导入之前进行，以便 init_db() 可以创建所有表
from app.models import AdminUser, Platform, Section, Category, Article, AIGenerationTask, AIConfig
from app.database import get_db

# 导入路由
from app.routes import auth, platforms, articles, tasks, sections, categories, ai_configs, upload
from app.admin import setup_admin_routes

# 导入响应模块
from fastapi.responses import FileResponse

# 注册路由
app.include_router(auth.router)
app.include_router(platforms.router)
app.include_router(sections.router)
app.include_router(categories.router)
app.include_router(articles.router)
app.include_router(tasks.router)
app.include_router(ai_configs.router)
app.include_router(upload.router)
from app.routes import admin_platforms
app.include_router(admin_platforms.router)

# 设置管理后台路由
setup_admin_routes(app)

# 显式处理 /admin/ 和 /admin 路由，确保返回 index.html
@app.get("/admin/", include_in_schema=False)
async def admin_index():
    """返回管理后台索引页面"""
    admin_index_path = ADMIN_DIR / "index.html"
    
    if admin_index_path.exists():
        return FileResponse(str(admin_index_path), media_type="text/html; charset=utf-8")
    
    # 如果找不到，返回错误并打印调试信息
    import os
    debug_info = {
        "detail": "Admin page not found",
        "admin_dir": str(ADMIN_DIR),
        "admin_index_path": str(admin_index_path),
        "exists": admin_index_path.exists(),
        "cwd": os.getcwd(),
    }
    return debug_info

# 处理 /admin 重定向到 /admin/
@app.get("/admin", include_in_schema=False)
async def admin_redirect():
    """重定向 /admin 到 /admin/"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/admin/", status_code=307)

# 挂载其他 admin 静态文件（CSS, JS等）
if ADMIN_DIR.exists():
    app.mount("/admin", StaticFiles(directory=str(ADMIN_DIR), html=True), name="admin")

# 初始化数据库端点（用于启动时初始化）
@app.get("/api/init", include_in_schema=False)
async def init_endpoint():
    """初始化数据库 - 内部使用"""
    try:
        from app.database import init_db
        init_db()
        return {"status": "success", "message": "Database initialized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 调试端点 - 检查管理员用户
@app.get("/api/debug/admin-users", include_in_schema=False)
async def debug_admin_users():
    """调试 - 列出所有管理员用户"""
    try:
        from app.database import SessionLocal
        from app.models import AdminUser
        db = SessionLocal()
        
        # 检查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        users = db.query(AdminUser).all()
        db.close()
        return {
            "count": len(users),
            "tables": tables,
            "users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

# 调试端点 - 创建默认管理员
@app.post("/api/debug/reset-admin-password", include_in_schema=False)
async def debug_reset_admin_password():
    """调试 - 重置管理员密码为admin123"""
    try:
        from app.database import SessionLocal
        from app.models import AdminUser
        from app.utils.security import hash_password
        
        db = SessionLocal()
        
        # 查找admin用户
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            return {"status": "error", "message": "Admin user not found"}
        
        # 重置密码
        admin.hashed_password = hash_password("admin123")
        db.commit()
        
        return {
            "status": "success",
            "message": "Password reset to admin123",
            "user": {"id": admin.id, "username": admin.username}
        }
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}


@app.post("/api/debug/create-admin", include_in_schema=False)
async def debug_create_admin():
    """调试 - 创建默认管理员用户"""
    try:
        from app.database import SessionLocal
        from app.models import AdminUser
        from app.utils.security import hash_password
        from datetime import datetime
        
        db = SessionLocal()
        
        # 检查是否已存在
        existing = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if existing:
            return {"status": "exists", "user": {"id": existing.id, "username": existing.username}}
        
        # 创建管理员
        admin = AdminUser(
            username="admin",
            email="admin@trustagency.com",
            full_name="Administrator",
            hashed_password=hash_password("admin123"),
            is_active=True,
            is_superadmin=True,
            created_at=datetime.utcnow(),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        return {
            "status": "created",
            "user": {
                "id": admin.id,
                "username": admin.username,
                "email": admin.email,
                "is_active": admin.is_active,
                "is_superadmin": admin.is_superadmin
            }
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

# 健康检查端点
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "TrustAgency Backend is running"
    }

# 公开文章预览路由 - /article/:slug
@app.get("/article/{slug}")
async def view_article(slug: str, db: Session = Depends(get_db)):
    """
    公开文章查看页面
    返回HTML页面，直接嵌入文章数据和Schema标签（服务端生成）
    """
    from sqlalchemy.orm import joinedload
    import json
    from bs4 import BeautifulSoup
    
    # 查询已发布的文章
    article = db.query(Article).options(joinedload(Article.section)).filter(
        and_(Article.slug == slug, Article.is_published == True)
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 '{slug}' 不存在或未发布")
    
    # 增加浏览量
    article.view_count = (article.view_count or 0) + 1
    db.add(article)
    db.commit()
    
    # 从article_view.html读取基础模板
    article_view_html = BACKEND_DIR / "static" / "article_view.html"
    if not article_view_html.exists():
        raise HTTPException(status_code=500, detail="文章预览页面不存在")
    
    # 读取HTML模板
    html_content = article_view_html.read_text(encoding='utf-8')
    
    # 准备文章数据JSON（与API响应格式一致）
    article_data = {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "content": article.content,
        "summary": article.summary,
        "section_id": article.section_id,
        "section_name": article.section.name if article.section else "未分类",
        "category_name": article.category_name,
        "author_id": article.author_id,
        "is_published": article.is_published,
        "view_count": article.view_count,
        "like_count": article.like_count,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "published_at": article.published_at.isoformat() if article.published_at else None,
    }
    
    # 生成Schema标签（服务端生成，而非客户端动态生成）
    # 提取纯文本和图片
    soup = BeautifulSoup(article.content, 'html.parser')
    plain_text = soup.get_text().replace('\n', ' ').strip()
    plain_text = ' '.join(plain_text.split())  # 清理空白
    
    # 提取所有图片URL
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            # 完整化URL
            if src.startswith('http'):
                images.append(src)
            elif src.startswith('/'):
                images.append(f"http://{os.getenv('SERVER_HOST', 'localhost:8001')}{src}")
            else:
                images.append(f"http://{os.getenv('SERVER_HOST', 'localhost:8001')}/{src}")
    
    # 生成摘要
    auto_summary = plain_text[:160] + ('…' if len(plain_text) > 160 else '')
    summary_text = (article.summary and article.summary.strip()) or auto_summary
    
    # 构建Schema.org Article 结构化数据（最新标准）
    schema_data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"http://{os.getenv('SERVER_HOST', 'localhost:8001')}/article/{article.slug}#article",
        "identifier": article.id,
        "headline": article.title,
        "description": summary_text,
        "articleBody": article.content,  # 完整HTML内容
        "articleSection": article.category_name or article.section.name if article.section else "未分类",
        "datePublished": (article.published_at or article.created_at).isoformat() if article.published_at or article.created_at else None,
        "dateModified": (article.published_at or article.created_at).isoformat() if article.published_at or article.created_at else None,
        "author": {
            "@type": "Person",
            "name": "Admin"
        },
        "publisher": {
            "@type": "Organization",
            "name": "TrustAgency"
        },
        "inLanguage": "zh-CN",
        "mainEntityOfPage": f"http://{os.getenv('SERVER_HOST', 'localhost:8001')}/article/{article.slug}",
        "image": images if images else None,  # 所有图片
        "wordCount": len(plain_text.split()),
        "isAccessibleForFree": True
    }
    
    # 移除None值
    schema_data = {k: v for k, v in schema_data.items() if v is not None}
    
    # 在HTML中嵌入文章数据和Schema标签（服务端生成）
    article_json = json.dumps(article_data, ensure_ascii=False)
    schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)
    
    schema_script = f'''<script type="application/ld+json">
{schema_json}
</script>
<script>window.__ARTICLE_DATA__ = {article_json};</script>'''
    
    html_content = html_content.replace('</head>', f'{schema_script}\n</head>')
    
    return HTMLResponse(content=html_content, status_code=200)

# 主前端路由 - 服务主站点的 index.html
SITE_DIR = BACKEND_DIR.parent / "site"

@app.get("/", include_in_schema=False)
async def main_index():
    """返回主站点的索引页面"""
    main_index_path = SITE_DIR / "index.html"
    
    if main_index_path.exists():
        return FileResponse(str(main_index_path), media_type="text/html; charset=utf-8")
    
    # 如果找不到，返回API信息
    return {
        "name": "TrustAgency API",
        "version": os.getenv("API_VERSION", "1.0.0"),
        "docs": "/api/docs"
    }

# 挂载主前端的静态资源
site_assets_dir = SITE_DIR / "assets"
if site_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(site_assets_dir)), name="site_assets")

# 挂载其他主站点的目录
for subdir in ["platforms", "guides", "wiki", "qa", "compare", "about", "legal"]:
    subdir_path = SITE_DIR / subdir
    if subdir_path.exists():
        app.mount(f"/{subdir}", StaticFiles(directory=str(subdir_path), html=True), name=f"site_{subdir}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=os.getenv("DEBUG", "True") == "True"
    )
