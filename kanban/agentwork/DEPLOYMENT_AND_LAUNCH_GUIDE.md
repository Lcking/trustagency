# TrustAgency 部署和上线指南

**版本**: 1.0.0  
**更新日期**: 2025-11-07  
**目标环境**: 生产环境

---

## 📋 目录

1. [上线前检查清单](#上线前检查清单)
2. [环境准备](#环境准备)
3. [部署步骤](#部署步骤)
4. [数据库迁移](#数据库迁移)
5. [配置 SSL/TLS](#配置-ssltls)
6. [监控和告警设置](#监控和告警设置)
7. [健康检查和验证](#健康检查和验证)
8. [回滚计划](#回滚计划)
9. [故障排除](#故障排除)
10. [上线后验证](#上线后验证)

---

## 上线前检查清单

在开始部署之前，请确保完成以下所有检查：

### 代码准备 ✓

- [ ] 所有代码合并到 main 分支
- [ ] 代码审查完成
- [ ] 单元测试通过 (100% 通过率)
- [ ] E2E 测试通过 (93 个测试)
- [ ] 没有 console.log 或 debug 代码
- [ ] 所有依赖都已更新到最新版本
- [ ] 代码中没有硬编码的密钥或敏感信息

### 环境准备 ✓

- [ ] 生产环境服务器可用
- [ ] 网络配置正确 (防火墙规则等)
- [ ] 域名已注册和配置
- [ ] SSL 证书已获取
- [ ] 数据库服务器可用
- [ ] Redis 实例可用
- [ ] 备份系统已配置

### 文档完善 ✓

- [ ] API 文档完成
- [ ] 部署指南编写完成
- [ ] 用户手册编写完成
- [ ] 维护文档编写完成
- [ ] 变更日志 (CHANGELOG) 编写完成

### 安全检查 ✓

- [ ] 数据库密码已更改
- [ ] JWT 密钥已更改
- [ ] API 密钥已更改
- [ ] 所有密钥已存储在安全的地方
- [ ] CORS 配置已正确设置
- [ ] HTTPS 已启用

### 容量规划 ✓

- [ ] 已评估预期用户数
- [ ] 已配置足够的服务器资源
- [ ] 已规划扩展策略
- [ ] 已评估数据库容量

### 监控准备 ✓

- [ ] 日志系统已配置
- [ ] 监控工具已部署
- [ ] 告警规则已配置
- [ ] 错误追踪已配置 (如 Sentry)

---

## 环境准备

### 1. 服务器要求

**最低配置**:
```
CPU: 2核
内存: 4GB
硬盘: 50GB SSD
操作系统: Ubuntu 20.04 LTS 或更新版本
```

**推荐配置**:
```
CPU: 4核
内存: 8GB
硬盘: 100GB SSD
操作系统: Ubuntu 22.04 LTS
```

### 2. 系统依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y \
  curl \
  wget \
  git \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3.10 \
  python3.10-venv \
  python3.10-dev \
  postgresql-client \
  redis-tools

# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 环境变量配置

创建生产环境变量文件 `.env.prod`:

```bash
# 复制示例文件
cp .env.example .env.prod

# 编辑配置
vim .env.prod
```

关键配置项:

```env
# 应用配置
ENVIRONMENT=production
DEBUG=False
API_TITLE=TrustAgency API
API_DESCRIPTION=Admin CMS with AI Content Generation
API_VERSION=1.0.0

# 数据库配置
DATABASE_URL=postgresql://username:password@db-host:5432/trustagency_prod
DB_ECHO=False

# Redis 配置
REDIS_URL=redis://redis-host:6379/0
REDIS_MAX_CONNECTIONS=50

# Celery 配置
CELERY_BROKER_URL=redis://redis-host:6379/0
CELERY_RESULT_BACKEND=redis://redis-host:6379/1

# JWT 配置 (生成新的密钥)
SECRET_KEY=your-very-secure-random-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS 配置
CORS_ORIGINS=["https://youromain.com"]

# Email 配置 (可选)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 监控配置 (可选)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# OpenAI 配置 (必需)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# 数据路径
DATA_PATH=/data/trustagency
TIMEZONE=Asia/Shanghai
```

### 4. 生成安全密钥

```bash
# 生成 JWT 密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成另一个密钥用于数据加密
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 部署步骤

### Phase 1: 前置准备 (5 分钟)

```bash
# 1. 连接到生产服务器
ssh user@production-server

# 2. 创建应用目录
sudo mkdir -p /opt/trustagency
sudo chown $USER:$USER /opt/trustagency
cd /opt/trustagency

# 3. 克隆项目
git clone https://github.com/your-org/trustagency.git .
git checkout main

# 4. 创建数据目录
mkdir -p /data/trustagency/{logs,backups,uploads}
```

### Phase 2: Docker 镜像准备 (10 分钟)

```bash
# 1. 构建后端镜像
cd /opt/trustagency
docker build -f backend/Dockerfile -t trustagency-backend:1.0.0 .

# 2. 构建前端镜像
docker build -f Dockerfile -t trustagency-frontend:1.0.0 .

# 3. 验证镜像
docker images | grep trustagency

# 输出应该显示:
# trustagency-backend     1.0.0    <id>    400MB    2 hours ago
# trustagency-frontend    1.0.0    <id>    50MB     2 hours ago
```

### Phase 3: 启动服务 (15 分钟)

```bash
# 1. 复制生产 Compose 文件
cp docker-compose.prod.yml docker-compose.yml

# 2. 启动所有服务
./docker-start-prod.sh

# 输出应该显示:
# ✓ 检查 Docker 版本
# ✓ 检查 Docker Compose 版本
# ✓ 验证环境配置
# ✓ 创建数据目录
# ✓ 启动 Frontend...
# ✓ 启动 Backend...
# ✓ 启动 Database...
# ✓ 启动 Redis...
# ✓ 启动 Celery Worker...
# ✓ 启动 Celery Beat...
# ✓ 所有服务已启动并健康

# 3. 检查服务状态
docker-compose ps

# 输出应该显示所有容器都在运行:
# NAME                    STATUS
# frontend                Up (healthy)
# backend                 Up (healthy)
# database                Up (healthy)
# redis                   Up (healthy)
# celery-worker           Up (healthy)
# celery-beat             Up (healthy)
```

### Phase 4: 配置反向代理 (10 分钟)

配置 Nginx 作为反向代理：

```bash
# 创建 Nginx 配置
sudo tee /etc/nginx/sites-available/trustagency > /dev/null <<EOF
upstream backend {
    server backend:8001;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到 HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 日志
    access_log /var/log/nginx/trustagency_access.log;
    error_log /var/log/nginx/trustagency_error.log;
    
    # API 路由到后端
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }
    
    # 前台路由到前端
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/trustagency /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 数据库迁移

### 1. 备份现有数据 (如适用)

```bash
# 备份生产数据库
docker-compose exec database pg_dump -U postgres trustagency_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 验证备份
ls -lh backup_*.sql
```

### 2. 初始化数据库

```bash
# 运行迁移脚本
docker-compose exec backend alembic upgrade head

# 或者创建所有表
docker-compose exec backend python init_db.py

# 验证表创建成功
docker-compose exec database psql -U postgres trustagency_prod -c "\dt"
```

### 3. 导入初始数据 (如需要)

```bash
# 导入示例数据
docker-compose exec backend python init_sample_data.py

# 验证数据导入
docker-compose exec database psql -U postgres trustagency_prod -c "SELECT COUNT(*) FROM platforms;"
```

---

## 配置 SSL/TLS

### 使用 Let's Encrypt 免费 SSL 证书

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# 证书将保存在: /etc/letsencrypt/live/yourdomain.com/

# 设置自动续期
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# 验证自动续期
sudo certbot renew --dry-run
```

### 自签名证书 (测试用)

```bash
# 如果不使用 Let's Encrypt
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# 复制到 Nginx 配置目录
sudo cp cert.pem /etc/ssl/certs/
sudo cp key.pem /etc/ssl/private/
```

---

## 监控和告警设置

### 1. 配置日志收集

```bash
# 创建日志目录
sudo mkdir -p /data/trustagency/logs
sudo chown 1001:1001 /data/trustagency/logs

# 配置日志轮转
sudo tee /etc/logrotate.d/trustagency > /dev/null <<EOF
/data/trustagency/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 nobody nobody
    sharedscripts
}
EOF
```

### 2. 配置 Prometheus 监控

```bash
# 创建 prometheus 配置
docker run --detach \
  --name prometheus \
  --network trustagency-net \
  -v /data/trustagency/prometheus.yml:/etc/prometheus/prometheus.yml \
  -p 9090:9090 \
  prom/prometheus:latest
```

### 3. 配置 Grafana 仪表板

```bash
# 启动 Grafana
docker run --detach \
  --name grafana \
  --network trustagency-net \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -p 3000:3000 \
  grafana/grafana:latest

# 访问 http://localhost:3000
# 默认用户名/密码: admin/admin
```

### 4. 配置告警规则

创建 `/data/trustagency/alerts.yml`:

```yaml
groups:
  - name: trustagency
    rules:
      - alert: BackendDown
        expr: up{job="backend"} == 0
        for: 2m
        annotations:
          summary: "Backend is down"
          
      - alert: HighCPUUsage
        expr: cpu_usage > 80
        for: 5m
        annotations:
          summary: "CPU usage is high"
          
      - alert: DatabaseConnectionError
        expr: db_connection_errors_total > 0
        for: 1m
        annotations:
          summary: "Database connection error"
```

---

## 健康检查和验证

### 1. API 端点检查

```bash
# 检查健康状态
curl https://yourdomain.com/api/health

# 预期响应:
# {"status":"ok","message":"TrustAgency Backend is running"}
```

### 2. 服务可用性检查

```bash
# 检查前端
curl -I https://yourdomain.com

# 检查 API 文档
curl -I https://yourdomain.com/api/docs

# 检查数据库连接
docker-compose exec backend python -c "from app.database import engine; print('DB OK' if engine else 'DB Failed')"

# 检查 Redis 连接
docker-compose exec redis redis-cli ping
```

### 3. 数据验证

```bash
# 检查平台数据
curl -X GET https://yourdomain.com/api/platforms?limit=1

# 检查文章数据
curl -X GET https://yourdomain.com/api/articles?limit=1

# 响应应该显示正确的数据结构
```

---

## 回滚计划

如果部署出现问题，按以下步骤回滚：

### 1. 立即停止新版本

```bash
# 停止所有服务
./docker-stop.sh

# 确认所有容器已停止
docker-compose ps
```

### 2. 恢复前一个版本

```bash
# 检查 Git 历史
git log --oneline | head -5

# 回滚到上一个版本
git checkout previous-version-tag

# 或直接从备份恢复
git pull origin main  # 回到最后已知的稳定版本
```

### 3. 恢复数据库 (如需要)

```bash
# 从备份恢复数据库
docker-compose exec database psql -U postgres trustagency_prod < backup_YYYYMMDD_HHMMSS.sql

# 或者使用容器卷快照
docker-compose down -v  # 删除卷
docker volume restore trustagency_postgres_data  # 恢复卷
```

### 4. 重启服务

```bash
# 重新启动所有服务
./docker-start-prod.sh

# 验证服务健康
curl https://yourdomain.com/api/health
```

---

## 故障排除

### 容器无法启动

```bash
# 检查日志
docker-compose logs backend
docker-compose logs database

# 检查资源使用
docker stats

# 检查网络连接
docker network inspect trustagency-net
```

### 数据库连接失败

```bash
# 检查数据库容器
docker-compose ps database

# 验证数据库凭证
echo "SELECT 1;" | docker-compose exec -T database psql -U postgres

# 检查防火墙规则
sudo ufw status
```

### 内存不足

```bash
# 检查内存使用
free -h
docker stats

# 增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Celery 任务未执行

```bash
# 检查 Celery 工作进程
docker-compose logs celery-worker

# 检查 Redis 连接
docker-compose exec redis redis-cli ping

# 重启 Celery
docker-compose restart celery-worker celery-beat
```

---

## 上线后验证

### 第一小时验证清单

- [ ] API 健康检查通过
- [ ] 前端可以正常访问
- [ ] 登录功能正常
- [ ] 可以创建/编辑/删除平台
- [ ] 可以创建/编辑/删除文章
- [ ] 可以提交 AI 生成任务
- [ ] 日志记录正常
- [ ] 监控系统正常运行

### 第一天验证清单

- [ ] 没有未处理的错误日志
- [ ] 系统性能良好 (响应时间 <500ms)
- [ ] 数据库查询性能良好
- [ ] 缓存命中率良好 (>80%)
- [ ] 没有内存泄漏迹象
- [ ] 备份系统运行正常
- [ ] 告警系统工作正常

### 第一周验证清单

- [ ] 系统稳定性良好 (正常运行时间 >99%)
- [ ] 用户反馈积极
- [ ] 没有安全问题报告
- [ ] 性能指标在预期范围内
- [ ] 备份策略有效

---

## 维护和持续监控

### 日常维护任务

```bash
# 每日检查
- 检查系统日志是否有错误
- 监控磁盘空间使用
- 检查数据库连接
- 验证备份完成

# 每周维护
- 检查系统安全更新
- 审查监控告警
- 清理过期日志
- 验证灾难恢复流程
```

### 性能优化建议

1. **缓存策略**
   - 启用 Redis 缓存
   - 设置 CDN 缓存前端资源
   - 配置浏览器缓存

2. **数据库优化**
   - 创建必要的索引
   - 定期分析查询性能
   - 考虑数据分区

3. **应用优化**
   - 启用 GZIP 压缩
   - 优化图像加载
   - 使用连接池

---

**部署完成时间**: 通常 30-60 分钟  
**关键联系方式**: 技术支持电话或邮箱  
**应急联系人**: 24/7 支持热线  

