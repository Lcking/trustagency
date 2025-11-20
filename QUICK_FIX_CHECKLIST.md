# ⚡ 立即行动清单 - 3 分钟快速修复

## 🎯 你的问题总结

```
当前状态：
├─ 后端已部署并运行 ✅
├─ 前端无法访问 ❌
├─ 登录返回 "Failed to fetch" ❌
└─ Nginx 返回 405 Method Not Allowed ❌

根本原因：
├─ 前端和后端路由冲突
├─ Nginx 配置不正确
└─ CORS 配置可能有问题
```

---

## 🚀 快速修复（3 步）

### 步骤 1：在服务器上运行诊断脚本（30秒）

```bash
ssh root@yycr.net

# 下载诊断脚本（如果还没有）
cd /opt/trustagency
git pull origin main

# 运行诊断
bash diagnose-production.sh
```

**预期结果**：查看哪些项目失败，这会指导你下一步

### 步骤 2：运行修复脚本（1分钟）

```bash
# 在服务器上运行
sudo bash fix-production-deployment.sh
```

**这个脚本会：**
- ✅ 检查 Docker 和 Nginx
- ✅ 创建正确的 Nginx 配置
- ✅ 启动后端容器
- ✅ 验证部署

### 步骤 3：验证部署（30秒）

```bash
# 本地测试
curl -I https://yycr.net/admin/

# 应该返回：
# HTTP/2 200
# (不是 405!)

# 如果还是 405，检查 Nginx 配置中是否有这一行：
grep "proxy_method" /etc/nginx/conf.d/trustagency.conf
```

---

## 🔍 如果还是不工作？

### 问题 1：仍然看到 405

**原因**：`proxy_method $request_method;` 未配置

**修复**：
```bash
sudo nano /etc/nginx/conf.d/trustagency.conf

# 找到这一行（应该在 location /api/ 块内）:
# proxy_method $request_method;

# 如果没有，添加它。保存后运行:
sudo nginx -s reload
```

### 问题 2：无法连接到后端

**原因**：Docker 容器没有运行

**修复**：
```bash
cd /opt/trustagency

# 启动容器
docker-compose -f docker-compose.prod.yml up -d

# 检查状态
docker-compose -f docker-compose.prod.yml ps

# 应该看到:
# trustagency-backend-prod    running
# trustagency-celery-worker   running
# trustagency-redis-prod      running
```

### 问题 3：前端白屏

**原因**：前端文件未部署

**修复**：
```bash
# 检查前端文件
ls -la /usr/share/nginx/html/admin/

# 如果目录为空，复制后端的前端文件
sudo cp -r /opt/trustagency/backend/site/admin/* /usr/share/nginx/html/admin/

# 检查权限
sudo chown -R www-data:www-data /usr/share/nginx/html/admin/
```

### 问题 4：登录成功但提示 CORS 错误

**原因**：CORS 配置与实际域名不匹配

**修复**：
```bash
# 编辑后端 .env
nano /opt/trustagency/backend/.env.prod

# 找到这一行:
CORS_ORIGINS=https://yycr.net,https://www.yycr.net

# 确保你的实际域名在这里

# 修改后重启后端
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📋 检查清单

运行以下命令，所有应该返回 `0` 或 `✅`：

```bash
# 1. Nginx 运行中？
systemctl is-active nginx && echo "✅" || echo "❌"

# 2. 后端容器运行中？
docker ps | grep trustagency-backend && echo "✅" || echo "❌"

# 3. 端口 80 开放？
netstat -tuln | grep ":80 " && echo "✅" || echo "❌"

# 4. 端口 8001 开放？
netstat -tuln | grep ":8001 " && echo "✅" || echo "❌"

# 5. 前端文件存在？
test -f /usr/share/nginx/html/admin/index.html && echo "✅" || echo "❌"

# 6. Nginx 配置正确？
nginx -t 2>&1 | grep "successful" && echo "✅" || echo "❌"

# 7. 后端 API 可达？
curl -s http://localhost:8001/api/health | grep -q "name\|version" && echo "✅" || echo "❌"

# 8. 代理转发工作？
curl -s http://localhost/api/health | grep -q "name\|version" && echo "✅" || echo "❌"
```

---

## 🎯 根据你的情况选择

### 情况 A：我只想快速让它工作

```bash
# 在服务器上运行（3 条命令）
cd /opt/trustagency
git pull origin main
sudo bash fix-production-deployment.sh
```

### 情况 B：我想理解发生了什么

```bash
# 先诊断
bash diagnose-production.sh

# 查看详细文档
cat PRODUCTION_DEPLOYMENT_ARCHITECTURE.md

# 然后手动修复
```

### 情况 C：我想完全重新部署

```bash
# 1. 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 2. 清理 Nginx 配置
sudo rm /etc/nginx/conf.d/trustagency.conf

# 3. 运行完整修复
sudo bash fix-production-deployment.sh
```

---

## 📞 还有问题？

检查这些文件获取更详细的帮助：

| 文件 | 适用场景 |
|------|--------|
| `PRODUCTION_DEPLOYMENT_ARCHITECTURE.md` | 理解部署架构 |
| `FRONTEND_DYNAMIC_CONFIG.md` | 如何动态配置前端 |
| `diagnose-production.sh` | 详细诊断 |
| `fix-production-deployment.sh` | 自动修复脚本 |

---

## ✅ 预期结果

修复成功后，你应该能够：

```
✅ 访问 https://yycr.net/admin/ → 显示登录页面
✅ 输入账号密码登录 → 进入仪表板
✅ 查看 API 文档 → https://yycr.net/api/docs
✅ 所有 CRUD 操作都能工作
```

---

## 🎊 成功标志

如果你看到这些，说明部署成功了：

1. **Nginx 日志无错误**
   ```bash
   tail -20 /var/log/nginx/trustagency_error.log
   # 应该看不到 502 或 proxy_pass 错误
   ```

2. **后端容器健康**
   ```bash
   docker ps | grep trustagency-backend
   # 应该显示 "healthy" 或 "up"
   ```

3. **能从前端成功登录**
   ```
   浏览器开发者工具 → Network 标签
   POST /api/auth/login → 应该返回 200
   ```

4. **没有 CORS 错误**
   ```
   浏览器控制台应该看不到：
   "Access to XMLHttpRequest has been blocked by CORS policy"
   ```

---

**现在就开始吧！** 🚀

选择上面的一个步骤并执行。如果卡住了，查看相应的文档文件。

