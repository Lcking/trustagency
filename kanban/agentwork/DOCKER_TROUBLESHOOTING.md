# Docker 故障排除指南

**Last Updated**: 2025-11-07  
**Version**: 1.0.0

---

## 🔍 常见问题和解决方案

### 1. 容器无法启动

#### 问题：容器立即退出

**症状**：
```
CONTAINER ID   IMAGE      STATUS
...           ...        Exited (1) 10 seconds ago
```

**解决方案**：

```bash
# 1. 查看详细错误日志
docker-compose logs backend

# 2. 查看特定服务的详细输出
docker-compose logs --tail=50 backend

# 3. 重建镜像
docker-compose build --no-cache backend

# 4. 检查环境变量
docker-compose config | grep DATABASE_URL

# 5. 检查依赖服务是否正常
docker-compose ps
```

#### 常见原因：
- ❌ 环境变量未设置
- ❌ 依赖服务未就绪
- ❌ 端口被占用
- ❌ 镜像构建失败
- ❌ 权限问题

---

### 2. 数据库连接失败

#### 问题：Backend 无法连接到 PostgreSQL

**症状**：
```
Error: could not connect to PostgreSQL at host 'db'
FATAL: Ident authentication failed for user "trustagency"
```

**解决方案**：

```bash
# 1. 检查 PostgreSQL 容器状态
docker-compose ps db

# 2. 检查 PostgreSQL 是否就绪
docker-compose exec db pg_isready -U trustagency

# 3. 手动测试连接
docker-compose exec db psql -U trustagency -d trustagency

# 4. 查看 PostgreSQL 日志
docker-compose logs db

# 5. 验证连接字符串
# 确保 DATABASE_URL 格式正确：
# postgresql://trustagency:trustagency@db:5432/trustagency

# 6. 重启数据库
docker-compose restart db

# 7. 重新初始化数据库
docker-compose down -v  # 删除卷
docker-compose up db    # 重新创建

# 8. 重新运行迁移
docker-compose exec backend alembic upgrade head
```

#### 常见原因：
- ❌ PostgreSQL 未完全启动
- ❌ 数据库用户名或密码错误
- ❌ 网络连接问题
- ❌ 迁移失败
- ❌ 卷权限问题

---

### 3. Redis 连接失败

#### 问题：无法连接到 Redis

**症状**：
```
ConnectionError: Error 111 connecting to redis:6379
redis.exceptions.ConnectionError: Error -2 getaddrinfo failed
```

**解决方案**：

```bash
# 1. 检查 Redis 容器
docker-compose ps redis

# 2. 测试 Redis 连接
docker-compose exec redis redis-cli ping

# 3. 检查 Redis 配置
docker-compose exec redis redis-cli CONFIG GET '*'

# 4. 查看 Redis 日志
docker-compose logs redis

# 5. 检查网络连接
docker-compose exec backend curl http://redis:6379

# 6. 重启 Redis
docker-compose restart redis

# 7. 完全重新创建
docker-compose down
docker-compose up redis
```

#### 常见原因：
- ❌ Redis 未启动
- ❌ 网络问题
- ❌ 端口占用
- ❌ 配置文件错误

---

### 4. 端口占用

#### 问题：无法绑定端口

**症状**：
```
ERROR: for frontend  Cannot start service frontend: 
  Ports are not available: exposing port 80 also exposes port 80 (tcp)
```

**解决方案**：

```bash
# 1. 查找占用端口的进程
# 前端占用 80
lsof -i :80
netstat -tulpn | grep :80

# API 占用 8001
lsof -i :8001

# 数据库占用 5432
lsof -i :5432

# Redis 占用 6379
lsof -i :6379

# 2. 杀死占用进程（macOS）
kill -9 <PID>

# 3. 或者修改 docker-compose.yml 中的端口
# 例如，将 80:80 改为 8080:80
# "80:80" -> "8080:80"

# 4. 查找已占用端口的应用
# macOS
sudo lsof -i :80

# Linux
sudo fuser 80/tcp

# 3. 停止占用端口的服务
sudo systemctl stop nginx  # 如果是 nginx
sudo systemctl stop apache2  # 如果是 apache
```

#### 常见原因：
- ❌ 本地应用（Nginx、Apache）已在运行
- ❌ 其他 Docker 容器正在使用
- ❌ 端口号冲突

---

### 5. 内存不足

