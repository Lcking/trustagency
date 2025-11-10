# ⚡ 快速修复指南 - 管理后台 404 问题

## 问题分析

- ✅ **代码已修复**: main.py、Dockerfile、index.html 都已更新
- ✅ **根本原因已找到**: Uvicorn 没有启用自动重载
- ⏳ **需要的步骤**: 重建镜像并重启容器

## 一键修复 (复制粘贴执行)

```bash
cd /Users/ck/Desktop/Project/trustagency && \
docker-compose down -v && \
docker-compose build --no-cache backend && \
docker-compose up -d && \
sleep 30 && \
echo "=== 验证修复 ===" && \
curl -s http://localhost:8001/admin/ | head -10
```

## 分步修复 (了解每一步)

### 第 1 步: 停止容器
```bash
cd /Users/ck/Desktop/Project/trustagency
docker-compose down -v
```

### 第 2 步: 重建镜像 (重要!)
```bash
docker-compose build --no-cache backend
```
**为什么这一步重要**: Dockerfile 现在包含 `--reload` 标志

### 第 3 步: 启动容器
```bash
docker-compose up -d
```

### 第 4 步: 等待启动完成
```bash
sleep 30
```

### 第 5 步: 验证修复

#### 验证 1: 检查后端
```bash
curl http://localhost:8001/admin/
```
**预期**: 返回 HTML 代码 (`<!DOCTYPE html...`)
**错误**: 返回 `{"detail":"Not Found"}`

#### 验证 2: 检查健康状态
```bash
curl http://localhost:8001/api/health
```
**预期**: `{"status":"ok","message":"..."}`

#### 验证 3: 检查 Nginx
```bash
curl http://localhost/admin/
```
**预期**: 返回 HTML 代码

## 如果仍然不工作?

### 调试步骤:

1. **查看日志**:
   ```bash
   docker-compose logs -f backend
   ```

2. **检查容器状态**:
   ```bash
   docker-compose ps
   ```

3. **手动进入容器**:
   ```bash
   docker exec -it trustagency-backend bash
   ls -la /app/site/admin/
   cat /app/app/main.py | head -70
   ```

4. **强制重建 (清除所有缓存)**:
   ```bash
   docker-compose down -v
   docker system prune -f
   docker-compose build --no-cache backend
   docker-compose up -d
   ```

## 关键代码变更

| 文件 | 行号 | 修改内容 | 原因 |
|-----|------|--------|-----|
| `main.py` | 26 | 扩展 CORS 源 | 支持 port 80 访问 |
| `main.py` | 39-42 | StaticFiles 移到最前 | FastAPI 优先级修复 |
| `main.py` | 61-67 | 添加备选路由 | 双保险 |
| `Dockerfile` | 最后一行 | 添加 `--reload` | 启用自动重载 |

## 预期最终结果

- ✅ `http://localhost:8001/admin/` → HTML 页面
- ✅ `http://localhost/admin/` → HTML 页面  
- ✅ 修改代码后自动重载 (无需手动重启)
- ✅ 登录成功,没有网络错误

---

**如果有任何问题,请运行调试步骤并查看 docker 日志。**
