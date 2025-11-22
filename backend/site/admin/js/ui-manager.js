/**
 * UI Manager - 页面导航和UI控制
 */

import { $ } from './utils/dom.js';
import { showToast } from './utils/ui.js';

class UIManager {
    constructor() {
        this.currentSection = null;
    }

    /**
     * 显示登录页面
     */
    showLoginPage() {
        const loginPage = $('#loginPage');
        const mainPage = $('#mainPage');
        
        if (loginPage) loginPage.style.display = 'flex';
        if (mainPage) mainPage.style.display = 'none';
    }

    /**
     * 显示主页面
     */
    showMainPage() {
        const loginPage = $('#loginPage');
        const mainPage = $('#mainPage');
        
        if (loginPage) loginPage.style.display = 'none';
        if (mainPage) mainPage.style.display = 'block';
    }

    /**
     * 切换到指定section
     * @param {string} section - section名称
     */
    showSection(section) {
        this.currentSection = section;
        
        // 隐藏所有内容区域
        document.querySelectorAll('.content-section').forEach(el => {
            el.style.display = 'none';
        });

        // 移除所有导航项的active状态
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('active');
        });

        // 显示目标section
        const targetSection = $(`#${section}Section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        // 激活对应的导航项
        const navItem = document.querySelector(`.nav-item[onclick*="${section}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }

        // 触发自定义事件,让其他模块可以监听
        window.dispatchEvent(new CustomEvent('section:changed', {
            detail: { section }
        }));
    }

    /**
     * 显示通知消息
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型: success, error, warning, info
     */
    showNotification(message, type = 'info') {
        showToast(message, type);
    }

    /**
     * 显示错误消息在指定元素
     * @param {string} elementId - 元素ID
     * @param {string} message - 错误消息
     */
    showError(elementId, message) {
        const errorElement = $(`#${elementId}`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    /**
     * 隐藏错误消息
     * @param {string} elementId - 元素ID
     */
    hideError(elementId) {
        const errorElement = $(`#${elementId}`);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
    }

    /**
     * 初始化UI事件监听
     */
    initialize() {
        // 监听section变化,可以在这里做一些全局处理
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
window.showNotification = (message, type) => uiManager.showNotification(message, type);
window.showError = (elementId, message) => uiManager.showError(elementId, message);

export default uiManager;
