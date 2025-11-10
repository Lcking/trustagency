# 🚀 TrustAgency 本地部署 - 快速指南

**目标**: 在 5-10 分钟内启动完整的本地开发环境  
**前提条件**: Docker & Docker Compose 已安装  
**日期**: 2025-11-07

---

## ✅ 预部署检查清单 (2 分钟)

### 1. 检查 Docker 和 Docker Compose

```bash
# 检查 Docker 版本 (需要 20.10+)
docker --version

# 检查 Docker Compose 版本 (需要 2.0+)
docker-compose --version

# 验证 Docker 守护进程运行
docker ps
```

**预期输出**:
```
Docker version 20.10.0 (或更高)
Docker Compose version 2.0.0 (或更高)
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS     NAMES
(空列表表示没有运行的容器，这是正常的)
```

### 2. 检查项目文件结构

```bash
# 进入项目目录
cd /Users/ck/Desktop/Project/trustagency

# 检查关键文件
ls -la | grep -E "docker-compose|Dockerfile|\.env"
```

**应该看到**:
- ✅ `docker-compose.yml` (开发环境配置)
- ✅ `Dockerfile` (后端容器定义)
- ✅ `.env.example` (环境变量模板)
- ✅ `backend/` 目录
- ✅ `site/` 目录 (前端)

### 3. 检查环境变量

```bash
# 查看 .env.example
cat .env.example

# 如果需要，复制为 .env
cp .env.example .env

# 编辑 .env (如有特殊需求)
# vim .env
```

---

## 🚀 启动本地环境 (3-5 分钟)

### 方式 1: 使用自动化脚本 (推荐)

```bash
# 进入项目目录
cd /Users/ck/Desktop/Project/trustagency

# 执行启动脚本
./docker-start.sh

# 等待所有服务启动完成 (约 30-60 秒)
# 你会看到：
# ✓ Backend service started
# ✓ Frontend service started
# ✓ Database service started
# ✓ Redis service started
# ✓ Celery worker started
```

### 方式 2: 手动使用 Docker Compose

```bash
# 进入项目目录
cd /Users/ck/Desktop/Project/trustagency

# 构建镜像 (首次运行，约 2-3 分钟)
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

**预期输出**:
```
NAME                    STATUS              PORTS
trustagency-frontend    Up 30 seconds       0.0.0.0:5173->5173/tcp
trustagency-backend     Up 30 seconds       0.0.0.0:8000->8000/tcp
trustagency-postgres    Up 30 seconds       0.0.0.0:5432->5432/tcp
trustagency-redis       Up 30 seconds       0.0.0.0:6379->6379/tcp
trustagency-celery      Up 30 seconds       (no ports)
```

### 方式 3: 查看实时日志

```bash
# 查看所有服务的实时日志
docker-compose logs -f

# 或查看特定服务的日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery
```

---

## 🌐 访问本地应用 (立即可用)

### 前端应用
```
网址: http://localhost:5173
类型: Vue.js 3 管理后台
功能: 平台管理、文章管理、AI 任务监控
```

### 后端 API
```
基础 URL: http://localhost:8000
API 文档: http://localhost:8000/docs (Swagger UI)
重定向: http://localhost:8000/redoc (ReDoc)
健康检查: http://localhost:8000/health
```

### 数据库
```
数据库: PostgreSQL
主机: localhost
端口: 5432
用户: postgres (默认)
密码: postgres (默认)
数据库: trustagency
```

### 缓存层
```
Redis: localhost:6379
用途: 缓存、会话存储、Celery 消息队列
```

---

## 🔍 第 1 步: 验证前后端对接 (5 分钟)

### 1a. 检查后端健康状态

```bash
# 检查 API 健康
curl http://localhost:8000/health

# 预期响应:
# {"status": "ok", "timestamp": "2025-11-07T..."}
```

### 1b. 检查前端是否能访问

```bash
# 在浏览器中打开
open http://localhost:5173

# 或使用 curl 查看 HTML
curl http://localhost:5173 | head -20
```

### 1c. 检查 API 文档

```bash
# 打开 Swagger UI
open http://localhost:8000/docs

