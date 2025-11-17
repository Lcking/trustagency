# 🌐 TrustAgency 线上部署架构说明

**创建日期**: 2025-11-17  
**更新日期**: 2025-11-17  
**部署环境**: 生产环境

---

## 📍 线上部署端口说明

### 🎯 核心答案

根据您项目的配置文件分析，**线上部署的是 Port 8001**

---

## 🏗️ 部署架构详解

### 本地开发环境

```
用户浏览器
    ↓
Port 8001 (前端服务)
    ↓
site/ 文件夹 (HTML/CSS/JS)
    
Port 8000 (后端 API) ← 单独用于测试
    ↓
backend/app/ (FastAPI)
    ↓
SQLite 数据库
```

### 生产环境（Docker Compose）

```
用户浏览器
    ↓
Nginx (Reverse Proxy) - Port 80/443
    ↓
Port 8001 (FastAPI Backend 容器)
    ├─ FastAPI 应用
    ├─ 前端文件 (内置)
    ├─ API 处理
    └─ 后台任务
    
    ↓ 依赖
    
PostgreSQL (Port 5432)
    └─ 生产数据库
    
Redis (Port 6379)
    └─ 缓存和消息队列
```

---

## 📊 配置文件对比

### .env.prod 配置

```
API_HOST=0.0.0.0
API_PORT=8001          ← **关键：生产环境使用 8001 端口**
ENVIRONMENT=production
```

### docker-compose.prod.yml 配置

```yaml
backend:
  ports:
    - "8001:8001"      ← **容器内 8001 映射到宿主机 8001**
  environment:
    - ENVIRONMENT=production
```

### nginx/default.conf 配置

```nginx
server {
    listen 80 default_server;  ← **Nginx 监听 80 端口（HTTP）**
    root /usr/share/nginx/html;
    
    # 所有请求都指向静态文件
    location / {
        try_files $uri $uri/ $uri/index.html =404;
    }
}
```

---

## 🚀 三种部署方式对比

### 方式 1: 本地开发 (当前)

| 组件 | 端口 | 访问方式 | 说明 |
|------|------|---------|------|
| 前端 | 8001 | http://localhost:8001/ | Python HTTP 服务器 |
| 后端 | 8000 | http://localhost:8000/api | FastAPI 服务器 |
| 数据库 | 本地 | 本地 SQLite | 开发用 SQLite |

**启动命令**:
```bash
bash run.sh
```

### 方式 2: Docker Compose 生产

| 组件 | 端口 | 访问方式 | 说明 |
|------|------|---------|------|
| **Nginx** | **80/443** | http://yourdomain.com | 反向代理 |
| 后端 | 8001 | 内部访问 | FastAPI 容器 |
| PostgreSQL | 5432 | 内部访问 | 生产数据库 |
| Redis | 6379 | 内部访问 | 缓存和队列 |
| Celery Worker | 内部 | 内部访问 | 后台任务 |
| Celery Beat | 内部 | 内部访问 | 定时任务 |

**启动命令**:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

**访问方式**:
- http://yourdomain.com (Nginx 80 端口)
- 不直接暴露 8001 端口

### 方式 3: Nginx 作为前端代理

```
用户 → Nginx (80/443) → FastAPI (8001)
                      ↓
                    静态文件 (site/)
                    ↓
                    API 路由 (/api)
```

---

## 🎯 应该部署哪个端口？

### ✅ **生产环境：部署 Port 8001**

**理由**:
1. FastAPI 应用在 Port 8001 运行
2. 前端文件已内置在 FastAPI 容器中
3. Nginx 反向代理到 8001
4. 用户通过 Nginx (80/443) 访问，**不直接访问 8001**

### ❌ **不部署 Port 8000**

**原因**:
- Port 8000 只用于本地开发测试
- 生产环境不需要独立的 API 服务器
- FastAPI 已经在 8001 端口处理 API 请求

