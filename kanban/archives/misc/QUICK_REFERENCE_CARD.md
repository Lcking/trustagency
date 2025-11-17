# 📌 TrustAgency - 快速参考卡片

## ⚡ 30 秒快速启动

```bash
cd /Users/ck/Desktop/Project/trustagency
bash run.sh
```

然后打开浏览器:
- 首页: http://localhost:8001/
- QA: http://localhost:8001/qa/
- Wiki: http://localhost:8001/wiki/
- 文章: http://localhost:8001/article/faq-what-is-leverage

---

## 🎯 系统构成

| 组件 | 端口 | 状态 | 命令 |
|------|------|------|------|
| 后端 API | 8000 | ✅ 就绪 | `cd backend && python -m uvicorn app.main:app --port 8000` |
| 前端服务 | 8001 | ✅ 就绪 | `cd site && python3 -m http.server 8001` |
| 数据库 | 本地 | ✅ 就绪 | SQLite (trustagency.db) |

---

## ✅ URL 访问指南

### 文章详情 - 3 种方式都支持

1. **ID 查询参数** (不推荐)
   ```
   http://localhost:8001/article?id=6
   ```

2. **Slug 查询参数** (备选)
   ```
   http://localhost:8001/article?slug=faq-what-is-leverage
   ```

3. **路径形式** ⭐ **最推荐**
   ```
   http://localhost:8001/article/faq-what-is-leverage
   ```

---

## 🔧 常用命令

### 验证系统
```bash
python3 /Users/ck/Desktop/Project/trustagency/verify_system.py
```

### Git 查看状态
```bash
cd /Users/ck/Desktop/Project/trustagency
git status
git log --oneline -5
```

### 查看数据库
```bash
cd /Users/ck/Desktop/Project/trustagency
sqlite3 trustagency.db ".tables"
```

### 查看 API 端点
```bash
curl http://localhost:8000/api/articles
curl http://localhost:8000/api/articles/1
curl "http://localhost:8000/api/articles/search/by-keyword?keyword=leverage"
```

---

## 📊 已修复的 7 个 Bug

| # | Bug | 状态 |
|---|-----|------|
| 1 | 后台新增平台 - 表单字段不完整 | ✅ |
| 2 | 前端平台详情页 - 字段显示不完整 | ✅ |
| 3 | 缺少"立即开户"按钮 | ✅ |
| 4 | 推荐平台区域限制 | ✅ |
| 5 | FAQ/Wiki/Guide 内容未同步到数据库 | ✅ |
| 6 | Wiki 搜索功能不工作 | ✅ |
| 7 | QA 页面前后端逻辑不匹配 | ✅ |

---

## 📈 新增功能

✨ **文章详情页** (`/article/index.html`)
- Markdown 支持
- 动态加载
- 多 URL 格式

✨ **SEO 优化**
- Slug 格式 URL
- 关键词友好
- 静态化外观

---

## 🚀 部署指令

### 本地开发
```bash
bash /Users/ck/Desktop/Project/trustagency/run.sh
```

### Docker 部署
```bash
cd /Users/ck/Desktop/Project/trustagency
docker-compose up -d
```

### 生产环境
参考: `DEPLOYMENT_GUIDE.md`

---

## 📚 文档位置

| 文档 | 位置 | 用途 |
|------|------|------|
| 使用指南 | `README_FINAL.md` | 功能和使用说明 |
| SEO 说明 | `SEO_OPTIMIZATION_COMPLETE.md` | URL 优化详情 |
| Bug 修复 | `BUG_FIXES_COMPLETED.md` | Bug 修复日志 |
| 部署指南 | `DEPLOYMENT_GUIDE.md` | 上线步骤 |
| 完成总结 | `COMPLETION_SUMMARY_FINAL_2025_11_17.md` | 项目总结 |

---

## ⚠️ 故障排查

### 问题: Port 已占用
```bash
lsof -i :8000
lsof -i :8001
# 然后 kill 对应进程
```

### 问题: 数据库连接失败
```bash
# 重建数据库
rm trustagency.db
cd backend && python -c "from app.main import app; from app.database import init_db; init_db()"
```

### 问题: 模块找不到
```bash
cd backend
pip install -r requirements.txt
```

---

## 🎉 项目状态

**当前版本**: 1.1 (SEO 优化版)  
**最后更新**: 2025-11-17 17:50 UTC+8  
**状态**: ✅ **生产就绪**

所有 7 个 Bug 已修复 ✅  
SEO 优化已完成 ✅  
系统验证已通过 ✅  

---

**准备好上线了！🚀**