# 你应该看到所有 API 端点列表：
# - POST /auth/login (登录)
# - GET /platforms (获取平台列表)
# - POST /articles (创建文章)
# - POST /tasks/submit (提交 AI 任务)
# 等等
```

### 1d. 检查前端网络请求

```bash
# 在浏览器的开发者工具中查看 Network 标签
# 1. 打开浏览器: http://localhost:5173
# 2. 按 F12 打开开发者工具
# 3. 切换到 Network 标签
# 4. 刷新页面
# 5. 查看是否有对后端的请求 (应该看到来自 /api/* 的请求)
```

---

## 🔐 第 2 步: 测试后台登录 (3 分钟)

### 2a. 获取默认管理员凭证

```bash
# 查看后端环境变量或初始化脚本
cat backend/main.py | grep -A 10 "默认用户\|admin"

# 或查看数据库初始化脚本
ls -la backend/migrations/
```

### 2b. 登录后台管理系统

**方式 1: 使用 API 登录**

```bash
# 获取 JWT Token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 预期响应:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "user": {
#     "id": 1,
#     "username": "admin",
#     "email": "admin@trustagency.com"
#   }
# }
```

**方式 2: 使用前端界面登录**

```
1. 打开: http://localhost:5173
2. 输入用户名: admin
3. 输入密码: admin123
4. 点击 "登录"
5. 应该看到管理后台仪表板
```

### 2c. 测试 JWT 认证

```bash
# 获取 token 后，使用它调用受保护的 API
TOKEN="your_token_here"

curl -X GET http://localhost:8000/platforms \
  -H "Authorization: Bearer $TOKEN"

# 预期响应:
# {
#   "success": true,
#   "data": [
#     {
#       "id": 1,
#       "name": "My Platform",
#       "description": "..."
#     }
#   ]
# }
```

---

## 🤖 第 3 步: 检查 AI 集成 (5 分钟)

### 3a. 验证 Celery 任务队列

```bash
# 查看 Celery 工作进程状态
docker-compose logs celery | tail -20

# 预期输出应包含:
# [INFO/MainProcess] celery@... ready. Mingle initial stake out.
# [INFO/MainProcess] Connected to redis://redis:6379//
```

### 3b. 检查 OpenAI API 配置

```bash
# 查看后端环境变量中的 OpenAI 设置
grep -i "openai\|ai\|gpt" backend/.env 2>/dev/null || echo "未找到 OpenAI 配置"

# 查看后端代码中的 AI 集成
find backend -name "*.py" -exec grep -l "openai\|ChatGPT\|GPT" {} \;
```

### 3c. 提交 AI 生成任务 (完整流程)

```bash
# 步骤 1: 获取认证 Token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

# 步骤 2: 创建一个平台 (如果还没有)
PLATFORM=$(curl -s -X POST http://localhost:8000/platforms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Platform", "description": "For testing AI"}' | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

echo "Platform ID: $PLATFORM"

# 步骤 3: 创建一篇文章
ARTICLE=$(curl -s -X POST http://localhost:8000/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"platform_id\": $PLATFORM, \"title\": \"Test Article\", \"content\": \"Original content\"}" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

echo "Article ID: $ARTICLE"

# 步骤 4: 提交 AI 生成任务
curl -X POST http://localhost:8000/tasks/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"article_id\": $ARTICLE,
    \"task_type\": \"content_generation\",
    \"parameters\": {
      \"prompt\": \"根据以下内容生成更详细的版本\",
      \"max_tokens\": 500,
      \"temperature\": 0.7
    }
  }"
```

### 3d. 监控 AI 任务进度

```bash
# 获取任务状态
TASK_ID="your_task_id_here"

curl -X GET http://localhost:8000/tasks/$TASK_ID/status \
  -H "Authorization: Bearer $TOKEN"

# 查看 Celery 日志
docker-compose logs celery | grep "Task\|SUCCESS\|FAILURE" | tail -20

# 进入 Redis CLI 查看队列
docker-compose exec redis redis-cli
# 在 Redis CLI 中运行:
# KEYS *
# LLEN celery  # 查看队列长度
```

---

## 📊 快速测试场景

### 场景 1: 完整的内容生成流程

```bash
# 1. 登录获取 Token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. 创建平台
curl -X POST http://localhost:8000/platforms \
  -H "Authorization: Bearer TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "AI Platform", "description": "Platform for testing AI features"}'

# 3. 创建文章
curl -X POST http://localhost:8000/articles \
  -H "Authorization: Bearer TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"platform_id": 1, "title": "Original Article", "content": "Some content"}'

# 4. 生成 AI 内容
curl -X POST http://localhost:8000/tasks/submit \
  -H "Authorization: Bearer TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"article_id": 1, "task_type": "content_generation", "parameters": {"prompt": "Write better content"}}'

