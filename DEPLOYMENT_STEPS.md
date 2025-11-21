# 🚀 数据库恢复部署步骤

## 目标
将项目恢复到提交 `9a98d02` 时的完整状态（包含完整的 SQLite 数据库）

## 前置条件
- 本地已有完整的 `trustagency` 项目代码
- 服务器 IP: `106.13.188.99`
- 服务器用户: `root`
- 服务器已安装 Docker 和 docker-compose

## 快速部署（推荐）

### 方式一：使用自动化脚本（最简单）

在你的 Mac 终端运行：

```bash
cd /Users/ck/Desktop/Project/trustagency
bash deploy_db.sh
```

该脚本会自动执行以下所有步骤。

---

## 手动部署步骤

如果自动化脚本有问题，按以下步骤手动执行：

### 步骤 1️⃣：本地生成数据库

```bash
cd /Users/ck/Desktop/Project/trustagency/backend
python3 restore_db.py trustagency.db
```

**验证** - 查看输出中的数据验证信息，确保：
- 栏目: 4
- 分类: 20  
- 平台: 4
- 管理员: 1

### 步骤 2️⃣：验证数据库内容

```bash
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db ".tables"
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db "SELECT COUNT(*) FROM platforms;"
```

应该看到 `4` 个平台。

### 步骤 3️⃣：复制数据库到服务器

```bash
scp /Users/ck/Desktop/Project/trustagency/backend/trustagency.db root@106.13.188.99:/root/trustagency/backend/
```

**注意**: 如果要求输入密码，输入你的服务器 root 密码。

### 步骤 4️⃣：在服务器上创建数据目录

```bash
ssh root@106.13.188.99 "mkdir -p /root/trustagency/backend/data && cp /root/trustagency/backend/trustagency.db /root/trustagency/backend/data/"
```

### 步骤 5️⃣：重启后端容器

```bash
ssh root@106.13.188.99 "cd /root/trustagency && docker-compose -f docker-compose.prod.yml restart backend"
```

### 步骤 6️⃣：等待容器启动

```bash
sleep 5
```

### 步骤 7️⃣：验证 API 响应

```bash
curl http://106.13.188.99:8001/api/platforms | head -c 200
```

应该看到 JSON 格式的平台数据，包含 `AlphaLeverage` 等。

---

## 📊 验证部署成功

访问以下 URL 验证：

1. **后端 API** - 查看平台列表
   ```
   http://106.13.188.99:8001/api/platforms
   ```
   
2. **后端 API** - 查看分类列表
   ```
   http://106.13.188.99:8001/api/categories
   ```

3. **前端** - 查看 UI
   ```
   http://106.13.188.99:3000
   ```

## 🔍 调试

### 查看后端容器日志
```bash
ssh root@106.13.188.99 "docker logs -f trustagency-backend"
```

### 检查数据库文件是否存在
```bash
ssh root@106.13.188.99 "ls -lh /root/trustagency/backend/data/trustagency.db"
```

### 直接在服务器查询数据库
```bash
ssh root@106.13.188.99 "sqlite3 /root/trustagency/backend/data/trustagency.db 'SELECT COUNT(*) FROM platforms;'"
```

### 查看 Docker 卷挂载
```bash
ssh root@106.13.188.99 "docker inspect trustagency-backend | grep -A 5 Mounts"
```

---

## 📝 数据库结构

恢复后的数据库包含：

### 平台 (4 个)
| ID | 名称 | 类型 |
|:--:|:---:|:---:|
| 1 | AlphaLeverage | 专业 |
| 2 | BetaMargin | 平衡 |
| 3 | GammaTrader | 新手友好 |
| 4 | 百度 | 高风险 |

### 栏目 (4 个)
- 常见问题 (FAQ)
- 百科 (Wiki)
- 指南 (Guide)
- 验证 (Review)

### 分类 (20 个)
- 每个栏目下 5 个分类

### 管理员账户
- 用户名: `admin`
- 密码: `admin123`
- Hash: `$2b$12$N9qo8uLOickgx2ZMRZoXyeIGlMw5YBNR5z7EcKxVx0.3S2KaUDSyO`

---

## ⚙️ 环境配置

### 本地环境 (`.env.local`)
```
DATABASE_URL=sqlite:///./trustagency.db
```

### 生产环境 (`.env.prod`)
```
DATABASE_URL=sqlite:////app/data/trustagency.db
```

### Docker Compose 配置 (`docker-compose.prod.yml`)
```yaml
services:
  backend:
    environment:
      - DATABASE_URL=sqlite:////app/data/trustagency.db
    volumes:
      - sqlite_data:/app/data

volumes:
  sqlite_data:
    driver: local
```

---

## 💾 文件位置参考

| 文件 | 位置 |
|:---:|:---:|
| 恢复脚本 | `backend/restore_db.py` |
| 自动部署脚本 | `deploy_db.sh` |
| 本地数据库 | `backend/trustagency.db` |
| 服务器数据库 | `/root/trustagency/backend/trustagency.db` |
| Docker 卷路径 | `/root/trustagency/backend/data/trustagency.db` |

---

## 🎯 完成标志

✅ 数据库文件创建成功
✅ 本地验证数据完整 (4 平台, 20 分类)
✅ 文件复制到服务器
✅ 容器重启成功
✅ API 返回正确的平台数据
✅ 前端可以正常显示数据

---

## ❓ 常见问题

**Q: 如何恢复到不同的提交？**
A: 查看提交 `9a98d02` 的 `backend/app/database.py` 中的 `init_db()` 函数，复制其逻辑到 `restore_db.py`。

**Q: 能否备份现有数据库？**
A: 是的，在运行之前执行：
```bash
ssh root@106.13.188.99 "cp /root/trustagency/backend/data/trustagency.db /root/trustagency/backend/data/trustagency.db.bak"
```

**Q: 如何清空数据库重新开始？**
A: 在服务器上运行：
```bash
ssh root@106.13.188.99 "rm /root/trustagency/backend/data/trustagency.db && cd /root/trustagency && docker-compose -f docker-compose.prod.yml restart backend"
```

---

**最后更新**: 2025-11-21
**目标提交**: 9a98d022467b0cf19cdd1862e9e0d5fa0acc03d7
