"""
FastAPI 应用主文件
"""
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import and_
import html

# 初始化日志系统
from app.utils.logging_setup import setup_logging
setup_logging()

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

SITE_NAME = os.getenv("SITE_NAME", "股票杠杆平台排行榜单")

# 公开站点基础 URL（用于 canonical / OG）
def get_public_site_url(request: Request) -> str:
    base_url = os.getenv("PUBLIC_SITE_URL")
    if base_url:
        return base_url.rstrip("/")
    return str(request.base_url).rstrip("/")

# CORS 配置 - 允许所有来源（本地开发）
cors_origins = os.getenv("CORS_ORIGINS", "")
if isinstance(cors_origins, str) and cors_origins.strip():
    import json
    try:
        cors_origins = json.loads(cors_origins)
    except json.JSONDecodeError:
        # 如果环境变量解析失败，使用默认列表
        cors_origins = ["http://localhost:8000", "http://localhost:8001", "http://127.0.0.1:8000", "http://127.0.0.1:8080"]
else:
    # 默认CORS白名单（本地开发环境）
    cors_origins = ["http://localhost:8000", "http://localhost:8001", "http://127.0.0.1:8000", "http://127.0.0.1:8080"]

# 调试：打印CORS配置
import sys
print(f"[CORS] Allowed origins: {cors_origins}", file=sys.stderr)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Gzip 压缩中间件 ====================
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

# ==================== 异常处理中间件 ====================
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""
    async def dispatch(self, request, call_next):
        from fastapi import HTTPException as FastAPIHTTPException
        from app.utils.error_handlers import (
            AppError, handle_app_error, handle_validation_error,
            handle_database_error, handle_general_error
        )
        from app.utils.exceptions import APIException
        
        try:
            response = await call_next(request)
            return response
        except AppError as exc:
            # 处理自定义应用错误
            return handle_app_error(exc)
        except APIException as exc:
            # 兼容旧的异常处理
            http_exc = exc.to_http_exception()
            return JSONResponse(
                status_code=http_exc.status_code,
                content=http_exc.detail,
            )
        except PydanticValidationError as exc:
            # 处理Pydantic验证错误
            return handle_validation_error(exc)
        except SQLAlchemyError as exc:
            # 处理数据库错误
            return handle_database_error(exc)
        except FastAPIHTTPException:
            # FastAPI HTTP异常直接抛出
            raise
        except Exception as exc:
            # 处理其他未捕获的异常
            import traceback
            error_msg = f"❌ Middleware caught: {exc.__class__.__name__}: {exc}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            sys.stderr.flush()
            return handle_general_error(exc)


