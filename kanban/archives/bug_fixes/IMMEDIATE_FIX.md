# 🆘 快速恢复指南 - 立即行动

你说系统"又卡住了"。这意味着前面修复可能失效或新的问题出现。

## 🚨 最可能的原因（按优先级）

### 1️⃣ **分类数据真的丢失了（oldbug001复现）**
这是最严重的。需要立即恢复。

### 2️⃣ **后端启动失败**
Python依赖问题或语法错误。

### 3️⃣ **前端页面加载失败**
JavaScript错误或API响应异常。

### 4️⃣ **数据库损坏**
SQLite文件损坏或版本不兼容。

---

## 🛠️ 立即执行的修复步骤

### **第0步：清理环境**

```bash
# 1. 停止所有后台进程
pkill -f "uvicorn"
pkill -f "python"
sleep 2

# 2. 删除Python缓存
find /Users/ck/Desktop/Project/trustagency -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /Users/ck/Desktop/Project/trustagency -name "*.pyc" -delete 2>/dev/null

# 3. 检查数据库是否损坏
ls -lh /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
```

### **第1步：恢复分类数据**

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 运行恢复脚本
python restore_categories.py

# 输出应该显示：
# ✅ 恢复完成! 共添加 XX 个分类
```

### **第2步：验证后端启动**

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 启动后端（前台，便于查看错误）
python -m uvicorn app.main:app --reload --port 8000

# 应该看到：
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **第3步：测试API基本功能**

```bash
# 在另一个终端运行

# 测试 API 是否响应
curl http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -v

# 测试 section API
curl http://localhost:8000/api/sections \
  -v

# 测试 category API
curl http://localhost:8000/api/categories \
  -v
```

### **第4步：打开浏览器验证**

```
http://localhost:8000/admin/

1. 登录页面是否正常显示？
2. 输入 admin / admin123
3. 点击登录
4. 是否能进入后台？
```

---

## ✅ 完整检查清单

运行后，逐项检查：

- [ ] 后端能启动（无错误）
- [ ] 分类数据已恢复（数量 > 0）
- [ ] 能成功登录
- [ ] 栏目管理页面能加载
- [ ] 栏目选择框有选项（不是空的）
- [ ] 选择栏目后，分类框有选项显示
- [ ] 能删除分类（bug009已修复）
- [ ] 能新增分类（bug009已修复）
- [ ] 能编辑平台（HTTP方法已修复为POST）
- [ ] commission_rate 能输入 0-1 的数值

---

## 🆘 如果还是卡住了

请告诉我：

1. **具体错误信息是什么？**
   ```
   复制并粘贴完整的错误文本
   ```

2. **卡在哪一步？**
   - [ ] 后端启动时
   - [ ] 登录时
   - [ ] 栏目管理页面
   - [ ] 其他（哪里？）

3. **浏览器console有错误吗？**
   ```
   打开浏览器F12，查看Console标签
   复制并粘贴任何红色错误信息
   ```

4. **数据库文件大小正常吗？**
   ```bash
   ls -lh /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
   
   应该显示: -rw-r--r--  XXX  trustagency.db (>1MB)
   ```

---

## 💾 备用方案：完全重置

如果以上都不行，我们可以：

1. 备份当前数据库
2. 删除数据库文件
3. 重新初始化数据库
4. 恢复所有数据

但首先，请告诉我你具体卡在哪里！

