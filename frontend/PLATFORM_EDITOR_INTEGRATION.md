# 前端集成指南 - 平台管理编辑界面

## 概述

本文档指导如何在前端管理系统中集成平台编辑功能。

---

## API 端点

### 1. 获取表单定义
用于动态生成编辑表单的UI元素。

```
GET /api/admin/platforms/form-definition
```

**响应示例：**
```json
{
  "sections": [
    {
      "title": "基础信息",
      "fields": [
        {
          "name": "name",
          "label": "平台名称",
          "type": "text",
          "required": true,
          "placeholder": "例: AlphaLeverage"
        },
        {
          "name": "slug",
          "label": "URL标识",
          "type": "text",
          "required": true,
          "placeholder": "例: alphaleverage"
        }
      ]
    },
    {
      "title": "为什么选择该平台",
      "fields": [
        {
          "name": "why_choose",
          "label": "为什么选择 (JSON)",
          "type": "json",
          "placeholder": "[{\"icon\":\"📚\",\"title\":\"...\",\"description\":\"...\"}]"
        }
      ]
    }
  ]
}
```

### 2. 获取平台列表（管理界面）

```
GET /api/admin/platforms/edit-list?skip=0&limit=100
```

**响应示例：**
```json
{
  "items": [
    {
      "id": 1,
      "name": "AlphaLeverage",
      "slug": "alpha-leverage",
      "rating": 4.8,
      "rank": 1,
      "platform_type": "专业",
      "is_active": true,
      "is_recommended": true,
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 3
}
```

### 3. 获取平台编辑表单数据

```
GET /api/admin/platforms/{platform_id}/edit
```

**响应示例：**
```json
{
  "id": 1,
  "name": "AlphaLeverage",
  "slug": "alpha-leverage",
  "description": "...",
  "rating": 4.8,
  "rank": 1,
  "why_choose": "[{\"icon\":\"📈\",\"title\":\"...\"}]",
  "account_types": "[{\"name\":\"基础\",\"leverage\":\"1:100\"}]",
  "fee_table": "[{\"type\":\"交易手续费\",\"basic\":\"0.20%\"}]",
  "trading_tools": "[{\"title\":\"图表\",\"description\":\"...\"}]",
  "opening_steps": "[{\"step_number\":1,\"title\":\"...\"}]",
  "safety_info": "[\"✓ 安全措施...\"]",
  "learning_resources": "[{\"title\":\"...\",\"link\":\"/...\"}]",
  "top_badges": "[\"推荐平台\",\"专业级\"]",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 4. 更新平台编辑表单数据

```
POST /api/admin/platforms/{platform_id}/edit
Content-Type: application/json

{
  "name": "AlphaLeverage",
  "description": "新的描述",
  "why_choose": "[{...}]",
  "account_types": "[{...}]",
  // 其他字段...
}
```

---

## 前端实现示例

### Vue 3 组件示例

```vue
<template>
  <div class="platform-editor">
    <!-- 平台列表 -->
    <div class="platform-list" v-if="!selectedPlatform">
      <h2>选择要编辑的平台</h2>
      <div class="platforms">
        <div
          v-for="platform in platforms"
          :key="platform.id"
          class="platform-card"
          @click="selectPlatform(platform.id)"
        >
          <h3>{{ platform.name }}</h3>
          <p>{{ platform.slug }}</p>
          <span class="rating">⭐ {{ platform.rating }}</span>
        </div>
      </div>
    </div>

    <!-- 编辑表单 -->
    <form v-if="selectedPlatform" @submit.prevent="savePlatform">
      <button type="button" @click="goBack" class="back-btn">← 返回</button>

      <h2>编辑: {{ selectedPlatform.name }}</h2>

      <!-- 动态表单部分 -->
      <div v-for="section in formSections" :key="section.title" class="form-section">
        <h3>{{ section.title }}</h3>

        <!-- 表单字段 -->
        <div v-for="field in section.fields" :key="field.name" class="form-group">
          <label :for="field.name">{{ field.label }}</label>

          <!-- 文本输入 -->
          <input
            v-if="field.type === 'text'"
            :id="field.name"
            v-model="formData[field.name]"
            type="text"
            :placeholder="field.placeholder"
            :required="field.required"
          />

          <!-- 文本域 -->
          <textarea
            v-else-if="field.type === 'textarea'"
            :id="field.name"
            v-model="formData[field.name]"
            :placeholder="field.placeholder"
            rows="4"
          ></textarea>

          <!-- JSON 编辑器 -->
          <div v-else-if="field.type === 'json'" class="json-editor">
            <textarea
              :id="field.name"
              v-model="formData[field.name]"
              :placeholder="field.placeholder"
              rows="6"
              class="json-input"
            ></textarea>
            <button
              type="button"
              @click="formatJson(field.name)"
              class="format-btn"
            >
              格式化 JSON
            </button>
          </div>

          <!-- 数字输入 -->
          <input
            v-else-if="field.type === 'number'"
            :id="field.name"
            v-model.number="formData[field.name]"
            type="number"
            :placeholder="field.placeholder"
          />

          <!-- 选择框 -->
          <select
            v-else-if="field.type === 'select'"
            :id="field.name"
            v-model="formData[field.name]"
          >
            <option value="">请选择</option>
            <option
              v-for="opt in field.options"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </select>

          <!-- 复选框 -->
          <input
            v-else-if="field.type === 'boolean'"
            :id="field.name"
            v-model="formData[field.name]"
            type="checkbox"
          />
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <button type="submit" class="save-btn">保存更改</button>
        <button type="button" @click="goBack" class="cancel-btn">取消</button>
      </div>
    </form>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 成功提示 -->
    <div v-if="success" class="success-message">
      保存成功！
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const API_BASE = 'http://localhost:8001/api';

