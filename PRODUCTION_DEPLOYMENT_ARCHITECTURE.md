# 🏗️ 生产环境部署架构 - 完整解决方案

## 📋 当前问题诊断

### 问题1：405 Method Not Allowed
```
curl -I https://yycr.net
HTTP/1.1 405 Method Not Allowed
Server: nginx/1.20.1
allow: GET
```

**根本原因**：Nginx 收到 HEAD 请求时，后端不允许该方法。

### 问题2：前端无法访问
```
前端访问 https://yycr.net/admin/ 返回后端 JSON
{"name":"TrustAgency API","version":"1.0.0","docs":"/api/docs"}
```

**根本原因**：前端没有部署到 Nginx；后端的 `/admin/` 路由正在被提供

### 问题3：登录失败 "Failed to fetch"
```javascript
网络错误: Failed to fetch
```

**根本原因**：CORS 问题或路由配置问题

---

## 🎯 解决方案架构

### 推荐架构：Nginx + FastAPI (SPA + API 分离)

```
┌─────────────────────────────────────────────────────────┐
│                    用户访问 (HTTPS)                      │
│                    https://yycr.net                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   /admin/*              /api/*
   (前端SPA)            (后端API)
   (静态文件)
        │                         │
        ▼                         ▼
┌─────────────────┐      ┌──────────────────┐
│  Nginx          │      │  FastAPI Backend │
│  静态文件服务   │      │  端口: 8001      │
│  端口: 443      │      │  Socket或TCP     │
└─────────────────┘      └──────────────────┘
```

### 配置步骤

#### Step 1: 准备前端构建产物

前端应该构建为静态文件，放在 Nginx 能访问的目录：
- `/usr/share/nginx/html/admin/` - 前端应用文件

#### Step 2: Nginx 反向代理配置

```nginx
server {
    listen 443 ssl http2;
    server_name yycr.net;
    
    # SSL证书
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # ===== 前端路由 =====
    location /admin {
        # SPA 前端路由：访问不存在的文件时返回 index.html
        try_files $uri $uri/ /admin/index.html;
    }
    
    # ===== 后端 API 代理 =====
    location /api {
        proxy_pass http://backend:8001;
        proxy_http_version 1.1;
        
        # 关键：允许所有 HTTP 方法
        proxy_method  $request_method;
        
        # 代理头部
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # ===== 健康检查端点 =====
    location /api/health {
        access_log off;
        proxy_pass http://backend:8001;
        proxy_set_header Host $host;
    }
    
    # ===== HTTP 重定向到 HTTPS =====
}

server {
    listen 80;
    server_name yycr.net;
    return 301 https://$server_name$request_uri;
}
```

#### Step 3: 后端 CORS 配置 (.env.prod)

```env
CORS_ORIGINS=https://yycr.net,https://www.yycr.net
```

#### Step 4: 后端 main.py 修改

```python
# 关键修改：不再在后端挂载前端静态文件
# 移除这些行：
# app.mount("/admin", StaticFiles(...))

# 只保留 API 路由
app.include_router(auth.router, prefix="/api")
app.include_router(platforms.router, prefix="/api")
# ... 其他路由
```

---

## 🚀 分步部署指南

### 1. 在服务器上拉取代码

```bash
cd /opt/trustagency
git pull origin main
```

### 2. 构建前端（在本地或 CI/CD 中）

```bash
# 在本地开发机器上
npm run build

# 产生的静态文件放在 dist/ 目录
# 需要复制到服务器的 /usr/share/nginx/html/admin/
```

### 3. 配置服务器上的 Nginx

```bash
# 连接到服务器
ssh root@yycr.net

# 创建 Nginx 配置
sudo tee /etc/nginx/conf.d/trustagency.conf > /dev/null <<'EOF'
# [上面的 Nginx 配置内容]
EOF

# 验证 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4. 启动后端容器

```bash
cd /opt/trustagency
docker-compose -f docker-compose.prod.yml up -d
```

### 5. 验证部署

```bash
# 检查 Nginx 状态
curl -I https://yycr.net/admin/

# 检查后端 API
curl -I https://yycr.net/api/health

# 检查登录端点
curl -X POST https://yycr.net/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 🔧 生产环境三种部署方案

### 方案 A：后端内置前端（当前配置）

