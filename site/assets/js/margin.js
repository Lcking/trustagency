/**
 * 两融数据模块 - 通用工具和API调用
 * 
 * 提供两融数据页面的公共功能，包括：
 * - API 调用封装
 * - 数据格式化
 * - 错误处理
 * - 图表渲染
 */

// API 配置
const MarginConfig = {
    // 获取 API 基础 URL
    getApiBase() {
        const configuredBase = window.API_BASE ?? '';
        if (configuredBase !== '') return configuredBase;
        
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8001';
        }
        return '';
    },
    
    // 请求超时时间（毫秒）
    timeout: 30000,
    
    // 重试次数
    maxRetries: 2
};

// 工具函数
const MarginUtils = {
    /**
     * 格式化金额（亿元）
     * @param {number|null|undefined} value - 金额（元）
     * @returns {string} 格式化后的字符串
     */
    formatAmount(value) {
        if (value === null || value === undefined) return '--';
        const yi = value / 1e8;
        if (Math.abs(yi) >= 10000) {
            return (yi / 10000).toFixed(2) + '万亿';
        }
        return yi.toFixed(2) + '亿';
    },
    
    /**
     * 格式化数量（万股）
     * @param {number|null|undefined} value - 数量（股）
     * @returns {string} 格式化后的字符串
     */
    formatVolume(value) {
        if (value === null || value === undefined) return '--';
        const wan = value / 10000;
        if (Math.abs(wan) >= 10000) {
            return (wan / 10000).toFixed(2) + '亿股';
        }
        return wan.toFixed(0) + '万股';
    },
    
    /**
     * 格式化变化率
     * @param {number} val - 变化率
     * @returns {string} HTML 字符串
     */
    formatChange(val) {
        const sign = val >= 0 ? '↑' : '↓';
        const cls = val >= 0 ? 'positive' : 'negative';
        return `<span class="${cls}">${sign} ${Math.abs(val).toFixed(2)}%</span>`;
    },
    
    /**
     * 获取排名样式类
     * @param {number} rank - 排名
     * @returns {string} CSS 类名
     */
    getRankClass(rank) {
        if (rank === 1) return 'rank-1';
        if (rank === 2) return 'rank-2';
        if (rank === 3) return 'rank-3';
        return 'rank-default';
    },
    
    /**
     * 规范化股票代码
     * @param {string} code - 输入的股票代码
     * @returns {string} 规范化后的代码
     */
    normalizeCode(code) {
        code = code.toUpperCase().trim();
        if (code.includes('.')) return code;
        
        if (code.startsWith('6')) return code + '.SH';
        if (code.startsWith('0') || code.startsWith('3')) return code + '.SZ';
        if (code.startsWith('8') || code.startsWith('4')) return code + '.BJ';
        if (code.startsWith('5')) return code + '.SH';
        if (code.startsWith('1')) return code + '.SZ';
        
        return code;
    },
    
    /**
     * 显示错误提示
     * @param {string} message - 错误信息
     * @param {string} containerId - 容器 ID
     */
    showError(message, containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${message}
                </div>
            `;
        }
    },
    
    /**
     * 显示加载状态
     * @param {string} containerId - 容器 ID
     */
    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                </div>
            `;
        }
    }
};

