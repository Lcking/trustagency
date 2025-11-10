# 🚀 Admin 清理完成 - 现在启动服务

**状态**: ✅ 清理已完成且验证通过

---

## 🎯 两种启动方式

### 方式 1️⃣: 使用 Docker Compose (推荐 - 最简单)

```bash
# 启动所有容器
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

**优势**:
- ✅ 一键启动所有服务 (后端 + 前端 + 数据库 + Redis)
- ✅ 生产级配置
- ✅ 完整的环境隔离
- ✅ 易于部署

**访问地址**:
- Admin 页面: http://localhost:8001/admin/
- 前端网站: http://localhost/
- API 文档: http://localhost:8001/api/docs

---

### 方式 2️⃣: 本地 Python (开发调试)

```bash
# 进入后端目录
cd backend

# 方法 A: 直接使用 Python 启动
python -m uvicorn app.main:app --port 8001 --reload

# 方法 B: 使用虚拟环境
source ../venv/bin/activate
python -m uvicorn app.main:app --port 8001 --reload

# 方法 C: 使用启动脚本
python ../quick_start_backend.py
```

**安装依赖** (如果需要):
```bash
pip install -r requirements.txt
```

**访问地址**:
- Admin 页面: http://localhost:8001/admin/
- API 文档: http://localhost:8001/api/docs

---

## ✅ 完成清单

在启动前，请确认:

- [x] ✅ `site/admin/` 目录已删除
- [x] ✅ `backend/site/admin/index.html` 存在
- [x] ✅ 快速验证脚本通过 (`python quick_verify.py`)
- [x] ✅ Tiptap CDN 资源完整
- [ ] ⏳ 选择启动方式并运行

---

## 🧪 启动后的测试

### 1. 访问 Admin 页面
```
http://localhost:8001/admin/
```

### 2. 查看 API 文档
```
http://localhost:8001/api/docs
```

### 3. 测试 Tiptap 编辑器
- 打开浏览器开发者工具 (F12)
- 查看 Console 标签
- 在编辑器中输入文本
- 测试工具栏功能

### 4. 检查诊断信息
在浏览器控制台运行:
```javascript
TiptapDiagnostics.check()
```

预期输出:
```javascript
{
  "Tiptap加载": true,
  "StartKit": true,
  "编辑器容器": true,
  "DOM就绪": true,
  "总体状态": "✅ 正常"
}
```

---

## 📊 容器状态检查

```bash
# 查看运行中的容器
docker-compose ps

# 查看特定服务的日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 进入容器
docker-compose exec backend bash
docker-compose exec db psql -U trustagency
```

---

## 🐛 故障排除

### 问题: Admin 页面返回 404

```bash
# 1. 检查后端是否运行
curl http://localhost:8001/api/health

# 2. 检查文件是否存在
ls -la backend/site/admin/index.html

# 3. 查看后端日志
docker-compose logs backend | grep -i admin
```

### 问题: 数据库连接失败

```bash
# 1. 检查数据库是否运行
docker-compose ps | grep db

# 2. 查看数据库日志
docker-compose logs db

# 3. 重新启动数据库
docker-compose restart db
```

### 问题: Tiptap 编辑器不加载

```bash
# 1. 打开浏览器开发者工具 (F12)
# 2. 查看 Console 标签查看错误
# 3. 查看 Network 标签确认 CDN 资源加载
# 4. 查看文件是否包含 Tiptap 脚本
grep -i tiptap backend/site/admin/index.html | head -5
```

---

## 🎓 环境配置

### Docker 环境变量
所有配置在 `docker-compose.yml` 中:

```yaml
environment:
  - DATABASE_URL=postgresql://trustagency:trustagency@db:5432/trustagency
  - REDIS_URL=redis://redis:6379/0
  - DEBUG=True
```

### 本地环境变量
创建 `.env` 文件:

```bash
DATABASE_URL=postgresql://localhost:5432/trustagency
REDIS_URL=redis://localhost:6379/0
DEBUG=True
API_TITLE=TrustAgency API
API_VERSION=1.0.0
```

---

## 📝 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看日志
docker-compose logs -f backend

# 进入后端容器
docker-compose exec backend bash

# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 清理容器和卷
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache
```

---

## ✨ 预期结果

### Admin 页面应该显示:

```
┌──────────────────────────────────────────┐
│   TrustAgency 后台管理系统                  │
├──────────────────────────────────────────┤
│ 侧边栏                主要内容区             │
│ ├─ 仪表板             ┌──────────────────┐│
│ ├─ 内容管理           │  Tiptap 编辑器    ││
│ ├─ 用户管理           │  [工具栏]         ││
│ └─ 系统设置           │                  ││
│                      │  [编辑区域]       ││
│                      └──────────────────┘│
└──────────────────────────────────────────┘
```

### 功能检查:
- ✅ 编辑器加载正常
- ✅ 工具栏按钮可用
- ✅ 文本输入正常
- ✅ 格式化功能正常
- ✅ 保存功能正常

---

## 🎯 立即开始

选择你的启动方式:

**简单方式 (推荐)**:
```bash
docker-compose up -d
```

**开发方式**:
```bash
cd backend
python -m uvicorn app.main:app --port 8001 --reload
```

然后访问: **http://localhost:8001/admin/**

---

**准备好了？开始启动吧！** 🚀

生成时间: 2025-11-09
