# 🚀 TrustAgency 线上部署指南 (2C4G CentOS 7.5)

## 📌 前言

项目已完全支持Docker Compose部署。**推荐使用Docker方案而非宝塔**，理由如下：

| 对比项 | 宝塔方案 | Docker方案 | 优势 |
|------|--------|----------|------|
| 内存占用 | 600MB+ | 轻量级 | Docker节省300MB |
| 资源隔离 | 否 | 是 | Docker更稳定 |
| 可扩展性 | 差 | 好 | Docker易于水平扩展 |
| Python支持 | 一般 | 专业 | Docker为Python优化 |
| 生产就绪 | 否 | 是 | Docker生产级别 |

---

## 第一步：服务器初始化

### 1.1 系统更新和基础工具

```bash
# SSH登录到服务器
ssh root@your-server-ip

# 更新系统包
yum update -y
yum install -y git curl wget

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

# 安装Docker Compose（推荐v2.24.0及以上）
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证Docker Compose安装
docker-compose --version
```

### 1.3 验证Docker环境

```bash
# 验证Docker可用性
docker ps

# 应该返回空列表（无容器），没有权限错误
```

---

## 第二步：项目部署

### 2.1 克隆项目到服务器

```bash
# 进入生产目录（推荐）
cd /opt

# 克隆项目
git clone https://github.com/Lcking/trustagency.git
cd trustagency

# 验证项目结构
ls -la | grep -E "docker-compose|\.env|backend|frontend"
```

### 2.2 配置生产环境

#### 2.2.1 创建 `.env.prod` 文件

```bash
# 复制示例文件
cp .env.prod.example .env.prod

# 编辑配置
nano .env.prod
```

#### 2.2.2 生成强随机密码和密钥

```bash
# 生成数据库密码（32字节随机）
DB_PASSWORD=$(openssl rand -base64 32)
echo "DB_PASSWORD=$DB_PASSWORD"

# 生成JWT密钥（32字符随机）
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SECRET_KEY=$SECRET_KEY"

# 复制这两个值到 .env.prod
```

#### 2.2.3 编辑 `.env.prod` 文件内容

```ini
# TrustAgency 生产环境配置

# ==================== 应用配置 ====================
ENVIRONMENT=production
DEBUG=False

# ==================== 数据库配置 ====================
# 粘贴上面生成的强随机密码
DB_PASSWORD=<your-strong-random-password-here>

# ==================== 安全配置 ====================
# 粘贴上面生成的JWT密钥
SECRET_KEY=<your-production-secret-key-here>

# ==================== 其他配置（可选） ====================
# OPENAI_API_KEY=sk-your-api-key-if-needed
```

### 2.3 预部署检查

```bash
# 运行部署前检查脚本
bash pre-deployment-checklist.sh

# 应该看到大量的 ✅ 通过检查

# 验证 Docker Compose 配置文件有效
docker-compose -f docker-compose.prod.yml config > /dev/null && echo "✅ 配置文件有效"
```

### 2.4 启动所有服务

```bash
# 第一次启动会构建镜像（可能需要5-10分钟）
docker-compose -f docker-compose.prod.yml up -d

# 查看实时日志（Ctrl+C退出）
docker-compose -f docker-compose.prod.yml logs -f

# 查看容器启动状态
docker-compose -f docker-compose.prod.yml ps
```

**预期输出：**
```
NAME                            STATUS              PORTS
trustagency-backend-prod        Up (healthy)        0.0.0.0:8001->8001/tcp
trustagency-celery-worker-prod  Up                  
trustagency-celery-beat-prod    Up                  
trustagency-db-prod             Up (healthy)        5432/tcp
trustagency-redis-prod          Up (healthy)        6379/tcp
```

### 2.5 验证后端服务

```bash
# 检查后端健康状态
curl http://localhost:8001/health

# 预期返回：{"status": "ok"}

# 查看API文档（本地测试）
curl -s http://localhost:8001/api/docs | head -20
```

---

## 第三步：配置反向代理和域名

### 选项A：使用宝塔的Nginx（如果已安装宝塔）

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

### 选项B：不使用宝塔，使用Docker Nginx

项目的Docker Compose已包含Nginx容器，暴露在80端口。如果要修改配置：

```bash
# 编辑Nginx配置
nano ./nginx/default.conf

# 重启Nginx容器
docker-compose -f docker-compose.prod.yml restart nginx
```

