# 🚀 TrustAgency 线上部署指南 (SQLite版本) - 2C4G CentOS 7.5

## 📌 版本说明

本指南针对 **SQLite 数据库版本**，特别优化了4GB内存的服务器配置。

- ✅ 使用SQLite替代PostgreSQL（节省1.5GB内存）
- ✅ SQLite数据库通过Docker卷持久化
- ✅ 包含Redis和Celery用于后台任务
- ✅ 完全去除PostgreSQL容器

---

## 第一步：服务器初始化

### 1.1 系统更新和基础工具

```bash
# SSH登录到服务器
ssh root@your-server-ip

# 更新系统包
yum update -y
yum install -y git curl wget nano

# 设置时区
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

### 1.2 安装Docker和Docker Compose

```bash
# 安装Docker官方源并安装
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 启动Docker并设置开机自启
systemctl start docker
systemctl enable docker

# 验证Docker安装
docker --version

# 安装Docker Compose（v2.24.0+）
# 🚀 如果官方源下载缓慢，使用国内镜像：
# curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64" \
#   -o /usr/local/bin/docker-compose
# 
# 或使用阿里云CDN（推荐在中国使用）：
curl -L "https://cdn.jsdelivr.net/gh/docker/compose@v2.24.0/contrib/linux/docker-compose-linux-x86_64" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证Docker Compose安装
docker-compose --version

# ⚡ 配置Docker国内镜像源（加快镜像拉取）
# 这一步很重要，可以显著提高部署速度！
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com",
    "https://docker.ycjszz.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 重启Docker使配置生效
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 1.3 验证Docker环境

```bash
# 验证Docker可用性
docker ps

# 输出应该是空列表，没有权限错误
```

---

## 第二步：项目部署

### 2.1 克隆项目到服务器

```bash
# 进入生产目录
cd /opt

# 克隆项目
git clone https://github.com/Lcking/trustagency.git
cd trustagency

# 验证项目结构
ls -la | grep -E "docker-compose|\.env|backend"
```

### 2.2 配置生产环境

#### 2.2.1 复制环境配置文件

```bash
# 复制示例配置文件
cp .env.prod.example .env.prod

# 编辑配置文件
nano .env.prod
```

#### 2.2.2 生成强随机密钥

```bash
# 生成JWT密钥（32字符随机）
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "生成的SECRET_KEY: $SECRET_KEY"

# 复制这个值到 .env.prod 中的 SECRET_KEY 字段
```

#### 2.2.3 编辑 `.env.prod` 文件内容

```bash
nano .env.prod
```

文件内容应该如下：

```ini
# TrustAgency 生产环境配置 (SQLite版本)

# 应用配置
ENVIRONMENT=production
DEBUG=False

# 数据库配置（SQLite）
DATABASE_URL=sqlite:////app/data/trustagency.db

# 安全配置 - 粘贴上面生成的SECRET_KEY
SECRET_KEY=<your-generated-secret-key-here>

# API配置
API_HOST=0.0.0.0
API_PORT=8001

# 日志配置
LOG_LEVEL=INFO
```

保存并退出（Ctrl+O → Enter → Ctrl+X）

### 2.3 验证配置和启动服务

#### ⚠️ 解决 SECRET_KEY 未被加载的问题

如果你看到以下警告，说明 Docker Compose **未能正确读取 `.env.prod` 文件**：
```
WARN[0000] The "SECRET_KEY" variable is not set. Defaulting to a blank string.
```

**根本原因**：Docker Compose 默认只查找当前目录下的 `.env` 文件（必须严格叫这个名字）。即使文件内容正确，如果名字是 `.env.prod`，Docker Compose 的 YAML 解析器也不会自动读取。

**解决方案（推荐方法）**：创建软链接，让 Docker Compose 以为它在读取默认的 `.env` 文件：

```bash
# ✅ 方法一：创建软链接（一劳永逸，推荐）
ln -s .env.prod .env

# 验证软链接已创建
ls -la .env

# 预期输出应该显示 .env -> .env.prod
```

**为什么推荐方法一？**
- ✅ 一次性配置，之后所有命令都无需加参数
- ✅ Docker Compose 自动读取 `.env` 变量
- ✅ 不易出错，最符合 Docker Compose 的设计意图

**备选方案（如不想创建软链接）**：

```bash
# 方法二：严格的参数顺序
# ⚠️ 重要：--env-file 必须紧跟 docker-compose 之后，在任何子命令之前

# ❌ 错误写法（可能导致报错）
docker-compose -f docker-compose.prod.yml up -d --env-file .env.prod

# ✅ 正确写法（--env-file 作为全局参数）
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

#### 启动服务

```bash
# 验证 Docker Compose 配置文件有效
# （如果已创建软链接 .env，这条命令不会再显示 SECRET_KEY 警告）
docker-compose -f docker-compose.prod.yml config > /dev/null && echo "✅ 配置文件有效"