#### 问题：容器因 OOM 被杀死

**症状**：
```
killed
Killed: 9
```

**解决方案**：

```bash
# 1. 查看容器资源使用情况
docker stats

# 2. 查看系统内存
free -h  # Linux
vm_stat | grep "Pages free"  # macOS

# 3. 检查 Docker 资源限制
docker info | grep Memory

# 4. 在 docker-compose 中设置内存限制
# services:
#   backend:
#     deploy:
#       resources:
#         limits:
#           memory: 1024M

# 5. 清理不用的镜像和卷
docker system prune -a --volumes

# 6. 分配更多内存给 Docker Desktop（macOS/Windows）
# Docker Desktop > Settings > Resources > Memory
```

#### 常见原因：
- ❌ 系统内存不足
- ❌ Docker 内存限制过低
- ❌ 应用内存泄漏
- ❌ 卷数据过大

---

### 6. 文件权限问题

#### 问题：Permission denied 错误

**症状**：
```
PermissionError: [Errno 13] Permission denied
Cannot open directory '/app': Permission denied
```

**解决方案**：

```bash
# 1. 检查卷权限
docker-compose exec backend ls -la /app

# 2. 修复权限
docker-compose exec backend chmod -R 755 /app

# 3. 修改所有者
docker-compose exec backend chown -R appuser:appgroup /app

# 4. 查看 Dockerfile 中的用户
# 确保 USER 指令设置正确

# 5. 重新构建镜像
docker-compose build --no-cache backend

# 6. 硬启动所有服务
docker-compose down
docker-compose up
```

#### 常见原因：
- ❌ 卷挂载权限问题
- ❌ 容器用户问题
- ❌ 文件系统权限问题

---

### 7. 网络问题

#### 问题：容器之间无法通信

**症状**：
```
Cannot resolve host 'db'
Name or service not known
```

**解决方案**：

```bash
# 1. 检查网络
docker network ls

# 2. 检查容器是否在同一网络
docker network inspect trustagency-net

# 3. 测试网络连接
docker-compose exec backend ping db

# 4. 测试 DNS 解析
docker-compose exec backend nslookup db

# 5. 查看网络驱动
docker network inspect trustagency-net | grep Driver

# 6. 重新创建网络
docker-compose down
docker-compose up

# 7. 检查防火墙规则
ufw status  # Linux
```

#### 常见原因：
- ❌ 容器不在同一网络
- ❌ DNS 解析失败
- ❌ 防火墙规则阻止
- ❌ 网络驱动不兼容

---

### 8. 构建失败

#### 问题：Docker 镜像构建失败

**症状**：
```
ERROR: failed to build image: failed to execute build step with docker run
Step 3/10 : RUN apt-get install -y ...
```

**解决方案**：

```bash
# 1. 查看完整构建日志
docker-compose build --progress=plain backend

# 2. 查看 Dockerfile 中的错误行
# 检查该行是否有问题

# 3. 手动测试命令
docker run --rm python:3.10-slim apt-get update

# 4. 检查 Dockerfile 语法
dockerfile_lint Dockerfile

# 5. 强制重新构建
docker-compose build --no-cache --progress=plain backend

# 6. 检查依赖文件
cat backend/requirements.txt

# 7. 清空构建缓存
docker builder prune -a

# 8. 重新构建
docker-compose build --no-cache backend
```

#### 常见原因：
- ❌ 依赖包安装失败
- ❌ Dockerfile 语法错误
- ❌ 网络问题
- ❌ 包版本冲突

---

### 9. 性能问题

#### 问题：应用响应缓慢

**症状**：
```
Response time: >5 seconds
High CPU/Memory usage
```

**解决方案**：

```bash
# 1. 监控资源使用
docker stats

# 2. 检查进程
docker-compose exec backend ps aux

# 3. 查看数据库连接
docker-compose exec db psql -c "SELECT * FROM pg_stat_activity;"

# 4. 分析数据库查询
# 在 backend 中启用 SQL 日志记录

# 5. 检查 Redis 性能
docker-compose exec redis redis-cli info stats

# 6. 优化镜像大小
docker images | grep trustagency

# 7. 水平扩展（如果使用集群）
# 增加 worker 并发数

# 8. 启用缓存
# 检查缓存配置

# 9. 数据库优化
docker-compose exec db psql -c "ANALYZE;"

# 10. 查看日志中的慢查询
docker-compose logs backend | grep "slow"
```