### 绑定域名

```bash
# 编辑服务器hosts文件（本地测试）或配置DNS记录
# DNS管理器中将A记录指向服务器IP

# 验证域名解析
nslookup yourdomain.com
ping yourdomain.com
```

---

## 第四步：配置SSL证书（HTTPS）

### 4.1 使用Let's Encrypt免费证书

```bash
# 安装Certbot
yum install -y epel-release
yum install -y certbot certbot-nginx

# 申请证书（需要域名已绑定）
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 证书位置：
# - 证书: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# - 私钥: /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 4.2 配置Nginx支持HTTPS

```bash
# 编辑之前创建的 trustagency.conf
cat > /www/server/nginx/conf/vhost/trustagency.conf << 'NGINX'
upstream backend {
    server 127.0.0.1:8001;
    keepalive 32;
}

# HTTP重定向到HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS服务
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL安全配置
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
    
    access_log /www/wwwlogs/trustagency_access.log;
    error_log /www/wwwlogs/trustagency_error.log;
}
NGINX

# 检查并重启Nginx
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

### 5.1 等待数据库就绪

```bash
# 查看PostgreSQL容器日志
docker-compose -f docker-compose.prod.yml logs db

# 等待看到这条消息：
# "database system is ready to accept connections"
```

### 5.2 初始化应用数据库

```bash
# 进入后端容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 初始化数据库（如需要）
python -m app.init_db

# 查看初始化结果
# 应该看到"✅ 数据库初始化完成"

# 退出容器
exit
```

---

## 第六步：验证完整部署

### 6.1 健康检查

```bash
# 检查后端API
curl http://localhost:8001/health

# 预期返回：{"status": "ok"}

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

# 停止并删除容器（**数据保留在volumes中**）
docker-compose -f docker-compose.prod.yml down

# 完全清理（**谨慎：删除所有容器和数据卷**）
docker-compose -f docker-compose.prod.yml down -v
```

### 7.2 资源监控

```bash
# 实时查看Docker资源使用
docker stats

# 查看具体容器资源
docker stats trustagency-backend-prod

# 查看磁盘使用
du -sh /var/lib/docker/volumes/*
df -h

# 清理未使用的镜像和容器
docker image prune -a --force
docker container prune --force
docker volume prune --force
```

### 7.3 定期备份

```bash
# 备份PostgreSQL数据库
docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
  -U trustagency trustagency > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库（如需要）
cat backup_20240101_120000.sql | \
  docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U trustagency trustagency

# 备份Redis数据
docker-compose -f docker-compose.prod.yml exec redis redis-cli BGSAVE

# 查看Redis备份位置
docker exec trustagency-redis-prod ls -lah /data/
```

### 7.4 查看日志文件

```bash
# 查看后端应用日志
cat /opt/trustagency/backend/logs/app.log

# 实时监控日志
tail -f /opt/trustagency/backend/logs/app.log

# 搜索错误
grep ERROR /opt/trustagency/backend/logs/app.log
```

---

## 第八步：安全加固

### 8.1 防火墙配置

```bash
# 启用防火墙
systemctl start firewalld
systemctl enable firewalld

# 开放HTTP/HTTPS/SSH端口
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp

# 重新加载防火墙
firewall-cmd --reload

# 查看开放的端口
firewall-cmd --list-ports
```

### 8.2 密钥安全

```bash
# 确保 .env.prod 只有root可读
chmod 600 /opt/trustagency/.env.prod

# 验证权限
ls -la /opt/trustagency/.env.prod
# 应该显示 -rw------- 

# 防止秘钥文件被上传到Git
echo ".env.prod" >> /opt/trustagency/.gitignore
echo ".env.prod.local" >> /opt/trustagency/.gitignore
```

### 8.3 修改默认密码

```bash
# SSH进入后台管理系统
http://yourdomain.com/admin/

# 使用默认用户登录
# 用户: admin
# 密码: admin123

# 进入 设置 → 修改密码
# 设置强密码（至少12字符，包含大小写字母、数字、特殊字符）
```

### 8.4 定期更新

```bash
# 更新系统
yum update -y

# 拉取最新的Docker镜像
docker-compose -f docker-compose.prod.yml pull

# 重建容器
docker-compose -f docker-compose.prod.yml up -d

# 查看更新日志
docker-compose -f docker-compose.prod.yml logs
```