# 注册异常处理中间件
app.add_middleware(ExceptionHandlerMiddleware)

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
from app.routes import auth, platforms, articles, tasks, sections, categories, ai_configs, upload, website_settings
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
app.include_router(website_settings.router)
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
@app.get("/article/{slug}", include_in_schema=False)
async def view_article(request: Request, slug: str, db: Session = Depends(get_db)):
    """公开文章查看页面 — 返回嵌入文章数据的HTML"""
    from sqlalchemy.orm import joinedload
    import json
    from bs4 import BeautifulSoup
    
    article = (
        db.query(Article)
        .options(joinedload(Article.section), joinedload(Article.category_obj))
        .filter(and_(Article.slug == slug, Article.is_published == True))
        .first()
    )
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或未发布")
    
    # 增加浏览量
    article.view_count = (article.view_count or 0) + 1
    db.add(article)
    db.commit()
    
    template_path = BACKEND_DIR / "static" / "article_view.html"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="模板文件不存在")
    html_content = template_path.read_text(encoding="utf-8")
    
    public_site_url = get_public_site_url(request)
    section_name = article.section.name if article.section else "未分类"
    category_name = article.category_obj.name if article.category_obj else "未分类"
    content_html = article.content or ""
    
    # 提取纯文本与图片
    try:
        soup = BeautifulSoup(content_html, "html.parser")
        plain_text = " ".join(soup.get_text().split())
    except Exception:
        plain_text = ""
    
    images: list[str] = []
    try:
        soup = BeautifulSoup(content_html, "html.parser")
        for img in soup.find_all("img"):
            src = (img.get("src") or "").strip()
            if not src:
                continue
            if src.startswith("http"):
                images.append(src)
            elif src.startswith("/"):
                images.append(f"{public_site_url}{src}")
            else:
                images.append(f"{public_site_url}/{src.lstrip('/')}")
    except Exception:
        pass
    
    auto_summary = (
        plain_text[:160] + ("…" if len(plain_text) > 160 else "") if plain_text else ""
    )
    summary_text = (article.summary and article.summary.strip()) or auto_summary
    
    seo_title = article.seo_title or article.title or SITE_NAME
    seo_description = article.meta_description or summary_text or ""
    seo_keywords = article.meta_keywords or ""
    
    article_url = f"{public_site_url}/article/{article.slug}"
    
    article_data = {
        "id": article.id,
        "title": article.title or "",
        "slug": article.slug,
        "content": content_html,
        "summary": article.summary or "",
        "section_name": section_name,
        "category_name": category_name,
        "view_count": article.view_count or 0,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "is_published": article.is_published,
        "seo_title": seo_title,
        "seo_keywords": seo_keywords,
        "seo_description": seo_description,
        "canonical_url": article_url,
    }
    
    pub_date = article.published_at or article.created_at
    pub_date_str = pub_date.isoformat() if pub_date else None
    
    schema_data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"{article_url}#article",
        "headline": article.title,
        "description": summary_text,
        "articleSection": category_name,
        "datePublished": pub_date_str,
        "mainEntityOfPage": article_url,
        "url": article_url,
        "author": {"@type": "Person", "name": "Admin"},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "inLanguage": "zh-CN",
        "image": images or None,
        "wordCount": len(plain_text.split()) if plain_text else 0,
    }
    schema_data = {k: v for k, v in schema_data.items() if v is not None}
    
    article_json = json.dumps(article_data, ensure_ascii=False)
    schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)
    
    # 组装 SSR 内容
    published_display = pub_date.strftime("%Y-%m-%d %H:%M") if pub_date else ""
    status_badge = (
        ""
        if article.is_published
        else '<span class="badge" style="background:#ffc107;color:#000">草稿</span>'
    )
    category_badge = (
        f'<span class="badge">分类 {html.escape(category_name)}</span>'
        if category_name
        else ""
    )
    summary_block = (
        f'<div class="summary-box"><strong>摘要：</strong>{html.escape(summary_text)}</div>'
        if summary_text
        else ""
    )
    public_link = (
        f'<p style="margin-top:24px;font-size:13px;color:#666;">公开链接：'
        f'<a href="/article/{article.slug}" target="_blank" rel="noopener">/article/{article.slug}</a></p>'
        if article.is_published and article.slug
        else ""
    )
    article_inner_html = f"""
        <h1>{html.escape(article.title or "")}</h1>
        <div class="meta">
          <span class="badge">栏目 {html.escape(section_name)}</span>
          {category_badge}
          {status_badge}
          <span>浏览 {article.view_count or 0}</span>
          {f'<span style="margin-left:8px">发布时间 {published_display}</span>' if published_display else ''}
        </div>
        {summary_block}
        <article class="content">{content_html}</article>
        {public_link}
    """
    
    # 使用 BeautifulSoup 修改整体 HTML，确保 meta / title / canonical 全量更新并注入 SSR 内容
    page_soup = BeautifulSoup(html_content, "html.parser")
    
    if page_soup.title:
        page_soup.title.string = f"{seo_title} - {SITE_NAME}"
    
    meta_map = {
        ("id", "seo-description"): ("content", seo_description),
        ("id", "seo-keywords"): ("content", seo_keywords),
        ("id", "og-title"): ("content", article.title or ""),
        ("id", "og-description"): ("content", seo_description),
        ("id", "og-url"): ("content", article_url),
        ("id", "twitter-title"): ("content", article.title or ""),
        ("id", "twitter-description"): ("content", seo_description),
    }
    for (attr_key, attr_val), (target_attr, target_value) in meta_map.items():
        tag = page_soup.find(attrs={attr_key: attr_val})
        if tag:
            tag[target_attr] = target_value
    
    canonical_tag = page_soup.find("link", {"id": "canonical"})
    if canonical_tag:
        canonical_tag["href"] = article_url
    
    container = page_soup.find(id="articleContainer")
    if container:
        container.clear()
        fragment = BeautifulSoup(article_inner_html, "html.parser")
        for child in fragment.contents:
            container.append(child)
    
    head_tag = page_soup.find("head")
    if head_tag:
        schema_tag = page_soup.new_tag("script", type="application/ld+json")
        schema_tag.string = schema_json
        head_tag.append(schema_tag)
        
        data_tag = page_soup.new_tag("script")
        data_tag.string = f"window.__ARTICLE_DATA__ = {article_json};"
        head_tag.append(data_tag)
    
    final_html = "<!DOCTYPE html>\n" + str(page_soup)
    return HTMLResponse(content=final_html, status_code=200)


