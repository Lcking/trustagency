# 🚀 本地开发快速参考卡

## 启动和停止

### 启动所有服务
```bash
cd /Users/ck/Desktop/Project/trustagency
bash ./docker-start.sh
```

### 停止所有服务
```bash
bash ./docker-stop.sh
```

### 清理所有数据
```bash
bash ./docker-clean.sh
```

---

## 快速访问

### 主应用地址
| 应用 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost/ | 主网站 |
| API Swagger 文档 | http://localhost:8001/docs | 交互式 API 文档 |
| API ReDoc 文档 | http://localhost:8001/redoc | 美化的 API 文档 |
| 后台管理 | http://localhost:8001/admin | 管理面板 |

---

## 登录凭证

```
用户名: admin
密码: admin123
```

---

## 常用容器命令

### 查看所有容器状态
```bash
docker-compose ps
```

### 查看特定容器日志（实时）
```bash
# 后端日志
docker-compose logs -f backend

# 前端日志
docker-compose logs -f frontend

# Celery Worker 日志
docker-compose logs -f celery-worker

# 数据库日志
docker-compose logs -f db

# Redis 日志
docker-compose logs -f redis
```

### 进入容器 Shell
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 进入数据库容器
docker-compose exec db psql -U trustagency -d trustagency

# 进入 Redis 容器
docker-compose exec redis redis-cli
```

### 重启单个容器
```bash
docker-compose restart backend
docker-compose restart frontend
docker-compose restart db
```

---

## API 测试命令

### 1. 健康检查
```bash
curl http://localhost:8001/api/health
```

### 2. 登录获取 Token
```bash
curl -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 3. 获取当前用户信息
```bash
# 首先获取 token，然后：
curl http://localhost:8001/api/admin/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. 获取所有平台
```bash
curl http://localhost:8001/api/platforms
```

### 5. 创建新平台
```bash
curl -X POST http://localhost:8001/api/platforms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name":"新平台","url":"https://example.com","description":"测试平台"}'
```

---

## 数据库操作

### 连接数据库
```bash
psql -h localhost -U trustagency -d trustagency
```

### 常用 SQL 查询
```sql
-- 查看所有表
\dt

-- 查看用户表结构
\d "User"

-- 查询所有用户
SELECT * FROM "User";

-- 查询所有平台
SELECT * FROM "Platform";

-- 查询所有文章
SELECT * FROM "Article";

-- 查询任务列表
SELECT * FROM "AIGenerationTask";
```

---

## Redis 操作

### 连接 Redis
```bash
redis-cli -h localhost
```

### 常用命令
```bash
# 查看所有 key
KEYS *

# 获取特定 key 的值
GET task:123

# 查看 key 的过期时间
TTL key_name

# 清空所有数据
FLUSHALL

# 查看数据库统计信息
INFO
```

---

## 日志和调试

### 查看容器构建历史
```bash
docker history trustagency-backend
docker history trustagency-frontend
```

### 检查容器网络
```bash
docker network ls
docker network inspect trustagency_trustagency-net
```

### 获取容器详细信息
```bash
docker-compose exec backend pip list
docker-compose exec backend python --version
```

### 端口占用检查
```bash
# 检查特定端口
lsof -i :80
lsof -i :8001
lsof -i :5432
lsof -i :6379
```

---

## 常见问题解决

### Docker Daemon 未运行
```bash
# 启动 Docker Desktop
open /Applications/Docker.app
```

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :PORT_NUMBER

# 终止进程
kill -9 PID
```

### 容器无法启动
```bash
# 查看详细错误日志
docker-compose logs [service-name]

# 重建镜像
docker-compose up --build
```

### 数据库连接失败
```bash
# 检查数据库容器是否运行
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

---

## 性能优化

### 查看容器资源使用
```bash
docker stats
```

### 清理未使用的镜像
```bash
docker image prune
```

### 清理未使用的容器
```bash
docker container prune
```

### 清理构建缓存
```bash
docker builder prune
```

---

## 开发工作流

### 1. 修改后端代码
```bash
# 代码修改后自动重新加载（已配置热更新）
# 只需保存文件即可

# 如果需要重新构建
docker-compose down
bash ./docker-start.sh --rebuild
```

### 2. 修改数据库模型
```bash
# 进入后端容器
docker-compose exec backend bash

# 创建新的迁移文件
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head
```

### 3. 修改前端页面
```bash
# 前端文件在 ./site 目录
# 保存后自动重新加载（Nginx 提供静态文件）
```

### 4. 管理依赖
```bash
# 添加新的 Python 包
docker-compose exec backend pip install package_name

# 更新 requirements.txt
docker-compose exec backend pip freeze > backend/requirements.txt

# 重建镜像应用新依赖
docker-compose down
bash ./docker-start.sh --rebuild
```

---

## 监控和维护

### 实时监控日志
```bash
# 所有服务日志
docker-compose logs -f

# 显示最后 100 行
docker-compose logs --tail=100
```

### 定期检查
```bash
# 检查容器健康状态
docker-compose ps

# 检查网络连接
docker network inspect trustagency_trustagency-net

# 检查卷状态
docker volume ls
```

### 备份数据
```bash
# 导出数据库
docker-compose exec db pg_dump -U trustagency trustagency > backup.sql

# 导入数据库
docker-compose exec -T db psql -U trustagency trustagency < backup.sql
```

---

## 提示和技巧

### 🔍 快速诊断
```bash
# 一键诊断所有问题
docker-compose ps
docker network ls
docker volume ls
docker logs [container_id]
```

### 📝 查看完整配置
```bash
# 查看合并后的 docker-compose 配置
docker-compose config
```

### 🔄 快速重启
```bash
# 重启所有容器但保留数据
docker-compose restart

# 完全重启（清空数据）
docker-compose down -v && bash ./docker-start.sh
```

### 🚀 性能优化
- 使用 `--build` 标志重新构建最新代码
- 使用 `--rebuild` 标志强制重新构建所有镜像
- 定期使用 `docker system prune` 清理不用的资源

---

## 快速命令速记

```bash
# 最常用的三个命令
docker-compose ps           # 查看状态
docker-compose logs -f      # 查看日志
docker-compose restart      # 重启服务

# 最常用的测试
curl http://localhost/              # 测试前端
curl http://localhost:8001/api/health  # 测试后端
```

---

**祝你开发愉快！🎉**

如有任何问题，请参考 `LOCAL_DEPLOYMENT_SUCCESS.md` 中的完整指南。
