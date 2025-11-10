# 快速参考 - Tiptap 编辑器和后端

## 🚀 一键启动

```bash
# 在终端中执行
cd /Users/ck/Desktop/Project/trustagency/backend
source venv/bin/activate
python -m uvicorn app.main:app --port 8001 --reload
```

## 🌐 访问地址

```
http://localhost:8001/admin/
用户: admin
密码: newpassword123
```

## 🛑 停止服务

```bash
# 按 Ctrl+C 停止（如果在前台运行）
# 或者
pkill -f "uvicorn app.main:app"
```

## 🔧 快速测试

```bash
# 测试后端连接
curl -s http://localhost:8001/api/debug/admin-users

# 测试admin页面
curl -i http://localhost:8001/admin/

# 检查编辑器
curl -s http://localhost:8001/admin/ | grep 'id="articleEditor"'
```

## 📝 编辑器功能

| 快捷键 | 功能 |
|--------|------|
| Ctrl+B | 粗体 |
| Ctrl+I | 斜体 |
| Ctrl+` | 代码 |
| Ctrl+Z | 撤销 |
| Ctrl+Y | 重做 |

## 🐛 诊断

**浏览器 F12 → Console**
```javascript
// 运行此命令检查编辑器
TiptapDiagnostics.check()

// 应输出:
// ✅ Tiptap Editor 类可用
// @tiptap/core: true
// @tiptap/starter-kit: true
```

## 📂 关键文件

```
后端入口: /Users/ck/Desktop/Project/trustagency/backend/app/main.py
编辑器页面: /Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html
启动脚本: /Users/ck/Desktop/Project/trustagency/auto_start_backend.py
完整指南: /Users/ck/Desktop/Project/trustagency/BACKEND_STARTUP_GUIDE.md
```

## 🆘 常见问题

### 404 Not Found
→ 后端没有启动，或路由配置错误

### 编辑器不显示
→ F12 → Console 查看错误，可能是 CDN 加载失败

### 无法登录
→ 检查用户凭证 (admin / newpassword123)

### 端口被占用
```bash
# 查看谁占用了8001
lsof -i :8001

# 强制杀死进程
kill -9 <PID>
```

## ✅ 验证成功

如果看到:
- ✅ 页面加载 (没有404)
- ✅ 工具栏显示
- ✅ Console 无错误
- ✅ TiptapDiagnostics 成功

那就是成功了！🎉

## 📊 架构

```
浏览器
  ↓ GET /admin/
FastAPI (port 8001)
  ↓ StaticFiles
  ↓ FileResponse
index.html (2505行)
  ├─ Tiptap CDN (5个库)
  ├─ UI界面
  └─ 编辑器初始化
```

---

**更多信息见**: `BACKEND_STARTUP_GUIDE.md` 和 `TIPTAP_COMPLETION_REPORT.md`