# 公开平台详情页路由 - /platforms/:slug (SSR)
@app.get("/platforms/{slug}", include_in_schema=False)
async def view_platform(request: Request, slug: str, db: Session = Depends(get_db)):
    """公开平台详情页 — 返回嵌入平台数据的HTML（SSR）"""
    import json
    from app.models import Platform
    
    # 排除静态资源和列表页
    if slug in ['index.html', ''] or '.' in slug:
        # 这是静态文件请求，跳过
        raise HTTPException(status_code=404, detail="Not found")
    
    # 查询平台
    platform = db.query(Platform).filter(Platform.slug == slug, Platform.is_active == True).first()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    # 读取模板
    template_path = BACKEND_DIR / "static" / "platform_view.html"
    if not template_path.exists():
        raise HTTPException(status_code=500, detail="模板文件不存在")
    html_content = template_path.read_text(encoding="utf-8")
    
    public_site_url = get_public_site_url(request)
    
    # 构建平台数据
    platform_data = {
        "id": platform.id,
        "name": platform.name or "",
        "slug": platform.slug or "",
        "description": platform.description or "",
        "rating": float(platform.rating) if platform.rating else 0,
        "rank": platform.rank,
        "min_leverage": float(platform.min_leverage) if platform.min_leverage else 1,
        "max_leverage": float(platform.max_leverage) if platform.max_leverage else 100,
        "commission_rate": float(platform.commission_rate) if platform.commission_rate else 0,
        "is_regulated": platform.is_regulated,
        "logo_url": platform.logo_url,
        "website_url": platform.website_url,
        "introduction": platform.introduction,
        "main_features": platform.main_features,
        "fee_structure": platform.fee_structure,
        "account_opening_link": platform.account_opening_link,
        "safety_rating": platform.safety_rating or "B",
        "founded_year": platform.founded_year,
        "fee_rate": float(platform.fee_rate) if platform.fee_rate else None,
        "is_recommended": platform.is_recommended,
        "why_choose": platform.why_choose,
        "trading_conditions": platform.trading_conditions,
        "fee_advantages": platform.fee_advantages,
        "account_types": platform.account_types,
        "trading_tools": platform.trading_tools,
        "opening_steps": platform.opening_steps,
        "security_measures": platform.security_measures,
        "customer_support": platform.customer_support,
        "learning_resources": platform.learning_resources,
        "platform_type": platform.platform_type,
        "platform_badges": platform.platform_badges,
        "overview_intro": platform.overview_intro,
    }
    
    platform_json = json.dumps(platform_data, ensure_ascii=False)
    
    # SEO 数据
    seo_title = platform.name or "平台详情"
    seo_description = platform.description or f"{platform.name} 平台详情、费用、杠杆比例等信息"
    platform_url = f"{public_site_url}/platforms/{platform.slug}/"
    
    # 构建 Schema.org 数据
    schema_data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": platform.name,
        "description": seo_description,
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web",
        "url": platform_url,
    }
    if platform.rating:
        schema_data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(platform.rating),
            "ratingCount": "100"
        }
    schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)
    
    # 使用 BeautifulSoup 修改 HTML
    from bs4 import BeautifulSoup
    page_soup = BeautifulSoup(html_content, "html.parser")
    
    # 更新 title
    if page_soup.title:
        page_soup.title.string = f"{seo_title} - {SITE_NAME}"
    
    # 更新 meta 标签
    meta_map = {
        ("id", "seo-description"): ("content", seo_description),
        ("id", "og-title"): ("content", f"{seo_title} - {SITE_NAME}"),
        ("id", "og-description"): ("content", seo_description),
        ("id", "og-url"): ("content", platform_url),
        ("id", "twitter-title"): ("content", f"{seo_title} - {SITE_NAME}"),
        ("id", "twitter-description"): ("content", seo_description),
    }
    for (attr_key, attr_val), (target_attr, target_value) in meta_map.items():
        tag = page_soup.find(attrs={attr_key: attr_val})
        if tag:
            tag[target_attr] = target_value
    
    # 更新 canonical
    canonical_tag = page_soup.find("link", {"id": "canonical"})
    if canonical_tag:
        canonical_tag["href"] = platform_url
    
    # 更新面包屑
    breadcrumb_tag = page_soup.find(id="breadcrumb-name")
    if breadcrumb_tag:
        breadcrumb_tag.string = platform.name
    
    # 注入 Schema 和数据
    head_tag = page_soup.find("head")
    if head_tag:
        schema_tag = page_soup.new_tag("script", type="application/ld+json")
        schema_tag.string = schema_json
        head_tag.append(schema_tag)
        
        data_tag = page_soup.new_tag("script")
        data_tag.string = f"window.__PLATFORM_DATA__ = {platform_json};"
        head_tag.append(data_tag)
    
    final_html = "<!DOCTYPE html>\n" + str(page_soup)
    return HTMLResponse(content=final_html, status_code=200)