# 5. 查看任务状态
curl -X GET http://localhost:8000/tasks/1/status \
  -H "Authorization: Bearer TOKEN_HERE"
```

### 场景 2: 查看完整的管理后台

```
1. 打开浏览器: http://localhost:5173
2. 登录 (admin / admin123)
3. 查看仪表板
4. 创建新平台
5. 创建新文章
6. 提交 AI 生成任务
7. 实时监控任务进度
```

---

## 🛠️ 常见问题排查

### 问题 1: 后端无法启动 (Port 8000 already in use)

```bash
# 查看占用 8000 端口的进程
lsof -i :8000

# 杀死占用端口的进程
kill -9 <PID>

# 或者使用不同的端口
docker-compose exec backend uvicorn main:app --host 0.0.0.0 --port 8001
```

### 问题 2: 数据库连接失败

```bash
# 检查数据库日志
docker-compose logs postgres

# 检查数据库连接
docker-compose exec postgres psql -U postgres -d trustagency -c "SELECT 1"

# 重置数据库
docker-compose down postgres
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### 问题 3: 前端无法访问后端 API

```bash
# 检查 CORS 配置
curl -I -X OPTIONS http://localhost:8000 \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET"

# 查看前端代码中的 API 基础 URL
cat site/src/api/client.js | grep "baseURL\|http"

# 检查网络连接
curl http://localhost:8000/health
```

### 问题 4: AI 任务未执行

```bash
# 检查 Celery 工作进程是否运行
docker-compose ps | grep celery

# 查看 Celery 日志
docker-compose logs celery

# 检查 Redis 连接
docker-compose exec redis redis-cli PING

# 检查 OpenAI API 密钥是否配置
env | grep OPENAI
```

---

## 📋 关键端点参考

### 认证 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录，获取 JWT Token |
| POST | `/auth/logout` | 用户登出 |
| POST | `/auth/refresh` | 刷新 Token |

### 平台管理 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/platforms` | 获取平台列表 |
| POST | `/platforms` | 创建新平台 |
| GET | `/platforms/{id}` | 获取特定平台 |
| PUT | `/platforms/{id}` | 更新平台 |
| DELETE | `/platforms/{id}` | 删除平台 |

### 文章管理 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/articles` | 获取文章列表 |
| POST | `/articles` | 创建新文章 |
| GET | `/articles/{id}` | 获取文章详情 |
| PUT | `/articles/{id}` | 更新文章 |
| DELETE | `/articles/{id}` | 删除文章 |

### AI 任务 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/tasks/submit` | 提交 AI 生成任务 |
| GET | `/tasks/{id}/status` | 查看任务状态 |
| GET | `/tasks` | 获取任务列表 |
| POST | `/tasks/{id}/cancel` | 取消任务 |

---

## 🎯 快速命令参考

```bash
# 启动环境
./docker-start.sh
# 或
docker-compose up -d

# 停止环境
./docker-stop.sh
# 或
docker-compose down

# 查看日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash

# 重启服务
docker-compose restart backend

# 清理所有 (删除容器、卷等)
./docker-clean.sh
# 或
docker-compose down -v

# 查看 Celery 任务
docker-compose exec celery celery -A app inspect active

# 查看 Redis 键
docker-compose exec redis redis-cli KEYS "*"
```

---

## ✅ 完整的首次部署检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] 项目文件结构完整
- [ ] 环境变量已配置 (.env)
- [ ] 后端服务已启动 (8000)
- [ ] 前端服务已启动 (5173)
- [ ] 数据库已初始化
- [ ] Redis 已启动
- [ ] Celery 工作进程已启动
- [ ] API 健康检查通过
- [ ] 管理员可以成功登录
- [ ] 前端可以访问后端 API
- [ ] AI 任务可以提交
- [ ] Celery 任务可以执行

---

## 🎊 下一步

部署成功后：

1. **探索 API**: 打开 http://localhost:8000/docs 查看 Swagger UI
2. **测试功能**: 在前端界面创建平台、文章并提交 AI 任务
3. **查看日志**: 使用 `docker-compose logs -f` 实时查看
4. **阅读文档**: 查看 `API_DOCUMENTATION_COMPLETE.md` 了解详细 API
5. **生产部署**: 当准备好时，使用 `DEPLOYMENT_AND_LAUNCH_GUIDE.md`

---

**部署时间**: 5-10 分钟  
**系统资源**: 4GB 内存 (推荐 8GB)  
**磁盘空间**: 2-3GB  

祝你本地部署顺利！🚀

