/**
 * Auth Module - 处理登录、认证、token管理
 */

import apiClient from '../api-client.js';
import { $, getById } from '../utils/dom.js';
import { showToast } from '../utils/ui.js';

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('token');
        this.currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        this.setupGlobalFetchInterceptor();
    }

    /**
     * 获取当前token
     */
    getToken() {
        return this.token;
    }

    /**
     * 获取当前用户
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * 检查是否已登录
     */
    isLoggedIn() {
        return !!(this.token && this.currentUser.username);
    }

    /**
     * 处理登录
     */
    async login(username, password) {
        try {
            const response = await fetch(`${apiClient.config.BASE_URL}/api/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                this.currentUser = data.user;
                localStorage.setItem('token', this.token);
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                
                // 更新apiClient的token
                apiClient.setToken(this.token);
                
                console.log('🎉 Login success');
                return { success: true, data };
            } else {
                console.error('❌ Login failed:', data.detail);
                return { success: false, error: data.detail || '登录失败' };
            }
        } catch (error) {
            console.error('💥 Login error:', error);
            return { success: false, error: '网络错误: ' + error.message };
        }
    }

    /**
     * 处理退出登录
     */
    logout() {
        this.token = null;
        this.currentUser = {};
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        apiClient.clearToken();
        console.log('👋 Logged out');
    }

    /**
     * 清除无效token（401错误时调用）
     */
    clearToken() {
        this.token = null;
        this.currentUser = {};
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
    }

    /**
     * 设置全局Fetch拦截器 - 自动添加token和处理401错误
     */
    setupGlobalFetchInterceptor() {
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            const [resource, options = {}] = args;
            
            // 跳过登录请求（不需要token）
            if (typeof resource === 'string' && resource.includes('/api/admin/login')) {
                return originalFetch.apply(this, args);
            }
            
            // 为其他API调用添加token
            const modifiedOptions = { ...options };
            const headers = modifiedOptions.headers || {};
            
            if (this.token && !headers['Authorization']) {
                headers['Authorization'] = `Bearer ${this.token}`;
            }
            
            modifiedOptions.headers = headers;
            
            return originalFetch.call(this, resource, modifiedOptions).then(async response => {
                // 处理401错误 - token过期
                if (response.status === 401 && typeof resource === 'string' && resource.includes('/api/')) {
                    console.warn('Token已过期或无效,请重新登录');
                    this.clearToken();
                    
                    // 触发自定义事件,让UI管理器显示登录页面
                    window.dispatchEvent(new CustomEvent('auth:logout', {
                        detail: { reason: 'token_expired' }
                    }));
                    
                    showToast('登录已过期,请重新登录', 'warning');
                }
                
                return response;
            });
        };
    }

    /**
     * 初始化认证系统
     */
    initialize() {
        // 检查登录状态,触发事件让UI管理器处理
        if (this.isLoggedIn()) {
            window.dispatchEvent(new CustomEvent('auth:login', {
                detail: { user: this.currentUser }
            }));
        } else {
            window.dispatchEvent(new CustomEvent('auth:logout'));
        }
    }
}

// 创建单例
const authManager = new AuthManager();

// 暴露到全局作用域(向后兼容)
window.authManager = authManager;

export default authManager;