# 第一次启动会构建镜像（需要5-10分钟，如使用国内镜像会更快）
docker-compose -f docker-compose.prod.yml up -d

# 查看实时日志（Ctrl+C退出）
docker-compose -f docker-compose.prod.yml logs -f

# 查看容器启动状态

# ✅ 预期输出（所有服务应该 Up 或 healthy）：
# NAME                            STATUS              PORTS
# trustagency-backend-prod        Up (healthy)        0.0.0.0:8001->8001/tcp
# trustagency-celery-worker-prod  Up                  
# trustagency-celery-beat-prod    Up                  
# trustagency-redis-prod          Up (healthy)        6379/tcp
```

**预期输出**：
```
NAME                            STATUS              PORTS
trustagency-backend-prod        Up (healthy)        0.0.0.0:8001->8001/tcp
trustagency-celery-worker-prod  Up                  
trustagency-celery-beat-prod    Up                  
trustagency-redis-prod          Up (healthy)        6379/tcp
```

### 2.4 验证后端服务

```bash
# 检查后端健康状态（⚠️ 注意：端点是 /api/health，不是 /health）
curl http://localhost:8001/api/health

# 预期返回：{"status":"ok","message":"TrustAgency Backend is running"}

# 查看API文档（本地测试）
curl -s http://localhost:8001/api/docs | head -20

# 或者直接在浏览器中访问
# http://localhost:8001/api/docs
```

---

## 第三步：配置反向代理和域名

### 选项A：使用已安装的宝塔Nginx（推荐）

```bash
# 进入宝塔Nginx配置目录
cd /www/server/nginx/conf/vhost

# 创建网站配置
cat > trustagency.conf << 'NGINX'
upstream backend {
    server 127.0.0.1:8001;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 记录访问日志
    access_log /www/wwwlogs/trustagency_access.log;
    error_log /www/wwwlogs/trustagency_error.log;
}
NGINX

# 检查Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

### 选项B：无宝塔，使用Docker Nginx（可选）

项目的Docker Compose已配置暴露在80端口，可直接使用。

### 绑定域名

```bash
# 配置DNS记录
# 在你的域名注册商将A记录指向服务器IP

# 验证域名解析
nslookup yourdomain.com
```

---

## 第四步：配置SSL证书（HTTPS）

### 4.1 使用Let's Encrypt免费证书

```bash
# 安装Certbot
yum install -y epel-release
yum install -y certbot certbot-nginx

# 申请证书（需要域名已正确解析）
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 证书位置：
# - 证书: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# - 私钥: /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 4.2 配置Nginx支持HTTPS

> ⚠️ 根据你是否安装宝塔面板，选择下面其一。

#### 方案A：系统原生Nginx（无宝塔，推荐）

```bash
sudo tee /etc/nginx/conf.d/trustagency.conf > /dev/null <<'NGINX'
upstream backend {
  server 127.0.0.1:8001;
  keepalive 32;
}

server {
  listen 80;
  listen [::]:80;
  server_name yourdomain.com www.yourdomain.com;
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  server_name yourdomain.com www.yourdomain.com;

  ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 10m;

  client_max_body_size 100M;

  location / {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
  }

  access_log /var/log/nginx/trustagency_access.log;
  error_log  /var/log/nginx/trustagency_error.log;
}
NGINX

# 确保日志目录存在
sudo mkdir -p /var/log/nginx
sudo touch /var/log/nginx/trustagency_access.log /var/log/nginx/trustagency_error.log
sudo chown nginx:nginx /var/log/nginx/trustagency_*log || true

# 检查并重载
sudo nginx -t && sudo systemctl reload nginx
```

#### 方案B：宝塔面板 Nginx

```bash
sudo mkdir -p /www/server/nginx/conf/vhost
sudo mkdir -p /www/wwwlogs
nano /www/server/nginx/conf/vhost/trustagency.conf

# 粘贴上面的同一份 server 配置

# 检查并重启宝塔 Nginx
nginx -t && systemctl restart nginx
```

### 4.3 设置证书自动续期

```bash
# 创建续期脚本
cat > /usr/local/bin/renew-ssl.sh << 'SCRIPT'
#!/bin/bash
certbot renew --quiet
systemctl reload nginx
SCRIPT

chmod +x /usr/local/bin/renew-ssl.sh

# 添加到crontab（每月检查一次）
(crontab -l 2>/dev/null; echo "0 3 1 * * /usr/local/bin/renew-ssl.sh") | crontab -
```

---

## 第五步：数据库初始化

### 5.1 等待SQLite数据库初始化

```bash
# 后端启动时会自动创建 trustagency.db 文件
# 查看日志确认初始化成功
docker-compose -f docker-compose.prod.yml logs backend | grep "✅"

