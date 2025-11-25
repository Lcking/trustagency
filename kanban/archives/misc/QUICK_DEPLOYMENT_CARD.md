# ⚡ 快速部署参考卡片

## 📋 一页纸部署清单

### 环境检查
```bash
# SSH登录到服务器
ssh root@YOUR_SERVER_IP

# 检查系统
cat /etc/os-release | grep VERSION
uname -m
free -h
```

### 系统准备（<5分钟）
```bash
# 更新系统
yum update -y
yum install -y git curl wget

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
systemctl start docker && systemctl enable docker

# 安装Docker Compose
curl -L https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证
docker --version && docker-compose --version
```

### 项目部署（<15分钟）
```bash
# 克隆项目
cd /opt
git clone https://github.com/Lcking/trustagency.git
cd trustagency

# 配置生产环境
cp .env.prod.example .env.prod

# 生成强密码和密钥
echo "DB_PASSWORD=$(openssl rand -base64 32)"
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"

# 编辑.env.prod，粘贴上面的值
nano .env.prod

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 检查状态
docker-compose -f docker-compose.prod.yml ps
```

### 验证部署（<5分钟）
```bash
# 检查后端
curl http://localhost:8001/health

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 访问应用
# 前端: http://yourdomain.com
# 后台: http://yourdomain.com/admin (admin/admin123)
# API文档: http://yourdomain.com/api/docs
```

### 配置域名和SSL（<10分钟）
```bash
# 如果已安装宝塔，配置反向代理
# 如果没有，使用Docker内置Nginx

# 申请SSL证书
yum install -y certbot
certbot certonly --standalone -d yourdomain.com

# 配置Nginx使用证书
# 编辑 nginx/default.conf 或宝塔Nginx配置
```

---

## 🆘 快速故障排查

| 问题 | 检查命令 | 解决方案 |
|------|---------|--------|
| 容器不启动 | `docker-compose logs backend` | 检查.env.prod密码是否正确 |
| 数据库连接失败 | `docker-compose exec db psql -U trustagency` | 等待db容器healthy（30s） |
| 内存溢出 | `free -h && docker stats` | 减少Celery并发：--concurrency=2 |
| 无法访问 | `curl http://localhost:8001/health` | 检查防火墙、Nginx配置 |
| API返回502 | `docker-compose logs backend` | 查看后端错误日志 |

---

## 📊 资源分配（2C4G建议）

```
Celery Worker: --concurrency=2 (不3或以上)
PostgreSQL: max_connections=50
Redis: maxmemory 256mb
Frontend: 静态文件, Nginx缓存
```

---

## 🔒 安全步骤

```bash
# 1. 修改默认密码
# 登录后台 → 设置 → 修改密码

# 2. 启用防火墙
systemctl start firewalld && systemctl enable firewalld
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload

# 3. 保护.env.prod
chmod 600 /opt/trustagency/.env.prod

# 4. 启用SSL
# 使用certbot申请Let's Encrypt证书
```

---

## 📈 监控命令

```bash
# 实时监控
docker stats

# 查看所有容器
docker-compose -f docker-compose.prod.yml ps

# 实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 进入容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 重启服务
docker-compose -f docker-compose.prod.yml restart backend

# 完整重启
docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d
```

---

## 📁 重要文件位置

```
项目目录: /opt/trustagency/
├── .env.prod              ← 生产配置（保密）
├── docker-compose.prod.yml  ← Docker配置
├── nginx/default.conf     ← Nginx配置
├── backend/
│   ├── Dockerfile         ← 后端镜像
│   └── requirements.txt    ← Python依赖
├── backend/logs/          ← 应用日志
└── DEPLOYMENT_GUIDE_2C4G.md ← 详细指南
```

---

## 🚀 一条命令启动

```bash
cd /opt/trustagency && \
cp .env.prod.example .env.prod && \
# 编辑.env.prod填入密码 && \
docker-compose -f docker-compose.prod.yml up -d && \
docker-compose -f docker-compose.prod.yml ps
```

---

## 💾 备份命令

```bash
# 备份数据库
docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
  -U trustagency trustagency > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
cat backup_20240101_120000.sql | \
  docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U trustagency trustagency
```

---

## ❌ 常见错误避免

```
❌ 不要：在生产环境使用 DEBUG=True
❌ 不要：使用简单密码（DB_PASSWORD和SECRET_KEY）
❌ 不要：开放所有防火墙端口
❌ 不要：在主分支部署前测试
❌ 不要：忘记修改默认管理员密码

✅ 要：使用强随机密码
✅ 要：配置SSL证书
✅ 要：启用防火墙
✅ 要：定期备份
✅ 要：监控日志
```

---

**需要帮助？** 查看详细指南：`DEPLOYMENT_GUIDE_2C4G.md`

**决策困惑？** 查看对比指南：`DEPLOYMENT_DECISION_GUIDE.md`
