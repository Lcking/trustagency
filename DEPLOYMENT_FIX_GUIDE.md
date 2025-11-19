# 🔧 部署问题修复指南

## 问题分析

你遇到的两个问题：

### ❌ 问题1：SECRET_KEY未设置
```
WARN[0000] The "SECRET_KEY" variable is not set. Defaulting to a blank string.
```

**原因**：`.env.prod` 文件不存在或未正确加载

**解决方案**：生成并设置 `SECRET_KEY`

### ❌ 问题2：Docker网络连接超时
```
Error response from daemon: Get "https://registry-1.docker.io/v2/": 
net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

**原因**：Docker Hub 服务器网络延迟或被限流

**解决方案**：配置国内镜像源

---

## 快速修复步骤 (在服务器上执行)

### 第1步：停止当前容器

```bash
# 进入项目目录
cd /opt/trustagency

# 停止所有容器
docker-compose -f docker-compose.prod.yml down
```

### 第2步：配置Docker国内镜像

```bash
# 创建或编辑 /etc/docker/daemon.json
sudo nano /etc/docker/daemon.json
```

**粘贴以下内容**（选择一个最快的镜像源）：

```json
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
```

**保存**: `Ctrl+O` → `Enter` → `Ctrl+X`

**重启Docker**：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 第3步：生成并设置 SECRET_KEY

```bash
# 生成强随机密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "生成的 SECRET_KEY: $SECRET_KEY"

# 复制这个值（下一步要用）
```

### 第4步：配置 .env.prod 文件

```bash
# 复制示例文件
cp /opt/trustagency/.env.prod.example /opt/trustagency/.env.prod

# 编辑配置文件
sudo nano /opt/trustagency/.env.prod
```

**修改以下内容**（使用上面生成的 SECRET_KEY）：

```ini
# TrustAgency 生产环境配置 (SQLite版本)

# 应用配置
ENVIRONMENT=production
DEBUG=False

# 数据库配置（SQLite）
DATABASE_URL=sqlite:////app/data/trustagency.db

# 安全配置 - 替换为你上面生成的 SECRET_KEY
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

# API配置
API_HOST=0.0.0.0
API_PORT=8001

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**保存**: `Ctrl+O` → `Enter` → `Ctrl+X`

### 第5步：验证配置文件

```bash
# 检查文件是否存在且内容正确
cat /opt/trustagency/.env.prod | grep SECRET_KEY

# 应该显示类似: SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
```

### 第6步：重新启动容器

```bash
# 进入项目目录
cd /opt/trustagency

# 使用env-file参数显式加载环境变量
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 或者直接启动（Docker会自动加载.env.prod）
docker-compose -f docker-compose.prod.yml up -d
```

### 第7步：验证启动状态

```bash
# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 应该看到所有容器状态为 "Up" 或 "(healthy)"
```

---

## 如果问题依然存在

### 方案A：使用本地镜像预加载

```bash
# 预先拉取镜像（使用国内镜像源）
docker pull redis:7-alpine
docker pull python:3.11-slim

# 然后启动
docker-compose -f docker-compose.prod.yml up -d
```

### 方案B：增加Docker超时时间

```bash
# 编辑 docker-compose.prod.yml
nano docker-compose.prod.yml

# 在 services 段下面添加：
services:
  backend:
    # ... 其他配置
    restart_policy:
      condition: on-failure
      delay: 10s
      max_attempts: 5
      window: 120s
```

### 方案C：手动构建镜像（跳过拉取）

```bash
# 使用本地已存在的镜像名称，如果不存在则构建
docker-compose -f docker-compose.prod.yml build --no-cache

# 然后启动
docker-compose -f docker-compose.prod.yml up -d
```

---

## 完整命令一键执行（仅供参考）

如果你想一次性执行所有步骤，可以运行：

```bash
#!/bin/bash
set -e

cd /opt/trustagency

echo "📝 1. 生成 SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "✅ SECRET_KEY: $SECRET_KEY"

echo "📝 2. 配置 .env.prod 文件..."
if [ ! -f .env.prod ]; then
    cp .env.prod.example .env.prod
fi

# 替换 SECRET_KEY（适用于 Linux/Mac）
sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.prod

echo "✅ .env.prod 已配置"

echo "📝 3. 配置 Docker 国内镜像..."
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
echo "✅ Docker 镜像源已配置"

echo "📝 4. 停止现有容器..."
docker-compose -f docker-compose.prod.yml down

echo "📝 5. 启动新容器..."
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

echo "📝 6. 等待容器就绪..."
sleep 10

echo "📝 7. 检查容器状态..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ 部署完成！"
echo ""
echo "📊 检查日志："
echo "docker-compose -f docker-compose.prod.yml logs -f"
```

---

## 验证部署成功

```bash
# 1. 检查所有容器运行状态
docker-compose -f docker-compose.prod.yml ps

# 预期输出：
# NAME                            STATUS              PORTS
# trustagency-backend-prod        Up (healthy)        0.0.0.0:8001->8001/tcp
# trustagency-celery-worker-prod  Up
# trustagency-celery-beat-prod    Up
# trustagency-redis-prod          Up (healthy)

# 2. 测试后端健康检查
curl http://localhost:8001/health

# 预期输出：{"status": "ok"}

# 3. 查看详细日志
docker-compose -f docker-compose.prod.yml logs backend | head -50
```

---

## 常见错误解决

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| `SECRET_KEY variable is not set` | .env.prod 未加载 | 使用 `--env-file .env.prod` 或检查文件存在 |
| `request canceled while waiting for connection` | Docker网络超时 | 配置国内镜像源 |
| `Permission denied` | 权限不足 | 使用 `sudo` 或加入 docker 组 |
| `Port 8001 already in use` | 端口被占用 | `docker ps` 查看占用进程，然后 `docker kill <id>` |
| `database is locked` | SQLite 并发锁 | 检查是否有多个后端实例，重启容器 |

---

## 下一步

✅ 部署完成后：

1. **修改默认密码**
   ```bash
   # 访问后台管理系统
   # URL: http://your-domain.com/admin/
   # 用户名: admin
   # 默认密码: admin123
   # 立即修改该密码！
   ```

2. **配置域名和HTTPS** - 参考主文档第四、五步

3. **设置备份** - 参考主文档第七步

4. **监控日志**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

---

## 📞 需要进一步帮助？

- 查看完整部署指南：`DEPLOYMENT_SQLITE.md`
- 检查Docker日志：`docker-compose logs <service-name>`
- 验证网络：`ping 8.8.8.8` 或配置代理

祝部署顺利！🚀
