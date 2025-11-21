# 🚀 本地开发启动指南

## 快速启动 (3步)

### 第1步: 清除缓存

在项目根目录执行：

```bash
# 清除Python缓存
find backend -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find backend -type f -name '*.pyc' -delete 2>/dev/null || true

# 清除前端缓存
cd frontend
rm -rf node_modules/.cache .next dist build
npm cache clean --force
cd ..
```

### 第2步: 生成本地数据库

```bash
cd backend
python3 restore_db.py trustagency.db
```

验证输出应该看到:
```
📊 平台类型分类:
   1. AlphaLeverage      → 专业
   2. BetaMargin         → 平衡
   3. GammaTrader        → 新手友好
   4. 百度               → 高风险
```

### 第3步: 启动服务

**方式A: 自动脚本启动 (推荐)**

```bash
cd /Users/ck/Desktop/Project/trustagency
bash start_local.sh
```

**方式B: 手动启动 (分别启动)**

#### 启动后端

在一个终端窗口：

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 创建虚拟环境 (首次)
python3 -m venv venv
source venv/bin/activate

# 安装依赖 (首次)
pip install -r requirements.txt

# 启动服务
export DATABASE_URL="sqlite:///./trustagency.db"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

输出应该显示:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

#### 启动前端

在另一个终端窗口：

```bash
cd /Users/ck/Desktop/Project/trustagency/frontend

# 安装依赖 (首次)
npm install

# 启动开发服务器
npm run dev
```

输出应该显示:
```
> VITE v... 
> ready in ... ms
> ➜  Local:   http://localhost:3000
```

---

## 📊 验证数据

### 1. 后端API验证

打开浏览器或用 curl：

```bash
# 查看平台列表（最重要）
curl http://localhost:8001/api/platforms | jq '.'

# 查看分类列表
curl http://localhost:8001/api/categories | jq '.'

# 查看栏目列表
curl http://localhost:8001/api/sections | jq '.'

# 查看AI配置
curl http://localhost:8001/api/ai-configs | jq '.'
```

**预期结果 - 平台数据**:

```json
[
  {
    "id": 1,
    "name": "AlphaLeverage",
    "platform_type": "专业",
    "rating": 4.8,
    "is_active": true
  },
  {
    "id": 2,
    "name": "BetaMargin",
    "platform_type": "平衡",
    "rating": 4.5,
    "is_active": true
  },
  {
    "id": 3,
    "name": "GammaTrader",
    "platform_type": "新手友好",
    "rating": 4.6,
    "is_active": true
  },
  {
    "id": 4,
    "name": "百度",
    "platform_type": "高风险",
    "rating": 4.7,
    "is_active": true
  }
]
```

### 2. API文档

访问 Swagger UI 查看完整API文档：

```
http://localhost:8001/docs
```

### 3. 前端UI验证

访问前端：

```
http://localhost:3000
```

检查:
- ✅ 首页是否正常加载
- ✅ 导航栏是否显示
- ✅ 平台卡片是否显示
- ✅ 分类是否显示
- ✅ 数据是否正确加载

---

## 🔍 数据库检查

直接查询本地数据库：

```bash
cd backend

# 查看有多少平台
sqlite3 trustagency.db "SELECT COUNT(*) FROM platforms;"

# 查看所有平台
sqlite3 trustagency.db "SELECT id, name, platform_type FROM platforms;"

# 查看有多少分类
sqlite3 trustagency.db "SELECT COUNT(*) FROM categories;"

# 查看管理员
sqlite3 trustagency.db "SELECT id, username FROM admin_users;"

# 查看栏目
sqlite3 trustagency.db "SELECT id, name, slug FROM sections;"
```

---

## 🛠️ 常见问题

### Q: 后端启动报错 "ModuleNotFoundError"

**A**: 确保虚拟环境激活并安装了所有依赖

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Q: 前端 npm 报错

**A**: 清除缓存并重新安装

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Q: 数据库锁定 "database is locked"

**A**: 删除旧数据库重新生成

```bash
cd backend
rm trustagency.db
python3 restore_db.py trustagency.db
```

### Q: 端口被占用

**A**: 更改端口

后端:
```bash
python3 -m uvicorn app.main:app --port 8002
```

前端:
```bash
npm run dev -- --port 3001
```

### Q: 如何停止服务

在启动服务的终端按 `Ctrl+C`，或：

```bash
# 找到进程
lsof -i :8001      # 后端
lsof -i :3000      # 前端

# 杀死进程
kill -9 <PID>
```

---

## 📝 完整流程总结

```bash
# 1. 清除缓存
find backend -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find backend -type f -name '*.pyc' -delete 2>/dev/null || true

# 2. 生成数据库
cd backend
python3 restore_db.py trustagency.db

# 3. 启动后端（新终端1）
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./trustagency.db"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 4. 启动前端（新终端2）
cd frontend
npm run dev

# 5. 访问
# 前端: http://localhost:3000
# 后端: http://localhost:8001
# API文档: http://localhost:8001/docs

# 6. 验证数据
curl http://localhost:8001/api/platforms | jq '.'
```

---

**最后更新**: 2025-11-21
