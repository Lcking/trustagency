# 前端 API 调用规范

**版本**: 1.0.0  
**最后更新**: 2025-11-12  
**适用范围**: 前端开发团队

---

## 📚 目录

1. [概述](#概述)
2. [API 客户端架构](#api-客户端架构)
3. [调用规范](#调用规范)
4. [错误处理](#错误处理)
5. [代码示例](#代码示例)
6. [常见模式](#常见模式)

---

## 概述

### 目标

- ✅ 统一前端 API 调用方式
- ✅ 提高代码可维护性和可读性
- ✅ 减少重复代码
- ✅ 便于团队沟通协作

### 核心原则

| 原则 | 说明 |
|-----|------|
| **单一职责** | 每个函数/模块只做一件事 |
| **一致性** | 所有调用遵循相同模式 |
| **可测试性** | 代码应易于单元测试 |
| **错误优雅** | 错误处理应用户友好 |
| **性能** | 合理使用缓存和异步 |

---

## API 客户端架构

### 推荐结构

```
src/
  └── api/
      ├── client.js          # API 客户端核心
      ├── config.js          # API 配置
      ├── interceptors.js    # 请求/响应拦截器
      ├── modules/
      │   ├── articles.js    # 文章接口
      │   ├── categories.js  # 分类接口
      │   ├── auth.js        # 认证接口
      │   ├── upload.js      # 上传接口
      │   └── ...
      └── __tests__/
          ├── client.test.js
          ├── articles.test.js
          └── ...
```

### 核心模块实现

#### 1. API 配置 (api/config.js)

```javascript
/**
 * API 配置文件
 */

const API_CONFIG = {
  // 环境配置
  development: {
    baseURL: 'http://localhost:8001/api',
    timeout: 10000,
    enableLogging: true,
  },
  production: {
    baseURL: 'https://api.trustagency.com/api',
    timeout: 10000,
    enableLogging: false,
  },
  
  // 通用配置
  headers: {
    'Content-Type': 'application/json',
  },
  
  // Token 配置
  token: {
    storageKey: 'api_token',
    headerName: 'Authorization',
    refreshThreshold: 5 * 60 * 1000, // 5 分钟内过期时自动刷新
  },
  
  // 重试配置
  retry: {
    maxRetries: 3,
    retryDelay: 1000, // 初始延迟 ms
    retryableStatus: [408, 429, 500, 502, 503, 504],
  },
  
  // 缓存配置
  cache: {
    enabled: true,
    defaultTTL: 5 * 60 * 1000, // 5 分钟
    endpoints: {
      '/categories': 30 * 60 * 1000, // 30 分钟
      '/sections': 30 * 60 * 1000,
    },
  },
};

export default API_CONFIG;
```

#### 2. API 客户端 (api/client.js)

```javascript
/**
 * API 客户端 - 核心类
 */

import axios from 'axios';
import API_CONFIG from './config';
import { applyInterceptors } from './interceptors';

class APIClient {
  constructor(config = {}) {
    const env = process.env.NODE_ENV || 'development';
    const baseConfig = API_CONFIG[env] || API_CONFIG.development;
    
    this.config = { ...baseConfig, ...config };
    
    // 创建 axios 实例
    this.instance = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: this.config.headers,
    });
    
    // 应用拦截器
    applyInterceptors(this.instance, this.config);
    
    // 初始化缓存
    this.cache = new Map();
    this.cacheTimestamps = new Map();
    
    // 初始化 token 管理
    this._initTokenManager();
  }
  
  /**
   * 初始化 Token 管理
   */
  _initTokenManager() {
    const { token: tokenConfig } = this.config;
    
    // 从本地存储恢复 token
    const savedToken = localStorage.getItem(tokenConfig.storageKey);
    if (savedToken) {
      try {
        const tokenData = JSON.parse(savedToken);
        this.setToken(tokenData.accessToken);
      } catch (e) {
        // Token 格式错误，清除
        this.clearToken();
      }
    }
  }
  
  /**
   * 设置 Token
   */
  setToken(token) {
    this.token = token;
    const { token: tokenConfig } = this.config;
    this.instance.defaults.headers.common[tokenConfig.headerName] = `Bearer ${token}`;
  }
  
  /**
   * 清除 Token
   */
  clearToken() {
    this.token = null;
    const { token: tokenConfig } = this.config;
    delete this.instance.defaults.headers.common[tokenConfig.headerName];
    localStorage.removeItem(tokenConfig.storageKey);
  }
  
  /**
   * 发送请求（带缓存支持）
   */
  async request(method, url, config = {}) {
    const { useCache = true, cache = {} } = config;
    const cacheKey = `${method}:${url}`;
    
    // 检查缓存
    if (useCache && method.toUpperCase() === 'GET') {
      const cachedData = this._getCachedData(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    try {
      const response = await this.instance.request({
        method,
        url,
        ...config,
      });
      
      // 缓存响应
      if (useCache && method.toUpperCase() === 'GET') {
        const ttl = cache.ttl || this.config.cache.defaultTTL;
        this._setCachedData(cacheKey, response.data, ttl);
      }
      
      return response.data;
    } catch (error) {
      throw this._normalizeError(error);
    }
  }
  
  /**
   * GET 请求
   */
  get(url, config = {}) {
    return this.request('GET', url, config);
  }
  
  /**
   * POST 请求
   */
  post(url, data, config = {}) {
    return this.request('POST', url, { data, ...config });
  }
  
  /**
   * PUT 请求
   */
  put(url, data, config = {}) {
    return this.request('PUT', url, { data, ...config });
  }
  
  /**
   * PATCH 请求
   */
  patch(url, data, config = {}) {
    return this.request('PATCH', url, { data, ...config });
  }
  
  /**
   * DELETE 请求
   */
  delete(url, config = {}) {
    return this.request('DELETE', url, config);
  }
  
  /**
   * 缓存管理 - 获取缓存数据
   */
  _getCachedData(key) {
    if (!this.cache.has(key)) return null;
    
    const timestamp = this.cacheTimestamps.get(key);
    const now = Date.now();
    
    // 检查是否过期
    if (now - timestamp > (this.config.cache.defaultTTL || 300000)) {
      this.cache.delete(key);
      this.cacheTimestamps.delete(key);
      return null;
    }
    
    return this.cache.get(key);
  }
  
  /**
   * 缓存管理 - 设置缓存数据
   */
  _setCachedData(key, data, ttl) {
    this.cache.set(key, data);
    this.cacheTimestamps.set(key, Date.now());
  }
  
  /**
   * 清除所有缓存
   */
  clearCache() {
    this.cache.clear();
    this.cacheTimestamps.clear();
  }
  
  /**
   * 错误规范化
   */
  _normalizeError(error) {
    if (error.response) {
      // 服务器响应了错误
      return {
        status: error.response.status,
        code: error.response.data?.error_code || 'UNKNOWN_ERROR',
        message: error.response.data?.detail || error.message,
        data: error.response.data,
      };
    } else if (error.request) {
      // 请求已发出但未收到响应
      return {
        status: 0,
        code: 'NETWORK_ERROR',
        message: '网络错误，请检查网络连接',
        data: error,
      };
    } else {
      // 请求设置出错
      return {
        status: 0,
        code: 'REQUEST_ERROR',
        message: error.message,
        data: error,
      };
    }
  }
}

// 创建全局客户端实例
export const apiClient = new APIClient();

export default APIClient;
```

#### 3. 拦截器 (api/interceptors.js)

```javascript
/**
 * API 拦截器
 */

export function applyInterceptors(axiosInstance, config) {
  /**
   * 请求拦截器
   */
  axiosInstance.interceptors.request.use(
    (reqConfig) => {
      // 添加请求 ID
      reqConfig.headers['X-Request-ID'] = generateRequestId();
      
      // 记录请求
      if (config.enableLogging) {
        console.log(`[API] ${reqConfig.method.toUpperCase()} ${reqConfig.url}`);
      }
      
      return reqConfig;
    },
    (error) => {
      console.error('[API] Request error:', error);
      return Promise.reject(error);
    }
  );
  
  /**
   * 响应拦截器
   */
  axiosInstance.interceptors.response.use(
    (response) => {
      // 记录响应
      if (config.enableLogging) {
        console.log(`[API] ${response.status} ${response.config.url}`);
      }
      return response;
    },
    async (error) => {
      const { response, config } = error;
      
      // 处理特定错误
      if (response?.status === 401) {
        // 认证失败 - 清除 token 并重定向到登录
        handleUnauthorized();
      }
      
      if (response?.status === 403) {
        // 权限不足
        handleForbidden();
      }
      
      // 重试逻辑
      if (shouldRetry(error, config)) {
        return retryRequest(axiosInstance, error, config);
      }
      
      return Promise.reject(error);
    }
  );
}

/**
 * 生成请求 ID
 */
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 检查是否应该重试
 */
function shouldRetry(error, config) {
  const { retry } = config;
  if (!retry) return false;
  
  config.retryCount = config.retryCount || 0;
  
  // 检查重试次数限制
  if (config.retryCount >= retry.maxRetries) {
    return false;
  }
  
  // 检查是否是可重试的错误
  if (error.response?.status && retry.retryableStatus.includes(error.response.status)) {
    return true;
  }
  
  // 网络错误可以重试
  if (!error.response) {
    return true;
  }
  
  return false;
}

/**
 * 重试请求
 */
function retryRequest(axiosInstance, error, config) {
  config.retryCount += 1;
  
  // 指数退避
  const delay = config.retry.retryDelay * Math.pow(2, config.retryCount - 1);
  
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(axiosInstance.request(config));
    }, delay);
  });
}

/**
 * 处理未认证错误
 */
function handleUnauthorized() {
  localStorage.removeItem('api_token');
  window.location.href = '/login';
}

/**
 * 处理权限不足错误
 */
function handleForbidden() {
  console.error('Permission denied');
  // 显示权限提示或重定向到无权限页面
}
```

#### 4. 文章接口模块 (api/modules/articles.js)

```javascript
/**
 * 文章接口模块
 */

import { apiClient } from '../client';

export const articlesAPI = {
  /**
   * 获取文章列表
   */
  async list(params = {}) {
    return apiClient.get('/articles', {
      params,
      useCache: true,
      cache: { ttl: 5 * 60 * 1000 }, // 5 分钟缓存
    });
  },
  
  /**
   * 获取单篇文章
   */
  async get(id) {
    return apiClient.get(`/articles/${id}`, {
      useCache: true,
      cache: { ttl: 10 * 60 * 1000 }, // 10 分钟缓存
    });
  },
  
  /**
   * 创建文章
   */
  async create(data) {
    return apiClient.post('/articles', data, {
      useCache: false, // 新建数据不缓存
    });
  },
  
  /**
   * 更新文章
   */
  async update(id, data) {
    return apiClient.put(`/articles/${id}`, data, {
      useCache: false,
    });
  },
  
  /**
   * 删除文章
   */
  async delete(id) {
    return apiClient.delete(`/articles/${id}`, {
      useCache: false,
    });
  },
  
  /**
   * 发布文章
   */
  async publish(id) {
    return apiClient.patch(`/articles/${id}/publish`, {}, {
      useCache: false,
    });
  },
  
  /**
   * 精选文章
   */
  async feature(id, isFeatured = true) {
    return apiClient.patch(`/articles/${id}/feature`, {
      is_featured: isFeatured,
    }, {
      useCache: false,
    });
  },
  
  /**
   * 搜索文章
   */
  async search(query, options = {}) {
    return apiClient.get('/articles', {
      params: {
        search: query,
        limit: options.limit || 20,
        ...options,
      },
      useCache: false, // 搜索结果不缓存
    });
  },
};

export default articlesAPI;
```

---

## 调用规范

### 1. 基础调用模式

```javascript
// ✅ 好的做法 - 使用 async/await
async function loadArticles() {
  try {
    const data = await articlesAPI.list({ limit: 20 });
    return data;
  } catch (error) {
    console.error('Failed to load articles:', error);
    showErrorToast(error.message);
  }
}

// ✅ 也可以用 Promise 链
function loadArticles() {
  return articlesAPI.list({ limit: 20 })
    .then(data => {
      console.log('Articles loaded:', data);
      return data;
    })
    .catch(error => {
      console.error('Failed to load articles:', error);
      showErrorToast(error.message);
    });
}

// ❌ 不要这样做 - 忽略错误
function loadArticles() {
  articlesAPI.list();
}
```

### 2. 参数传递

```javascript
// ✅ 好的做法 - 清晰的参数命名
const response = await articlesAPI.list({
  skip: 0,
  limit: 20,
  search: 'python',
  category_id: 5,
  sort_by: 'like_count',
  sort_order: 'desc',
});

// ❌ 不要这样做 - 魔法数字
const response = await articlesAPI.list({
  0, 20, 'python', 5, 'like_count', 'desc'
});
```

### 3. 长操作处理

```javascript
// ✅ 显示加载状态
async function handleSubmit(formData) {
  setLoading(true);
  setError(null);
  
  try {
    const result = await articlesAPI.create(formData);
    showSuccessToast('文章已创建');
    navigateTo(`/articles/${result.id}`);
  } catch (error) {
    setError(error.message);
    showErrorToast(error.message);
  } finally {
    setLoading(false);
  }
}

// ✅ 在模板中使用加载状态
<button onClick={handleSubmit} disabled={loading}>
  {loading ? '创建中...' : '创建文章'}
</button>
```

### 4. 条件请求

```javascript
// ✅ 避免不必要的请求
async function maybeLoadArticle(articleId) {
  // 如果已缓存且有效，不发起新请求
  const cached = await articlesAPI.get(articleId);
  
  if (isCacheValid(cached)) {
    return cached;
  }
  
  // 否则强制刷新
  return articlesAPI.get(articleId, { useCache: false });
}

// ✅ 使用 debounce 处理搜索
import { debounce } from 'lodash';

const handleSearch = debounce(async (query) => {
  const results = await articlesAPI.search(query);
  setResults(results);
}, 300);
```

---

## 错误处理

### 错误分类

```javascript
const ERROR_TYPES = {
  // 请求错误
  VALIDATION_ERROR: 400,
  
  // 认证错误
  UNAUTHORIZED: 401,
  
  // 权限错误
  FORBIDDEN: 403,
  
  // 资源错误
  NOT_FOUND: 404,
  
  // 冲突错误
  CONFLICT: 409,
  
  // 业务错误
  UNPROCESSABLE_ENTITY: 422,
  
  // 服务器错误
  INTERNAL_ERROR: 500,
};
```

### 通用错误处理

```javascript
/**
 * 处理 API 错误
 */
function handleAPIError(error) {
  const { status, code, message } = error;
  
  switch (status) {
    case 400:
      // 验证错误 - 显示具体字段错误
      showFieldErrors(error.data?.details);
      break;
    
    case 401:
      // 认证错误 - 清除 token 并重定向
      apiClient.clearToken();
      window.location.href = '/login';
      showToast('登录已过期，请重新登录');
      break;
    
    case 403:
      // 权限错误
      showToast('您没有权限执行此操作');
      break;
    
    case 404:
      // 资源不存在
      showToast('请求的资源不存在');
      break;
    
    case 409:
      // 冲突 - 如重复数据
      showToast(message, 'warning');
      break;
    
    case 422:
      // 业务逻辑错误
      showToast(message);
      break;
    
    default:
      // 其他错误
      showToast('请求失败，请稍后重试');
  }
}
```

---

## 代码示例

### 完整的文章编辑流程

```javascript
/**
 * 文章编辑页面组件
 */

export default function ArticleEditor({ articleId }) {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  
  // 加载文章
  useEffect(() => {
    loadArticle();
  }, [articleId]);
  
  async function loadArticle() {
    setLoading(true);
    setError(null);
    
    try {
      const data = await articlesAPI.get(articleId);
      setArticle(data);
    } catch (err) {
      setError(err.message);
      showErrorToast('加载文章失败');
    } finally {
      setLoading(false);
    }
  }
  
  async function handleSave(formData) {
    setSaving(true);
    setError(null);
    
    try {
      const updated = await articlesAPI.update(articleId, formData);
      setArticle(updated);
      showSuccessToast('文章已保存');
    } catch (err) {
      setError(err.message);
      
      // 根据错误类型显示不同的提示
      if (err.status === 409) {
        showErrorToast('文章内容已被其他用户修改，请刷新后重试');
      } else {
        showErrorToast(err.message);
      }
    } finally {
      setSaving(false);
    }
  }
  
  async function handlePublish() {
    if (!confirm('确定要发布此文章吗？')) return;
    
    setSaving(true);
    
    try {
      const updated = await articlesAPI.publish(articleId);
      setArticle(updated);
      showSuccessToast('文章已发布');
    } catch (err) {
      showErrorToast(err.message);
    } finally {
      setSaving(false);
    }
  }
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!article) return <div>文章不存在</div>;
  
  return (
    <div className="editor">
      <h1>编辑文章</h1>
      
      <ArticleForm
        initialData={article}
        onSave={handleSave}
        disabled={saving}
      />
      
      <button 
        onClick={handlePublish}
        disabled={saving || article.is_published}
      >
        {article.is_published ? '已发布' : '发布文章'}
      </button>
    </div>
  );
}
```

---

## 常见模式

### 1. 刷新列表

```javascript
// 在创建、更新、删除后刷新列表
async function createAndRefresh(formData) {
  try {
    await articlesAPI.create(formData);
    
    // 清除列表缓存
    apiClient.clearCache();
    
    // 重新加载列表
    const articles = await articlesAPI.list();
    setArticles(articles.data);
    
    showSuccessToast('创建成功');
  } catch (error) {
    showErrorToast(error.message);
  }
}
```

### 2. 无限滚动

```javascript
async function loadMoreArticles() {
  if (loading || !hasMore) return;
  
  setLoading(true);
  
  try {
    const response = await articlesAPI.list({
      skip: articles.length,
      limit: 20,
    });
    
    setArticles([...articles, ...response.data]);
    setHasMore(response.data.length === 20);
  } catch (error) {
    showErrorToast(error.message);
  } finally {
    setLoading(false);
  }
}
```

### 3. 搜索防抖

```javascript
import { useCallback } from 'react';

function SearchArticles() {
  const [results, setResults] = useState([]);
  
  const handleSearch = useCallback(
    debounce(async (query) => {
      if (!query.trim()) {
        setResults([]);
        return;
      }
      
      try {
        const data = await articlesAPI.search(query);
        setResults(data.data);
      } catch (error) {
        console.error('Search failed:', error);
      }
    }, 300),
    []
  );
  
  return (
    <input
      type="text"
      placeholder="搜索文章..."
      onChange={(e) => handleSearch(e.target.value)}
    />
  );
}
```

---

## 📋 检查清单

在提交代码前，检查：

- [ ] 所有 API 调用都使用了 try/catch 或 .catch()
- [ ] 所有长操作都显示了加载状态
- [ ] 错误消息对用户友好
- [ ] 敏感操作（删除等）有确认对话框
- [ ] 使用了适当的缓存策略
- [ ] 代码已测试
- [ ] 没有硬编码的 API 路径或参数

---

**版本**: 1.0.0  
**最后更新**: 2025-11-12
