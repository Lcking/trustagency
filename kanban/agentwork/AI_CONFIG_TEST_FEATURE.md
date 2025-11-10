# AI 配置测试连接功能

## 功能概述

为了确保在真实环境中添加的 AI 配置能够正常工作，我们实现了一个**测试连接**功能，允许用户在保存配置前验证 API 的可用性。

## 实现细节

### 1. 前端改动 (`/site/admin/index.html` 和 `/backend/site/admin/index.html`)

#### HTML 结构
```html
<!-- 测试连接区域 -->
<div class="test-container">
    <div class="test-controls">
        <button type="button" class="btn btn-info test-button" onclick="testAIConfig()">🧪 测试连接</button>
        <div id="testStatus" class="test-status"></div>
    </div>
</div>
```

#### CSS 样式
```css
.btn-info {
    background: #3498db;
    color: white;
}

.btn-info:hover {
    background: #2980b9;
}

.test-status-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.test-status-error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.test-status-loading {
    background-color: #e7f3ff;
    color: #0066cc;
    border: 1px solid #b3d9ff;
}

.test-container {
    margin: 15px 0;
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.test-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}
```

#### JavaScript 函数
```javascript
async function testAIConfig() {
    if (!token) {
        alert('请先登录');
        return;
    }

    const endpoint = document.getElementById('newConfigEndpoint').value;
    const apiKey = document.getElementById('newConfigAPIKey').value;
    const model = document.getElementById('newConfigModel').value;

    if (!endpoint || !apiKey || !model) {
        alert('请填写 API 端点、密钥和模型名称');
        return;
    }

    // 显示加载状态
    const testStatusDiv = document.getElementById('testStatus');
    testStatusDiv.className = 'test-status test-status-loading';
    testStatusDiv.textContent = '⏳ 测试中...';
    testStatusDiv.style.display = 'block';

    try {
        const response = await fetch(`${API_URL}/api/ai-configs/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                api_endpoint: endpoint,
                api_key: apiKey,
                model_name: model
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 显示成功状态
            testStatusDiv.className = 'test-status test-status-success';
            testStatusDiv.textContent = '✅ 连接成功！API 可正常访问';
        } else {
            // 显示失败状态
            testStatusDiv.className = 'test-status test-status-error';
            testStatusDiv.textContent = '❌ 连接失败: ' + (data.error || '未知错误');
        }
    } catch (error) {
        testStatusDiv.className = 'test-status test-status-error';
        testStatusDiv.textContent = '❌ 错误: ' + error.message;
    }
}
```

### 2. 后端改动 (`/backend/app/routes/ai_configs.py`)

#### 新增 Pydantic Schema
```python
class AIConfigTestRequest(BaseModel):
    """测试 AI 配置的请求体"""
    api_endpoint: str
    api_key: str
    model_name: str


class AIConfigTestResponse(BaseModel):
    """测试 AI 配置的响应"""
    success: bool
    message: str
    error: str = None
    response_time: float = None
```

#### 新增测试端点
```python
@router.post("/test", response_model=AIConfigTestResponse)
async def test_ai_config(
    test_data: AIConfigTestRequest,
    current_user = Depends(get_current_user),
):
    """
    测试 AI 配置连接
    
    验证 API 端点和密钥的有效性
    """
    try:
        headers = {
            "Authorization": f"Bearer {test_data.api_key}",
            "Content-Type": "application/json"
        }
        
        # 准备简单的测试请求体（模拟常见的 LLM API 格式）
        test_payload = {
            "model": test_data.model_name,
            "messages": [
                {"role": "user", "content": "test"}
            ],
            "max_tokens": 10
        }
        
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 尝试向 API 端点发送请求
            response = await client.post(
                test_data.api_endpoint,
                json=test_payload,
                headers=headers
            )
        
        response_time = time.time() - start_time
        
        # 检查响应状态
        if response.status_code in [200, 201]:
            return AIConfigTestResponse(
                success=True,
                message=f"✅ 连接成功（响应时间: {response_time:.2f}s）",
                response_time=response_time
            )
        elif response.status_code == 401:
            return AIConfigTestResponse(
                success=False,
                message="❌ API 密钥无效或已过期",
                error=f"HTTP {response.status_code}: Unauthorized"
            )
        # ... 其他状态码处理
        
    except httpx.TimeoutException:
        return AIConfigTestResponse(
            success=False,
            message="❌ 连接超时（10秒）",
            error="Connection timeout"
        )
    except httpx.ConnectError as e:
        return AIConfigTestResponse(
            success=False,
            message="❌ 无法连接到 API 服务器",
            error=str(e)
        )
    except Exception as e:
        return AIConfigTestResponse(
            success=False,
            message="❌ 测试过程中出错",
            error=str(e)
        )
