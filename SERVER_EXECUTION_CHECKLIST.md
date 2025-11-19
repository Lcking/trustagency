# ✅ 服务器修复执行检查清单

## 📋 在服务器上执行以下步骤

### 步骤 1️⃣ : 拉取最新代码

```bash
cd /opt/trustagency
git pull origin main
```

**预期结果：**
```
Already up to date.
或
Updating xxx..xxx
```

---

### 步骤 2️⃣ : 执行一键修复脚本

```bash
bash fix-memory-error.sh
```

**脚本会输出：**
```
════════════════════════════════════════════════════════
🔧 Docker 内存不足修复
════════════════════════════════════════════════════════
...
```

**耗时：** 10-15 分钟

---

### 步骤 3️⃣ : 等待完成并检查结果

脚本完成后，运行：

```bash
docker-compose -f docker-compose.prod.yml ps
```

**成功标志（全部应该是 Up 或 healthy）：**
```
NAME                 COMMAND              STATUS
backend              docker-python...     Up (healthy)
celery-worker        docker-python...     Up
celery-beat          docker-python...     Up
redis                docker-redis...      Up (healthy)
```

---

### 步骤 4️⃣ : 验证 API 工作

```bash
curl http://localhost:8001/health
```

**成功响应：**
```json
{"status": "ok"}
```

---

## 🆘 如果脚本失败

### 诊断信息收集

运行这些命令获取诊断信息：

```bash
# 1. 查看系统资源
free -h
df -h /

# 2. 查看 Docker 状态
docker system df
docker-compose -f docker-compose.prod.yml logs --tail=50

# 3. 查看具体错误
docker-compose -f docker-compose.prod.yml logs backend | tail -100
```

### 快速重试 - 方案 A（推荐）

```bash
cd /opt/trustagency

# 清理
docker-compose -f docker-compose.prod.yml down
docker system prune -a -f
docker builder prune -a -f

# 重启
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 等待 10-15 分钟
sleep 600

# 验证
docker-compose -f docker-compose.prod.yml ps
```

### 激进清理 - 方案 B

```bash
cd /opt/trustagency

# 停止一切
docker-compose -f docker-compose.prod.yml down
docker stop $(docker ps -q) 2>/dev/null || true
docker rm $(docker ps -a -q) 2>/dev/null || true

# 删除所有镜像
docker rmi -f $(docker images -q) 2>/dev/null || true

# 系统清理
docker volume prune -f
docker system prune -a -f

# 重新启动
bash fix-memory-error.sh
```

### 应急 - 增加 Swap - 方案 C

```bash
# 创建 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 验证
free -h

# 重新运行修复
bash fix-memory-error.sh
```

---

## ✨ 成功修复后

### 1. 验证所有服务

```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查日志是否有错误
docker-compose -f docker-compose.prod.yml logs --tail=20
```

### 2. 测试 API

```bash
# 健康检查
curl http://localhost:8001/health

# 测试登录端点
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### 3. 访问后台管理系统

```
http://your-domain.com/admin/
用户名: admin
密码: admin123
```

⚠️ **立即修改默认密码！**

---

## 📊 修复进度追踪

| 步骤 | 任务 | 状态 | 备注 |
|-----|------|------|------|
| 1 | 拉取最新代码 | ⏳ | `git pull origin main` |
| 2 | 执行修复脚本 | ⏳ | `bash fix-memory-error.sh` |
| 3 | 验证容器状态 | ⏳ | `docker-compose ps` |
| 4 | 测试 API | ⏳ | `curl /health` |
| 5 | 访问后台 | ⏳ | 修改默认密码 |

---

## 🔍 实时监控修复过程

在另一个终端监控：

```bash
# 实时查看内存和容器
watch -n 2 'free -h && echo "---" && docker-compose -f docker-compose.prod.yml ps'

# 或查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 💾 保存诊断日志

如果需要诊断，保存详细日志：

```bash
# 保存所有信息到日志文件
bash fix-memory-error.sh 2>&1 | tee repair_$(date +%Y%m%d_%H%M%S).log

# 查看保存的日志
ls -lh repair_*.log
```

---

## 🎯 预计时间表

- **第 1-2 分钟**：清理 Docker 资源
- **第 2-3 分钟**：删除旧镜像和卷
- **第 3-5 分钟**：等待 Docker Hub 连接
- **第 5-15 分钟**：构建后端镜像（关键阶段）
- **第 15-17 分钟**：启动所有容器
- **第 17-20 分钟**：初始化数据库和缓存

**总计：15-20 分钟**

---

## 🆘 常见问题

### Q: 脚本超过 20 分钟还没完成？
A: 这是正常的。镜像构建在慢速网络上可能需要 15-20 分钟。不要中断脚本。

### Q: 看到 "pull access denied" 错误？
A: Docker 镜像源可能有问题。检查：
```bash
cat /etc/docker/daemon.json | grep -i registry
```

### Q: 看到 "Killed" 或 "exit 137" 错误？
A: 这就是内存不足错误。运行方案 C（增加 Swap）后重试。

### Q: 修复后容器仍然 Exited？
A: 查看日志：
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

---

## 📞 需要更多帮助？

查看详细文档：

```bash
# 打开快速参考
cat MEMORY_ERROR_QUICK_FIX.md

# 打开详细指南
cat FIX_MEMORY_ERROR.md

# 打开这个完整指南
cat MEMORY_ISSUE_COMPLETE.md
```

---

**准备好了？现在就在服务器上执行吧！**

```bash
cd /opt/trustagency
bash fix-memory-error.sh
```

**祝修复顺利！✨**
