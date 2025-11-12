# 📖 API 文档快速入门指南

**版本**: 1.0.0  
**更新时间**: 2025-11-12

---

## 🎯 快速导航

### 👨‍💼 我是项目经理
→ 阅读 **[B1_COMPLETION_SUMMARY.md](./B1_COMPLETION_SUMMARY.md)** 的前两部分
- 了解生成了什么
- 查看统计数据
- 理解项目进度

### 👨‍💻 我是后端开发者
1. 快速查看: **[API_GUIDE.md](./API_GUIDE.md)** - 5 分钟快速了解
2. 集成开发: **[API_GUIDE.md](./API_GUIDE.md)** - 最佳实践部分
3. 错误处理: **[ERROR_CODES.md](./ERROR_CODES.md)** - 所有 22 个错误代码
4. 完整审查: **[API_AUDIT.md](./API_AUDIT.md)** - 全面的端点列表

### 👨‍💼 我是前端开发者
1. 架构设计: **[FRONTEND_API_SPEC.md](./FRONTEND_API_SPEC.md)** - 前 50 行
2. 实现代码: **[FRONTEND_API_SPEC.md](./FRONTEND_API_SPEC.md)** - 4 个核心模块
3. 错误处理: **[ERROR_CODES.md](./ERROR_CODES.md)** - 前端处理示例
4. 实时示例: **[FRONTEND_API_SPEC.md](./FRONTEND_API_SPEC.md)** - 文章编辑器示例

### 🧪 我是 QA/测试工程师
1. 导入集合: **[Postman_Collection.json](./Postman_Collection.json)**
2. 配置环境: 设置 `base_url` 和 `token`
3. 开始测试: 使用预配置的 30+ 个测试用例
4. 查看参数: **[API_GUIDE.md](./API_GUIDE.md)** - 常见操作示例

---

## 📋 文件清单

| 文件 | 大小 | 用途 | 优先级 |
|------|------|------|--------|
| **B1_COMPLETION_SUMMARY.md** | 5 KB | 任务完成总结，文档索引 | 🔴 必读 |
| **API_AUDIT.md** | 60 KB | 45+ 个端点的完整审计报告 | 🟡 重要 |
| **API_GUIDE.md** | 50 KB | 后端集成指南，最佳实践 | 🔴 必读 |
| **FRONTEND_API_SPEC.md** | 70 KB | 前端实现指南，4 个模块 | 🔴 必读 |
| **ERROR_CODES.md** | 40 KB | 22 个错误代码的完整参考 | 🔴 必读 |
| **Postman_Collection.json** | 80 KB | 30+ 个预配置的 API 测试用例 | 🟡 重要 |
| **QUICKSTART.md** | 8 KB | 本文档，快速入门指南 | 🟢 可选 |

**总计**: 文档大小约 313 KB，包含 2000+ 行详细内容

---

## ⏱️ 阅读时间参考

- **5 分钟**: API_GUIDE.md 的"基础知识"部分
- **15 分钟**: API_AUDIT.md 的概览
- **30 分钟**: FRONTEND_API_SPEC.md 的架构部分
- **1 小时**: 一个文件的完整阅读
- **2 小时**: 全部文档浏览

---

## 🔑 关键概念速览

### API 基础 URL
```
开发环境: http://localhost:8001
生产环境: https://api.trustagency.com
API 版本: v1 (在基础 URL 中)
```

### 认证方式
```
类型: JWT Bearer Token
获取: POST /api/admin/login
使用: Authorization: Bearer <token>
有效期: 24 小时
```

### 响应格式
```json
{
  "data": {...},           // 实际数据
  "error_code": "...",     // 错误代码
  "status_code": 200,      // HTTP 状态码
  "message": "..."         // 可选的消息
}
```

### 常用分页参数
```
skip: 0          // 跳过的记录数 (偏移量)
limit: 10        // 每页记录数 (最多 100)
sort_by: field   // 排序字段
sort_order: desc // 排序顺序 (asc/desc)
```

---

## 🚀 5 分钟快速开始

### 1. 启动后端服务器
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

### 2. 访问 Swagger UI
在浏览器打开: **http://localhost:8001/api/docs**

