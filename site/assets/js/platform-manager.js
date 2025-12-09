/**
 * Platform Management Module
 * Handles platform display, filtering, and API integration
 */

(function() {
    'use strict';

    window.TrustAgency = window.TrustAgency || {};

    const PlatformManager = {
        state: {
            platforms: [],
            filteredPlatforms: [],
            loading: false,
            currentPage: 1,
            pageSize: 12,
            sortBy: 'ranking',
            platformSource: 'all',  // 'all', '券商平台', '民间平台', '黑名单'
            filters: {
                minLeverage: null,
                maxLeverage: null,
                minRating: null,
                country: null,
                category: null
            }
        },

        /**
         * Initialize platform manager
         */
        async init(containerId = 'platforms-container') {
            this.container = document.getElementById(containerId);
            if (!this.container) {
                console.error('Platform container not found:', containerId);
                return;
            }

            // Setup event listeners
            this.setupFilters();
            this.setupPagination();
            this.setupSourceFilter();

            // Load initial data
            await this.loadPlatforms();
        },

        /**
         * Load platforms from API
         */
        async loadPlatforms() {
            try {
                this.state.loading = true;
                this.showLoading();

                const query = {
                    page: this.state.currentPage,
                    limit: this.state.pageSize,
                    // Bug004修复：支持按推荐排序和按评分排序
                    sort_by: this.state.sortBy,
                    ...this.state.filters
                };

                const response = await apiClient.getPlatforms(query);
                
                this.state.platforms = response.data || response.items || response;
                
                // 先按来源筛选，再排序
                let filtered = this.filterBySource(this.state.platforms);
                this.state.filteredPlatforms = this.sortPlatforms(filtered);

                this.render();
                this.updatePaginationInfo(response.total || this.state.platforms.length);
            } catch (error) {
                this.showError(apiClient.formatErrorMessage(error));
                console.error('Failed to load platforms:', error);
            } finally {
                this.state.loading = false;
            }
        },

        /**
         * 按平台来源筛选
         */
        filterBySource(platforms) {
            if (this.state.platformSource === 'all') {
                return platforms;
            }
            return platforms.filter(p => p.platform_source === this.state.platformSource);
        },

        /**
         * 设置平台来源筛选标签
         */
        setupSourceFilter() {
            const sourceButtons = document.querySelectorAll('[data-source]');
            sourceButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    // 使用 e.currentTarget 确保引用的是绑定事件的按钮元素
                    const clickedButton = e.currentTarget;
                    
                    // 移除所有active状态和aria-pressed
                    sourceButtons.forEach(b => {
                        b.classList.remove('active');
                        b.setAttribute('aria-pressed', 'false');
                    });
                    // 添加当前按钮的active状态和aria-pressed
                    clickedButton.classList.add('active');
                    clickedButton.setAttribute('aria-pressed', 'true');
                    
                    // 更新状态并重新加载
                    this.state.platformSource = clickedButton.dataset.source;
                    this.state.currentPage = 1;
                    this.loadPlatforms();
                });
            });
        },

        /**
         * Bug004修复：根据sortBy参数排序平台列表
         */
        sortPlatforms(platforms) {
            const sorted = [...platforms];
            
            switch(this.state.sortBy) {
                case 'rating':
                    // 评分最高排在前面
                    return sorted.sort((a, b) => (b.rating || 0) - (a.rating || 0));
                case 'leverage':
                    // 杠杆最高排在前面
                    return sorted.sort((a, b) => (b.max_leverage || 0) - (a.max_leverage || 0));
                case 'fee':
                    // 费率最低排在前面
                    return sorted.sort((a, b) => (a.commission_rate || 0) - (b.commission_rate || 0));
                case 'ranking':
                default:
                    // 推荐排序：推荐的平台优先，然后按评分排序
                    return sorted.sort((a, b) => {
                        if (a.is_recommended && !b.is_recommended) return -1;
                        if (!a.is_recommended && b.is_recommended) return 1;
                        return (b.rating || 0) - (a.rating || 0);
                    });
            }
        },

        /**
         * Setup filter controls
         */
        setupFilters() {
            // Leverage range filter
            const leverageMinInput = document.getElementById('filter-leverage-min');
            const leverageMaxInput = document.getElementById('filter-leverage-max');
            if (leverageMinInput) {
                leverageMinInput.addEventListener('change', (e) => {
                    this.state.filters.minLeverage = e.target.value || null;
                    this.state.currentPage = 1;
                    this.loadPlatforms();
                });
            }
            if (leverageMaxInput) {
                leverageMaxInput.addEventListener('change', (e) => {
                    this.state.filters.maxLeverage = e.target.value || null;
                    this.state.currentPage = 1;
                    this.loadPlatforms();
                });
            }

            // Rating filter
            const ratingFilter = document.getElementById('filter-rating');
            if (ratingFilter) {
                ratingFilter.addEventListener('change', (e) => {
                    this.state.filters.minRating = e.target.value || null;
                    this.state.currentPage = 1;
                    this.loadPlatforms();
                });
            }

            // Sort by
            const sortBySelect = document.getElementById('sort-by');
            if (sortBySelect) {
                sortBySelect.addEventListener('change', (e) => {
                    this.state.sortBy = e.target.value || 'ranking';
                    this.state.currentPage = 1;
                    this.loadPlatforms();
                });
            }

            // Clear filters button
            const clearButton = document.getElementById('clear-filters');
            if (clearButton) {
                clearButton.addEventListener('click', () => {
                    this.clearFilters();
                });
            }

            // Search
            const searchInput = document.getElementById('platform-search');
            if (searchInput) {
                let searchTimeout;
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        this.searchPlatforms(e.target.value);
                    }, 300);
                });
            }
        },

        /**
         * Search platforms
         */
        async searchPlatforms(query) {
            if (!query.trim()) {
                this.state.filteredPlatforms = this.state.platforms;
                this.render();
                return;
            }

            try {
                this.showLoading();
                const results = await apiClient.searchPlatforms(query);
                this.state.filteredPlatforms = results.data || results.items || results;
                this.render();
            } catch (error) {
                this.showError('搜索失败，请重试');
                console.error('Search failed:', error);
            }
        },

        /**
         * Clear all filters
         */
        clearFilters() {
            this.state.filters = {
                minLeverage: null,
                maxLeverage: null,
                minRating: null,
                country: null,
                category: null
            };
            this.state.currentPage = 1;
            this.state.sortBy = 'ranking';
            this.state.platformSource = 'all';

            // Reset form inputs
            document.querySelectorAll('[data-filter]').forEach(elem => {
                elem.value = '';
            });

            // Reset source filter buttons
            const sourceButtons = document.querySelectorAll('[data-source]');
            sourceButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-pressed', 'false');
                if (btn.dataset.source === 'all') {
                    btn.classList.add('active');
                    btn.setAttribute('aria-pressed', 'true');
                }
            });

            // Reset sort select
            const sortSelect = document.getElementById('sort-by');
            if (sortSelect) {
                sortSelect.value = 'ranking';
            }

            this.loadPlatforms();
        },

        /**
         * Setup pagination
         */
        setupPagination() {
            const prevBtn = document.getElementById('pagination-prev');
            const nextBtn = document.getElementById('pagination-next');

            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    if (this.state.currentPage > 1) {
                        this.state.currentPage--;
                        this.loadPlatforms();
                        this.scrollToTop();
                    }
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    this.state.currentPage++;
                    this.loadPlatforms();
                    this.scrollToTop();
                });
            }
        },

        /**
         * Render platforms
         */
        render() {
            if (!this.container) return;

            if (this.state.filteredPlatforms.length === 0) {
                this.container.innerHTML = `
                    <div class="alert alert-info text-center" role="alert">
                        <p class="mb-0">未找到符合条件的平台</p>
                    </div>
                `;
                return;
            }

            this.container.innerHTML = this.state.filteredPlatforms.map(platform => 
                this.createPlatformCard(platform)
            ).join('');

            // Add click handlers
            this.container.querySelectorAll('.platform-card').forEach(card => {
                card.addEventListener('click', () => {
                    const platformId = card.dataset.platformId;
                    this.viewPlatformDetails(platformId);
                });
            });
        },

        /**
         * Create platform card HTML
         */
        createPlatformCard(platform) {
            const leverage = platform.max_leverage || '未公开';
            const feeRate = platform.fee_rate ? `${platform.fee_rate}%` : '未公开';
            const rating = platform.rating || 0;
            const ratingStars = this.createStars(rating);
            const recommendedBadge = platform.is_recommended ? '<span class="badge bg-success me-2">⭐ 推荐</span>' : '';
            const foundedYear = platform.founded_year || '未公开';
            
            // 平台来源标识
            const platformSource = platform.platform_source || '民间平台';
            const isBlacklist = platformSource === '黑名单';
            const isBroker = platformSource === '券商平台';
            
            // 根据来源设置卡片样式
            let headerClass = 'bg-primary';
            let headerStyle = 'background-color: #0d6efd !important;';
            let cardBorderClass = '';
            let sourceBadge = '';
            let warningBanner = '';
            
            if (isBlacklist) {
                headerClass = 'bg-danger';
                headerStyle = 'background-color: #dc3545 !important;';
                cardBorderClass = 'border-danger border-2';
                sourceBadge = '<span class="badge bg-danger me-2">⚠️ 黑名单</span>';
                warningBanner = `
                    <div class="alert alert-danger py-1 px-2 mb-2 small">
                        <strong>⚠️ 风险警示：</strong>该平台存在风险，请谨慎甄别！
                    </div>
                `;
            } else if (isBroker) {
                headerClass = 'bg-success';
                headerStyle = 'background-color: #198754 !important;';
                sourceBadge = '<span class="badge bg-success me-2">🏦 券商</span>';
            } else {
                sourceBadge = '<span class="badge bg-secondary me-2">🏢 民间</span>';
            }

            return `
                <div class="col-md-6 col-lg-4">
                    <article class="card h-100 shadow-sm hover-lift platform-card position-relative ${cardBorderClass}" 
                             data-platform-id="${platform.id}" 
                             aria-label="${platform.name} 平台">
                        ${isBlacklist ? '<div class="position-absolute top-0 start-0 m-2 platform-warning-badge"><span class="badge bg-danger fs-6" aria-label="风险警示">⚠️</span></div>' : ''}
                        <div class="card-header ${headerClass} text-white" style="${headerStyle}">
                            <h3 class="card-title h5 mb-0" style="color: white;">${this.escapeHtml(platform.name)}</h3>
                        </div>
                        <div class="card-body">
                            ${warningBanner}
                            <div class="mb-3">
                                ${sourceBadge}
                                ${recommendedBadge}
                                <span class="badge bg-info">成立于 ${foundedYear}</span>
                            </div>
                            <p class="card-text text-muted text-truncate-2">
                                ${this.escapeHtml(platform.description || '专业交易平台')}
                            </p>
                            <div class="mb-3">
                                <div class="small mb-2">
                                    <strong>评分:</strong>
                                    <span class="rating">${ratingStars}</span>
                                    <span class="text-muted">(${rating.toFixed(1)})</span>
                                </div>
                            </div>
                            <ul class="list-unstyled small mb-3">
                                <li class="mb-2">
                                    <strong>最高杠杆:</strong>
                                    <span class="badge bg-light text-dark">1:${leverage}</span>
                                </li>
                                <li class="mb-2">
                                    <strong>费率范围:</strong>
                                    <span class="badge bg-light text-dark">${feeRate}</span>
                                </li>
                                <li class="mb-2">
                                    <strong>安全评级:</strong>
                                    <span class="badge ${isBlacklist ? 'bg-danger' : 'bg-warning'} text-dark">${platform.safety_rating || 'B'}</span>
                                </li>
                                <li class="mb-2">
                                    <strong>成立年份:</strong>
                                    <span class="badge bg-light text-dark">${foundedYear}</span>
                                </li>
                            </ul>
                        </div>
                        <div class="card-footer ${isBlacklist ? 'bg-danger bg-opacity-10' : 'bg-light'}">
                            <a href="/platforms/${this.sanitizeUrlSegment(platform.slug || platform.id)}/" class="btn ${isBlacklist ? 'btn-outline-danger' : 'btn-primary'} btn-sm w-100">
                                ${isBlacklist ? '查看风险详情' : '查看详情'}
                            </a>
                        </div>
                    </article>
                </div>
            `;
        },

        /**
         * Create star rating display
         */
        createStars(rating) {
            const fullStars = Math.floor(rating);
            const hasHalfStar = rating % 1 >= 0.5;
            let stars = '';

            for (let i = 0; i < 5; i++) {
                if (i < fullStars) {
                    stars += '★';
                } else if (i === fullStars && hasHalfStar) {
                    stars += '◆';
                } else {
                    stars += '☆';
                }
            }

            return stars;
        },

        /**
         * View platform details
         */
        async viewPlatformDetails(platformId) {
            try {
                const platform = await apiClient.getPlatform(platformId);
                // Navigate to platform detail page
                window.location.href = `/platforms/${platform.slug || platformId}/`;
            } catch (error) {
                this.showError('加载平台详情失败');
                console.error('Failed to load platform details:', error);
            }
        },

        /**
         * Update pagination info
         */
        updatePaginationInfo(total) {
            const paginationInfo = document.getElementById('pagination-info');
            if (paginationInfo) {
                const startItem = (this.state.currentPage - 1) * this.state.pageSize + 1;
                const endItem = Math.min(this.state.currentPage * this.state.pageSize, total);
                paginationInfo.textContent = `显示 ${startItem}-${endItem} 项（共 ${total} 项）`;
            }

            // Update pagination buttons
            const prevBtn = document.getElementById('pagination-prev');
            const nextBtn = document.getElementById('pagination-next');

            if (prevBtn) {
                prevBtn.disabled = this.state.currentPage === 1;
            }

            if (nextBtn) {
                const hasMore = this.state.currentPage * this.state.pageSize < total;
                nextBtn.disabled = !hasMore;
            }
        },

        /**
         * Show loading state
         */
        showLoading() {
            if (!this.container) return;
            // Bug006修复：只显示spinner，不显示加载中文字
            this.container.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                </div>
            `;
        },

        /**
         * Show error message
         */
        showError(message) {
            const errorContainer = document.getElementById('error-message');
            if (errorContainer) {
                errorContainer.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <strong>错误:</strong> ${this.escapeHtml(message)}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
                    </div>
                `;
            }
        },

        /**
         * Escape HTML
         */
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        /**
         * Sanitize URL path segment
         * Encodes special characters to prevent XSS in href attributes
         */
        sanitizeUrlSegment(segment) {
            if (!segment) return '';
            // Convert to string and encode URI component
            const str = String(segment);
            // Only allow alphanumeric, hyphens, and underscores for slug/id
            // This is more restrictive than encodeURIComponent for extra safety
            if (/^[\w-]+$/.test(str)) {
                return str;
            }
            // If contains special chars, encode it
            return encodeURIComponent(str);
        },

        /**
         * Scroll to top
         */
        scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    // Export to global scope
    window.TrustAgency.PlatformManager = PlatformManager;

    // Auto-initialize if container exists
    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('platforms-container')) {
            PlatformManager.init();
        }
    });

})();
