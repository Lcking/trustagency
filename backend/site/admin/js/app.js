/**
 * 主应用入口文件
 */

// 导入配置
import { API_CONFIG } from './config.js';

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
        this.checkAuth = this.checkAuth.bind(this);
        this.showLoginPage = this.showLoginPage.bind(this);
        this.showMainPage = this.showMainPage.bind(this);
        this.logout = this.logout.bind(this);
    }
    
    /**
     * 初始化应用
     */
    async init() {
        console.log('🚀 应用初始化...');
        
        // 检查认证状态
        const isAuthenticated = await this.checkAuth();
        
        if (isAuthenticated) {
            this.showMainPage();
        } else {
            this.showLoginPage();
        }
        
        // 设置全局错误处理
        this.setupErrorHandling();
        
        console.log('✅ 应用初始化完成');
    }
    
    /**
     * 检查认证状态
     */
    async checkAuth() {
        try {
            if (!authAPI.isAuthenticated()) {
                return false;
            }
            
            // 获取当前用户信息
            this.currentUser = await authAPI.getCurrentUser();
            return true;
        } catch (error) {
            console.error('认证检查失败:', error);
            return false;
        }
    }
    
    /**
     * 显示登录页面
     */
    showLoginPage() {
        show($('#loginPage'));
        hide($('#mainPage'));
        
        // 绑定登录表单提交
        const loginForm = $('#loginForm');
        if (loginForm) {
            loginForm.onsubmit = async (e) => {
                e.preventDefault();
                await this.handleLogin();
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
            showToast(firstError, 'error');
            return;
        }
        
        try {
            showLoading('登录中...');
            
            await authAPI.login(data.username, data.password);
            this.currentUser = await authAPI.getCurrentUser();
            
            hideLoading();
            showToast('登录成功！', 'success');
            
            // 延迟跳转以显示提示
            setTimeout(() => {
                this.showMainPage();
            }, 500);
        } catch (error) {
            hideLoading();
            showToast(error.message || '登录失败', 'error');
        }
    }
    
    /**
     * 显示主页面
     */
    showMainPage() {
        hide($('#loginPage'));
        show($('#mainPage'));
        
        // 显示用户信息
        this.updateUserInfo();
        
        // 绑定导航事件
        this.bindNavigation();
        
        // 绑定登出事件
        const logoutBtn = $('#logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = () => this.logout();
        }
        
        // 默认显示文章管理页面
        this.navigateTo('articles');
    }
    
    /**
     * 更新用户信息显示
     */
    updateUserInfo() {
        const userNameEl = $('#userName');
        const userRoleEl = $('#userRole');
        
        if (userNameEl && this.currentUser) {
            userNameEl.textContent = this.currentUser.username;
        }
        
        if (userRoleEl && this.currentUser) {
            const roleText = this.currentUser.is_superadmin ? '超级管理员' : '普通用户';
            userRoleEl.textContent = roleText;
        }
    }
    
    /**
     * 绑定导航事件
     */
    bindNavigation() {
        delegate($('.sidebar'), 'click', '.nav-item', (e) => {
            e.preventDefault();
            const page = e.target.dataset.page;
            if (page) {
                this.navigateTo(page);
            }
        });
    }
    
    /**
     * 导航到指定页面
     */
    navigateTo(page) {
        // 移除所有active类
        $$('.nav-item').forEach(item => item.classList.remove('active'));
        
        // 添加active类到当前项
        const currentItem = $(`.nav-item[data-page="${page}"]`);
        if (currentItem) {
            currentItem.classList.add('active');
        }
        
        // 隐藏所有页面
        $$('.page').forEach(p => hide(p));
        
        // 显示当前页面
        const currentPage = $(`#${page}Page`);
        if (currentPage) {
            show(currentPage);
            this.currentPage = page;
            
            // 加载页面数据
            this.loadPageData(page);
        }
    }
    
    /**
     * 加载页面数据
     */
    async loadPageData(page) {
        switch (page) {
            case 'articles':
                await this.loadArticles();
                break;
            case 'tasks':
                await this.loadTasks();
                break;
            case 'platforms':
                await this.loadPlatforms();
                break;
            case 'sections':
                await this.loadSections();
                break;
            case 'categories':
                await this.loadCategories();
                break;
            case 'ai-configs':
                await this.loadAIConfigs();
                break;
        }
    }
    
    /**
     * 加载文章列表
     */
    async loadArticles() {
        try {
            showLoading('加载文章列表...');
            const data = await articlesAPI.getList({ page: 1, per_page: 20 });
            hideLoading();
            
            // TODO: 渲染文章列表
            console.log('文章列表:', data);
        } catch (error) {
            hideLoading();
            showToast('加载文章列表失败', 'error');
        }
    }
    
    /**
     * 加载任务列表
     */
    async loadTasks() {
        try {
            showLoading('加载任务列表...');
            const data = await tasksAPI.getList({ page: 1, per_page: 20 });
            hideLoading();
            
            // TODO: 渲染任务列表
            console.log('任务列表:', data);
        } catch (error) {
            hideLoading();
            showToast('加载任务列表失败', 'error');
        }
    }
    
    /**
     * 加载平台列表
     */
    async loadPlatforms() {
        try {
            const data = await platformsAPI.getList();
            // TODO: 渲染平台列表
            console.log('平台列表:', data);
        } catch (error) {
            showToast('加载平台列表失败', 'error');
        }
    }
    
    /**
     * 加载栏目列表
     */
    async loadSections() {
        try {
            const data = await sectionsAPI.getList();
            // TODO: 渲染栏目列表
            console.log('栏目列表:', data);
        } catch (error) {
            showToast('加载栏目列表失败', 'error');
        }
    }
    
    /**
     * 加载分类列表
     */
    async loadCategories() {
        try {
            const data = await categoriesAPI.getList();
            // TODO: 渲染分类列表
            console.log('分类列表:', data);
        } catch (error) {
            showToast('加载分类列表失败', 'error');
        }
    }
    
    /**
     * 加载AI配置列表
     */
    async loadAIConfigs() {
        try {
            const data = await aiConfigsAPI.getList();
            // TODO: 渲染AI配置列表
            console.log('AI配置列表:', data);
        } catch (error) {
            showToast('加载AI配置列表失败', 'error');
        }
    }
    
    /**
     * 登出
     */
    async logout() {
        const confirmed = await showConfirm('确定要退出登录吗？');
        if (!confirmed) return;
        
        try {
            await authAPI.logout();
            this.currentUser = null;
            showToast('已退出登录', 'success');
            this.showLoginPage();
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
