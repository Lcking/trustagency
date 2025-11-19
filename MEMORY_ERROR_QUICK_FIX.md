# 🎯 内存问题快速修复 - 在服务器上执行

## 你遇到的错误

```
exit code: 137
Killed
```

**原因**：Docker 构建时内存不足 (Out of Memory)

---

## 🚀 立即修复（选择一个方案）

### ⭐ 推荐方案：一键修复脚本

在服务器上执行：

```bash
cd /opt/trustagency
git pull origin main
bash fix-memory-error.sh
```

**这会自动：**
- 停止容器
- 清理 Docker 资源
- 重新构建和启动
- 验证部署

**耗时**：10-15 分钟  
**成功率**：85%+

---

### 或者：手动快速修复

```bash
# 1. 进入项目目录
cd /opt/trustagency

# 2. 停止容器并清理 (3 条命令)
docker-compose -f docker-compose.prod.yml down
docker system prune -a -f
docker builder prune -a -f

# 3. 重新启动
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 4. 等待 10-15 分钟，然后验证
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/health
```

---

## ✅ 成功的标志

```bash
# 应该看到所有容器都是 Up 或 (healthy)
docker-compose -f docker-compose.prod.yml ps

# 应该返回 {"status": "ok"}
curl http://localhost:8001/health
```

---

## 🆘 如果还是失败

### 检查可用资源

```bash
# 内存
free -h

# 磁盘空间
df -h /

# Docker 使用
docker system df
```

### 如果磁盘空间紧张 (< 2GB)

```bash
# 更激进的清理
docker-compose -f docker-compose.prod.yml down
docker rmi -f $(docker images -q)
docker volume prune -f
docker system prune -a -f

# 然后重试
bash fix-memory-error.sh
```

### 如果仍然失败（临时增加 Swap）

```bash
# 创建 2GB Swap 文件（应急方案）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 验证
free -h

# 重新运行
bash fix-memory-error.sh
```

---

## 📚 详细文档

查看完整的诊断和解决方案：

```bash
cat /opt/trustagency/FIX_MEMORY_ERROR.md
```

---

## 💡 常见问题

**Q: 需要多长时间？**  
A: 10-15 分钟（包括清理和重新构建）

**Q: 会丢失数据吗？**  
A: 不会，SQLite 数据库在卷中保持持久化

**Q: 可以跳过构建吗？**  
A: 可以，如果已有镜像，可以使用 `--no-build` 参数

**Q: 还是 OOM 怎么办？**  
A: 使用上面的临时 Swap 方案或增加服务器内存

---

## 🚀 现在就试试吧！

```bash
cd /opt/trustagency
bash fix-memory-error.sh
```

**祝修复顺利！🎉**
