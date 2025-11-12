# API 错误代码参考

**版本**: 1.0.0  
**最后更新**: 2025-11-12

---

## 🔍 快速查询

| HTTP 状态码 | 错误类型 | 常见原因 | 解决方案 |
|-----------|---------|--------|--------|
| 400 | VALIDATION_ERROR | 请求参数不合法 | 检查参数格式和类型 |
| 401 | UNAUTHORIZED | 未登录或 token 过期 | 重新登录获取 token |
| 403 | FORBIDDEN | 权限不足 | 使用有权限的账户 |
| 404 | NOT_FOUND | 资源不存在 | 检查资源 ID |
| 409 | CONFLICT | 资源冲突（如重复数据） | 修改冲突的字段 |
| 422 | BUSINESS_ERROR | 业务规则错误 | 检查业务逻辑 |
| 500 | INTERNAL_ERROR | 服务器错误 | 稍后重试或联系支持 |

---

## 📚 详细错误代码

### 验证错误 (400 Bad Request)

这类错误表示请求的参数或数据格式不合法。

#### VALIDATION_ERROR
- **含义**: 请求数据验证失败
- **HTTP 状态码**: 400
- **常见原因**:
  - 必需字段缺失
  - 字段类型错误
  - 字段值超出范围
  
**示例响应**:
```json
{
  "detail": "1 validation error for Request body",
  "error_code": "VALIDATION_ERROR",
  "status_code": 400,
  "errors": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**处理方式**:
```javascript
catch (error) {
  if (error.status === 400) {
    // 提取字段错误
    const fieldErrors = error.data?.errors || [];
    fieldErrors.forEach(err => {
      const field = err.loc[err.loc.length - 1];
      showFieldError(field, err.msg);
    });
  }
}
```

#### INVALID_PARAMETER
- **含义**: 参数值无效
- **HTTP 状态码**: 400
- **常见原因**:
  - 参数类型错误
  - 参数值超出允许范围
  - 参数值格式不正确

**示例**:
```
GET /api/articles?limit=abc

响应:
{
  "detail": "Invalid parameter: limit must be an integer",
  "error_code": "INVALID_PARAMETER",
  "status_code": 400
}
```

#### MISSING_PARAMETER
- **含义**: 必需参数缺失
- **HTTP 状态码**: 400
- **常见原因**:
  - 在请求体中没有提供必需字段
  - 在 URL 路径中缺少参数

**示例**:
```
POST /api/articles
(缺少 title 字段)

响应:
{
  "detail": "Missing required parameter: title",
  "error_code": "MISSING_PARAMETER",
  "status_code": 400
}
```

#### INVALID_FORMAT
- **含义**: 参数格式不正确
- **HTTP 状态码**: 400
- **常见原因**:
  - 日期格式不对
  - Email 格式不对
  - URL 格式不对

**示例**:
```
POST /api/articles
{
  "title": "My Article",
  "created_at": "2025-13-45"  // 无效日期
}

响应:
{
  "detail": "Invalid date format, expected: YYYY-MM-DD",
  "error_code": "INVALID_FORMAT",
  "status_code": 400
}
```

---

### 认证错误 (401 Unauthorized)

这类错误表示用户未认证或认证失败。

#### UNAUTHORIZED
- **含义**: 未认证或认证失败
- **HTTP 状态码**: 401
- **常见原因**:
  - 没有提供 token
  - token 格式错误
  - 用户凭证无效

**示例**:
```
GET /api/articles (不带 Authorization header)

响应:
{
  "detail": "Not authenticated",
  "error_code": "UNAUTHORIZED",
  "status_code": 401
}
```

**处理方式**:
```javascript
catch (error) {
  if (error.status === 401) {
    // 清除 token 并重定向到登录
    apiClient.clearToken();
    window.location.href = '/login';
    showToast('登录已过期，请重新登录');
  }
}
```

#### TOKEN_EXPIRED
- **含义**: Token 已过期
- **HTTP 状态码**: 401
- **常见原因**:
  - token 使用时间超过 24 小时
  - 用户长时间未操作

**示例**:
```json
{
  "detail": "Token expired",
  "error_code": "TOKEN_EXPIRED",
  "status_code": 401
}
```

#### INVALID_TOKEN
- **含义**: Token 无效或被篡改
- **HTTP 状态码**: 401
- **常见原因**:
  - token 格式不对
  - token 签名无效
  - token 被篡改

**示例**:
```json
{
  "detail": "Invalid token",
  "error_code": "INVALID_TOKEN",
  "status_code": 401
}
```

#### CREDENTIALS_INVALID
- **含义**: 凭证不匹配
- **HTTP 状态码**: 401
- **常见原因**:
  - 用户名或密码错误
  - 账户被禁用

**示例**:
```
POST /api/auth/login
{
  "username": "admin",
  "password": "wrong_password"
}

