# 🎯 Port 部署对应关系 - 快速查询表

**最后更新**: 2025-11-17

---

## 📌 核心答案

```
您的问题：线上部署用哪个端口？

✅ 答案：Port 8001

解释：
- Port 8000 = 本地开发用
- Port 8001 = 生产环境用 ✅
```

---

## 📊 三个部署场景对比

### 场景 1️⃣ 本地开发 (localhost)

```
您: bash run.sh

系统启动:
├─ Port 8000 ← FastAPI 后端 API
└─ Port 8001 ← HTML 前端文件

访问:
├─ http://localhost:8001/ ← 看页面
└─ http://localhost:8000/api/ ← 看 API
```

### 场景 2️⃣ 生产环境 (Docker - 推荐)

```
您: docker-compose -f docker-compose.prod.yml up -d

系统启动:
├─ Port 80   ← Nginx (对用户)
├─ Port 443  ← Nginx HTTPS (对用户)
└─ Port 8001 ← FastAPI (内部)
   ├─ Port 5432 (PostgreSQL - 内部)
   └─ Port 6379 (Redis - 内部)

访问:
├─ http://yourdomain.com ← 用户看到的 (80)
├─ https://yourdomain.com ← 安全访问 (443)
└─ Port 8001 不对外暴露 ✅
```

### 场景 3️⃣ 混合部署 (开发+生产)

```
后端: docker run ... -p 8001:8001
前端: npm start ... -p 3000

Port 8000 = 不用
Port 8001 = 后端容器
Port 3000 = 前端应用
```

---

## 🗂️ 文件配置对应表

| 文件 | 配置项 | 值 | 环境 | 说明 |
|------|--------|-----|------|------|
| .env.prod | API_PORT | **8001** | 生产 | ✅ 线上用这个 |
| docker-compose.prod.yml | ports | 8001:8001 | 生产 | ✅ 容器映射 |
| nginx/default.conf | listen | 80 | 生产 | ✅ 用户访问 |
| run.sh | backend port | 8000 | 开发 | ← 本地测试 |
| run.sh | frontend port | 8001 | 开发 | ← 本地看页面 |

---

## 🌐 网络拓扑图

### 开发环境

```
浏览器
  ├─→ http://localhost:8001/ (前端)
  └─→ http://localhost:8000/api/ (后端)
  
对应文件:
  ├─ /site (HTML/CSS/JS)
  └─ /backend (FastAPI)
```

### 生产环境

```
浏览器 (互联网)
  ↓
Port 80/443 (Nginx)
  ↓
Port 8001 (FastAPI)
  ↓
PostgreSQL + Redis (内部)
  
对应容器:
  ├─ nginx (reverse proxy)
  ├─ backend:8001 (FastAPI + 前端文件)
  ├─ db:5432 (PostgreSQL)
  └─ redis:6379 (Redis)
```

---

## ✅ 决策树

```
问题：我要部署系统
  │
  ├─→ 本地开发?
  │   └─→ 使用 Port 8000 (后端) + 8001 (前端)
  │       命令: bash run.sh
  │       访问: http://localhost:8001/
  │
  └─→ 生产环境?
      └─→ 使用 Port 8001 (FastAPI)
          命令: docker-compose -f docker-compose.prod.yml up -d
          访问: https://yourdomain.com
          备注: Nginx 处理 80/443, 内部转到 8001
```

---

## 📋 配置速查

### 我要看生产配置

**文件**: `.env.prod`
```
API_PORT=8001 ✅
```

### 我要看本地开发配置

**文件**: `run.sh`
```
backend port: 8000
frontend port: 8001
```

### 我要看 Docker 生产配置

**文件**: `docker-compose.prod.yml`
```yaml
ports:
  - "8001:8001"  ✅
```

### 我要看 Nginx 配置

**文件**: `nginx/default.conf`
```nginx
listen 80 default_server;  ✅
```

---

## 🚀 快速部署指令

### 本地启动

```bash
cd /Users/ck/Desktop/Project/trustagency
bash run.sh
# 然后访问: http://localhost:8001/
```

### 生产启动

```bash
cd /Users/ck/Desktop/Project/trustagency
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
# 然后访问: https://yourdomain.com
```

---

## ❓ 常见问题

### Q1: 8000 和 8001 的区别?
```
8000 = 后端 API 服务 (开发用)
8001 = FastAPI 主应用 (生产用)
```

### Q2: 线上为什么用 8001 不用 8000?
```
因为生产环境配置文件 (.env.prod) 明确指定:
API_PORT=8001
```

### Q3: 用户可以直接访问 8001 吗?
```
不应该。生产环境应该:
1. 用户 → Port 80/443 (Nginx)
2. Nginx → Port 8001 (内部)
3. 防火墙只开放 80/443
```

### Q4: 为什么要用 Nginx?
```
优点:
- 反向代理安全
- 隐藏内部端口
- 处理 SSL/TLS
- 提供静态文件
- 负载均衡
```

---

## 📊 端口使用总结表

| 端口 | 用途 | 环境 | 开放 | 说明 |
|------|------|------|------|------|
| 80 | HTTP 访问 | 生产 | ✅ 对外 | Nginx 监听 |
| 443 | HTTPS 访问 | 生产 | ✅ 对外 | Nginx + SSL |
| 8000 | 后端 API | 本地 | ❌ 仅本地 | 开发测试 |
| 8001 | FastAPI | 生产 | ❌ 仅内部 | Nginx 后端 |
| 5432 | PostgreSQL | 生产 | ❌ 仅内部 | 数据库 |
| 6379 | Redis | 生产 | ❌ 仅内部 | 缓存队列 |

---

## 🎯 最终答案

**您问**: "我线上部署的是哪个呢？"

**我答**: 
```
✅ Port 8001 (FastAPI 应用)
   └─ 由 Nginx (80/443) 反向代理

❌ Port 8000 (仅用于本地开发)
   └─ 生产环境不需要
```

**记住**: 
- 用户看到: Port 80/443
- 系统用: Port 8001
- 只配置 8001，不配置 8000

---

**参考文档**: 查看 `PRODUCTION_DEPLOYMENT_PORT_GUIDE.md` 了解详情

