/**
 * API 客户端基类
 * 提供统一的HTTP请求封装
 */

import { API_CONFIG, STORAGE_KEYS, HTTP_STATUS, ERROR_MESSAGES } from './config.js';

class APIClient {
    constructor(baseURL = API_CONFIG.BASE_URL) {
        this.baseURL = baseURL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.retryTimes = API_CONFIG.RETRY_TIMES;
        this.retryDelay = API_CONFIG.RETRY_DELAY;
    }

    /**
     * 获取认证token
     */
    getToken() {
        return localStorage.getItem(STORAGE_KEYS.TOKEN);
    }

    /**
     * 设置认证token
     */
    setToken(token) {
        if (token) {
            localStorage.setItem(STORAGE_KEYS.TOKEN, token);
        } else {
            localStorage.removeItem(STORAGE_KEYS.TOKEN);
        }
    }

    /**
     * 构建完整URL
     */
    buildURL(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseURL);
        
        Object.keys(params).forEach(key => {
            const value = params[key];
            if (value !== null && value !== undefined && value !== '') {
                url.searchParams.append(key, value);
            }
        });
        
        return url.toString();
    }

    /**
     * 构建请求头
     */
    buildHeaders(customHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * 处理响应
     */
    async handleResponse(response) {
        // 处理204 No Content
        if (response.status === HTTP_STATUS.NO_CONTENT) {
            return null;
        }

        // 尝试解析JSON
        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = null;
        }

        // 检查HTTP状态码
        if (!response.ok) {
            // 401 未授权，跳转登录
            if (response.status === HTTP_STATUS.UNAUTHORIZED) {
                this.handleUnauthorized();
                throw new Error(data?.message || ERROR_MESSAGES.AUTH_ERROR);
            }

            // 403 权限不足
            if (response.status === HTTP_STATUS.FORBIDDEN) {
                throw new Error(data?.message || ERROR_MESSAGES.PERMISSION_ERROR);
            }

            // 404 未找到
            if (response.status === HTTP_STATUS.NOT_FOUND) {
                throw new Error(data?.message || ERROR_MESSAGES.NOT_FOUND);
            }

            // 500 服务器错误
            if (response.status === HTTP_STATUS.INTERNAL_ERROR) {
                throw new Error(data?.message || ERROR_MESSAGES.SERVER_ERROR);
            }

            // 其他错误
            throw new Error(data?.message || data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR);
        }

        return data;
    }

    /**
     * 处理未授权情况
     */
    handleUnauthorized() {
        // 清除token和用户信息
        this.setToken(null);
        localStorage.removeItem(STORAGE_KEYS.USER);

        // 显示登录页面
        if (typeof window.showLoginPage === 'function') {
            window.showLoginPage();
        } else {
            // 刷新页面
            window.location.reload();
        }
    }

    /**
     * 请求超时处理
     */
    createTimeoutPromise() {
        return new Promise((_, reject) => {
            setTimeout(() => {
                reject(new Error(ERROR_MESSAGES.TIMEOUT_ERROR));
            }, this.timeout);
        });
    }

    /**
     * 执行请求（带重试）
     */
    async executeRequest(fetchPromise, retryCount = 0) {
        try {
            const response = await Promise.race([
                fetchPromise,
                this.createTimeoutPromise()
            ]);
            return await this.handleResponse(response);
        } catch (error) {
            // 网络错误且还有重试次数
            if (retryCount < this.retryTimes && error.message.includes('网络')) {
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                return this.executeRequest(fetchPromise, retryCount + 1);
            }
            throw error;
        }
    }

    /**
     * 通用请求方法
     */
    async request(endpoint, options = {}) {
        const { 
            method = 'GET', 
            params = {}, 
            data = null, 
            headers = {},
            ...otherOptions 
        } = options;

        const url = this.buildURL(endpoint, params);
        const requestHeaders = this.buildHeaders(headers);

        const fetchOptions = {
            method,
            headers: requestHeaders,
            ...otherOptions
        };

        // 添加请求体
        if (data && method !== 'GET' && method !== 'HEAD') {
            fetchOptions.body = JSON.stringify(data);
        }

        return this.executeRequest(fetch(url, fetchOptions));
    }

    /**
     * GET 请求
     */
    async get(endpoint, params = {}, options = {}) {
        return this.request(endpoint, {
            method: 'GET',
            params,
            ...options
        });
    }

    /**
     * POST 请求
     */
    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            data,
            ...options
        });
    }

    /**
     * PUT 请求
     */
    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            data,
            ...options
        });
    }

    /**
     * PATCH 请求
     */
    async patch(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            data,
            ...options
        });
    }

    /**
     * DELETE 请求
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    }

    /**
     * 上传文件
     */
    async upload(endpoint, file, data = {}, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);
        
        Object.keys(data).forEach(key => {
            formData.append(key, data[key]);
        });

        const token = this.getToken();
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // 如果提供了进度回调，使用XMLHttpRequest
        if (onProgress) {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });

                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            resolve(JSON.parse(xhr.responseText));
                        } catch (e) {
                            resolve(xhr.responseText);
                        }
                    } else {
                        reject(new Error(`上传失败: ${xhr.statusText}`));
                    }
                });

                xhr.addEventListener('error', () => {
                    reject(new Error(ERROR_MESSAGES.NETWORK_ERROR));
                });

                xhr.open('POST', this.buildURL(endpoint));
                
                Object.keys(headers).forEach(key => {
                    xhr.setRequestHeader(key, headers[key]);
                });
                
                xhr.send(formData);
            });
        }

        // 否则使用fetch
        return fetch(this.buildURL(endpoint), {
            method: 'POST',
            headers,
            body: formData
        }).then(response => this.handleResponse(response));
    }
}

// 创建全局实例
const apiClient = new APIClient();

export default apiClient;
export { APIClient };