# 应该看到：
# ✅ 数据库表创建成功
# ✅ 默认管理员创建成功
# ✅ 默认栏目创建成功
# ✅ 默认平台创建成功
# ✅ 默认 AI 配置创建成功
```

### 5.2 验证数据库文件

```bash
# 检查SQLite数据库文件大小
docker-compose -f docker-compose.prod.yml exec backend ls -lh /app/data/trustagency.db

# 或直接查看卷中的文件
ls -lh /var/lib/docker/volumes/trustagency_sqlite_data/_data/trustagency.db
```

---

## 第六步：验证完整部署

### 6.1 健康检查

```bash
# 检查后端API（⚠️ 注意：端点是 /api/health，不是 /health）
curl http://localhost:8001/api/health

# 预期返回：
# {"status":"ok","message":"TrustAgency Backend is running"}

# 检查所有容器健康状态
docker-compose -f docker-compose.prod.yml ps

# 所有HEALTH列应该显示 (healthy) 或 Up
```

### 6.2 访问应用

```bash
# 前端地址
http://yourdomain.com

# 后台管理系统
http://yourdomain.com/admin/
# 默认用户: admin
# 默认密码: admin123（**请立即修改**）

# API文档（Swagger）
http://yourdomain.com/api/docs

# OpenAPI Schema
http://yourdomain.com/api/openapi.json
```

### 6.3 测试核心功能

```bash
# 测试登录
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 应该返回包含token的响应
```

---

## 第七步：监控和维护

### 7.1 常用管理命令

```bash
# 查看所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看实时日志（所有服务）
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend

# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 停止所有服务（数据保留）
docker-compose -f docker-compose.prod.yml stop

# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 停止并删除容器（数据保留在卷中）
docker-compose -f docker-compose.prod.yml down
```

### 7.2 资源监控

```bash
# 实时查看Docker资源使用
docker stats

# 查看SQLite数据库文件大小
du -sh /var/lib/docker/volumes/trustagency_sqlite_data/_data/

# 查看总磁盘使用
df -h

# 清理未使用的Docker资源
docker system prune -a
```

### 7.3 SQLite数据库备份

```bash
# 备份SQLite数据库文件
cp /var/lib/docker/volumes/trustagency_sqlite_data/_data/trustagency.db \
   ./backup_$(date +%Y%m%d_%H%M%S).db

# 或通过容器备份
docker-compose -f docker-compose.prod.yml exec backend \
  cp /app/data/trustagency.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db

# 查看备份
docker-compose -f docker-compose.prod.yml exec backend ls -lh /app/data/

# 恢复数据库（如需要）
# 停止容器
docker-compose -f docker-compose.prod.yml down

# 替换数据库文件
cp ./backup_20240101_120000.db \
   /var/lib/docker/volumes/trustagency_sqlite_data/_data/trustagency.db

# 重启容器
docker-compose -f docker-compose.prod.yml up -d
```

### 7.4 定期维护脚本

```bash
# 创建日常备份脚本
cat > /usr/local/bin/backup-trustagency.sh << 'SCRIPT'
#!/bin/bash
BACKUP_DIR="/opt/trustagency/backups"
mkdir -p $BACKUP_DIR

# 备份SQLite数据库
docker-compose -f /opt/trustagency/docker-compose.prod.yml exec -T backend \
  sqlite3 /app/data/trustagency.db ".dump" > \
  $BACKUP_DIR/trustagency_$(date +%Y%m%d_%H%M%S).sql

# 保留最近30天的备份
find $BACKUP_DIR -name "trustagency_*.sql" -mtime +30 -delete

echo "✅ 备份完成"
SCRIPT

chmod +x /usr/local/bin/backup-trustagency.sh

# 添加到crontab（每天凌晨2点备份）
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-trustagency.sh") | crontab -
```

---

## 🆘 故障排查

### 问题1：调用 `/health` 端点返回 404

```bash
# ❌ 错误：返回 Not Found (404)
curl http://localhost:8001/health
# {"detail":"Not Found"}

# ✅ 正确：使用完整路径 /api/health
curl http://localhost:8001/api/health
# {"status":"ok","message":"TrustAgency Backend is running"}

# 所有 API 端点都在 /api 路径下
# 正确的端点列表：
# - /api/health          (健康检查)
# - /api/auth/login      (登录)
# - /api/docs            (Swagger 文档)
# - /api/openapi.json    (OpenAPI Schema)
```

### 问题1：SECRET_KEY 变量未被加载警告

```bash
# 症状：看到以下警告
WARN[0000] The "SECRET_KEY" variable is not set. Defaulting to a blank string.
WARN[0000] The "SECRET_KEY" variable is not set. Defaulting to a blank string.

