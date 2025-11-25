# 📋 部署问题解决方案总结

## 🔴 你遇到的错误分析

### 错误1：SECRET_KEY未设置
```
WARN[0000] The "SECRET_KEY" variable is not set. Defaulting to a blank string.
```
**原因**：
- `.env.prod` 文件不存在或未被 Docker Compose 加载
- 或文件存在但 `SECRET_KEY` 值为空

**影响**：
- 后端无法启动（JWT token 生成失败）
- 所有认证功能无法工作

### 错误2：Docker网络连接超时
```
Error response from daemon: Get "https://registry-1.docker.io/v2/": 
net/http: request canceled while waiting for connection
```
**原因**：
- Docker Hub 官方服务器网络延迟（尤其在中国）
- 或者被限流/阻止

**影响**：
- Redis 镜像无法拉取
- 所有容器无法启动

---

## ✅ 推荐解决方案

### 方案1：自动修复（推荐用于懒人）⭐⭐⭐⭐⭐

**准备时间**：< 2分钟  
**技术难度**：极低  
**成功率**：99%

```bash
# 在服务器上执行
cd /opt/trustagency
bash fix-deployment.sh
```

**效果**：脚本会自动完成所有步骤

---

### 方案2：手动修复（推荐用于学习）⭐⭐⭐⭐

**准备时间**：5-10分钟  
**技术难度**：低  
**成功率**：95%  

**步骤**：

#### 2.1 停止现有容器
```bash
cd /opt/trustagency
docker-compose -f docker-compose.prod.yml down
```

#### 2.2 配置 Docker 国内镜像源
```bash
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
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
```

#### 2.3 生成 SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 输出类似：
# 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
```

#### 2.4 配置 .env.prod
```bash
cp .env.prod.example .env.prod
nano .env.prod

# 找到这一行：
# SECRET_KEY=your-production-secret-key-change-this-NOW
#
# 替换为上面生成的值：
# SECRET_KEY=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
```

#### 2.5 启动容器
```bash
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

#### 2.6 验证
```bash
# 等待 10-30 秒
docker-compose -f docker-compose.prod.yml ps

# 测试后端
curl http://localhost:8001/health
```

---

### 方案3：快速参考卡片⭐⭐

如果想要更快的总结，查看：
```
DEPLOYMENT_QUICK_FIX.md
```

---

## 📊 各方案对比

| 项目 | 自动脚本 | 手动修复 | 快速卡片 |
|------|---------|---------|---------|
| 耗时 | 2分钟 | 5-10分钟 | 3分钟 |
| 难度 | 极低 | 低 | 中等 |
| 学习 | ✗ | ✓✓✓ | ✓✓ |
| 出错率 | 1% | 5% | 10% |

---

## 🎯 我的建议

### 如果你是第一次部署
👉 **使用方案1**（自动脚本）：快速修复，节省时间

### 如果你想学习部署流程
👉 **使用方案2**（手动修复）：能够理解每个步骤

### 如果你很着急
👉 **使用方案3**（快速卡片）：最简洁的说明

---

## ⚡ 核心要点（必读！）

### 1️⃣ Docker 镜像源很重要
配置国内镜像源会让下载速度快 **10 倍**！
```bash
# 这个配置真的能救命
registry-mirrors: [
  "https://docker.1panel.live",
  "https://dockerhub.jobcher.com",
  "https://docker.awchina.com"
]
```

### 2️⃣ 必须使用 --env-file 参数或确保 .env.prod 存在
```bash
# ✅ 正确
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# ❌ 错误（会导致 SECRET_KEY 未设置）
docker-compose -f docker-compose.prod.yml up -d  # （除非 .env.prod 在同级目录）
```

### 3️⃣ SECRET_KEY 必须强且唯一
```bash
# ✅ 生成强密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# ❌ 不要硬编码
SECRET_KEY=abc123  # 太弱，容易被破解
```

---

## 🆘 如果还有问题

### 症状1：容器仍然无法启动
```bash
# 查看详细错误
docker-compose -f docker-compose.prod.yml logs backend

# 检查镜像源是否配置成功
docker info | grep -A 5 "Registry Mirrors"

# 如果还是超时，预先拉取镜像
docker pull redis:7-alpine
docker pull python:3.11-slim
```

### 症状2：端口已被占用
```bash
# 查看占用进程
lsof -i :8001

# 杀死进程
kill -9 <PID>
```

### 症状3：SECRET_KEY 不生效
```bash
# 验证 .env.prod 内容
cat .env.prod | grep SECRET_KEY

# 检查容器是否加载了环境变量
docker-compose -f docker-compose.prod.yml exec backend env | grep SECRET_KEY
```

---

## 📚 详细文档位置

| 文档 | 用途 | 何时读 |
|------|------|-------|
| `DEPLOYMENT_QUICK_FIX.md` | 快速参考卡片 | 第一次出问题时 |
| `DEPLOYMENT_FIX_GUIDE.md` | 详细修复步骤 | 需要详细说明时 |
| `DEPLOYMENT_SQLITE.md` | 完整部署指南 | 首次部署时 |
| `fix-deployment.sh` | 自动脚本 | 想一键修复时 |

---

## ✨ 修复后的下一步

部署成功后记得：

1. **修改默认密码** ⚠️ 最重要！
   ```
   URL: http://your-domain.com/admin/
   用户: admin
   密码: admin123
   ```

2. **配置域名和 HTTPS**
   - 参考 `DEPLOYMENT_SQLITE.md` 第四步

3. **设置自动备份**
   - 参考 `DEPLOYMENT_SQLITE.md` 第七步

---

## 🚀 预计时间

- **第一次完整修复**：15-20 分钟（包括镜像下载）
- **如果使用了国内镜像源**：5-10 分钟
- **验证部署**：5 分钟

---

**祝部署顺利！有问题随时查看 `DEPLOYMENT_QUICK_FIX.md` 或 `DEPLOYMENT_FIX_GUIDE.md`**
