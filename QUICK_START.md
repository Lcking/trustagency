# 快速启动指南

## 🚀 5 分钟快速开始

### 步骤 1：初始化数据库

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 验证系统准备就绪
python scripts/verify_system.py

# 初始化数据库并导入平台数据
python scripts/init_platform_data.py
```

预期输出：
```
=== 检查数据库列 ===
需要添加 9 个列: {...}
  ✓ 添加列: why_choose
  ✓ 添加列: account_types
  ...
✓ 所有列已添加

=== 初始化平台详情数据 ===
✓ 更新平台: AlphaLeverage (alpha-leverage)
✓ 更新平台: BetaMargin (beta-margin)
✓ 更新平台: GammaTrader (gamma-trader)

✓ 初始化完成！
```

### 步骤 2：启动后端服务

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 启动 FastAPI 服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

预期输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### 步骤 3：验证 API

在新的终端窗口中，测试 API 端点：

```bash
# 获取表单定义
curl http://localhost:8001/api/admin/platforms/form-definition

# 获取平台列表
curl http://localhost:8001/api/admin/platforms/edit-list

# 获取单个平台详情
curl http://localhost:8001/api/admin/platforms/1/edit
```

### 步骤 4：在前端中集成

在前端项目中，使用提供的 Vue/React 组件：

```javascript
// 导入组件
import { PlatformEditor } from '@/components/PlatformEditor';

// 在页面中使用
<template>
  <PlatformEditor />
</template>
```

---

## 📚 完整文档

### 后端文档
- 完整实现清单：`/backend/PLATFORM_DETAILS_IMPLEMENTATION.md`
- 数据库初始化：`/backend/scripts/init_platform_data.py`
- 管理 API 路由：`/backend/app/routes/admin_platforms.py`

### 前端文档
- 集成指南：`/frontend/PLATFORM_EDITOR_INTEGRATION.md`
- Vue 3 组件示例
- React 组件示例

---

## 🔍 验证检查清单

- [ ] 数据库连接成功
- [ ] 9 个新列已添加到 platform 表
- [ ] 三个平台的详情数据已导入
- [ ] 后端服务运行在 8001 端口
- [ ] `/api/docs` 可以访问（Swagger UI）
- [ ] 所有新 API 端点都有响应
- [ ] 前端能够成功加载表单定义
- [ ] 能够编辑和保存平台数据

---

## 📊 数据验证

### 检查数据库中的平台数据

```bash
# 使用 SQLite CLI
sqlite3 app.db

# 查询平台数据
SELECT id, name, slug, 
       length(why_choose) as why_choose_len,
       length(account_types) as account_types_len,
       length(fee_table) as fee_table_len
FROM platform;

# 查看具体的 JSON 数据
SELECT json_extract(why_choose, '$[0].title') FROM platform WHERE id = 1;

# 退出
.quit
```

### API 测试脚本

```python
import requests
import json

API_BASE = "http://localhost:8001/api"

# 测试 1: 获取表单定义
response = requests.get(f"{API_BASE}/admin/platforms/form-definition")
print(f"✓ 表单定义: {len(response.json()['sections'])} 个部分")

# 测试 2: 获取平台列表
response = requests.get(f"{API_BASE}/admin/platforms/edit-list")
print(f"✓ 平台列表: {response.json()['total']} 个平台")

# 测试 3: 获取平台详情
response = requests.get(f"{API_BASE}/admin/platforms/1/edit")
platform = response.json()
print(f"✓ 平台详情: {platform['name']}")
print(f"  - why_choose: {len(platform.get('why_choose', '')) > 0}")
print(f"  - account_types: {len(platform.get('account_types', '')) > 0}")
print(f"  - fee_table: {len(platform.get('fee_table', '')) > 0}")

# 测试 4: 更新平台
update_data = {
    "description": "更新后的描述"
}
response = requests.post(
    f"{API_BASE}/admin/platforms/1/edit",
    json=update_data
)
print(f"✓ 更新平台: {response.status_code}")
```

运行脚本：
```bash
python test_api.py
```

---

## 🐛 常见问题

### Q: 数据库迁移失败怎么办？

A: 检查以下几点：
1. 确保数据库文件存在：`backend/app.db`
2. 查看错误日志获取具体错误信息
3. 手动运行 SQL 命令添加列：
   ```sql
   ALTER TABLE platform ADD COLUMN why_choose TEXT;
   ALTER TABLE platform ADD COLUMN account_types TEXT;
   -- 等等...
   ```

### Q: 后端无法启动怎么办？

A: 检查以下几点：
1. Python 虚拟环境是否激活
2. 依赖是否已安装：`pip install -r requirements.txt`
3. 8001 端口是否被占用：`lsof -i :8001`

### Q: API 返回 404 怎么办？

A: 确保：
1. 路由已在 `main.py` 中注册
2. 检查 URL 是否正确
3. 查看 Swagger 文档：`http://localhost:8001/api/docs`

### Q: JSON 字段无法保存怎么办？

A: 检查以下几点：
1. 确认 JSON 格式正确
2. 使用 JSON 验证工具验证数据
3. 查看 API 响应错误信息

---

## 🔄 工作流程

### 编辑现有平台

1. 访问管理后台
2. 从平台列表中选择要编辑的平台
3. 系统加载平台详情数据
4. 填充表单字段
5. 点击"保存"提交更改
6. 系统显示成功或错误信息

### 添加新平台

1. 首先在后端创建平台记录
2. 然后可以通过管理编辑界面更新其详情信息

### 批量导入平台数据

1. 扩展 `init_platform_data.py` 脚本
2. 添加新平台的数据模板
3. 运行脚本导入数据

---

## 📈 下一步

1. **前端集成** - 在管理后台中集成平台编辑界面
2. **富文本编辑** - 为某些字段添加富文本编辑器
3. **媒体管理** - 添加上传和管理平台 Logo 等媒体
4. **预览功能** - 在编辑时实时预览平台页面
5. **历史记录** - 记录平台信息的修改历史
6. **国际化** - 支持多语言平台描述

---

## 📞 获取帮助

### 文件位置

- 后端完整清单：`PLATFORM_DETAILS_IMPLEMENTATION.md`
- 前端集成指南：`PLATFORM_EDITOR_INTEGRATION.md`
- API 文档：`http://localhost:8001/api/docs`

### 查看日志

```bash
# 后端日志
tail -f /Users/ck/Desktop/Project/trustagency/backend/logs/app.log

# 数据库查询
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/app.db ".tables"
```

---

**最后更新：2024**
**版本：1.0.0**
