/**
 * Dashboard Page Module
 */

import apiClient from '../api-client.js';
import { $ } from '../utils/dom.js';
import { showToast } from '../utils/ui.js';

class DashboardPage {
    constructor() {
        this.stats = null;
    }

    /**
     * 加载仪表盘数据
     */
    async load() {
        try {
            const response = await fetch(`${apiClient.config.BASE_URL}/api/admin/stats`, {
                headers: {
                    'Authorization': `Bearer ${apiClient.getToken()}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load dashboard data');
            }

            const data = await response.json();
            this.stats = data;
            this.render(data);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            showToast('加载仪表盘数据失败', 'error');
            
            // 显示默认数据
            this.render({
                total_platforms: 0,
                total_articles: 0,
                total_tasks: 0,
                pending_tasks: 0
            });
        }
    }

    /**
     * 渲染仪表盘
     */
    render(data) {
        const dashboardContent = $('#dashboardContent');
        if (!dashboardContent) return;

        dashboardContent.innerHTML = `
            <div class="dashboard-stats">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-info">
                        <div class="stat-value">${data.total_platforms || 0}</div>
                        <div class="stat-label">平台总数</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📝</div>
                    <div class="stat-info">
                        <div class="stat-value">${data.total_articles || 0}</div>
                        <div class="stat-label">文章总数</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🤖</div>
                    <div class="stat-info">
                        <div class="stat-value">${data.total_tasks || 0}</div>
                        <div class="stat-label">AI任务总数</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⏳</div>
                    <div class="stat-info">
                        <div class="stat-value">${data.pending_tasks || 0}</div>
                        <div class="stat-label">待处理任务</div>
                    </div>
                </div>
            </div>
            <div class="dashboard-welcome">
                <h2>欢迎使用 TrustAgency 后台管理系统</h2>
                <p>从左侧菜单选择功能模块开始管理</p>
            </div>
        `;
    }

    /**
     * 初始化
     */
    initialize() {
        // 监听section变化
        window.addEventListener('section:changed', (e) => {
            if (e.detail.section === 'dashboard') {
                this.load();
            }
        });
    }
}

// 创建单例
const dashboardPage = new DashboardPage();

// 暴露到全局作用域(向后兼容)
window.loadDashboard = () => dashboardPage.load();

export default dashboardPage;