# 原因：Docker Compose 默认只查找 .env 文件，不会自动读取 .env.prod

# ✅ 解决方案 1（推荐）：创建软链接
ln -s .env.prod .env
# 之后所有命令无需加参数，直接运行：
docker-compose -f docker-compose.prod.yml up -d

# ✅ 解决方案 2：使用正确的参数顺序
# --env-file 必须紧跟 docker-compose 之后
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 验证 SECRET_KEY 已被正确加载
docker-compose -f docker-compose.prod.yml config | grep -A 2 "SECRET_KEY"
# 应该显示你生成的随机密钥，而不是空值
```

### 问题2：容器启动失败

```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs backend

# 常见原因：
# 1. .env.prod配置错误 → 检查SECRET_KEY
# 2. 端口冲突 → 检查8001端口是否被占用
# 3. 内存不足 → 运行 free -h 检查内存

# 解决：
# - 检查.env.prod格式是否正确
# - 杀死占用8001的进程：lsof -i :8001 && kill -9 <PID>
# - 查看内存：free -h
```

### 问题2：无法连接数据库

```bash
# 检查SQLite数据库文件是否存在
ls -lh /var/lib/docker/volumes/trustagency_sqlite_data/_data/trustagency.db

# 检查文件权限
docker-compose -f docker-compose.prod.yml exec backend \
  ls -lh /app/data/trustagency.db

# 重新初始化数据库
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 问题3：Celery任务无法执行

```bash
# 检查Redis是否运行
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# 查看Celery任务队列
docker-compose -f docker-compose.prod.yml exec celery-worker \
  celery -A app.celery_tasks inspect active

# 查看任务统计
docker-compose -f docker-compose.prod.yml exec celery-worker \
  celery -A app.celery_tasks inspect stats
```

### 问题4：内存不足（4GB服务器）

```bash
# 查看当前内存使用
free -h

# 查看Docker容器内存占用
docker stats --no-stream

# 如果内存紧张，优化：
# 1. 减少Celery并发（编辑docker-compose.prod.yml）
#    --concurrency=1（而不是2）
# 2. 停止其他不必要的服务
# 3. 增加Redis内存限制的积极性
```

### 问题5：网站无法访问

```bash
# 检查Nginx是否运行
systemctl status nginx

# 查看Nginx错误日志
tail -f /www/wwwlogs/trustagency_error.log

# 检查防火墙
firewall-cmd --list-ports

# 测试后端连接
curl -v http://localhost:8001/health
```

---

## 📊 资源分配（2C4G配置）

### 内存使用

```
总内存: 4GB
├── 操作系统: 500MB
├── 后端API: 800MB (FastAPI)
├── Celery Worker: 400MB (concurrency=2)
├── Celery Beat: 200MB
├── Redis: 300MB
├── SQLite: 50-200MB（根据数据量）
└── 缓冲/缓存: 650MB-1GB
```

### Docker资源限制（docker-compose.prod.yml）

```yaml
Backend:
  memory: 1.5G  # 最大内存
  cpus: 2       # 最大CPU

Celery Worker:
  memory: 700M
  cpus: 1

Celery Beat:
  memory: 400M
  cpus: 0.5

Redis:
  memory: 300M
  cpus: 0.5
```

---

## ✅ 部署完成检查清单

- [ ] 服务器系统已更新
- [ ] Docker和Docker Compose已安装
- [ ] 项目代码已克隆到 /opt/trustagency
- [ ] .env.prod已配置（SECRET_KEY已设置）
- [ ] docker-compose.prod.yml检查通过
- [ ] 所有容器已成功启动
- [ ] 容器状态显示为healthy或Up
- [ ] 后端API健康检查通过
- [ ] 前端网站可访问
- [ ] 后台管理可登录（admin/admin123）
- [ ] API文档可访问
- [ ] SSL证书已配置
- [ ] 防火墙已开放必要端口（80/443）
- [ ] 默认管理员密码已修改
- [ ] SQLite数据库备份脚本已配置
- [ ] 监控日志已设置

---

## 🔗 相关资源

- **项目GitHub**: https://github.com/Lcking/trustagency
- **Docker官方文档**: https://docs.docker.com
- **Docker Compose参考**: https://docs.docker.com/compose
- **FastAPI部署指南**: https://fastapi.tiangolo.com/deployment
- **SQLite文档**: https://www.sqlite.org/docs.html
- **Nginx文档**: https://nginx.org/en/docs
- **Let's Encrypt**: https://letsencrypt.org

---

**部署时间预估**: 20-30分钟（第一次构建镜像较慢）  
**技术支持**: 查看项目文档或GitHub Issues

祝部署顺利！ 🚀