// API 客户端
const MarginAPI = {
    /**
     * 发起 API 请求
     * @param {string} endpoint - API 端点
     * @param {object} options - 请求选项
     * @returns {Promise<object>} 响应数据
     */
    async request(endpoint, options = {}) {
        const url = `${MarginConfig.getApiBase()}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), MarginConfig.timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    ...options.headers
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `请求失败: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请稍后重试');
            }
            throw error;
        }
    },
    
    /**
     * 获取两融概览
     * @returns {Promise<object>}
     */
    async getOverview() {
        return this.request('/api/margin/overview');
    },
    
    /**
     * 获取趋势数据
     * @param {number} days - 天数
     * @returns {Promise<object>}
     */
    async getTrend(days = 30) {
        return this.request(`/api/margin/trend?days=${days}`);
    },
    
    /**
     * 获取排行榜
     * @param {string} orderBy - 排序字段
     * @param {number} limit - 数量
     * @returns {Promise<object>}
     */
    async getRanking(orderBy = 'rzye', limit = 20) {
        return this.request(`/api/margin/ranking?order_by=${orderBy}&limit=${limit}`);
    },
    
    /**
     * 获取个股历史
     * @param {string} code - 股票代码
     * @param {number} days - 天数
     * @returns {Promise<object>}
     */
    async getStockHistory(code, days = 90) {
        const normalizedCode = MarginUtils.normalizeCode(code);
        return this.request(`/api/margin/stock/${normalizedCode}?days=${days}`);
    },
    
    /**
     * 搜索股票
     * @param {string} keyword - 关键词
     * @param {number} limit - 数量
     * @returns {Promise<object>}
     */
    async search(keyword, limit = 20) {
        return this.request(`/api/margin/search?keyword=${encodeURIComponent(keyword)}&limit=${limit}`);
    }
};

// 图表工具
const MarginChart = {
    instances: {},
    
    /**
     * 创建或更新趋势图表
     * @param {string} canvasId - Canvas 元素 ID
     * @param {object} data - 图表数据
     * @param {object} options - 额外选项
     */
    createTrendChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element ${canvasId} not found`);
            return null;
        }
        
        const ctx = canvas.getContext('2d');
        
        // 销毁已存在的图表
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const labels = data.map(d => d.date.slice(5)); // MM-DD
        const rzye = data.map(d => d.rzye / 1e8);
        const rqye = data.map(d => d.rqye / 1e8);
        const rzrqye = data.map(d => d.rzrqye / 1e8);
        
        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '融资余额(亿)',
                        data: rzye,
                        borderColor: '#f5576c',
                        backgroundColor: 'rgba(245, 87, 108, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '融券余额(亿)',
                        data: rqye,
                        borderColor: '#4facfe',
                        backgroundColor: 'rgba(79, 172, 254, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '两融余额(亿)',
                        data: rzrqye,
                        borderColor: '#43e97b',
                        backgroundColor: 'rgba(67, 233, 123, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(0) + '亿';
                            }
                        }
                    }
                },
                ...options
            }
        });
        
        return this.instances[canvasId];
    },
    
    /**
     * 创建个股趋势图表
     * @param {string} canvasId - Canvas 元素 ID
     * @param {object} data - 图表数据
     * @param {string} dataKey - 数据键名
     */
    createStockChart(canvasId, data, dataKey = 'rzye') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const labels = data.map(d => d.date.slice(5));
        const values = data.map(d => (d[dataKey] || 0) / 1e8);
        
        const color = dataKey.includes('rq') ? '#4facfe' : '#f5576c';
        
        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: this.getDataLabel(dataKey),
                    data: values,
                    borderColor: color,
                    backgroundColor: color.replace(')', ', 0.1)').replace('rgb', 'rgba'),
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: value => value.toFixed(2) + '亿'
                        }
                    }
                }
            }
        });
        
        return this.instances[canvasId];
    },
    
    /**
     * 获取数据标签
     * @param {string} key - 数据键名
     * @returns {string} 标签名称
     */
    getDataLabel(key) {
        const labels = {
            'rzye': '融资余额(亿)',
            'rzmre': '融资买入(亿)',
            'net_buy': '融资净买入(亿)',
            'rqye': '融券余额(亿)',
            'rqyl': '融券余量(万股)',
            'rzrqye': '两融余额(亿)'
        };
        return labels[key] || key;
    },
    
    /**
     * 销毁图表
     * @param {string} canvasId - Canvas 元素 ID
     */
    destroy(canvasId) {
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
            delete this.instances[canvasId];
        }
    }
};

// 导出到全局
window.MarginConfig = MarginConfig;
window.MarginUtils = MarginUtils;
window.MarginAPI = MarginAPI;
window.MarginChart = MarginChart;