---

## 📋 生产部署检查清单

### 网络配置

- [ ] Nginx 配置在 Port 80/443
- [ ] FastAPI 后端配置在 Port 8001
- [ ] 防火墙只允许 80/443 对外
- [ ] 8001 端口仅内部访问（可选，看安全策略）

### 端口映射

```
互联网用户
    ↓
Port 80/443 (Nginx - 公开)
    ↓
Port 8001 (FastAPI - 内部)
    ↓
PostgreSQL/Redis (完全内部)
```

### 安全配置

- [ ] 生成强密钥 (SECRET_KEY)
- [ ] 配置 HTTPS/SSL
- [ ] 设置 CORS 策略
- [ ] 更新数据库密码
- [ ] 配置 SMTP 邮件
- [ ] 启用防火墙规则

---

## 💻 启动生产环境

### 步骤 1: 准备生产配置

```bash
# 复制生产环境配置文件
cp .env.prod.example .env.prod

# 编辑生产配置（修改敏感信息）
nano .env.prod
```

### 步骤 2: 启动 Docker Compose

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 步骤 3: 验证部署

```bash
# 检查 Nginx
curl http://localhost:80/

# 检查后端 API (内部访问)
curl http://localhost:8001/api/articles

# 查看进程
docker ps | grep trustagency
```

### 步骤 4: 配置域名

```bash
# 更新 Nginx 配置中的域名
# 编辑 nginx/default.conf
server_name yourdomain.com;

# 配置 SSL 证书 (Let's Encrypt)
# 或使用自签名证书
```

---

## 📊 容器内部通信

### Docker 网络拓扑

```
trustagency-net (自定义网络)
│
├─ backend (FastAPI) - Port 8001
│   ├─ 接收 Nginx 的请求
│   ├─ 连接 PostgreSQL (db:5432)
│   └─ 连接 Redis (redis:6379)
│
├─ db (PostgreSQL) - Port 5432
│   └─ 存储所有数据
│
├─ redis (Redis) - Port 6379
│   ├─ 缓存
│   └─ 消息队列
│
├─ celery-worker
│   └─ 后台任务处理
│
└─ celery-beat
    └─ 定时任务调度
```

### 服务间通信

```
Nginx → backend:8001        (HTTP)
backend → db:5432           (PostgreSQL)
backend → redis:6379        (Redis)
celery → redis:6379         (Message Broker)
celery-beat → redis:6379    (Broker)
```

---

## 🔐 端口安全策略

### 对外暴露

```
Port 80   (HTTP)  ← Nginx
Port 443  (HTTPS) ← Nginx + SSL
```

### 内部使用（防火墙保护）

```
Port 8001  (FastAPI) - 仅容器内
Port 5432  (PostgreSQL) - 仅容器内
Port 6379  (Redis) - 仅容器内
```

### 本地开发（允许所有）

```
Port 8000  (后端 API - 开发)
Port 8001  (前端服务 - 开发)
```

---

## 🚀 快速答案总结

| 问题 | 答案 |
|------|------|
| **线上用什么端口?** | **Port 8001 (FastAPI)** |
| **用户访问哪个端口?** | **Port 80/443 (Nginx)** |
| **Port 8000 用途?** | 本地开发和测试 |
| **Port 8001 作用?** | 生产环境主应用 |
| **需要两个都部署?** | **否**，只需要 8001 |
| **Nginx 的作用?** | 反向代理 + 静态文件 |

---

## ✅ 最终建议

✅ **生产环境部署**: 仅部署 Port 8001  
✅ **使用 Nginx**: 作为反向代理 (Port 80/443)  
✅ **配置 SSL**: 启用 HTTPS  
✅ **隐藏 8001**: 防火墙只允许 80/443  
✅ **使用 Docker**: 便于管理和扩展

---

**现在您清楚了！线上部署就是 Port 8001！** 🚀