响应:
{
  "detail": "Invalid credentials",
  "error_code": "CREDENTIALS_INVALID",
  "status_code": 401
}
```

---

### 授权错误 (403 Forbidden)

这类错误表示用户虽然已认证，但权限不足。

#### FORBIDDEN
- **含义**: 禁止访问此资源
- **HTTP 状态码**: 403
- **常见原因**:
  - 用户没有访问此资源的权限
  - 资源为私有或受限

**示例**:
```json
{
  "detail": "Access forbidden",
  "error_code": "FORBIDDEN",
  "status_code": 403
}
```

#### PERMISSION_DENIED
- **含义**: 权限不足
- **HTTP 状态码**: 403
- **常见原因**:
  - 用户不是管理员
  - 用户没有删除权限

**示例**:
```
DELETE /api/articles/1 (普通用户)

响应:
{
  "detail": "Only administrators can delete articles",
  "error_code": "PERMISSION_DENIED",
  "status_code": 403
}
```

#### INSUFFICIENT_PRIVILEGES
- **含义**: 权限等级不足
- **HTTP 状态码**: 403
- **常见原因**:
  - 操作需要更高的权限等级
  - 用户等级不符合要求

**示例**:
```json
{
  "detail": "Superadmin privileges required",
  "error_code": "INSUFFICIENT_PRIVILEGES",
  "status_code": 403
}
```

---

### 资源错误 (404 Not Found)

这类错误表示请求的资源不存在。

#### NOT_FOUND
- **含义**: 资源不存在
- **HTTP 状态码**: 404
- **常见原因**:
  - 资源已被删除
  - 资源 ID 不存在

**示例**:
```
GET /api/articles/99999

响应:
{
  "detail": "Article not found",
  "error_code": "NOT_FOUND",
  "status_code": 404
}
```

#### RESOURCE_NOT_FOUND
- **含义**: 指定的资源未找到
- **HTTP 状态码**: 404
- **常见原因**:
  - 关联的资源不存在

**示例**:
```
GET /api/articles?category_id=999

响应:
{
  "detail": "Category (ID: 999) not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "status_code": 404
}
```

---

### 冲突错误 (409 Conflict)

这类错误表示请求与现有资源产生冲突。

#### CONFLICT
- **含义**: 资源冲突
- **HTTP 状态码**: 409
- **常见原因**:
  - 资源已存在（重复创建）
  - 并发修改导致冲突

**示例**:
```json
{
  "detail": "Resource conflict",
  "error_code": "CONFLICT",
  "status_code": 409
}
```

#### DUPLICATE_ENTRY
- **含义**: 重复条目
- **HTTP 状态码**: 409
- **常见原因**:
  - 某个唯一字段已存在
  - 尝试创建重复的资源

**示例**:
```
POST /api/articles
{
  "slug": "existing-article"  // 这个 slug 已存在
}

响应:
{
  "detail": "Article with slug 'existing-article' already exists",
  "error_code": "DUPLICATE_ENTRY",
  "status_code": 409
}
```

**处理方式**:
```javascript
catch (error) {
  if (error.status === 409 && error.code === 'DUPLICATE_ENTRY') {
    showErrorToast('已存在相同的内容，请检查');
    // 可以提示用户修改冲突字段
  }
}
```

#### RESOURCE_EXISTS
- **含义**: 资源已存在
- **HTTP 状态码**: 409
- **常见原因**:
  - 资源已存在

**示例**:
```json
{
  "detail": "Category already exists",
  "error_code": "RESOURCE_EXISTS",
  "status_code": 409
}
```

---

### 业务逻辑错误 (422 Unprocessable Entity)

这类错误表示请求虽然格式正确，但违反了业务规则。

#### BUSINESS_ERROR
- **含义**: 业务逻辑错误
- **HTTP 状态码**: 422
- **常见原因**:
  - 操作违反业务规则
  - 数据状态不允许此操作

**示例**:
```
PATCH /api/articles/1/publish
(文章缺少必要字段)

响应:
{
  "detail": "Cannot publish article without content",
  "error_code": "BUSINESS_ERROR",
  "status_code": 422
}
```

#### INVALID_STATE
- **含义**: 状态无效
- **HTTP 状态码**: 422
- **常见原因**:
  - 资源处于不允许该操作的状态

**示例**:
```
PATCH /api/articles/1/publish
(文章已发布)