#### 常见原因：
- ❌ 资源限制不足
- ❌ 数据库查询不优化
- ❌ 缓存未配置
- ❌ 网络延迟
- ❌ 磁盘 I/O 瓶颈

---

### 10. 日志问题

#### 问题：无法访问日志

**症状**：
```
no such file or directory: '/var/log/nginx/access.log'
```

**解决方案**：

```bash
# 1. 查看容器日志
docker-compose logs

# 2. 查看特定服务日志
docker-compose logs backend

# 3. 实时查看日志
docker-compose logs -f backend

# 4. 查看最后 N 行
docker-compose logs --tail=100 backend

# 5. 查看特定时间范围的日志
docker-compose logs --since 2025-11-07T10:00:00 backend

# 6. 查看时间戳日志
docker-compose logs --timestamps backend

# 7. 进入容器查看日志文件
docker-compose exec backend bash

# 8. 查看日志文件大小
docker-compose exec backend du -sh /var/log/nginx/

# 9. 清空日志
docker-compose exec backend truncate -s 0 /var/log/nginx/access.log
```

#### 常见原因：
- ❌ 日志目录不存在
- ❌ 日志卷挂载问题
- ❌ 权限不足
- ❌ 日志文件太大

---

## 🔧 高级调试

### 进入容器调试

```bash
# 进入 backend 容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec db psql -U trustagency

# 进入 Redis 容器
docker-compose exec redis redis-cli

# 在容器中安装调试工具
docker-compose exec backend apt-get install -y vim curl
```

### Docker 系统诊断

```bash
# 系统信息
docker system df
docker system df -v

# 清理系统
docker system prune -a

# 检查健康状态
docker ps --filter "health=unhealthy"

# 查看事件
docker events --filter type=container
```

### 检查点和恢复

```bash
# 创建容器检查点
docker checkpoint create container_name checkpoint_name

# 恢复检查点
docker start --checkpoint checkpoint_name container_name
```

---

## 📋 调试检查清单

- [ ] 所有容器都在运行吗？ (`docker-compose ps`)
- [ ] 所有容器都通过了健康检查吗？
- [ ] 网络连接正常吗？(`docker network ls`)
- [ ] 卷是否正确挂载？(`docker volume ls`)
- [ ] 环境变量是否设置正确？(`docker-compose config`)
- [ ] 日志中有错误吗？(`docker-compose logs`)
- [ ] 系统资源充足吗？(`docker stats`)
- [ ] 防火墙规则正确吗？
- [ ] 端口没有被占用吗？(`lsof -i :PORT`)
- [ ] 时间同步正常吗？(`date` 和容器内时间)

---

## 🆘 获取帮助

### 收集诊断信息

```bash
#!/bin/bash
# 创建诊断报告

echo "=== Docker Version ===" > docker_diagnostics.txt
docker --version >> docker_diagnostics.txt

echo -e "\n=== Docker Compose Version ===" >> docker_diagnostics.txt
docker-compose --version >> docker_diagnostics.txt

echo -e "\n=== Container Status ===" >> docker_diagnostics.txt
docker-compose ps >> docker_diagnostics.txt

echo -e "\n=== System Resources ===" >> docker_diagnostics.txt
docker stats --no-stream >> docker_diagnostics.txt

echo -e "\n=== Recent Logs ===" >> docker_diagnostics.txt
docker-compose logs --tail=50 >> docker_diagnostics.txt

echo -e "\n=== Network Info ===" >> docker_diagnostics.txt
docker network inspect trustagency-net >> docker_diagnostics.txt

echo "Diagnostics saved to docker_diagnostics.txt"
```

### 提交问题时包含

1. Docker 和 Docker Compose 版本
2. 操作系统信息
3. 容器状态输出
4. 完整错误日志
5. 资源使用情况
6. docker-compose.yml 配置（隐藏敏感信息）

---

## 📚 相关资源

- Docker 官方文档：https://docs.docker.com
- Docker Compose 官方文档：https://docs.docker.com/compose
- Docker 问题排查指南：https://docs.docker.com/config/containers/troubleshoot/
- PostgreSQL Docker 问题：https://hub.docker.com/_/postgres
- Redis Docker 问题：https://hub.docker.com/_/redis

---

**Status**: ✅ Complete  
**Last Updated**: 2025-11-07

