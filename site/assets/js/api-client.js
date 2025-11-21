/**
 * TrustAgency API Client
 * Handles all communication with the backend API
 * Version: 1.0.0
 */

(function() {
    'use strict';

    // ========================================
    // Configuration
    // ========================================
    
    // Get API base URL dynamically
    function getAPIUrl() {
        // First check localStorage
        const storedURL = localStorage.getItem('apiBaseURL');
        if (storedURL) {
            return storedURL;
        }
        
        // Otherwise use current host and port
        const host = window.location.hostname;
        let port = window.location.port || '80';
        const protocol = window.location.protocol === 'https:' ? 'https' : 'http';
        
        // 如果前端运行在 8000 端口（HTTP 文件服务器），后端 API 在 8001
        if (port === '8000') {
            port = '8001';
        }
        
        // 如果前端运行在 80 或 443，使用同一端口（Nginx 代理场景）
        // 否则使用当前端口（开发环境）
        
        // Return API base URL
        return `${protocol}://${host}:${port}/api`;
    }
    
    const API_CONFIG = {
        baseURL: getAPIUrl(),
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000,
        enableLogging: localStorage.getItem('apiDebug') === 'true'
    };

    // Token storage keys
    const TOKEN_KEY = 'auth_token';
    const REFRESH_TOKEN_KEY = 'refresh_token';
    const EXPIRES_AT_KEY = 'token_expires_at';

    // ========================================
    // API Client Class
    // ========================================

    class APIClient {
        constructor(config = {}) {
            this.config = { ...API_CONFIG, ...config };
            this.requestInProgress = new Map();
            this.cache = new Map();
            this.cacheExpiry = new Map();
        }

        /**
         * Make HTTP request with retry logic
         */
        async request(method, endpoint, options = {}) {
            const url = `${this.config.baseURL}${endpoint}`;
            const cacheKey = `${method}:${endpoint}`;

            // Check cache for GET requests
            if (method === 'GET' && !options.skipCache && this.cache.has(cacheKey)) {
                if (!this.isCacheExpired(cacheKey)) {
                    this.log(`Cache hit: ${url}`);
                    return this.cache.get(cacheKey);
                }
            }

            // Check if request is already in progress (prevent duplicate requests)
            if (method === 'GET' && this.requestInProgress.has(cacheKey)) {
                return this.requestInProgress.get(cacheKey);
            }

            // Prepare request
            const headers = this.prepareHeaders(options.headers || {});
            const config = {
                method,
                headers,
                signal: this.createAbortSignal(this.config.timeout)
            };

            if (['POST', 'PUT', 'PATCH'].includes(method) && options.data) {
                config.body = JSON.stringify(options.data);
            }

            // Execute request with retry logic
            let lastError;
            for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
                try {
                    this.log(`Request: ${method} ${url} (attempt ${attempt + 1})`);
                    
                    const promise = fetch(url, config);
                    if (method === 'GET') {
                        this.requestInProgress.set(cacheKey, promise);
                    }

                    const response = await promise;
                    
                    if (method === 'GET') {
                        this.requestInProgress.delete(cacheKey);
                    }

                    return await this.handleResponse(response, cacheKey);
                } catch (error) {
                    lastError = error;
                    
                    if (method === 'GET') {
                        this.requestInProgress.delete(cacheKey);
                    }

                    // Check if error is retryable
                    if (this.isRetryableError(error) && attempt < this.config.retryAttempts - 1) {
                        const delay = this.config.retryDelay * Math.pow(2, attempt);
                        this.log(`Retry in ${delay}ms after error: ${error.message}`);
                        await this.delay(delay);
                        continue;
                    }
                    
                    throw error;
                }
            }

            throw lastError || new Error('Request failed');
        }

        /**
         * Handle response and caching
         */
        async handleResponse(response, cacheKey) {
            const contentType = response.headers.get('content-type');
            let data;

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            // Handle errors
            if (!response.ok) {
                this.log(`Response error: ${response.status} - ${JSON.stringify(data)}`, 'error');
                
                // Refresh token if 401
                if (response.status === 401) {
                    await this.refreshToken();
                }

                throw new APIError(
                    data?.detail || data?.message || 'Request failed',
                    response.status,
                    data
                );
            }

            // Cache successful GET responses
            if (response.ok && cacheKey) {
                this.setCache(cacheKey, data);
            }

            this.log(`Response success: ${response.status} - ${cacheKey || 'no-cache'}`);
            return data;
        }

        /**
         * Prepare request headers
         */
        prepareHeaders(customHeaders = {}) {
            const headers = {
                'Content-Type': 'application/json',
                ...customHeaders
            };

            // Add auth token if available
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            return headers;
        }

        /**
         * Token Management
         */
        getToken() {
            const token = localStorage.getItem(TOKEN_KEY);
            const expiresAt = localStorage.getItem(EXPIRES_AT_KEY);
            
            // Check if token is expired
            if (token && expiresAt) {
                if (new Date() >= new Date(expiresAt)) {
                    this.clearTokens();
                    return null;
                }
            }
            
            return token;
        }

        setToken(token, expiresIn = 3600) {
            localStorage.setItem(TOKEN_KEY, token);
            const expiresAt = new Date(Date.now() + expiresIn * 1000);
            localStorage.setItem(EXPIRES_AT_KEY, expiresAt.toISOString());
        }

        setRefreshToken(token) {
            localStorage.setItem(REFRESH_TOKEN_KEY, token);
        }

        clearTokens() {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
            localStorage.removeItem(EXPIRES_AT_KEY);
        }

        async refreshToken() {
            const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
            if (!refreshToken) {
                this.clearTokens();
                window.dispatchEvent(new CustomEvent('auth:logout'));
                return false;
            }

            try {
                const response = await this.request('POST', '/auth/refresh', {
                    data: { refresh_token: refreshToken },
                    skipRetry: true
                });
                
                this.setToken(response.access_token, response.expires_in);
                return true;
            } catch (error) {
                this.log(`Token refresh failed: ${error.message}`, 'error');
                this.clearTokens();
                window.dispatchEvent(new CustomEvent('auth:logout'));
                return false;
            }
        }

        /**
         * Cache Management
         */
        setCache(key, data, ttl = 5 * 60 * 1000) {
            this.cache.set(key, data);
            this.cacheExpiry.set(key, Date.now() + ttl);
        }

        isCacheExpired(key) {
            const expiry = this.cacheExpiry.get(key);
            return !expiry || Date.now() > expiry;
        }

        clearCache() {
            this.cache.clear();
            this.cacheExpiry.clear();
        }

        /**
         * Utility Methods
         */
        createAbortSignal(timeout) {
            const controller = new AbortController();
            setTimeout(() => controller.abort(), timeout);
            return controller.signal;
        }

        isRetryableError(error) {
            // Retry on network errors or specific status codes
            return error.name === 'AbortError' || 
                   error.message === 'Failed to fetch' ||
                   error instanceof TypeError;
        }

        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        log(message, level = 'info') {
            if (!this.config.enableLogging) return;
            
            const timestamp = new Date().toISOString();
            switch(level) {
                case 'error':
                    console.error(`[${timestamp}] API ERROR: ${message}`);
                    break;
                case 'warn':
                    console.warn(`[${timestamp}] API WARN: ${message}`);
                    break;
                default:
                    console.log(`[${timestamp}] API: ${message}`);
            }
        }

        // ========================================
        // Authentication Endpoints
        // ========================================

        /**
         * Register new user
         */
        async register(data) {
            const response = await this.request('POST', '/auth/register', { data });
            if (response.access_token) {
                this.setToken(response.access_token, response.expires_in);
                this.setRefreshToken(response.refresh_token);
            }
            return response;
        }

        /**
         * Login
         */
        async login(username, password) {
            const response = await this.request('POST', '/auth/login', {
                data: { username, password },
                skipCache: true
            });
            if (response.access_token) {
                this.setToken(response.access_token, response.expires_in);
                this.setRefreshToken(response.refresh_token);
            }
            return response;
        }

        /**
         * Logout
         */
        async logout() {
            try {
                await this.request('POST', '/auth/logout', { data: {} });
            } finally {
                this.clearTokens();
            }
        }

        /**
         * Get current user
         */
        async getCurrentUser() {
            return this.request('GET', '/auth/me', { skipCache: true });
        }

        // ========================================
        // Platform Endpoints
        // ========================================

        /**
         * Get all platforms
         */
        async getPlatforms(query = {}) {
            const params = this.buildQueryString(query);
            return this.request('GET', `/platforms${params}`);
        }

        /**
         * Get single platform
         */
        async getPlatform(platformId) {
            return this.request('GET', `/platforms/${platformId}`);
        }

        /**
         * Create platform (admin only)
         */
        async createPlatform(data) {
            return this.request('POST', '/platforms', { data });
        }

        /**
         * Update platform (admin only)
         */
        async updatePlatform(platformId, data) {
            return this.request('PUT', `/platforms/${platformId}`, { data });
        }

        /**
         * Delete platform (admin only)
         */
        async deletePlatform(platformId) {
            return this.request('DELETE', `/platforms/${platformId}`);
        }

        /**
         * Search platforms
         */
        async searchPlatforms(query, filters = {}) {
            const params = this.buildQueryString({ search: query, ...filters });
            return this.request('GET', `/platforms${params}`, { skipCache: true });
        }

        // ========================================
        // Article Endpoints
        // ========================================

        /**
         * Get all articles
         */
        async getArticles(query = {}) {
            const params = this.buildQueryString(query);
            return this.request('GET', `/articles${params}`);
        }

        /**
         * Get single article
         */
        async getArticle(articleId) {
            return this.request('GET', `/articles/${articleId}`);
        }

        /**
         * Create article (admin only)
         */
        async createArticle(data) {
            return this.request('POST', '/articles', { data });
        }

        /**
         * Update article (admin only)
         */
        async updateArticle(articleId, data) {
            return this.request('PUT', `/articles/${articleId}`, { data });
        }

        /**
         * Delete article (admin only)
         */
        async deleteArticle(articleId) {
            return this.request('DELETE', `/articles/${articleId}`);
        }

        /**
         * Search articles
         */
        async searchArticles(query, filters = {}) {
            const params = this.buildQueryString({ search: query, ...filters });
            return this.request('GET', `/articles${params}`, { skipCache: true });
        }

        /**
         * Get articles by category
         */
        async getArticlesByCategory(category, query = {}) {
            const params = this.buildQueryString(query);
            return this.request('GET', `/articles/category/${category}${params}`);
        }

        // ========================================
        // AI Task Endpoints
        // ========================================

        /**
         * Generate article using AI
         */
        async generateArticle(data) {
            return this.request('POST', '/tasks/generate', { data });
        }

        /**
         * Get task status
         */
        async getTaskStatus(taskId) {
            return this.request('GET', `/tasks/${taskId}`, { skipCache: true });
        }

        /**
         * Get task result
         */
        async getTaskResult(taskId) {
            return this.request('GET', `/tasks/${taskId}/result`);
        }

        /**
         * List user tasks
         */
        async getUserTasks(query = {}) {
            const params = this.buildQueryString(query);
            return this.request('GET', `/tasks${params}`, { skipCache: true });
        }

        // ========================================
        // Admin Endpoints
        // ========================================

        /**
         * Get admin statistics
         */
        async getStats() {
            return this.request('GET', '/admin/stats');
        }

        /**
         * Get admin users
         */
        async getUsers(query = {}) {
            const params = this.buildQueryString(query);
            return this.request('GET', `/admin/users${params}`);
        }

        /**
         * Get health check
         */
        async healthCheck() {
            return this.request('GET', '/health');
        }

        // ========================================
        // Utility Methods
        // ========================================

        /**
         * Build query string from object
         */
        buildQueryString(params = {}) {
            if (Object.keys(params).length === 0) {
                return '';
            }
            const query = Object.entries(params)
                .filter(([, value]) => value !== null && value !== undefined)
                .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
                .join('&');
            return query ? `?${query}` : '';
        }

        /**
         * Format error message for display
         */
        formatErrorMessage(error) {
            if (error instanceof APIError) {
                if (error.statusCode === 401) {
                    return '登录已过期，请重新登录';
                } else if (error.statusCode === 403) {
                    return '你没有权限执行此操作';
                } else if (error.statusCode === 404) {
                    return '请求的资源不存在';
                } else if (error.statusCode === 422) {
                    // Validation error
                    if (error.data?.detail) {
                        return error.data.detail;
                    }
                }
                return error.message || '请求失败，请重试';
            }
            return error?.message || '请求失败，请重试';
        }
    }

    // ========================================
    // Error Class
    // ========================================

    class APIError extends Error {
        constructor(message, statusCode = 500, data = null) {
            super(message);
            this.name = 'APIError';
            this.statusCode = statusCode;
            this.data = data;
        }
    }

    // ========================================
    // Global Instance and Exports
    // ========================================

    // Create global instance
    window.apiClient = new APIClient();

    // Export to global scope
    window.TrustAgency = window.TrustAgency || {};
    window.TrustAgency.APIClient = APIClient;
    window.TrustAgency.APIError = APIError;
    window.TrustAgency.apiClient = window.apiClient;

    // Backward compatibility
    window.trustAgency = {
        api: window.apiClient,
        APIClient,
        APIError
    };

})();
