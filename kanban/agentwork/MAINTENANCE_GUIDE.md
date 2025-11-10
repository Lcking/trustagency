# TrustAgency 维护和监控指南

**版本**: 1.0.0  
**更新日期**: 2025-11-07  
**对象**: 系统管理员和技术支持人员

---

## 📋 目录

1. [系统监控](#系统监控)
2. [日志管理](#日志管理)
3. [性能监控](#性能监控)
4. [数据库维护](#数据库维护)
5. [备份和恢复](#备份和恢复)
6. [安全维护](#安全维护)
7. [常见问题排查](#常见问题排查)
8. [定期维护计划](#定期维护计划)
9. [故障恢复](#故障恢复)
10. [升级指南](#升级指南)

---

## 系统监控

### 1. 服务健康检查

#### 基本健康检查

```bash
# 检查所有服务状态
docker-compose ps

# 预期输出 - 所有服务 Status 为 "Up (healthy)":
# NAME            STATUS
# frontend        Up (healthy)
# backend         Up (healthy)
# database        Up (healthy)
# redis           Up (healthy)
# celery-worker   Up (healthy)
# celery-beat     Up (healthy)
```

#### API 健康检查

```bash
# 检查后端 API 健康状态
curl http://localhost:8001/api/health

# 预期响应:
# {"status":"ok","message":"TrustAgency Backend is running"}

# 在生产环境
curl https://yourdomain.com/api/health
```

#### 数据库健康检查

```bash
# 检查数据库连接
docker-compose exec database pg_isready -U postgres

# 预期输出: accepting connections

# 详细检查
docker-compose exec database psql -U postgres -c "SELECT version();"
```

#### Redis 健康检查

```bash
# 检查 Redis 连接
docker-compose exec redis redis-cli ping

# 预期输出: PONG

# 详细检查
docker-compose exec redis redis-cli INFO
```

### 2. 资源使用监控

```bash
# 实时资源使用
docker stats

# 输出示例:
# CONTAINER   CPU %   MEM USAGE / LIMIT     MEM %   NET I/O
# backend     0.15%   245.3 MiB / 1 GiB     23.9%   1.2 GB / 894 MB
# database    0.22%   187.2 MiB / 1 GiB     18.3%   890 MB / 1.2 GB

# 检查磁盘空间
df -h

# 预期: 可用空间应 >20%

# 检查内存
free -h
```

### 3. 网络监控

```bash
# 检查容器网络
docker network inspect trustagency-net

# 检查端口占用
netstat -tuln | grep LISTEN

# 预期端口:
# 80 (HTTP)
# 443 (HTTPS)
# 8001 (API)
# 5432 (PostgreSQL)
# 6379 (Redis)
```

---

## 日志管理

### 1. 查看容器日志

```bash
# 查看特定服务日志
docker-compose logs backend
docker-compose logs database
docker-compose logs redis
docker-compose logs celery-worker

# 实时跟踪日志
docker-compose logs -f backend

# 查看最后 100 行
docker-compose logs --tail=100 backend

# 查看特定时间范围的日志
docker-compose logs --since 2025-11-07T10:00:00 backend

# 查看所有服务日志
docker-compose logs
```

### 2. 日志文件位置

```
/data/trustagency/logs/
├── backend.log          # 后端应用日志
├── database.log         # 数据库日志
├── redis.log            # Redis 日志
├── celery.log           # Celery 任务日志
├── nginx_access.log     # Nginx 访问日志
└── nginx_error.log      # Nginx 错误日志
```

### 3. 日志级别

日志级别从低到高：

```
DEBUG   - 调试信息
INFO    - 一般信息
WARNING - 警告消息
ERROR   - 错误消息
CRITICAL - 严重错误
```

### 4. 日志轮转

```bash
# 检查日志大小
ls -lh /data/trustagency/logs/

# 手动轮转日志
logrotate -f /etc/logrotate.d/trustagency

# 清理旧日志 (保留最近 7 天)
find /data/trustagency/logs -type f -mtime +7 -delete
```

### 5. 日志分析

```bash
# 查找错误
grep ERROR /data/trustagency/logs/backend.log

# 统计错误数
grep ERROR /data/trustagency/logs/backend.log | wc -l

# 查找特定错误
grep "Connection refused" /data/trustagency/logs/backend.log

# 查看最常见的错误
grep ERROR /data/trustagency/logs/backend.log | sort | uniq -c | sort -rn
```

---

## 性能监控

### 1. API 响应时间

```bash
# 测试单个请求
time curl http://localhost:8001/api/platforms

# 批量测试 (需要 Apache Bench)
ab -n 100 -c 10 http://localhost:8001/api/platforms

# 输出包含:
# - 平均响应时间
# - 最小/最大响应时间
# - 吞吐量 (RPS)
```

### 2. 数据库查询性能

```bash
# 进入数据库
docker-compose exec database psql -U postgres trustagency_prod

# 启用查询计时
\timing on

# 执行查询
SELECT COUNT(*) FROM articles;

# 查看查询计划
EXPLAIN ANALYZE SELECT * FROM articles WHERE category = 'tutorial';

# 列出所有索引
\d articles
```

### 3. Redis 性能

```bash
# 进入 Redis
docker-compose exec redis redis-cli

# 查看统计信息
INFO stats

# 重要指标:
# - total_commands_processed: 总命令数
# - instantaneous_ops_per_sec: 每秒操作数
# - keyspace_hits: 缓存命中
# - keyspace_misses: 缓存未命中

# 监控命令
MONITOR

# 退出监控
Ctrl+C
```

### 4. Celery 任务监控

```bash
# 查看 Celery 统计
docker-compose exec backend celery -A app.celery_app inspect active

# 查看工作进程
docker-compose exec backend celery -A app.celery_app inspect active_queues

# 查看已完成任务
docker-compose exec backend celery -A app.celery_app inspect registered
```

### 5. 建立性能基准

```bash
# 记录基准数据
docker stats --no-stream > baseline_$(date +%Y%m%d).txt

# 对比性能变化
diff baseline_20251101.txt baseline_20251107.txt
```

---

## 数据库维护

### 1. 数据库备份

#### 自动备份

```bash
# 创建备份脚本
cat > /data/trustagency/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/data/trustagency/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/trustagency_$TIMESTAMP.sql"

docker-compose exec database pg_dump \
  -U postgres \
  trustagency_prod > "$BACKUP_FILE"

gzip "$BACKUP_FILE"
echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /data/trustagency/backup.sh

# 添加 cron 定时任务
crontab -e

# 每天凌晨 2 点执行备份
0 2 * * * /data/trustagency/backup.sh
```

#### 手动备份

```bash
# 备份数据库
docker-compose exec database pg_dump \
  -U postgres \
  trustagency_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
gzip backup_*.sql

# 验证备份文件大小
ls -lh backup_*.sql.gz

# 应该是几 MB 大小
```

### 2. 数据库优化

```bash
# 进入数据库
docker-compose exec database psql -U postgres trustagency_prod

# 分析表
ANALYZE;

# 真空清理 (仅在服务停止时运行)
VACUUM FULL;

# 重建索引
REINDEX DATABASE trustagency_prod;

# 检查表大小
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname='public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. 数据库连接池

```bash
# 检查当前连接
docker-compose exec database psql -U postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# 终止空闲连接
docker-compose exec database psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '1 hour';"
```

### 4. 数据库升级

```bash
# 检查当前 PostgreSQL 版本
docker-compose exec database psql -U postgres --version

# 升级步骤:
# 1. 备份数据库
./backup.sh

# 2. 停止应用
./docker-stop.sh

# 3. 更新 Docker 镜像版本
# 编辑 docker-compose.prod.yml
# 将 postgres:15-alpine 改为 postgres:16-alpine

# 4. 重启服务
./docker-start-prod.sh

# 5. 验证升级
docker-compose exec database psql -U postgres --version
```

---

## 备份和恢复

### 1. 完整系统备份

```bash
# 备份所有数据
mkdir -p backups_full_$(date +%Y%m%d)

# 备份数据库
docker-compose exec database pg_dump -U postgres trustagency_prod > backups_full_$(date +%Y%m%d)/database.sql

# 备份应用代码
tar czf backups_full_$(date +%Y%m%d)/app_code.tar.gz \
  --exclude=__pycache__ \
  --exclude=.pytest_cache \
  --exclude=venv \
  ./

# 备份配置文件
tar czf backups_full_$(date +%Y%m%d)/config.tar.gz \
  .env.prod \
  docker-compose.prod.yml \
  nginx/default.conf

# 备份数据卷
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/backups_full_$(date +%Y%m%d)/postgres_data.tar.gz -C /data .

# 验证备份完整性
ls -lh backups_full_$(date +%Y%m%d)/
```

### 2. 数据库恢复

```bash
# 从备份恢复
docker-compose exec -T database psql -U postgres trustagency_prod < backup_20251107_120000.sql

# 或者通过管道
gunzip -c backup_20251107_120000.sql.gz | \
  docker-compose exec -T database psql -U postgres trustagency_prod

# 验证恢复
docker-compose exec database psql -U postgres trustagency_prod -c "SELECT COUNT(*) FROM articles;"
```

### 3. 灾难恢复

```bash
# 1. 停止所有服务
./docker-stop.sh

# 2. 删除数据卷
docker-compose down -v

# 3. 从备份创建新卷
docker volume create postgres_data

# 4. 导入备份数据
gunzip -c backup_20251107_120000.sql.gz | \
  docker run -i --rm \
  -v postgres_data:/var/lib/postgresql/data \
  -e POSTGRES_DB=trustagency_prod \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  postgres:15-alpine \
  psql -U postgres

# 5. 重启服务
./docker-start-prod.sh

# 6. 验证数据
curl https://yourdomain.com/api/health
```

### 4. 备份存储

```bash
# 备份到云存储 (AWS S3)
aws s3 cp backup_20251107_120000.sql.gz s3://trustagency-backups/

# 或使用 rclone 备份到多个云服务
rclone copy backup_20251107_120000.sql.gz remote:backups/

# 定期清理本地旧备份
find /data/trustagency/backups -name "*.sql.gz" -mtime +30 -delete

# 定期验证备份可恢复性 (每月)
# 在测试环境中恢复一次备份，确保可用
```

---

## 安全维护

### 1. 更新和补丁

```bash
# 检查系统更新
sudo apt update
sudo apt list --upgradable

# 应用更新
sudo apt upgrade -y

# 更新 Docker 镜像
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull nginx:alpine

# 重启服务
./docker-stop.sh
./docker-start-prod.sh
```

### 2. 访问控制

```bash
# 检查用户权限
ls -la /data/trustagency/

# 所有文件应属于特定用户
sudo chown -R app:app /data/trustagency/

# 设置适当的权限
sudo chmod -R 750 /data/trustagency/
sudo chmod 600 /data/trustagency/.env.prod

# 审核 SSH 密钥
ssh-keygen -l -f ~/.ssh/id_rsa.pub
```

### 3. 密钥轮转

```bash
# 更新 JWT 密钥
# 1. 生成新密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. 更新 .env.prod
# SECRET_KEY=new_secret_key_here

# 3. 重启后端服务
docker-compose restart backend

# 4. 用户需要重新登录
```

### 4. SSL 证书更新

```bash
# 自动续期 Let's Encrypt 证书
sudo certbot renew

# 或手动续期
sudo certbot certonly --nginx -d yourdomain.com

# 验证证书
sudo certbot certificates

# 查看证书过期日期
openssl x509 -enddate -noout -in /etc/letsencrypt/live/yourdomain.com/cert.pem
```

### 5. 安全审计

```bash
# 检查 SQL 注入漏洞
grep -r "\.format(" backend/app/ | grep SQL

# 检查硬编码密钥
grep -r "password\|secret\|key" .env* | grep -v ".example"

# 扫描依赖漏洞
pip list --outdated

# 运行安全扫描
python -m bandit -r backend/app/
```

---

## 常见问题排查

### 问题 1: 数据库连接失败

**症状**: 
```
Error: could not translate host name "database" to address
```

**排查步骤**:
```bash
# 检查数据库容器
docker-compose ps database

# 检查网络连接
docker network inspect trustagency-net

# 检查环境变量
docker-compose exec backend env | grep DATABASE_URL

# 手动测试连接
docker-compose exec backend python -c "from app.database import engine; print('OK')"
```

**解决方案**:
```bash
# 重启数据库
docker-compose restart database

# 或完全重启
./docker-stop.sh
./docker-start-prod.sh
```

### 问题 2: Redis 缓存失效

**症状**:
```
RedisConnectionError: Error 111 connecting to localhost:6379
```

**排查步骤**:
```bash
# 检查 Redis 容器
docker-compose ps redis

# 检查 Redis 连接
docker-compose exec redis redis-cli ping

# 查看 Redis 日志
docker-compose logs redis
```

**解决方案**:
```bash
# 清空 Redis 缓存
docker-compose exec redis redis-cli FLUSHALL

# 重启 Redis
docker-compose restart redis
```

### 问题 3: 高内存使用

**症状**:
```
Out of memory error
```

**排查步骤**:
```bash
# 查看内存使用
docker stats

# 查看最大内存用户
docker ps -a --format "{{.Names}}: {{.Status}}" | sort
```

**解决方案**:
```bash
# 增加内存限制 (docker-compose.prod.yml)
# deploy:
#   resources:
#     limits:
#       memory: 2G

# 或清理不需要的容器/镜像
docker container prune -f
docker image prune -a -f
```

### 问题 4: Celery 任务队列堆积

**症状**:
```
AI 生成任务执行缓慢
```

**排查步骤**:
```bash
# 检查 Celery 任务
docker-compose exec backend celery -A app.celery_app inspect active

# 查看队列长度
docker-compose exec redis redis-cli LLEN celery

# 查看工作进程
docker-compose exec backend celery -A app.celery_app inspect active_queues
```

**解决方案**:
```bash
# 增加工作进程数
# 在 docker-compose.prod.yml 中修改 concurrency

# 或手动重启 Celery
docker-compose restart celery-worker celery-beat

# 清空失败的任务
docker-compose exec redis redis-cli DEL celery-task-meta-*
```

### 问题 5: 前端访问缓慢

**症状**:
```
页面加载缓慢，首页需要 5+ 秒
```

**排查步骤**:
```bash
# 检查网络延迟
curl -w "@curl-format.txt" https://yourdomain.com

# 检查 Nginx 日志
tail -f /var/log/nginx/trustagency_error.log

# 检查资源使用
docker stats frontend
```

**解决方案**:
```bash
# 启用 CDN
# 配置 CloudFlare 或其他 CDN

# 启用压缩
# 在 Nginx 配置中启用 gzip

# 优化图片
# 使用 WebP 格式
# 压缩静态资源
```

---

## 定期维护计划

### 每天
- [ ] 检查服务健康状态
- [ ] 检查错误日志
- [ ] 验证备份完成

### 每周
- [ ] 检查磁盘空间使用
- [ ] 验证 API 响应时间
- [ ] 审查监控告警
- [ ] 清理旧日志

### 每月
- [ ] 数据库优化 (ANALYZE, VACUUM)
- [ ] 性能基准对比
- [ ] 安全补丁更新
- [ ] 灾难恢复测试
- [ ] 容量规划评估

### 每季度
- [ ] 完整系统审计
- [ ] 依赖包更新
- [ ] SSL 证书验证
- [ ] 用户权限审查

### 每年
- [ ] 安全审计
- [ ] 架构审查
- [ ] 技术栈升级评估
- [ ] 容量规划和扩展

---

## 故障恢复

### 故障响应流程

```
1. 发现问题 (5 分钟)
   ↓
2. 评估影响范围 (5 分钟)
   ↓
3. 启动恢复流程 (1-5 分钟)
   ↓
4. 实施修复 (5-30 分钟)
   ↓
5. 验证修复 (5 分钟)
   ↓
6. 准备事后分析 (当天)
   ↓
7. 事后分析和改进 (1 周内)
```

### 故障恢复时间目标 (RTO)

| 故障类型 | RTO | RPO |
|---------|------|------|
| 单个服务故障 | <5 分钟 | <1 分钟 |
| 数据库故障 | <30 分钟 | <1 分钟 |
| 整个系统宕机 | <1 小时 | <1 小时 |

### 应急联系方式

```
技术主管: +86 10-xxxx-xxxx (24/7)
数据库管理员: +86 10-xxxx-xxxx (24/7)
基础设施团队: support@trustagency.com
```

---

## 升级指南

### 应用升级

```bash
# 1. 备份数据
./backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 构建新镜像
docker build -f backend/Dockerfile -t trustagency-backend:1.1.0 .

# 4. 停止旧容器
./docker-stop.sh

# 5. 启动新容器
./docker-start-prod.sh

# 6. 验证升级
curl https://yourdomain.com/api/health
```

### 数据库升级

```bash
# 在升级前备份
./backup.sh

# 运行迁移
docker-compose exec backend alembic upgrade head

# 验证
docker-compose exec database psql -U postgres trustagency_prod -c "SELECT version();"
```

### 依赖升级

```bash
# 检查可升级的依赖
pip list --outdated

# 更新依赖
pip install --upgrade package_name

# 更新 requirements.txt
pip freeze > requirements.txt

# 测试所有功能
./test_task7_integration.sh
./test_task8_openai.sh
```

---

**维护者**: TrustAgency 系统团队  
**最后更新**: 2025-11-07  
**版本**: 1.0.0