### 3. 测试登录
```bash
curl -X POST "http://localhost:8001/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 4. 获取文章列表
```bash
curl -X GET "http://localhost:8001/api/articles?limit=10"
```

### 5. 导入 Postman 集合
- 打开 Postman
- 点击 "Import"
- 选择 `Postman_Collection.json`
- 开始测试

---

## 📊 API 端点概览

### 按类型分类

**认证 (3 个)**
```
POST   /api/admin/login              登录
GET    /api/admin/me                 获取用户信息
POST   /api/admin/logout             登出
```

**文章 (12 个)**
```
GET    /api/articles                 列表 (支持搜索、过滤、排序)
POST   /api/articles                 创建
GET    /api/articles/{id}            获取单篇
PUT    /api/articles/{id}            更新
DELETE /api/articles/{id}            删除
PATCH  /api/articles/{id}/publish    发布
PATCH  /api/articles/{id}/feature    精选
GET    /api/articles/{slug}/html     获取 HTML 版本
... 还有 4 个
```

**分类 (8 个)** - 标准 CRUD
**栏目 (6 个)** - 标准 CRUD
**平台 (4 个)** - 配置管理
**AI 配置 (6 个)** - 模型配置
**上传 (2 个)** - 单/多文件
**任务 (2 个)** - 状态查询

**详细列表见**: API_AUDIT.md

---

## ❓ 常见问题

### 1. 如何获取 Token？
答: 调用登录端点，使用返回的 `access_token` 在后续请求中使用:
```
Authorization: Bearer <token>
```

### 2. Token 过期了怎么办？
答: 重新登录获取新 Token，参考 API_GUIDE.md 的"Token 管理"部分

### 3. 为什么返回 401 错误？
答: 查看 ERROR_CODES.md 中的"认证错误"部分，常见原因:
- 未提供 Token
- Token 格式不正确
- Token 已过期

### 4. 如何调试 API 问题？
答: 
1. 查看响应的 `error_code` 字段
2. 在 ERROR_CODES.md 中查找对应代码
3. 按照"处理方式"部分进行调试

### 5. 前端如何缓存数据？
答: FRONTEND_API_SPEC.md 的"api/client.js"部分有完整实现

### 6. 如何处理文件上传？
答: 使用 `/api/upload/single` 或 `/api/upload/multiple` 端点，参考 API_GUIDE.md

### 7. 分页应该如何使用？
答: 使用 `skip` 和 `limit` 参数:
```
GET /api/articles?skip=0&limit=10   // 第 1 页
GET /api/articles?skip=10&limit=10  // 第 2 页
GET /api/articles?skip=20&limit=10  // 第 3 页
```

### 8. 如何搜索内容？
答: 使用 `search` 查询参数:
```
GET /api/articles?search=bitcoin   // 搜索标题、内容、摘要
```

---

## 🔍 文件内容导航

### API_AUDIT.md 中查找
- **第 1 部分**: 统计数据和概览
- **第 2 部分**: 按模块详细列表
- **第 3 部分**: 审计检查清单
- **第 4 部分**: 改进建议

### API_GUIDE.md 中查找
- **基础**: 快速入门 (5-10 分钟读完)
- **认证**: Token 流程详解
- **操作**: 5 个代码示例
- **最佳实践**: 5 个推荐模式
- **常见问题**: 8 个 FAQ

### FRONTEND_API_SPEC.md 中查找
- **架构**: 推荐的文件结构
- **实现**: 4 个完整的模块代码
- **使用**: 如何调用这些模块
- **示例**: 真实的编辑器组件
- **模式**: 列表、搜索、无限滚动

### ERROR_CODES.md 中查找
- **快速查询**: 按 HTTP 状态码查表
- **详细说明**: 按错误代码查找
- **处理方式**: 每个错误的解决方案
- **代码示例**: 前端和后端处理代码

---

## 📞 获取帮助

### 需要快速回答?
→ 查看 **ERROR_CODES.md** 或相应文件的"常见问题"部分

### 需要完整指南?
→ 阅读 **API_GUIDE.md** 或 **FRONTEND_API_SPEC.md** 的相关章节

### 需要生产环境部署建议?
→ 查看 **API_AUDIT.md** 的"改进建议"部分

### 需要看代码示例?
→ **FRONTEND_API_SPEC.md** 有 500+ 行可复制的代码

### 需要进行 API 测试?
→ 导入 **Postman_Collection.json** 并开始测试

---

## ✅ 检查清单

在开始项目前，确保你已经:

- [ ] 阅读了本快速入门指南
- [ ] 根据你的角色阅读了相应的文档
- [ ] 查看了你需要的代码示例
- [ ] 理解了错误处理的方式
- [ ] (如果是 QA) 导入了 Postman 集合

---

## 🎓 学习路径

### 初学者路径 (第 1 天)
1. 阅读本文件 (5 分钟)
2. 阅读 API_Guide.md 的"基础"部分 (10 分钟)
3. 测试 Postman 集合中的 3 个简单请求 (10 分钟)
4. ✅ 现在你可以开始基本集成

### 中级路径 (第 2-3 天)
1. 阅读 FRONTEND_API_SPEC.md 的架构部分 (20 分钟)
2. 查看 4 个 API 模块的完整代码 (30 分钟)
3. 实现一个简单的文章列表页面 (1 小时)
4. ✅ 现在你可以处理更复杂的场景

### 高级路径 (第 4-7 天)
1. 阅读完整的 API_AUDIT.md (30 分钟)
2. 深入学习错误处理 (20 分钟)
3. 实现缓存、分页、搜索等高级功能 (2-3 小时)
4. 参与性能优化讨论 (1 小时)
5. ✅ 现在你是 API 集成专家

---

## 📈 项目里程碑

- ✅ **2025-11-12**: B-1 任务完成 - API 审计与文档
- ⏳ **下一步**: B-2 任务 - 性能优化 (预计)
- ⏳ **下一步**: B-3 任务 - 部署和监控 (预计)

---

## 📚 相关资源

- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc
- **OpenAPI JSON**: http://localhost:8001/api/openapi.json
- **GitHub 仓库**: [链接待补充]
- **内部 Wiki**: [链接待补充]

---

## 💡 提示

1. **书签这个文件** - 快速参考时会很有用
2. **打印 API_AUDIT.md** - 团队评审时更方便
3. **分享 Postman 集合** - 让全队可以测试 API
4. **定期更新** - API 变化时更新相应文档

---

**版本**: 1.0.0  
**最后更新**: 2025-11-12  
**作者**: AI Assistant  
**状态**: ✅ 完成

---

**祝你工作顺利! 如有问题，请参考相应的文档文件。** 🚀