// 数据
const platforms = ref([]);
const selectedPlatform = ref(null);
const formData = ref({});
const formSections = ref([]);
const error = ref('');
const success = ref('');

// 获取平台列表
const loadPlatforms = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/platforms/edit-list`);
    platforms.value = response.data.items;
  } catch (e) {
    error.value = '加载平台列表失败';
  }
};

// 获取表单定义
const loadFormDefinition = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/platforms/form-definition`);
    formSections.value = response.data.sections;
  } catch (e) {
    error.value = '加载表单定义失败';
  }
};

// 选择平台
const selectPlatform = async (platformId: number) => {
  try {
    const response = await axios.get(`${API_BASE}/admin/platforms/${platformId}/edit`);
    selectedPlatform.value = response.data;
    formData.value = { ...response.data };
  } catch (e) {
    error.value = '加载平台数据失败';
  }
};

// 保存平台
const savePlatform = async () => {
  try {
    await axios.post(
      `${API_BASE}/admin/platforms/${selectedPlatform.value.id}/edit`,
      formData.value
    );
    success.value = true;
    setTimeout(() => (success.value = false), 3000);
  } catch (e) {
    error.value = '保存失败: ' + (e.response?.data?.detail || e.message);
  }
};

// 返回
const goBack = () => {
  selectedPlatform.value = null;
  formData.value = {};
};

// 格式化 JSON
const formatJson = (fieldName: string) => {
  try {
    const value = formData.value[fieldName];
    if (typeof value === 'string') {
      const parsed = JSON.parse(value);
      formData.value[fieldName] = JSON.stringify(parsed, null, 2);
    }
  } catch {
    error.value = 'JSON 格式不正确';
  }
};

// 初始化
onMounted(() => {
  loadPlatforms();
  loadFormDefinition();
});
</script>

<style scoped>
.platform-editor {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.platform-list {
  padding: 20px;
}

.platforms {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.platform-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.platform-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.2);
}

.platform-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.platform-card p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.rating {
  display: inline-block;
  margin-top: 10px;
  background: #fff3cd;
  padding: 4px 8px;
  border-radius: 4px;
}

form {
  background: #f9f9f9;
  padding: 30px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.back-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
}

.back-btn:hover {
  background: #5a6268;
}

.form-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.form-section h3 {
  margin-top: 0;
  color: #333;
  border-left: 4px solid #007bff;
  padding-left: 10px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

input,
textarea,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.json-editor {
  position: relative;
}

.json-input {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.format-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #007bff;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.format-btn:hover {
  background: #0056b3;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.save-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.save-btn:hover {
  background: #218838;
}

.cancel-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #5a6268;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 20px;
  border: 1px solid #f5c6cb;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 20px;
  border: 1px solid #c3e6cb;
}
</style>
```

---

## React 组件示例

```tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8001/api';

