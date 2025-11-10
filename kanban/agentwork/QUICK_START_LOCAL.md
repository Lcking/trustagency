# 🚀 本地部署快速手册 - 5 分钟快速开始

**目标**: 快速在本地启动完整的 TrustAgency 系统  
**时间**: 5-10 分钟  
**前提**: Docker & Docker Compose 已安装

---

## ⚡ 一键启动 (推荐)

### 步骤 1: 进入项目目录

```bash
cd /Users/ck/Desktop/Project/trustagency
```

### 步骤 2: 启动所有服务

```bash
./docker-start.sh
```

### 步骤 3: 等待启动完成

```
✓ Backend service started
✓ Frontend service started  
✓ Database service started
✓ Redis service started
✓ Celery worker started
```

**预计时间**: 30-60 秒

---

## 🌐 访问应用

| 服务 | 地址 | 用途 |
|------|------|------|
| **前端** | http://localhost:5173 | 管理后台 |
| **API** | http://localhost:8000 | RESTful API |
| **API 文档** | http://localhost:8000/docs | Swagger UI |
| **数据库** | localhost:5432 | PostgreSQL |
| **缓存** | localhost:6379 | Redis |

---

## 🔐 登录凭证

```
用户名: admin
密码:   admin123
```

### 登录步骤

1. 打开浏览器: http://localhost:5173
2. 输入用户名: `admin`
3. 输入密码: `admin123`
4. 点击登录
5. 进入管理后台 ✅

---

## 🧪 快速测试场景

### 场景 1: 验证前后端对接

```bash
# 检查后端健康状态
curl http://localhost:8000/api/health

# 期望输出:
# {"status": "ok", "message": "TrustAgency Backend is running"}
```

### 场景 2: 测试登录 API

```bash
# 获取 JWT Token
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 期望输出:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "user": {"id": 1, "username": "admin", ...}
# }
```

### 场景 3: 测试 AI 功能

```bash
# 1. 获取 Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 2. 创建平台
curl -X POST http://localhost:8000/api/platforms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Platform", "description": "For testing"}'

# 3. 提交 AI 生成任务
curl -X POST http://localhost:8000/api/tasks/generate-articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titles": ["Python 入门", "FastAPI 教程"], "category": "guide"}'
```

---

## 📊 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只看后端日志
docker-compose logs -f backend

# 只看 Celery 日志 (AI 任务)
docker-compose logs -f celery

# 只看前端日志
docker-compose logs -f frontend
```

---

## 🛑 停止服务

```bash
# 停止所有服务
./docker-stop.sh

# 或手动停止
docker-compose down

# 完全清理 (删除数据卷)
./docker-clean.sh
```

---

## ✅ 快速验证清单

启动后检查以下项目:

- [ ] 后端服务运行: `curl http://localhost:8000/api/health`
- [ ] 前端可访问: `open http://localhost:5173`
- [ ] API 文档可见: `open http://localhost:8000/docs`
- [ ] 可以登录: admin / admin123
- [ ] Redis 运行: `docker-compose exec redis redis-cli PING`
- [ ] Celery 运行: `docker-compose logs celery | grep "ready"`
- [ ] 数据库可连接: `docker-compose exec postgres psql -U postgres -d trustagency -c "SELECT 1"`

---

## 🔍 完整验证文档

详细的技术验证步骤，请查看:

- **LOCAL_DEPLOYMENT_GUIDE.md** - 完整部署指南
- **LOCAL_DEPLOYMENT_VERIFICATION.md** - 详细验证清单
- **API_DOCUMENTATION_COMPLETE.md** - API 参考文档

---

## 🎯 常见问题

### Q1: 端口已被占用

```bash
# 查看占用 8000 端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用不同端口启动
docker-compose -f docker-compose.yml -p trustagency-dev up -d
```

### Q2: 无法连接到后端

```bash
# 检查后端是否运行
docker-compose ps | grep backend

# 查看后端日志
docker-compose logs backend

# 检查 CORS 配置
curl -i -X OPTIONS http://localhost:8000 \
  -H "Origin: http://localhost:5173"
```

### Q3: 登录失败

```bash
# 检查数据库连接
docker-compose logs postgres

# 检查数据库中是否有 admin 用户
docker-compose exec postgres psql -U postgres -d trustagency \
  -c "SELECT * FROM admin_users WHERE username='admin';"

# 如果没有，重新初始化数据库
docker-compose exec backend python -c "from app.init_db import init_db; init_db()"
```

### Q4: AI 任务无法执行

```bash
# 检查 Celery 是否运行
docker-compose logs celery

# 检查 Redis 连接
docker-compose exec redis redis-cli PING

# 查看队列状态
docker-compose exec celery celery -A app inspect active
```

---

## 📈 后续步骤

### 1. 探索 API
打开 http://localhost:8000/docs 查看完整的 API 文档

### 2. 测试功能
- 创建平台
- 创建文章
- 提交 AI 生成任务
- 实时监控任务进度

### 3. 查看源代码
- 后端: `/backend/app/`
- 前端: `/site/`
- 测试: `/tests/`

### 4. 阅读完整文档
- `LOCAL_DEPLOYMENT_GUIDE.md` - 完整部署指南
- `API_DOCUMENTATION_COMPLETE.md` - API 参考
- `USER_MANUAL.md` - 用户手册
- `DEPLOYMENT_AND_LAUNCH_GUIDE.md` - 生产部署

---

## 🎊 完成！

你现在有了一个完整的本地开发环境，包括:

✅ **完整的后端系统**
- FastAPI 框架
- PostgreSQL 数据库
- JWT 认证
- 34+ API 端点

✅ **高效的任务队列**
- Celery 异步任务
- Redis 消息代理
- AI 内容生成支持

✅ **专业的前端应用**
- Vue.js 3 管理后台
- 实时数据更新
- 完整的功能模块

✅ **企业级功能**
- 多租户支持 (平台管理)
- 权限控制 (基于角色)
- 文章管理 (完整 CRUD)
- AI 任务监控

---

## 💡 小贴士

```bash
# 快速重启所有服务
docker-compose restart

# 查看容器统计信息
docker stats

# 进入容器进行调试
docker-compose exec backend bash
docker-compose exec postgres bash

# 执行数据库迁移
docker-compose exec backend alembic upgrade head

# 查看实时监控
watch -n 1 'docker-compose ps'
```

---

**准备好开始了吗？** 🚀

```bash
cd /Users/ck/Desktop/Project/trustagency
./docker-start.sh
```

祝你开发愉快！