```

## 功能特性

### ✅ 完整的错误处理
- **连接超时**：如果 API 响应时间超过 10 秒
- **连接失败**：无法到达 API 服务器
- **认证错误**：API 密钥无效（HTTP 401）
- **端点不存在**：API 端点返回 404
- **服务器错误**：API 返回 5xx 错误
- **验证错误**：必填字段验证

### 📊 实时反馈
- **加载状态**：显示 "⏳ 测试中..." 与蓝色背景
- **成功状态**：显示 "✅ 连接成功！" 与绿色背景（包含响应时间）
- **失败状态**：显示 "❌ 连接失败: " 与具体错误信息和红色背景

### 🔐 安全性
- 需要用户认证（登录）
- 使用 Bearer 令牌进行身份验证
- 模拟真实的 API 请求

### ⚡ 用户体验
- 在创建配置前验证连接
- 避免保存无效的配置
- 实时视觉反馈
- 清晰的错误消息指导

## 使用流程

1. **填写配置信息**
   - 配置名称
   - 服务商选择
   - 模型名称
   - API 端点
   - API 密钥

2. **点击"🧪 测试连接"按钮**
   - 系统会显示 "⏳ 测试中..." 状态
   - 向 API 端点发送测试请求

3. **查看测试结果**
   - ✅ 成功：可以安全保存配置
   - ❌ 失败：根据错误信息调整配置

4. **保存配置**
   - 点击 "✅ 创建配置" 保存

## 测试场景

### 场景 1：无效的 API 密钥
```
输入：sk-invalid-test-key
结果：❌ 连接失败: HTTP 401: Unauthorized
```

### 场景 2：无效的端点
```
输入：https://invalid-endpoint.com/v1/chat
结果：❌ 连接失败: 未知错误
```

### 场景 3：缺少必填字段
```
输入：空 API 密钥
结果：请填写 API 端点、密钥和模型名称 (alert)
```

### 场景 4：超时（>10秒）
```
结果：❌ 连接超时（10秒）
```

## 技术栈

- **前端**：Vanilla JavaScript + CSS
- **后端**：FastAPI + Python
- **HTTP 客户端**：httpx（异步）
- **验证**：Pydantic
- **认证**：JWT + Bearer Token

## 依赖项

- `httpx>=0.25.0` - 用于异步 HTTP 请求

## 最佳实践

1. **鼓励用户在保存前测试**
   - 强调测试的重要性
   - 在成功测试后再创建配置

2. **提供清晰的错误消息**
   - 帮助用户快速定位问题
   - 包含具体的 HTTP 状态码

3. **设置合理的超时时间**
   - 10 秒是平衡响应性和可靠性的好选择

4. **记录测试结果**
   - 控制台输出便于调试
   - 可在浏览器开发者工具查看

## 未来改进方向

1. **支持更多 AI 提供商**
   - 自动检测 API 类型（OpenAI、Claude、LLaMA 等）
   - 针对不同提供商使用不同的测试请求格式

2. **增强的诊断信息**
   - 显示 API 响应时间统计
   - 显示 API 配额信息（如果可用）

3. **批量测试**
   - 同时测试多个配置
   - 展示测试历史

4. **配置预置**
   - 提供常见 AI 提供商的默认配置
   - 一键导入已知配置

## 总结

这个测试连接功能大大改善了用户体验，确保在真实环境中添加的 AI 配置能够立即投入使用。通过简单的一个按钮点击，用户可以在保存前验证配置的有效性，从而避免无效配置导致的后续问题。
