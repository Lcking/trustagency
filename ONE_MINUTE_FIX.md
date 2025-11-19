# 🚀 一分钟快速修复指南

## 📍 你的问题

```
❌ Docker 构建失败
❌ 错误: exit code 137 (OOM - 内存不足)
❌ 服务器: 2C4G CentOS 7.5
```

---

## ✅ 解决方案（一个命令）

在你的服务器上执行：

```bash
cd /opt/trustagency && bash fix-memory-error.sh
```

**完成耗时：10-15 分钟**

---

## 📊 该脚本会做什么

1. ✓ 停止现有容器
2. ✓ 清理 Docker 资源
3. ✓ 重新构建镜像
4. ✓ 启动所有服务
5. ✓ 验证部署成功

---

## ✨ 成功标志

脚本完成后：

```bash
# 运行这个检查
docker-compose -f docker-compose.prod.yml ps
```

**你应该看到：**
- backend: **Up (healthy)** ✓
- redis: **Up (healthy)** ✓
- celery-worker: **Up** ✓
- celery-beat: **Up** ✓

---

## 🎯 后续访问

```
URL: http://your-domain.com/admin/
用户: admin
密码: admin123

⚠️ 立即修改密码!
```

---

## 🆘 如果还是失败？

### 方案 A: 快速重试

```bash
cd /opt/trustagency
docker-compose -f docker-compose.prod.yml down
docker system prune -a -f
bash fix-memory-error.sh
```

### 方案 B: 增加 Swap（最有效）

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h  # 验证
bash fix-memory-error.sh
```

---

## 📚 完整文档

- `FINAL_DEPLOYMENT_SUMMARY.md` - 完整总结
- `MEMORY_ERROR_QUICK_FIX.md` - 详细诊断
- `FIX_MEMORY_ERROR.md` - 技术细节
- `SERVER_EXECUTION_CHECKLIST.md` - 执行清单

---

**现在就执行吧！**

```bash
cd /opt/trustagency && bash fix-memory-error.sh
```
