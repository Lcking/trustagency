# 快速启动指南

## 一步启动本地开发环境

### 步骤 1: 启动后端

```bash
cd /Users/ck/Desktop/Project/trustagency/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**预期输出**:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### 步骤 2: 在浏览器中访问

- **主页**: http://localhost:8001
- **管理面板**: http://localhost:8001/admin
- **API 文档**: http://localhost:8001/api/docs

### 步骤 3: 登录管理面板

```
用户名: admin
密码: admin123
```

---

## 验证数据完整性

### 快速验证命令

```bash
# 验证平台数据 (应该返回 4 个平台)
curl http://localhost:8001/api/platforms | python3 -c "import json, sys; print(len(json.load(sys.stdin)['data']))"

# 验证分类数据 (应该返回 20 个分类)
curl http://localhost:8001/api/categories | python3 -c "import json, sys; print(len(json.load(sys.stdin)))"

# 验证分栏数据 (应该返回 4 个分栏)
curl http://localhost:8001/api/sections | python3 -c "import json, sys; print(len(json.load(sys.stdin)['data']))"

# 验证登录功能
curl -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  python3 -c "import json, sys; data = json.load(sys.stdin); print('✅ Login OK' if 'access_token' in data else '❌ Login Failed')"
```

---

## 平台 Platform Type 验证

```bash
curl http://localhost:8001/api/platforms | python3 << 'PYEOF'
import json, sys
platforms = json.load(sys.stdin)['data']
for p in platforms:
    print(f"{p['name']:15} → {p['platform_type']:10} (rank: {p['rank']})")
PYEOF
```

**预期输出**:
```
AlphaLeverage   → 专业        (rank: 1)
BetaMargin      → 平衡        (rank: 2)
GammaTrader     → 新手友好    (rank: 3)
百度            → 高风险      (rank: 4)
```

---

## 数据库操作

### 检查数据库存在

```bash
ls -lh /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
```

### 重新生成数据库

```bash
cd /Users/ck/Desktop/Project/trustagency/backend
rm trustagency.db  # 删除旧数据库
python3 restore_db.py trustagency.db  # 生成新数据库
```

### 查看数据库内容

```bash
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db

# 在 sqlite3 提示符中执行:
.tables  # 显示所有表
SELECT COUNT(*) FROM platforms;  # 查看平台数
SELECT COUNT(*) FROM categories;  # 查看分类数
SELECT name, platform_type FROM platforms;  # 查看平台和类型
SELECT * FROM admin_users;  # 查看管理员账户
.quit  # 退出
```

---

## 常见问题

### Q: 后端启动失败，提示数据库错误

**A**: 重新生成数据库
```bash
cd /Users/ck/Desktop/Project/trustagency/backend
python3 restore_db.py trustagency.db
```

### Q: 登录失败，提示 "Invalid credentials"

**A**: 检查管理员账户
```bash
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
SELECT username, is_active FROM admin_users;
```

如果记录不存在，重新生成数据库。

### Q: 平台 API 返回 500 错误

**A**: 检查数据库模式
```bash
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
PRAGMA table_info(platforms);
```

确保有 39 列，包括 `platform_type` 列。

### Q: 前端页面不显示

**A**: 检查后端是否运行，以及静态文件路径是否正确
```bash
curl http://localhost:8001/ | head -20
```

应该返回 HTML 内容。

---

## 部署前清单

- [ ] 后端成功启动
- [ ] 所有 API 端点返回正确数据
- [ ] 登录功能正常
- [ ] 前端页面正确显示
- [ ] 数据库文件大小约 57 KB
- [ ] 4 个平台都有正确的 platform_type
- [ ] 数据库已备份

---

## 文件路径速查

| 文件/目录 | 路径 |
|----------|------|
| 后端主目录 | `/Users/ck/Desktop/Project/trustagency/backend/` |
| 后端主文件 | `/Users/ck/Desktop/Project/trustagency/backend/app/main.py` |
| 数据库 | `/Users/ck/Desktop/Project/trustagency/backend/trustagency.db` |
| 前端文件 | `/Users/ck/Desktop/Project/trustagency/site/` |
| 环境配置 | `/Users/ck/Desktop/Project/trustagency/.env` |
| 生产配置 | `/Users/ck/Desktop/Project/trustagency/.env.prod` |
| 项目根目录 | `/Users/ck/Desktop/Project/trustagency/` |

---

## Git 相关

### 当前状态

```bash
cd /Users/ck/Desktop/Project/trustagency
git status
git log --oneline -5
```

### 目标 Commit

```
9a98d022467b0cf19cdd1862e9e0d5fa0acc03d7
chore: 配置SQLite用于生产环境 - 优化4GB服务器资源占用
```

### 查看特定 Commit

```bash
git show 9a98d02
```

---

## 生成报告

完整验证报告位于:
`/Users/ck/Desktop/Project/trustagency/LOCAL_VERIFICATION_REPORT.md`

