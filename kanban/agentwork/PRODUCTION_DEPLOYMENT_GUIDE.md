# 🚀 生产部署准备指南 - TrustAgency

> **目标**: 确保从 GitHub 推送到生产环境部署时**零问题**

---

## 📋 核心问题分析

当前存在的问题：
1. ❌ `.env` 文件硬编码了本地路径 (`/Users/ck/Desktop/...`)
2. ❌ `ADMIN_DIR` 路径计算依赖 `__file__`，在不同环境会产生问题
3. ❌ 数据库在本地和 Docker 中分离（SQLite vs PostgreSQL）
4. ❌ 没有数据库迁移脚本，无法自动升级生产数据库
5. ❌ `.env` 可能被 commit 到 GitHub，暴露敏感信息

---

## 🔧 立即需要修复

### 1️⃣ **修复 .env 配置（最关键）**

编辑 `/Users/ck/Desktop/Project/trustagency/backend/.env`：

**当前（错误）：**
```
DATABASE_URL=sqlite:///./trustagency.db
BACKEND_DIR=/Users/ck/Desktop/Project/trustagency/backend
```

**应该改为（正确）：**
```
# 本地开发环境
DATABASE_URL=postgresql://trustagency:trustagency@localhost:5432/trustagency
BACKEND_DIR=${BACKEND_DIR:-.}

# 生产环境（通过容器环境变量覆盖）
# DATABASE_URL=postgresql://user:pass@prod-db:5432/db
```

**关键改进：**
- ✅ 使用 PostgreSQL（生产级别）
- ✅ 用环境变量 `${BACKEND_DIR:-.}` 而不是硬编码
- ✅ 支持容器环境变量覆盖

### 2️⃣ **创建 .env.example 模板**

```bash
cp /Users/ck/Desktop/Project/trustagency/backend/.env /Users/ck/Desktop/Project/trustagency/backend/.env.example
```

编辑 `.env.example`，移除敏感值：

```properties
# FastAPI
ENVIRONMENT=development
DEBUG=False
API_TITLE=TrustAgency API
API_VERSION=1.0.0
API_DESCRIPTION=Admin CMS with AI Content Generation

# Backend Directory (auto-detected if not set)
BACKEND_DIR=

# Database (使用生产级别数据库)
DATABASE_URL=postgresql://trustagency:trustagency@localhost:5432/trustagency

# Security (应该由环境变量提供)
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-in-production

# OpenAI (可选)
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# CORS
CORS_ORIGINS=["http://localhost:8000", "http://localhost:8001"]
```

### 3️⃣ **修复 app/main.py 中的路径逻辑**

改进 BACKEND_DIR 和 ADMIN_DIR 的计算：

```python
import os
from pathlib import Path

# 多层备选策略，支持多个环境
def get_backend_dir():
    """获取后端目录，支持多环境"""
    # 优先级顺序
    candidates = [
        # 1. 环境变量（推荐用于 Docker）
        os.getenv("BACKEND_DIR"),
        # 2. 相对于当前 app/main.py 的目录
        str(Path(__file__).parent.parent),
        # 3. 当前工作目录
        os.getcwd(),
        # 4. Docker 容器内的默认路径
        "/app",
    ]
    
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate).resolve()
    
    # 最后的保障
    return Path(__file__).parent.parent

BACKEND_DIR = get_backend_dir()
ADMIN_DIR = BACKEND_DIR / "site" / "admin"

# 调试输出
import sys
print(f"[INIT] BACKEND_DIR: {BACKEND_DIR}", file=sys.stderr)
print(f"[INIT] ADMIN_DIR: {ADMIN_DIR}", file=sys.stderr)
print(f"[INIT] ADMIN_DIR exists: {ADMIN_DIR.exists()}", file=sys.stderr)
```

---

## 📦 数据库迁移配置

### 创建 Alembic 迁移脚本

```bash
cd /Users/ck/Desktop/Project/trustagency/backend
alembic init migrations
```

编辑 `migrations/env.py`：

```python
# 支持自动生成迁移
from app.models import *  # 导入所有模型

target_metadata = Base.metadata
```

创建初始迁移：

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

生成迁移后，在 Docker 启动时运行：

```dockerfile
# 在 Dockerfile 中
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8001"]
```

---

## 🐳 Docker 生产部署配置

### 创建 `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: trustagency-backend-prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
      - DATABASE_URL=postgresql://trustagency:${DB_PASSWORD}@db:5432/trustagency
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - BACKEND_DIR=/app
    ports:
      - "8001:8001"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=trustagency
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=trustagency
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trustagency"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 创建 `.env.prod` 模板

