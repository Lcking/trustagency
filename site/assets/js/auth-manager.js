/**
 * Authentication Module
 * Handles user login, registration, and token management
 */

(function() {
    'use strict';

    window.TrustAgency = window.TrustAgency || {};

    const AuthManager = {
        state: {
            currentUser: null,
            isAuthenticated: false,
            isLoading: false
        },

        /**
         * Initialize auth manager
         */
        async init() {
            this.setupAuthUI();
            await this.checkAuthStatus();
            this.setupEventListeners();
        },

        /**
         * Check if user is authenticated
         */
        async checkAuthStatus() {
            const token = apiClient.getToken();
            if (!token) {
                this.state.isAuthenticated = false;
                return;
            }

            try {
                this.state.currentUser = await apiClient.getCurrentUser();
                this.state.isAuthenticated = true;
                this.updateAuthUI();
            } catch (error) {
                apiClient.clearTokens();
                this.state.isAuthenticated = false;
            }
        },

        /**
         * Login
         */
        async login(username, password) {
            try {
                this.state.isLoading = true;
                const response = await apiClient.login(username, password);
                this.state.currentUser = response.user;
                this.state.isAuthenticated = true;
                this.updateAuthUI();
                window.dispatchEvent(new CustomEvent('auth:login', { detail: response.user }));
                return true;
            } catch (error) {
                console.error('Login failed:', error);
                window.dispatchEvent(new CustomEvent('auth:loginFailed', { detail: error.message }));
                return false;
            } finally {
                this.state.isLoading = false;
            }
        },

        /**
         * Register
         */
        async register(userData) {
            try {
                this.state.isLoading = true;
                const response = await apiClient.register(userData);
                this.state.currentUser = response.user;
                this.state.isAuthenticated = true;
                this.updateAuthUI();
                window.dispatchEvent(new CustomEvent('auth:register', { detail: response.user }));
                return true;
            } catch (error) {
                console.error('Registration failed:', error);
                window.dispatchEvent(new CustomEvent('auth:registerFailed', { detail: error.message }));
                return false;
            } finally {
                this.state.isLoading = false;
            }
        },

        /**
         * Logout
         */
        async logout() {
            try {
                await apiClient.logout();
                this.state.currentUser = null;
                this.state.isAuthenticated = false;
                this.updateAuthUI();
                window.dispatchEvent(new CustomEvent('auth:logout'));
            } catch (error) {
                console.error('Logout failed:', error);
                this.state.currentUser = null;
                this.state.isAuthenticated = false;
            }
        },

        /**
         * Setup authentication UI
         */
        setupAuthUI() {
            // Create auth container if it doesn't exist
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;

            const authContainer = document.createElement('div');
            authContainer.id = 'auth-container';
            authContainer.className = 'd-flex align-items-center';
            authContainer.innerHTML = `
                <div id="auth-anonymous" class="d-none">
                    <button type="button" class="btn btn-primary btn-sm" id="login-btn">登录</button>
                    <button type="button" class="btn btn-outline-primary btn-sm ms-2" id="register-btn">注册</button>
                </div>
                <div id="auth-authenticated" class="d-none">
                    <span class="text-muted me-3"><span id="user-name"></span></span>
                    <button type="button" class="btn btn-outline-danger btn-sm" id="logout-btn">登出</button>
                </div>
            `;

            const navbarNav = navbar.querySelector('.navbar-nav');
            const navbarCollapse = navbar.querySelector('.navbar-collapse');
            if (navbarNav && navbarCollapse) {
                // Insert after navbar-nav, inside the collapse div
                navbarNav.parentNode.insertBefore(authContainer, navbarNav.nextSibling);
            }
        },

        /**
         * Update auth UI based on authentication state
         */
        updateAuthUI() {
            const anonEl = document.getElementById('auth-anonymous');
            const authEl = document.getElementById('auth-authenticated');

            if (this.state.isAuthenticated && this.state.currentUser) {
                if (anonEl) anonEl.classList.add('d-none');
                if (authEl) {
                    authEl.classList.remove('d-none');
                    const nameEl = authEl.querySelector('#user-name');
                    if (nameEl) {
                        nameEl.textContent = this.state.currentUser.full_name || this.state.currentUser.username;
                    }
                }
            } else {
                if (anonEl) anonEl.classList.remove('d-none');
                if (authEl) authEl.classList.add('d-none');
            }
        },

        /**
         * Setup event listeners
         */
        setupEventListeners() {
            document.addEventListener('click', (e) => {
                if (e.target.id === 'login-btn') {
                    this.showLoginModal();
                } else if (e.target.id === 'register-btn') {
                    this.showRegisterModal();
                } else if (e.target.id === 'logout-btn') {
                    this.logout();
                }
            });

            // Listen for auth logout events
            window.addEventListener('auth:logout', () => {
                console.log('User logged out');
            });
        },

        /**
         * Show login modal
         */
        showLoginModal() {
            const html = `
                <div class="modal" id="login-modal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">登录</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <form id="login-form">
                                <div class="modal-body">
                                    <div class="mb-3">
                                        <label for="login-username" class="form-label">用户名</label>
                                        <input type="text" class="form-control" id="login-username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="login-password" class="form-label">密码</label>
                                        <input type="password" class="form-control" id="login-password" required>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                    <button type="submit" class="btn btn-primary">登录</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            `;

            const container = document.body;
            const existingModal = document.getElementById('login-modal');
            if (existingModal) existingModal.remove();

            container.insertAdjacentHTML('beforeend', html);
            const modalEl = document.getElementById('login-modal');
            const modal = new bootstrap.Modal(modalEl);

            const form = document.getElementById('login-form');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                if (await this.login(username, password)) {
                    modal.hide();
                    form.reset();
                }
            });

            modal.show();
        },

        /**
         * Show register modal
         */
        showRegisterModal() {
            const html = `
                <div class="modal" id="register-modal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">注册</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <form id="register-form">
                                <div class="modal-body">
                                    <div class="mb-3">
                                        <label for="register-username" class="form-label">用户名</label>
                                        <input type="text" class="form-control" id="register-username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="register-email" class="form-label">邮箱</label>
                                        <input type="email" class="form-control" id="register-email" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="register-password" class="form-label">密码</label>
                                        <input type="password" class="form-control" id="register-password" required>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                    <button type="submit" class="btn btn-primary">注册</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            `;

            const container = document.body;
            const existingModal = document.getElementById('register-modal');
            if (existingModal) existingModal.remove();

            container.insertAdjacentHTML('beforeend', html);
            const modalEl = document.getElementById('register-modal');
            const modal = new bootstrap.Modal(modalEl);

            const form = document.getElementById('register-form');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('register-username').value;
                const email = document.getElementById('register-email').value;
                const password = document.getElementById('register-password').value;

                if (await this.register({ username, email, password })) {
                    modal.hide();
                    form.reset();
                }
            });

            modal.show();
        }
    };

    // Export to global scope
    window.TrustAgency.AuthManager = AuthManager;

    // Auto-initialize
    // Check if DOM is already loaded (for scripts loaded after page load)
    if (document.readyState === 'loading') {
        // DOM is still loading
        document.addEventListener('DOMContentLoaded', function() {
            AuthManager.init();
        });
    } else {
        // DOM is already loaded
        AuthManager.init();
    }

})();