响应:
{
  "detail": "Article is already published",
  "error_code": "INVALID_STATE",
  "status_code": 422
}
```

#### OPERATION_NOT_ALLOWED
- **含义**: 操作不允许
- **HTTP 状态码**: 422
- **常见原因**:
  - 当前状态下不允许此操作
  - 资源被锁定或受限

**示例**:
```
DELETE /api/articles/1
(文章已发布，不能直接删除)

响应:
{
  "detail": "Cannot delete published articles",
  "error_code": "OPERATION_NOT_ALLOWED",
  "status_code": 422
}
```

---

### 服务器错误 (500 Internal Server Error)

这类错误表示服务器发生错误。

#### INTERNAL_ERROR
- **含义**: 服务器内部错误
- **HTTP 状态码**: 500
- **常见原因**:
  - 未预期的异常
  - 代码 bug

**示例**:
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "status_code": 500
}
```

**处理方式**:
```javascript
catch (error) {
  if (error.status === 500) {
    showErrorToast('服务器错误，请稍后重试');
    // 可以上报错误到监控系统
    reportError(error);
  }
}
```

#### DATABASE_ERROR
- **含义**: 数据库操作失败
- **HTTP 状态码**: 500
- **常见原因**:
  - 数据库连接断开
  - 数据库查询失败

**示例**:
```json
{
  "detail": "Database error",
  "error_code": "DATABASE_ERROR",
  "status_code": 500
}
```

#### EXTERNAL_SERVICE_ERROR
- **含义**: 外部服务错误
- **HTTP 状态码**: 500
- **常见原因**:
  - 第三方 API 不可用
  - 外部服务超时

**示例**:
```json
{
  "detail": "External AI service is unavailable",
  "error_code": "EXTERNAL_SERVICE_ERROR",
  "status_code": 500
}
```

---

## 🛠️ 前端处理示例

### 通用错误处理

```javascript
/**
 * 根据错误类型显示用户友好的消息
 */
function handleAPIError(error) {
  const errorMessages = {
    VALIDATION_ERROR: '请求参数有误，请检查后重试',
    UNAUTHORIZED: '登录已过期，请重新登录',
    FORBIDDEN: '您没有权限执行此操作',
    NOT_FOUND: '请求的资源不存在',
    RESOURCE_NOT_FOUND: '资源不存在',
    DUPLICATE_ENTRY: '已存在相同的内容',
    RESOURCE_EXISTS: '资源已存在',
    CONFLICT: '操作冲突，请稍后重试',
    INVALID_STATE: '当前状态不支持此操作',
    OPERATION_NOT_ALLOWED: '不允许执行此操作',
    BUSINESS_ERROR: error.message || '操作失败',
    INTERNAL_ERROR: '服务器错误，请稍后重试',
    DATABASE_ERROR: '数据库错误，请稍后重试',
    EXTERNAL_SERVICE_ERROR: '外部服务暂时不可用',
  };
  
  const message = errorMessages[error.code] || error.message || '请求失败';
  
  return {
    message,
    severity: error.status >= 500 ? 'error' : 'warning',
  };
}

// 使用
try {
  await api.articles.create(data);
} catch (error) {
  const { message, severity } = handleAPIError(error);
  showToast(message, severity);
}
```

### 字段级错误处理

```javascript
/**
 * 处理验证错误并显示字段错误
 */
function handleValidationError(error) {
  if (error.status !== 400 || error.code !== 'VALIDATION_ERROR') {
    return;
  }
  
  const fieldErrors = {};
  const errors = error.data?.errors || [];
  
  errors.forEach(err => {
    const field = err.loc[err.loc.length - 1];
    fieldErrors[field] = err.msg;
  });
  
  return fieldErrors;
}

// 在表单中使用
async function handleSubmit(formData) {
  try {
    await api.articles.create(formData);
    showSuccessToast('创建成功');
  } catch (error) {
    const fieldErrors = handleValidationError(error);
    if (fieldErrors) {
      form.setErrors(fieldErrors);
    } else {
      const { message } = handleAPIError(error);
      showErrorToast(message);
    }
  }
}
```

---

## 📊 错误统计

| 分类 | 个数 | 说明 |
|-----|------|------|
| 验证错误 | 4 | 请求参数相关 |
| 认证错误 | 4 | 登录和 token 相关 |
| 授权错误 | 3 | 权限相关 |
| 资源错误 | 2 | 资源不存在 |
| 冲突错误 | 3 | 数据重复或冲突 |
| 业务错误 | 3 | 业务规则违反 |
| 服务器错误 | 3 | 服务器端问题 |
| **总计** | **22** | |

---

## 🔗 相关资源

- [API 使用指南](./API_GUIDE.md)
- [API 审计报告](./API_AUDIT.md)
- [前端调用规范](./FRONTEND_API_SPEC.md)

---

**版本**: 1.0.0  
**最后更新**: 2025-11-12
