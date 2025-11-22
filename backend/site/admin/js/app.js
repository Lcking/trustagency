/**
 * 主应用入口文件
 */

// 导入配置
import { API_CONFIG } from './config.js';

// 导入认证和UI管理器
import authManager from './modules/auth.js';
import uiManager from './modules/ui.js';

// 导入API服务
import authAPI from './api/auth.js';
import articlesAPI from './api/articles.js';
import tasksAPI from './api/tasks.js';
import platformsAPI from './api/platforms.js';
import sectionsAPI from './api/sections.js';
import categoriesAPI from './api/categories.js';
import aiConfigsAPI from './api/ai-configs.js';
import uploadAPI from './api/upload.js';

// 导入工具函数
import { $, $$, show, hide, getFormData, setFormData, delegate } from './utils/dom.js';
import { showToast, showConfirm, showLoading, hideLoading, progressBar } from './utils/ui.js';
import { formatDate, formatRelativeTime, formatFileSize, truncate } from './utils/format.js';
import { validateForm, validators } from './utils/validation.js';
import { storage } from './utils/storage.js';

/**
 * 应用主类
 */
class App {
    constructor() {
        this.currentPage = null;
        this.currentUser = null;
        this.editor = null;
        
        // 绑定this
        this.init = this.init.bind(this);
        this.handleLogin = this.handleLogin.bind(this);
        this.logout = this.logout.bind(this);
    }
    
    /**
     * 初始化应用
     */
    async init() {
        console.log('🚀 应用初始化...');
        
        // 初始化认证和UI管理器
        authManager.initialize();
        uiManager.initialize();
        
        // 设置全局错误处理
        this.setupErrorHandling();
        
        // 如果已登录,显示主页面并加载初始数据
        if (authManager.isLoggedIn()) {
            uiManager.showMainPage();
            this.loadInitialData();
        } else {
            // 绑定登录表单
            this.bindLoginForm();
            uiManager.showLoginPage();
        }
        
        console.log('✅ 应用初始化完成');
    }
    
    /**
     * 绑定登录表单
     */
    bindLoginForm() {
        const loginForm = $('#loginForm');
        if (loginForm) {
            loginForm.onsubmit = (e) => {
                e.preventDefault();
                this.handleLogin();
            };
        }
    }
    
    /**
     * 处理登录
     */
    async handleLogin() {
        const form = $('#loginForm');
        const data = getFormData(form);
        
        // 验证表单
        const validation = validateForm(data, {
            username: [validators.required()],
            password: [validators.required(), validators.min(6)]
        });
        
        if (!validation.valid) {
            const firstError = Object.values(validation.errors)[0];
            uiManager.showError('loginError', firstError);
            return;
        }
        
        try {
            showLoading('登录中...');
            
            const result = await authManager.login(data.username, data.password);
            
            hideLoading();
            
            if (result.success) {
                showToast('登录成功！', 'success');
                
                // 延迟跳转以显示提示
                setTimeout(() => {
                    uiManager.showMainPage();
                    this.loadInitialData();
                }, 500);
            } else {
                uiManager.showError('loginError', result.error);
            }
        } catch (error) {
            hideLoading();
            uiManager.showError('loginError', '网络错误: ' + error.message);
        }
    }
    
    /**
     * 加载初始数据
     */
    async loadInitialData() {
        try {
            // 触发app:ready事件,让各功能模块加载数据
            window.dispatchEvent(new CustomEvent('app:ready'));
        } catch (error) {
            console.error('加载初始数据失败:', error);
        }
    }
    
    /**
     * 登出
     */
    async logout() {
        const confirmed = await showConfirm('确定要退出登录吗？');
        if (!confirmed) return;
        
        try {
            authManager.logout();
            showToast('已退出登录', 'success');
            uiManager.showLoginPage();
            this.bindLoginForm();
        } catch (error) {
            showToast('退出失败', 'error');
        }
    }
    
    /**
     * 设置全局错误处理
     */
    setupErrorHandling() {
        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise错误:', event.reason);
            showToast('操作失败，请重试', 'error');
        });
        
        window.addEventListener('error', (event) => {
            console.error('全局错误:', event.error);
        });
    }
}

// 创建应用实例并导出
const app = new App();

// DOM加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}

// 导出应用实例供全局使用
window.app = app;

export default app;
