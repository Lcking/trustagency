/**
 * UI Manager - 页面导航、显示控制、通知
 */

import authManager from './auth.js';
import { $, getById } from '../utils/dom.js';
import { showToast } from '../utils/ui.js';

class UIManager {
    constructor() {
        this.currentSection = null;
    }

    /**
     * 显示登录页面
     */
    showLoginPage() {
        const loginPage = getById('loginPage');
        const mainPage = getById('mainPage');
        
        if (loginPage) loginPage.style.display = 'flex';
        if (mainPage) mainPage.style.display = 'none';
    }

    /**
     * 显示主页面
     */
    showMainPage() {
        const loginPage = getById('loginPage');
        const mainPage = getById('mainPage');
        const currentUsername = getById('currentUsername');
        
        if (loginPage) loginPage.style.display = 'none';
        if (mainPage) mainPage.style.display = 'flex';
        if (currentUsername) {
            currentUsername.textContent = authManager.getCurrentUser().username || 'User';
        }
    }

    /**
     * 切换到指定section
     */
    showSection(section) {
        this.currentSection = section;
        
        // 隐藏所有内容区
        document.querySelectorAll('.content-section').forEach(el => {
            el.classList.remove('active');
        });

        // 移除所有菜单项的active状态
        document.querySelectorAll('.menu-item').forEach(el => {
            el.classList.remove('active');
        });

        // 显示目标section
        const targetSection = getById(section);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // 激活对应的菜单项
        const menuItem = document.querySelector(`.menu-item[data-section="${section}"]`);
        if (menuItem) {
            menuItem.classList.add('active');
        }

        // 触发自定义事件,让各功能模块知道要加载数据
        window.dispatchEvent(new CustomEvent('section:changed', {
            detail: { section }
        }));
    }

    /**
     * 显示错误消息
     */
    showError(elementId, message) {
        const errorElement = getById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    /**
     * 隐藏错误消息
     */
    hideError(elementId) {
        const errorElement = getById(elementId);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
    }

    /**
     * 初始化UI系统
     */
    initialize() {
        // 监听认证事件
        window.addEventListener('auth:login', (e) => {
            console.log('Auth event: login', e.detail.user);
            this.showMainPage();
            
            // 触发初始化事件,让各模块加载数据
            window.dispatchEvent(new CustomEvent('app:ready'));
        });

        window.addEventListener('auth:logout', (e) => {
            console.log('Auth event: logout', e.detail?.reason);
            this.showLoginPage();
        });

        // 监听section变化
        window.addEventListener('section:changed', (e) => {
            console.log(`Section changed to: ${e.detail.section}`);
        });
    }
}

// 创建单例
const uiManager = new UIManager();

// 暴露到全局作用域(向后兼容)
window.showLoginPage = () => uiManager.showLoginPage();
window.showMainPage = () => uiManager.showMainPage();
window.showSection = (section) => uiManager.showSection(section);
window.showError = (elementId, message) => uiManager.showError(elementId, message);

export default uiManager;
