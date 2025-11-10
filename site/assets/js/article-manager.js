/**
 * Article Management Module
 * Handles article display, search, and API integration
 */

(function() {
    'use strict';

    window.TrustAgency = window.TrustAgency || {};

    const ArticleManager = {
        state: {
            articles: [],
            filteredArticles: [],
            loading: false,
            currentPage: 1,
            pageSize: 10,
            category: null,
            sortBy: 'date_desc',
            searchQuery: '',
            filters: {
                category: null,
                featured: null,
                tag: null
            }
        },

        /**
         * Initialize article manager
         */
        async init(containerId = 'articles-container', categoryFilter = null) {
            this.container = document.getElementById(containerId);
            if (!this.container) {
                console.error('Article container not found:', containerId);
                return;
            }

            if (categoryFilter) {
                this.state.category = categoryFilter;
                this.state.filters.category = categoryFilter;
            }

            // Setup event listeners
            this.setupFilters();
            this.setupPagination();

            // Load initial data
            await this.loadArticles();
        },

        /**
         * Load articles from API
         */
        async loadArticles() {
            try {
                this.state.loading = true;
                this.showLoading();

                const query = {
                    page: this.state.currentPage,
                    limit: this.state.pageSize,
                    sort_by: this.state.sortBy,
                    ...this.state.filters
                };

                const response = this.state.category
                    ? await apiClient.getArticlesByCategory(this.state.category, query)
                    : await apiClient.getArticles(query);
                
                this.state.articles = response.data || response.items || response;
                this.state.filteredArticles = this.state.articles;

                this.render();
                this.updatePaginationInfo(response.total || this.state.articles.length);
            } catch (error) {
                this.showError(apiClient.formatErrorMessage(error));
                console.error('Failed to load articles:', error);
            } finally {
                this.state.loading = false;
            }
        },

        /**
         * Setup filter controls
         */
        setupFilters() {
            // Sort by
            const sortBySelect = document.getElementById('sort-by');
            if (sortBySelect) {
                sortBySelect.addEventListener('change', (e) => {
                    this.state.sortBy = e.target.value || 'date_desc';
                    this.state.currentPage = 1;
                    this.loadArticles();
                });
            }

            // Category filter
            const categorySelect = document.getElementById('filter-category');
            if (categorySelect) {
                categorySelect.addEventListener('change', (e) => {
                    this.state.filters.category = e.target.value || null;
                    this.state.currentPage = 1;
                    this.loadArticles();
                });
            }

            // Featured filter
            const featuredSelect = document.getElementById('filter-featured');
            if (featuredSelect) {
                featuredSelect.addEventListener('change', (e) => {
                    this.state.filters.featured = e.target.value ? (e.target.value === 'true') : null;
                    this.state.currentPage = 1;
                    this.loadArticles();
                });
            }

            // Search
            const searchInput = document.getElementById('article-search');
            if (searchInput) {
                let searchTimeout;
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        this.searchArticles(e.target.value);
                    }, 300);
                });
            }

            // Clear filters
            const clearButton = document.getElementById('clear-filters');
            if (clearButton) {
                clearButton.addEventListener('click', () => {
                    this.clearFilters();
                });
            }
        },

        /**
         * Search articles
         */
        async searchArticles(query) {
            this.state.searchQuery = query;
            
            if (!query.trim()) {
                this.state.filteredArticles = this.state.articles;
                this.render();
                return;
            }

            try {
                this.showLoading();
                const results = await apiClient.searchArticles(query, this.state.filters);
                this.state.filteredArticles = results.data || results.items || results;
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
                category: this.state.category,
                featured: null,
                tag: null
            };
            this.state.currentPage = 1;
            this.state.sortBy = 'date_desc';
            this.state.searchQuery = '';

            // Reset form inputs
            document.querySelectorAll('[data-filter]').forEach(elem => {
                elem.value = '';
            });

            this.loadArticles();
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
                        this.loadArticles();
                        this.scrollToTop();
                    }
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    this.state.currentPage++;
                    this.loadArticles();
                    this.scrollToTop();
                });
            }
        },

        /**
         * Render articles
         */
        render() {
            if (!this.container) return;

            if (this.state.filteredArticles.length === 0) {
                this.container.innerHTML = `
                    <div class="alert alert-info text-center" role="alert">
                        <p class="mb-0">暂无相关文章</p>
                    </div>
                `;
                return;
            }

            this.container.innerHTML = this.state.filteredArticles.map(article =>
                this.createArticleCard(article)
            ).join('');

            // Add click handlers
            this.container.querySelectorAll('.article-card').forEach(card => {
                card.addEventListener('click', () => {
                    const articleId = card.dataset.articleId;
                    this.viewArticleDetails(articleId);
                });
            });
        },

        /**
         * Create article card HTML
         */
        createArticleCard(article) {
            const date = new Date(article.created_at);
            const formattedDate = date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
            const featuredBadge = article.is_featured ? '<span class="badge bg-warning text-dark me-2">⭐ 精选</span>' : '';
            const tags = article.tags ? article.tags.map(tag => 
                `<span class="badge bg-light text-dark me-1">${this.escapeHtml(tag)}</span>`
            ).join('') : '';

            return `
                <article class="col-md-6 mb-4 article-card" 
                         data-article-id="${article.id}"
                         aria-label="${this.escapeHtml(article.title)}">
                    <div class="card h-100 shadow-sm hover-lift">
                        ${article.featured_image ? `
                            <img src="${this.escapeHtml(article.featured_image)}" 
                                 class="card-img-top" 
                                 alt="${this.escapeHtml(article.title)}">
                        ` : ''}
                        <div class="card-body">
                            <div class="mb-2">
                                ${featuredBadge}
                                <span class="badge bg-secondary">${this.escapeHtml(article.category || '未分类')}</span>
                            </div>
                            <h3 class="card-title h5 mb-2">
                                <a href="/articles/${article.slug || article.id}/" class="text-decoration-none text-dark">
                                    ${this.escapeHtml(article.title)}
                                </a>
                            </h3>
                            <p class="card-text text-muted text-truncate-3">
                                ${this.escapeHtml(article.summary || article.content?.substring(0, 150) || '暂无摘要')}
                            </p>
                            ${tags ? `<div class="mb-3">${tags}</div>` : ''}
                        </div>
                        <div class="card-footer bg-light d-flex justify-content-between align-items-center">
                            <small class="text-muted">${formattedDate}</small>
                            <a href="/articles/${article.slug || article.id}/" class="btn btn-sm btn-outline-primary">阅读全文</a>
                        </div>
                    </div>
                </article>
            `;
        },

        /**
         * View article details
         */
        async viewArticleDetails(articleId) {
            try {
                const article = await apiClient.getArticle(articleId);
                window.location.href = `/articles/${article.slug || articleId}/`;
            } catch (error) {
                this.showError('加载文章失败');
                console.error('Failed to load article:', error);
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
                    <p class="mt-3 text-muted">加载文章中...</p>
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
    window.TrustAgency.ArticleManager = ArticleManager;

    // Auto-initialize if container exists
    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('articles-container')) {
            ArticleManager.init();
        }
    });

})();
