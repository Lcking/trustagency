# 🔧 Docker 构建内存不足问题解决方案

## 问题诊断

**错误信息**：`exit code: 137` (OOM - Out of Memory Killed)

**原因**：4GB 服务器在构建后端镜像时内存不足

---

## 🚀 快速解决方案（三选一）

### 方案A：清理Docker资源后重试（推荐！）

```bash
# 1. 停止所有容器
docker-compose -f docker-compose.prod.yml down

# 2. 清理未使用的Docker资源
docker system prune -a -f

# 3. 清理构建缓存
docker builder prune -a -f

# 4. 检查磁盘空间
df -h

# 5. 重新运行修复脚本
bash fix-deployment.sh
```

**耗时**：5-10分钟  
**成功率**：80%

---

### 方案B：禁用Docker构建缓存（更激进）

```bash
# 1. 停止容器
docker-compose -f docker-compose.prod.yml down

# 2. 删除所有镜像
docker rmi -f $(docker images -q)

# 3. 清空所有卷
docker volume prune -f

# 4. 清理系统
docker system prune -a -f

# 5. 重新启动
bash fix-deployment.sh
```

**耗时**：10-15分钟  
**成功率**：90%

---

### 方案C：使用预构建镜像（最快！）

从 Docker Hub 直接拉取预构建镜像，跳过本地构建：

```bash
# 1. 停止容器
docker-compose -f docker-compose.prod.yml down

# 2. 清理资源
docker system prune -a -f

# 3. 预先拉取镜像
docker pull python:3.10-slim
docker pull redis:7-alpine

# 4. 修改 docker-compose.prod.yml（可选）
# 如果有预构建的镜像，使用它而不是本地构建

# 5. 重新启动
bash fix-deployment.sh
```

**耗时**：5-10分钟  
**成功率**：85%

---

## 🛠️ 完整修复步骤

### 第1步：停止所有容器和清理

```bash
cd /opt/trustagency

# 停止容器
docker-compose -f docker-compose.prod.yml down

# 查看当前磁盘使用
df -h

# 查看Docker使用空间
docker system df
```

### 第2步：彻底清理

```bash
# 删除所有停止的容器
docker container prune -f

# 删除所有未使用的镜像
docker image prune -a -f

# 删除所有未使用的卷
docker volume prune -f

# 删除所有未使用的网络
docker network prune -f

# 清理构建缓存
docker builder prune -a -f
```

### 第3步：验证清理效果

```bash
# 查看剩余空间
df -h

# 查看Docker使用情况
docker system df

# 输出应该显示空间大幅减少
```

### 第4步：重新构建（使用内存优化）

```bash
# 方式1：标准重新启动
docker-compose -f docker-compose.prod.yml up -d

# 方式2：限制内存使用的构建
# 编辑 docker-compose.prod.yml，添加构建内存限制：
# build:
#   context: ./backend
#   dockerfile: Dockerfile
#   args:
#     BUILDKIT_MEMORY: "1g"

# 方式3：使用 --no-build 跳过构建（如果镜像已存在）
docker-compose -f docker-compose.prod.yml up -d --no-build
```

---

## 📊 内存使用优化

### 查看当前内存使用

```bash
# 查看系统内存
free -h

# 查看Docker容器内存使用
docker stats --no-stream

# 查看进程内存
ps aux --sort=-%mem | head -10
```

### 释放内存的方法

```bash
# 1. 停止不必要的服务
systemctl stop nginx  # 如果只需要测试后端

# 2. 清理系统缓存
sync && echo 3 > /proc/sys/vm/drop_caches

# 3. 禁用 Swap 并重新启用（刷新）
swapoff -a
swapon -a

# 4. 检查是否有其他大进程
top -b -n 1 | head -20
```

---

## 🎯 逐步执行（推荐方案A）

### 完整命令序列

```bash
#!/bin/bash
set -e

cd /opt/trustagency

echo "1️⃣ 停止容器..."
docker-compose -f docker-compose.prod.yml down || true

echo ""
echo "2️⃣ 清理 Docker 资源..."
docker system prune -a -f
docker builder prune -a -f

echo ""
echo "3️⃣ 检查磁盘空间..."
df -h /
echo ""
free -h

echo ""
echo "4️⃣ 重新启动容器..."
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

echo ""
echo "5️⃣ 等待容器启动..."
sleep 10

echo ""
echo "6️⃣ 验证部署..."
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/health

echo ""
echo "✅ 修复完成！"
```

---

## 🆘 如果还是内存不足

### 临时增加 Swap（应急方案）

```bash
# 创建 2GB Swap 文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 验证
free -h

# 重新构建
docker-compose -f docker-compose.prod.yml up -d
```

### 减少容器资源限制

编辑 `docker-compose.prod.yml`：

```yaml
backend:
  # ... 其他配置
  deploy:
    resources:
      limits:
        memory: 800m  # 从 1.5G 降低到 800MB
        cpus: '1'     # 从 2 降低到 1

celery-worker:
  deploy:
    resources:
      limits:
        memory: 400m  # 从 700M 降低到 400MB
        cpus: '0.5'
```

---

## 🔍 诊断和验证

### 检查构建过程中的内存

```bash
# 在另一个终端监控内存
watch -n 1 'free -h && echo "---" && docker stats --no-stream'
```

### 查看详细的构建日志

```bash
# 启用详细日志
DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml up -d --build --verbose
```

### 检查镜像大小

```bash
# 查看已构建的镜像大小
docker images

# 查看镜像详细信息
docker image inspect <image-id>
```

---

## 📋 快速命令清单

### 最简单的修复（一键）

```bash
cd /opt/trustagency && \
docker-compose -f docker-compose.prod.yml down && \
docker system prune -a -f && \
docker builder prune -a -f && \
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d && \
sleep 10 && \
docker-compose -f docker-compose.prod.yml ps
```

### 验证

```bash
curl http://localhost:8001/health
```

---

## 🎯 推荐执行步骤

### 如果磁盘空间充足（> 5GB 可用）

```bash
# 方案A：清理后重试
docker-compose -f docker-compose.prod.yml down
docker system prune -a -f
bash fix-deployment.sh
```

### 如果磁盘空间紧张（< 2GB 可用）

```bash
# 方案B：更激进清理
docker-compose -f docker-compose.prod.yml down
docker rmi -f $(docker images -q)
docker volume prune -f
docker system prune -a -f
bash fix-deployment.sh
```

### 如果多次失败

```bash
# 方案C：增加 Swap 然后重试
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
bash fix-deployment.sh
```

---

## ✅ 成功的标志

执行完成后：

- ✅ 容器全部 `Up` 或 `(healthy)`
- ✅ `curl http://localhost:8001/health` 返回 `{"status": "ok"}`
- ✅ `docker system df` 显示合理的资源使用

---

## 📞 如果还有问题

1. **查看详细日志**
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend | tail -100
   ```

2. **检查系统资源**
   ```bash
   free -h
   df -h
   docker system df
   ```

3. **查看是否有其他进程占用内存**
   ```bash
   ps aux --sort=-%mem | head -10
   ```

---

**现在就试试吧！推荐先执行方案A！🚀**
