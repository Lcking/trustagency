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
                    sort_by: this.state.sortBy,
                    ...this.state.filters
                };

                const response = await apiClient.getPlatforms(query);
                
                this.state.platforms = response.data || response.items || response;
                this.state.filteredPlatforms = this.state.platforms;

                this.render();
                this.updatePaginationInfo(response.total || this.state.platforms.length);            } catch (error) {
                this.showError(apiClient.formatErrorMessage(error));
                console.error('Failed to load platforms:', error);
            } finally {
                this.state.loading = false;
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

            // Reset form inputs
            document.querySelectorAll('[data-filter]').forEach(elem => {
                elem.value = '';
            });

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

            return `
                <div class="col-md-6 col-lg-4">
                    <article class="card h-100 shadow-sm hover-lift platform-card" 
                             data-platform-id="${platform.id}" 
                             aria-label="${platform.name} 平台">
                        <div class="card-header bg-primary text-white">
                            <h3 class="card-title h5 mb-0">${this.escapeHtml(platform.name)}</h3>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
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
                                    <span class="text-success fw-bold">${platform.safety_rating || 'B'}</span>
                                </li>
                            </ul>
                        </div>
                        <div class="card-footer bg-light">
                            <a href="/platforms/${platform.slug || platform.id}/" class="btn btn-primary btn-sm w-100">查看详情</a>
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
            this.container.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <p class="mt-3 text-muted">加载平台数据中...</p>
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
