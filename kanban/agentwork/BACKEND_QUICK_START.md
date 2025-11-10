# 🚀 后端快速启动指南

## 一分钟快速启动

### 步骤 1: 打开终端

```bash
cd /Users/ck/Desktop/Project/trustagency/backend
```

### 步骤 2: 启动后端服务器

**方式 A: 使用启动脚本 (推荐)**

```bash
chmod +x start_backend.sh
./start_backend.sh
```

**方式 B: 直接命令**

```bash
PYTHONPATH=/Users/ck/Desktop/Project/trustagency/backend \
./venv/bin/python -m uvicorn app.main:app --reload --port 8001
```

### 步骤 3: 验证服务器运行

```bash
# 新打开一个终端窗口，运行:
curl http://localhost:8001/api/docs
```

---

## 🎯 服务器启动后

### ✅ 快速验证

1. **API 文档** (Swagger)
   ```
   http://localhost:8001/api/docs
   ```

2. **API 文档** (ReDoc)
   ```
   http://localhost:8001/api/redoc
   ```

3. **测试登录**
   ```bash
   curl -X POST http://localhost:8001/api/admin/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

### 📊 可用的 API 端点

#### 认证 (5 个)
- `POST /api/admin/login` - 登录
- `POST /api/admin/register` - 注册
- `GET /api/admin/me` - 获取当前用户
- `POST /api/admin/change-password` - 改密码
- `POST /api/admin/logout` - 登出

#### 平台 (9 个)
- `GET /api/platforms` - 列表 (支持搜索、排序、分页)
- `POST /api/platforms` - 创建
- `GET /api/platforms/{id}` - 获取
- `PUT /api/platforms/{id}` - 更新
- `DELETE /api/platforms/{id}` - 删除
- `POST /api/platforms/{id}/toggle-status` - 激活/停用
- `POST /api/platforms/{id}/toggle-featured` - 特色标记
- `POST /api/platforms/bulk/update-ranks` - **批量排名** ⭐
- `GET /api/platforms/featured/list` - 特色列表
- `GET /api/platforms/regulated/list` - 受监管列表

#### 文章 (15 个)
- `GET /api/articles` - 列表 (支持搜索、分类、排序、分页)
- `POST /api/articles` - 创建
- `GET /api/articles/{id}` - 获取
- `PUT /api/articles/{id}` - 更新
- `DELETE /api/articles/{id}` - 删除
- `POST /api/articles/{id}/publish` - 发布
- `POST /api/articles/{id}/unpublish` - 取消发布
- `POST /api/articles/{id}/toggle-featured` - 特色标记
- `POST /api/articles/{id}/like` - 点赞
- `GET /api/articles/search/by-keyword` - 搜索
- `GET /api/articles/featured/list` - 特色列表
- `GET /api/articles/trending/list` - 热门文章
- `GET /api/articles/by-category/{category}` - 按分类
- `GET /api/articles/by-platform/{platform_id}` - 按平台
- `GET /api/articles/by-author/{author_id}` - 按作者

---

## 🔧 常见问题

### Q1: 后端无法启动 - "Address already in use"

**解决**:
```bash
# 杀死占用 8001 端口的进程
lsof -i :8001 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# 等待 2 秒后重新启动
sleep 2
./start_backend.sh
```

### Q2: 导入错误 "No module named..."

**解决**:
```bash
# 重新安装所有依赖
./venv/bin/pip install -r requirements.txt

# 或仅安装缺失的包
./venv/bin/pip install <package_name>
```

### Q3: 后端启动但 API 文档为空

**解决**:
```bash
# 清除浏览器缓存或使用 Incognito 模式
# 访问: http://localhost:8001/api/docs?v=1
```

### Q4: 数据库连接错误

**解决**:
```bash
# 确保有 .env 文件
cat .env

# 如果没有，创建一个
cp .env.example .env

# 初始化数据库
./venv/bin/python app/init_db.py
```

---

## 📝 实用命令

### 查看日志

```bash
# 实时查看日志 (如果使用 run_backend.sh)
tail -f /tmp/trustagency_backend.log
```

### 重启服务

```bash
# 杀死当前服务
pkill -f "uvicorn.*8001"

# 重新启动
./start_backend.sh
```

### 测试 API

```bash
# 获取所有平台
curl http://localhost:8001/api/platforms

# 搜索平台
curl "http://localhost:8001/api/platforms?search=bitcoin"

# 排序平台 (按排名)
curl "http://localhost:8001/api/platforms?sort_by=rank&order=asc"

# 获取热门文章
curl http://localhost:8001/api/articles/trending/list

# 获取特色文章
curl http://localhost:8001/api/articles/featured/list
```

---

## 🎯 下一步

### Task 6: FastAPI Admin

```bash
# 当后端正常运行后，启动 Task 6
# FastAPI Admin 管理后台集成
# 预计时间: 1.5 小时
```

---

## 📞 支持信息

| 项目 | 地址 | 状态 |
|------|------|------|
| 前端 | http://localhost:8000 | ✅ 运行中 |
| 后端 | http://localhost:8001 | ✅ 运行中 |
| API 文档 | http://localhost:8001/api/docs | ✅ 可用 |
| 数据库 | SQLite/PostgreSQL | ✅ 就绪 |

---

**🚀 后端已完全就绪！**  
**📊 所有 29 个 API 端点都可用！**  
**✨ 开始测试吧！**