**优点**：
- 部署简单
- 只需启动一个服务
- 适合小规模应用

**缺点**：
- 前后端耦合
- 不利于独立扩展
- 前端变更需要重启后端

**适用场景**：MVP、小型应用

### 方案 B：Nginx + FastAPI（推荐）

**优点**：
- 前后端完全分离
- 灵活独立部署
- 前端更新无需重启后端
- 支持多个后端实例负载均衡
- 前端可使用 CDN

**缺点**：
- 需要维护 Nginx 配置
- 多个服务进程

**适用场景**：中等规模、需要高可用性

### 方案 C：Docker 容器编排 + Kubernetes

**优点**：
- 自动化部署和扩展
- 自我修复
- 灰度发布

**缺点**：
- 复杂度高
- 学习曲线陡

**适用场景**：大规模应用、多租户

---

## 📝 前端构建和部署配置

### 前端项目根目录 package.json

```json
{
  "scripts": {
    "build": "vite build --base=/admin/",
    "build:prod": "vite build --mode production --base=/admin/"
  }
}
```

### vite.config.js

```javascript
export default {
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // 生成的文件放在 /admin 路径下
  },
  base: '/admin/',
}
```

### 部署脚本：deploy-frontend.sh

```bash
#!/bin/bash
set -e

echo "📦 构建前端..."
npm run build:prod

echo "📤 上传到服务器..."
scp -r dist/* root@yycr.net:/usr/share/nginx/html/admin/

echo "🔄 重载 Nginx..."
ssh root@yycr.net "sudo nginx -s reload"

echo "✅ 前端部署完成！"
```

---

## 🔐 安全性检查清单

- [ ] SSL/TLS 证书已配置
- [ ] Nginx 已启用 HSTS
- [ ] CORS 已正确配置
- [ ] 后端关闭了不必要的调试端点（/api/docs 在生产)
- [ ] 密钥管理已就位
- [ ] 日志记录已配置
- [ ] WAF 规则已配置（可选）
- [ ] 备份策略已实施

---

## 💾 数据持久化

### SQLite 数据库

```yaml
volumes:
  - ./backend/data:/app/data:rw  # 持久化数据库文件
  - ./backend/logs:/app/logs:rw  # 持久化日志
```

### Redis 缓存

```yaml
volumes:
  - redis_data:/data:rw  # 持久化 Redis 数据
```

---

## 🎯 立即行动清单

### 如果你有前端代码：
1. [ ] 在本地构建前端：`npm run build`
2. [ ] 将 dist/ 上传到 `/usr/share/nginx/html/admin/`
3. [ ] 使用上面的 Nginx 配置
4. [ ] 重启 Nginx

### 如果你没有前端代码：
1. [ ] 后端目前提供前端（/backend/site/admin/index.html）
2. [ ] 修改 main.py 不挂载前端
3. [ ] 让 Nginx 直接服务静态文件
4. [ ] 从后端的 site/admin 复制文件到 Nginx

---

## 🆘 故障排查

### 问题：405 Method Not Allowed
```bash
# 解决：确保 Nginx 配置允许所有 HTTP 方法
proxy_method $request_method;
# 或者明确列出：
proxy_method GET POST PUT DELETE PATCH OPTIONS HEAD;
```

### 问题：CORS 错误
```bash
# 解决：检查后端 CORS 配置
curl -v https://yycr.net/api/health -H "Origin: https://yycr.net"
# 应该看到 Access-Control-Allow-Origin 响应头
```

### 问题：前端白屏
```bash
# 检查前端文件是否存在
ls -la /usr/share/nginx/html/admin/

# 检查 Nginx 日志
tail -100f /var/log/nginx/error.log
```

### 问题：登录无法重定向
```javascript
// 前端需要配置 API 基础 URL
const API_URL = 'https://yycr.net/api';  // 不要用 localhost!
```

---

## 📞 下一步行动

现在选择你的场景：

**场景1：你有完整的前端代码**
→ 按照"前端构建和部署配置"进行构建和部署

**场景2：你只有后端和前端 index.html**
→ 使用后端内置的前端，配置 Nginx 代理到后端

**场景3：你想快速测试**
→ 使用方案 A（后端内置前端），修复 405 错误

让我知道你的情况，我会给你具体的命令！