```bash
# 生产环境配置（从不 commit 到 GitHub）
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-production-secret-key-here
DB_PASSWORD=your-strong-database-password
OPENAI_API_KEY=your-production-api-key
```

---

## ✅ 部署前检查清单

### 代码质量

- [ ] 所有硬编码路径已改为环境变量
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] `.env.example` 已创建并提交
- [ ] 没有敏感信息在代码中
- [ ] 所有依赖已固定版本（requirements.txt）

### 数据库

- [ ] 迁移脚本已创建
- [ ] 生产数据库使用 PostgreSQL
- [ ] 备份策略已制定
- [ ] 连接池已配置

### Docker

- [ ] Dockerfile 使用 non-root 用户
- [ ] 多阶段构建已配置
- [ ] 镜像大小已优化
- [ ] 健康检查已配置
- [ ] 资源限制已设置

### 安全

- [ ] SECRET_KEY 已更新
- [ ] 数据库密码已更改
- [ ] CORS 已正确配置
- [ ] HTTPS 已配置（如适用）
- [ ] API 认证已启用

### 监控

- [ ] 日志级别已设置（生产为 INFO）
- [ ] 健康检查端点已配置
- [ ] 错误追踪已设置
- [ ] 性能监控已配置

---

## 🚀 部署步骤

### 本地验证

```bash
# 1. 使用生产配置测试
export ENVIRONMENT=production
export DEBUG=False
source venv/bin/activate
python -m uvicorn app.main:app --port 8001

# 2. 测试 API
curl http://localhost:8001/api/health
```

### GitHub 推送

```bash
# 1. 确保敏感文件在 .gitignore 中
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo "*.db" >> .gitignore
echo "__pycache__" >> .gitignore

# 2. 提交代码
git add .
git commit -m "feat: production deployment ready"
git push origin main
```

### 生产部署

```bash
# 在生产服务器上

# 1. 克隆代码
git clone https://github.com/your-org/trustagency.git
cd trustagency

# 2. 创建生产 .env 文件
cp backend/.env.example backend/.env.prod
# 编辑 backend/.env.prod，填入生产值

# 3. 启动服务
docker-compose -f docker-compose.prod.yml --env-file backend/.env.prod up -d

# 4. 验证
docker-compose logs -f backend
```

---

## 📋 GitHub 推送前最终检查

```bash
# 1. 检查不应该 commit 的文件
git status

# 2. 验证 .gitignore
cat .gitignore | grep -E "\.env|\.db|__pycache__"

# 3. 检查是否有硬编码路径
grep -r "/Users/ck/Desktop" /Users/ck/Desktop/Project/trustagency/backend/app

# 4. 检查是否有敏感信息
grep -r "sk-" /Users/ck/Desktop/Project/trustagency/backend/app
grep -r "password" /Users/ck/Desktop/Project/trustagency/backend/app
```

---

## 📚 关键文件清单

应该在 GitHub 上：
- ✅ 所有应用代码
- ✅ Dockerfile 和 docker-compose.yml
- ✅ .env.example（无敏感值）
- ✅ requirements.txt
- ✅ Alembic 迁移脚本
- ✅ 部署文档

**不**应该在 GitHub 上：
- ❌ .env（包含敏感信息）
- ❌ *.db（本地数据库）
- ❌ __pycache__
- ❌ .venv 目录
- ❌ node_modules（如果有前端）

---

## 🎯 关键改动总结

| 项目 | 当前状态 | 应该修改 | 优先级 |
|------|--------|--------|------|
| 数据库 | SQLite（开发）+ PostgreSQL（Docker） | 统一 PostgreSQL | 🔴 高 |
| 路径 | 硬编码 `/Users/ck/Desktop/...` | 环境变量 | 🔴 高 |
| .env | 包含敏感信息 | .env.example + 环境变量 | 🔴 高 |
| 迁移 | 无迁移脚本（硬编码 init_db） | Alembic | 🟠 中 |
| 日志 | DEBUG=True | 环境相关 | 🟠 中 |
| 健康检查 | 基础配置 | 完整配置 | 🟡 低 |

---

## 📞 立即行动

1. ⏹️ **停止当前开发**
2. ✅ **按照本文档修复以上问题**
3. 🧪 **本地完整测试**
4. 📤 **推送到 GitHub**
5. 🚀 **生产部署**

---

**这样才能确保生产环境部署零问题！** 💪