export const PlatformEditor: React.FC = () => {
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [formData, setFormData] = useState({});
  const [formSections, setFormSections] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // 加载平台列表
  useEffect(() => {
    const loadData = async () => {
      try {
        const [platformsRes, definitionRes] = await Promise.all([
          axios.get(`${API_BASE}/admin/platforms/edit-list`),
          axios.get(`${API_BASE}/admin/platforms/form-definition`),
        ]);
        setPlatforms(platformsRes.data.items);
        setFormSections(definitionRes.data.sections);
      } catch (e) {
        setError('加载数据失败');
      }
    };
    loadData();
  }, []);

  // 选择平台
  const handleSelectPlatform = async (platformId: number) => {
    try {
      const response = await axios.get(
        `${API_BASE}/admin/platforms/${platformId}/edit`
      );
      setSelectedPlatform(response.data);
      setFormData(response.data);
    } catch (e) {
      setError('加载平台数据失败');
    }
  };

  // 处理表单变化
  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));
  };

  // 保存
  const handleSave = async () => {
    try {
      await axios.post(
        `${API_BASE}/admin/platforms/${selectedPlatform.id}/edit`,
        formData
      );
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
      setError('保存失败');
    }
  };

  // 返回
  const handleGoBack = () => {
    setSelectedPlatform(null);
    setFormData({});
  };

  if (!selectedPlatform) {
    return (
      <div className="platform-list">
        <h2>选择要编辑的平台</h2>
        <div className="platforms-grid">
          {platforms.map((platform) => (
            <div
              key={platform.id}
              className="platform-card"
              onClick={() => handleSelectPlatform(platform.id)}
            >
              <h3>{platform.name}</h3>
              <p>{platform.slug}</p>
              <span>⭐ {platform.rating}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="platform-editor">
      <button onClick={handleGoBack} className="back-btn">
        ← 返回
      </button>

      <h2>编辑: {selectedPlatform.name}</h2>

      {formSections.map((section) => (
        <div key={section.title} className="form-section">
          <h3>{section.title}</h3>
          {section.fields.map((field) => (
            <div key={field.name} className="form-group">
              <label htmlFor={field.name}>{field.label}</label>
              {field.type === 'text' && (
                <input
                  id={field.name}
                  type="text"
                  value={formData[field.name] || ''}
                  onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                />
              )}
              {field.type === 'json' && (
                <textarea
                  id={field.name}
                  value={formData[field.name] || ''}
                  onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  rows={6}
                />
              )}
              {/* 其他字段类型... */}
            </div>
          ))}
        </div>
      ))}

      <div className="form-actions">
        <button onClick={handleSave} className="save-btn">
          保存更改
        </button>
        <button onClick={handleGoBack} className="cancel-btn">
          取消
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">保存成功！</div>}
    </div>
  );
};
```

---

## 字段类型处理指南

### 1. JSON 字段编辑

**why_choose 编辑器示例：**

```javascript
const renderWhyChooseEditor = () => {
  const items = JSON.parse(formData.why_choose || '[]');
  
  return (
    <div>
      {items.map((item, index) => (
        <div key={index} className="why-choose-item">
          <input
            value={item.icon}
            onChange={(e) => {
              items[index].icon = e.target.value;
              setFormData('why_choose', JSON.stringify(items));
            }}
            placeholder="表情符号"
          />
          <input
            value={item.title}
            onChange={(e) => {
              items[index].title = e.target.value;
              setFormData('why_choose', JSON.stringify(items));
            }}
            placeholder="标题"
          />
          <textarea
            value={item.description}
            onChange={(e) => {
              items[index].description = e.target.value;
              setFormData('why_choose', JSON.stringify(items));
            }}
            placeholder="描述"
          />
        </div>
      ))}
    </div>
  );
};
```

### 2. 费用表编辑器

```javascript
const renderFeeTableEditor = () => {
  const rows = JSON.parse(formData.fee_table || '[]');
  
  return (
    <table>
      <thead>
        <tr>
          <th>类型</th>
          <th>基础</th>
          <th>专业</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={index}>
            <td>
              <input
                value={row.type}
                onChange={(e) => {
                  rows[index].type = e.target.value;
                  setFormData('fee_table', JSON.stringify(rows));
                }}
              />
            </td>
            <td>
              <input
                value={row.basic}
                onChange={(e) => {
                  rows[index].basic = e.target.value;
                  setFormData('fee_table', JSON.stringify(rows));
                }}
              />
            </td>
            <td>
              <input
                value={row.pro}
                onChange={(e) => {
                  rows[index].pro = e.target.value;
                  setFormData('fee_table', JSON.stringify(rows));
                }}
              />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

---

## 测试建议

### 1. 表单验证测试

```javascript
// 测试必填字段
// 测试JSON字段格式验证
// 测试数字范围验证
// 测试URL字段格式
```

### 2. 提交测试

```javascript
// 测试创建新平台
// 测试更新现有平台
// 测试部分更新
// 测试错误处理
```

### 3. 性能测试

```javascript
// 测试大型JSON字段编辑
// 测试表单响应时间
// 测试列表加载时间
```

---

## 故障排查

### 问题：JSON 字段无法保存

**解决方案：**
- 确保JSON格式正确
- 使用JSON.parse()验证
- 检查API响应错误信息

### 问题：表单字段不显示

**解决方案：**
- 检查form-definition端点是否返回正确数据
- 确保字段名称与formData对象键一致
- 检查浏览器控制台错误

### 问题：更新后数据未生效

**解决方案：**
- 清除浏览器缓存
- 确保API响应中包含更新后的数据
- 检查后端日志

---

## 性能优化建议

1. **表单加载**
   - 使用Promise.all()并行加载表单定义和平台列表
   - 实现表单缓存

2. **JSON编辑**
   - 使用编辑器库（如Monaco Editor）处理JSON
   - 实现自动保存草稿

3. **列表显示**
   - 实现虚拟滚动处理大列表
   - 添加搜索和过滤功能

---

版本：1.0.0