# 主前端路由 - 服务主站点的 index.html
def get_site_dir():
    """
    获取前端site目录的正确路径，支持多种环境配置
    
    优先级：
    1. 环境变量 SITE_DIR（推荐）
    2. /site（容器默认挂载点）
    3. BACKEND_DIR.parent / "site"（本地开发时的相对位置）
    4. 当前工作目录的 site 目录
    """
    candidates = [
        # 1. 环境变量设置的路径
        os.getenv("SITE_DIR"),
        # 2. 容器中的标准路径
        "/site",
        # 3. 相对于后端目录的位置（本地开发）
        BACKEND_DIR.parent / "site",
        # 4. 当前工作目录
        Path.cwd() / "site",
    ]
    
    for candidate in candidates:
        if candidate:
            try:
                path = Path(candidate).resolve()
                if path.exists():
                    return path
            except (OSError, ValueError):
                continue
    
    # 如果都找不到，返回首选项（通常在容器中会存在）
    return Path("/site")

SITE_DIR = get_site_dir()

if os.getenv("DEBUG", "False") == "True":
    print(f"[INIT] SITE_DIR: {SITE_DIR}", file=sys.stderr)
    print(f"[INIT] SITE_DIR exists: {SITE_DIR.exists()}", file=sys.stderr)

@app.get("/", include_in_schema=False)
async def main_index():
    """返回主站点的索引页面"""
    main_index_path = SITE_DIR / "index.html"
    
    # 调试信息
    import os
    debug_info = {
        "site_dir": str(SITE_DIR),
        "main_index_path": str(main_index_path),
        "exists": main_index_path.exists(),
        "cwd": os.getcwd(),
        "backend_dir": str(BACKEND_DIR),
    }
    
    if os.getenv("DEBUG", "False") == "True":
        print(f"[ROUTE /] {debug_info}", file=sys.stderr)
    
    if main_index_path.exists():
        return FileResponse(str(main_index_path), media_type="text/html; charset=utf-8")
    
    # 如果找不到，返回调试信息
    return debug_info

# 挂载主前端的静态资源
site_assets_dir = SITE_DIR / "assets"
if site_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(site_assets_dir)), name="site_assets")

# 挂载其他主站点的目录
# 注意：platforms 不在此列表中，因为平台详情页由 SSR 路由 /platforms/{slug} 处理
for subdir in ["guides", "wiki", "qa", "compare", "about", "legal"]:
    subdir_path = SITE_DIR / subdir
    if subdir_path.exists():
        app.mount(f"/{subdir}", StaticFiles(directory=str(subdir_path), html=True), name=f"site_{subdir}")

# 平台列表页单独处理（只提供 /platforms/ 的 index.html）
@app.get("/platforms/", include_in_schema=False)
async def platforms_index():
    """返回平台列表页"""
    platforms_index_path = SITE_DIR / "platforms" / "index.html"
    if platforms_index_path.exists():
        return FileResponse(str(platforms_index_path), media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="平台列表页不存在")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=os.getenv("DEBUG", "True") == "True"
    )