---

## 🆘 故障排查

### 问题1：容器启动失败

```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs backend

# 常见原因：
# 1. .env.prod配置错误 → 检查DB_PASSWORD和SECRET_KEY
# 2. 端口冲突 → 检查8001端口是否被占用
# 3. 内存不足 → 运行 free -h 检查内存
```

### 问题2：数据库连接错误

```bash
# 检查PostgreSQL是否运行
docker-compose -f docker-compose.prod.yml ps db

# 测试数据库连接
docker-compose -f docker-compose.prod.yml exec db \
  psql -U trustagency -d trustagency -c "SELECT 1"

# 检查连接字符串
grep DATABASE_URL .env.prod
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

# 如果内存紧张，优化方案：

# 1. 减少Celery并发（编辑docker-compose.prod.yml）
# 将以下行：
# command: celery -A app.celery_tasks worker --loglevel=info --concurrency=4
# 改为：
# command: celery -A app.celery_tasks worker --loglevel=info --concurrency=2

# 2. 减少PostgreSQL连接数
# 在docker-compose.prod.yml中修改：
# POSTGRES_INITDB_ARGS=-c max_connections=50 -c shared_buffers=128MB

# 3. 减少Redis内存限制
# redis-server --maxmemory 256mb
```

### 问题5：网站无法访问

```bash
# 检查Nginx是否运行
docker-compose -f docker-compose.prod.yml ps nginx
# 或 systemctl status nginx

# 查看Nginx日志
docker-compose -f docker-compose.prod.yml logs nginx
# 或 tail -f /www/wwwlogs/trustagency_error.log

# 检查防火墙
firewall-cmd --list-ports

# 测试后端连接
curl -v http://localhost:8001/health
```

---

## 📊 性能优化建议（2C4G）

### 资源分配策略

```
总内存: 4GB
├── 操作系统: 500MB
├── 后端API: 800MB (FastAPI + Gunicorn)
├── Celery Worker: 500MB (concurrency=2)
├── Celery Beat: 200MB
├── PostgreSQL: 1.5GB (shared_buffers=256MB)
├── Redis: 256MB
└── 缓冲/缓存: 244MB
```

### Docker Compose优化

```yaml
# docker-compose.prod.yml 中的资源限制
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### PostgreSQL优化

```bash
# 查看当前配置
docker-compose -f docker-compose.prod.yml exec db \
  psql -U trustagency -c "SHOW shared_buffers;"

# 启用连接池（可选）
# 编辑 docker-compose.prod.yml，添加PgBouncer服务
```

### 缓存优化

```bash
# 查看Redis内存使用
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory

# 查看Redis键数量
docker-compose -f docker-compose.prod.yml exec redis redis-cli DBSIZE

# 清理过期键
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHDB
```

---

## 📋 部署完成检查清单

- [ ] 服务器系统已更新（yum update -y）
- [ ] Docker已安装并启动
- [ ] Docker Compose已安装
- [ ] 项目代码已克隆到 /opt/trustagency
- [ ] .env.prod已配置（DB_PASSWORD和SECRET_KEY）
- [ ] 所有容器已成功启动（docker-compose ps显示healthy）
- [ ] 后端API健康检查通过（curl localhost:8001/health）
- [ ] 前端网站可访问（http://yourdomain.com）
- [ ] 后台管理可登录（http://yourdomain.com/admin）
- [ ] API文档可访问（http://yourdomain.com/api/docs）
- [ ] SSL证书已配置（HTTPS可用）
- [ ] 防火墙已开放必要端口
- [ ] 默认管理员密码已修改
- [ ] 日志收集已配置
- [ ] 备份策略已制定
- [ ] 监控告警已设置（可选）

---

## 🔗 相关资源

- **项目GitHub**: https://github.com/Lcking/trustagency
- **Docker官方文档**: https://docs.docker.com
- **Docker Compose参考**: https://docs.docker.com/compose
- **FastAPI部署指南**: https://fastapi.tiangolo.com/deployment
- **PostgreSQL文档**: https://www.postgresql.org/docs
- **Nginx文档**: https://nginx.org/en/docs
- **Let's Encrypt**: https://letsencrypt.org

---

**部署时间预估**: 30-45分钟（第一次构建镜像较慢）  
**技术支持**: 查看项目文档或GitHub Issues

祝部署顺利！ 🚀
