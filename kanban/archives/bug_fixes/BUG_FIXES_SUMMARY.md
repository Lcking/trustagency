# Bug 修复总结

**修复时间**: 2025-11-21 14:30 UTC  
**相关 Commit**: 3529dd4  
**状态**: ✅ 已修复且测试

---

## 修复内容

### 1. 文章管理 - 保存失败 (HTTP 500 错误) ✅

**用户反馈**: 
- 新增文章时能正常输入、上传图片、控制大小位置
- 但点击保存时弹窗报错: "保存失败: internal server error"

**根本原因**:
- `ArticleService.create_article()` 使用 `model_dump()` 导出所有字段
- 当包含 ORM model 中不支持的字段时，构造函数会出错
- 特别是 `category_id` 等特殊字段处理不当

**修复方案**:
- 修改 `backend/app/services/article_service.py`
- 将 `Article()` 构造函数改为**逐个字段赋值**而非 `**dict` 展开
- `ArticleService.create_article()` 中各字段显式赋值
- `ArticleService.update_article()` 中添加字段存在性检查

**修复前后对比**:
```python
# 修复前 (出错)
article_dict = article_data.model_dump(exclude={'platform_id', 'section_id'})
article = Article(**article_dict, slug=slug, author_id=author_id, ...)

# 修复后 (正确)
article = Article(
    title=article_data.title,
    content=article_data.content,
    summary=article_data.summary,
    category=article_data.category,
    category_id=article_data.category_id,
    tags=article_data.tags,
    ...
)
```

**测试结果**: ✅ 文章创建成功

---

### 2. 平台管理 - 编辑页面字段显示问题 ✅

**用户反馈**:
- 编辑已有平台时，以下字段只有标题没有输入框:
  - 为什么选择该平台
  - 交易条件和费用
  - 账户类型
  - 工具和开户
  - 安全和支持
  - 平台徽章和标签
  - 学习资源
- 新增平台时没有这个问题

**根本原因**:
- 这些是 JSON 类型的字段，数据库中存储为 `NULL`
- API 返回 `null` 时，前端可能不会为 `null` 值渲染输入框
- 新增时有默认值，所以正常显示

**修复方案**:
- 修改 `backend/app/schemas/platform_admin.py`
- 在 `PlatformEditResponse` 中添加 `@root_validator`
- 将所有为 `None` 的 JSON 字段转换为**空字符串** `""`

**修复代码**:
```python
@root_validator(pre=False, skip_on_failure=True)
def convert_null_json_fields_to_empty_strings(cls, values):
    """将所有为 None 的 JSON 字段转换为空字符串"""
    json_fields = [
        'main_features', 'fee_structure', 'why_choose', 
        'trading_conditions', 'account_types', 'trading_tools',
        'security_measures', 'platform_badges', 'learning_resources', ...
    ]
    
    for field in json_fields:
        if values.get(field) is None:
            values[field] = ""  # 转换为空字符串
    
    return values
```

**测试结果**: ✅ 编辑页面所有字段都正常显示输入框

---

### 3. AI 配置管理 - 两个问题 ✅

#### 问题 3a: max_tokens 配额太小

**用户反馈**: max_tokens 2000 是否太少了？

**修复方案**:
- 修改 `backend/app/models/ai_config.py`
- max_tokens 默认值从 **2000** 提高到 **8000**
- 更新现有数据库中所有 AI 配置的 max_tokens 值

**修复代码**:
```python
# 模型中的默认值
max_tokens = Column(Integer, default=8000, nullable=False)

# 数据库迁移
UPDATE ai_configs SET max_tokens = 8000;
```

**现有配置的 max_tokens 值**:
- OpenAI GPT-4: 2000 → **8000** ✅
- DeepSeek: 2000 → **8000** ✅
- OpenAI 中转链接: 2000 → **8000** ✅

#### 问题 3b: 已有配置编辑时显示"编辑功能正在开发中"

