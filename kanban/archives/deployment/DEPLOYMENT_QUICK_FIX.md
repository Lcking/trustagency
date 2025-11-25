# 🚀 部署问题快速解决卡片

## 你遇到的错误

```
WARN[0000] The "SECRET_KEY" variable is not set. Defaulting to a blank string.
Error response from daemon: Get "https://registry-1.docker.io/v2/": 
net/http: request canceled while waiting for connection
```

---

## 立即执行（3步修复）

### 在服务器上执行以下命令：

```bash
cd /opt/trustagency

# 1️⃣ 停止现有容器
docker-compose -f docker-compose.prod.yml down

# 2️⃣ 配置 Docker 国内镜像（必须！加速10倍）
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerhub.jobcher.com",
    "https://docker.awchina.com"
  ]
}
EOF

sudo systemctl daemon-reload && sudo systemctl restart docker

# 3️⃣ 生成 SECRET_KEY 并配置 .env.prod
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
cp .env.prod.example .env.prod
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env.prod

# 4️⃣ 重新启动容器
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 5️⃣ 验证状态（等待 10-30 秒）
docker-compose -f docker-compose.prod.yml ps
```

---

## 或者：一键执行脚本

```bash
# 上传脚本到服务器
scp fix-deployment.sh root@your-server:/opt/trustagency/

# 连接服务器后执行
ssh root@your-server
cd /opt/trustagency
bash fix-deployment.sh
```

---

## 验证成功

```bash
# 查看所有容器状态（应该都是 Up 或 healthy）
docker-compose -f docker-compose.prod.yml ps

# 测试后端接口
curl http://localhost:8001/health

# 查看实时日志（看有没有错误）
docker-compose -f docker-compose.prod.yml logs -f
```

**预期输出**：
- ✅ 所有容器状态为 `Up` 或 `(healthy)`
- ✅ `curl` 返回：`{"status": "ok"}`
- ✅ 日志中显示：`✅ 数据库初始化成功` 等信息

---

## 问题诊断

### 问题：仍然超时

```bash
# 检查网络
ping 8.8.8.8

# 查看镜像配置是否生效
docker info | grep -A 5 "Registry Mirrors"

# 预加载镜像（跳过拉取）
docker pull redis:7-alpine
docker pull python:3.11-slim
```

### 问题：PORT 8001 已占用

```bash
# 查看占用进程
lsof -i :8001

# 杀死进程
kill -9 <PID>

# 或修改 docker-compose.prod.yml 中的端口
# ports: ["8002:8001"]
```

### 问题：SECRET_KEY 不生效

```bash
# 检查 .env.prod 是否正确
cat .env.prod | grep SECRET_KEY

# 确保使用了 --env-file 参数
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 检查容器环境变量
docker-compose -f docker-compose.prod.yml exec backend env | grep SECRET_KEY
```

---

## 文档位置

- 完整部署指南：`DEPLOYMENT_SQLITE.md`
- 详细修复指南：`DEPLOYMENT_FIX_GUIDE.md`
- 修复脚本：`fix-deployment.sh`

---

## 下一步

部署成功后：

1. **访问后台**
   ```
   URL: http://your-domain.com/admin/
   用户: admin
   密码: admin123
   ```

2. **立即修改默认密码** ⚠️

3. **配置域名和 HTTPS**
   - 参考 `DEPLOYMENT_SQLITE.md` 第四步

4. **设置备份**
   - 参考 `DEPLOYMENT_SQLITE.md` 第七步

---

**需要帮助？查看日志：**
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```