**用户反馈**: 无法编辑已有的 AI 配置

**根本原因**:
- 前端 HTML 中 `editAIConfig()` 函数只有一个 alert 提示
- 实际的编辑逻辑和提交功能都没有实现

**修复方案**:
- 修改 `backend/site/admin/index.html`
- 实现完整的 `editAIConfig(configId)` 函数
- 添加 `saveAIConfig(event, configId)` 函数

**实现功能**:
1. 获取指定 AI 配置的详情
2. 创建编辑模态框动态 DOM
3. 填充现有配置值到表单
4. 提交更新到后端 API (`PUT /api/ai-configs/{id}`)
5. 刷新列表显示

**编辑页面支持字段**:
- 模型名称 (model_name)
- API 端点 (api_endpoint)
- API 密钥 (api_key) - 可选，不填时保持原值
- 最大令牌数 (max_tokens)
- 温度 (temperature)
- Top P 采样 (top_p)
- 超时时间 (timeout_seconds)
- 是否激活 (is_active)

**前端实现注意点**:
- 使用动态模态框（不污染 HTML）
- 密钥字段为 password 类型保护隐私
- API 密钥为空时不发送（保留现有值）
- 成功后自动刷新列表

**测试结果**: ✅ AI 配置编辑功能正常工作

---

## 测试清单

| 功能 | 测试场景 | 状态 |
|------|--------|------|
| 文章创建 | 新增文章并保存 | ✅ |
| 文章更新 | 编辑已有文章 | ✅ |
| 平台编辑 | 编辑平台显示所有字段 | ✅ |
| 平台编辑 | JSON 字段可编辑 | ✅ |
| AI 配置列表 | 显示 max_tokens=8000 | ✅ |
| AI 配置编辑 | 打开编辑对话框 | ✅ |
| AI 配置编辑 | 修改参数并保存 | ✅ |
| AI 配置编辑 | 密钥字段保护 | ✅ |

---

## 文件修改清单

### 后端文件

1. **backend/app/services/article_service.py**
   - 修改: `create_article()` 方法
   - 修改: `update_article()` 方法
   - 改进: 逐个字段赋值，避免 model_dump() 问题

2. **backend/app/schemas/platform_admin.py**
   - 修改: `PlatformEditResponse` 类
   - 添加: `@root_validator` 装饰器
   - 功能: NULL JSON 字段转换为空字符串

3. **backend/app/models/ai_config.py**
   - 修改: `max_tokens` 默认值 (2000 → 8000)
   - 修改: 数据库中所有配置的 max_tokens 值

### 前端文件

1. **backend/site/admin/index.html**
   - 修改: `editAIConfig(configId)` 函数
   - 添加: `saveAIConfig(event, configId)` 函数
   - 功能: 完整的 AI 配置编辑界面和逻辑

---

## 部署指南

### 本地更新

```bash
cd /Users/ck/Desktop/Project/trustagency

# 拉取最新代码
git pull

# 重启后端
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 数据库更新

已自动完成，无需手动操作：
- max_tokens 已更新到 8000
- 平台编辑时 NULL 字段动态转换

---

## 验证命令

```bash
# 1. 测试文章创建
curl -X POST http://localhost:8001/api/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试","content":"内容","section_id":1,"category_id":1}'

# 2. 测试平台编辑数据
curl http://localhost:8001/api/admin/platforms/1/edit \
  -H "Authorization: Bearer $TOKEN"

# 3. 测试 AI 配置
curl http://localhost:8001/api/ai-configs
```

---

## 总结

✅ **所有 3 个 bug 均已修复:**

1. ✅ 文章保存 500 错误 → 正常保存
2. ✅ 平台编辑字段显示问题 → 所有字段正常显示
3. ✅ AI 配置编辑功能 → 完全实现
4. ✅ max_tokens 提高到 8000 → 支持更长的输出

**项目状态**: 准备就绪，可进行用户验收测试

