/* Minimal JavaScript - Focus on Enhancement Only */

/* ============================================
   Polyfills and Compatibility
   ============================================ */
if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        var el = this;
        do {
            if (Element.prototype.matches.call(el, s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}

// CustomEvent polyfill for IE
if (typeof window.CustomEvent !== "function") {
    function CustomEvent(event, params) {
        params = params || { bubbles: false, cancelable: false, detail: null };
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    }
    CustomEvent.prototype = window.Event.prototype;
    window.CustomEvent = CustomEvent;
}

/* ============================================
   Global Configuration
   ============================================ */
window.TrustAgency = window.TrustAgency || {};

TrustAgency.config = {
    debug: false,
    lang: 'zh-CN'
};

/* ============================================
   Initialization
   ============================================ */
document.addEventListener('DOMContentLoaded', function() {
    TrustAgency.init();
});

TrustAgency.init = function() {
    TrustAgency.initializeAccessibility();
    TrustAgency.initializeFormValidation();
    TrustAgency.initializeDropdowns();
    TrustAgency.initializeSmoothScroll();
    TrustAgency.initializeLazyLoad();
};

/* ============================================
   Accessibility Enhancements
   ============================================ */
TrustAgency.initializeAccessibility = function() {
    TrustAgency.setupFocusIndicators();
    TrustAgency.setupSkipToContent();
    TrustAgency.setupAriaLive();
    TrustAgency.setupMenuKeyboard();
};

TrustAgency.setupFocusIndicators = function() {
    var isKeyboardNav = false;
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            isKeyboardNav = true;
            document.body.classList.add('keyboard-nav');
        }
    });
    
    document.addEventListener('mousedown', function() {
        isKeyboardNav = false;
        document.body.classList.remove('keyboard-nav');
    });
};

TrustAgency.setupSkipToContent = function() {
    var skipLink = document.querySelector('.skip-to-content');
    if (!skipLink) return;
    
    skipLink.addEventListener('click', function(e) {
        e.preventDefault();
        var mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.setAttribute('tabindex', '-1');
            mainContent.focus();
            // Remove tabindex after focus
            mainContent.addEventListener('blur', function() {
                mainContent.removeAttribute('tabindex');
            });
        }
    });
};

TrustAgency.setupAriaLive = function() {
    // Create aria-live region for dynamic updates
    var liveRegion = document.querySelector('[aria-live="polite"]');
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);
    }
};

TrustAgency.announceToScreenReader = function(message) {
    var liveRegion = document.getElementById('live-region');
    if (liveRegion) {
        // Clear previous message
        liveRegion.textContent = '';
        // Use setTimeout to ensure screen reader picks up the change
        setTimeout(function() {
            liveRegion.textContent = message;
        }, 100);
    }
};

TrustAgency.setupMenuKeyboard = function() {
    // Handle dropdown menus with keyboard
    var dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    
    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                var menu = this.nextElementSibling;
                if (menu && menu.classList.contains('dropdown-menu')) {
                    var items = menu.querySelectorAll('.dropdown-item');
                    if (e.key === 'ArrowDown' && items.length > 0) {
                        items[0].focus();
                    }
                }
            }
        });
    });
};

/* ============================================
   Form Validation
   ============================================ */
TrustAgency.initializeFormValidation = function() {
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', TrustAgency.validateForm);
    });
};

TrustAgency.validateForm = function(e) {
    if (!this.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        TrustAgency.announceToScreenReader('表单中存在错误');
    }
    this.classList.add('was-validated');
};

/* ============================================
   Dropdown Handling
   ============================================ */
TrustAgency.initializeDropdowns = function() {
    // This is mainly handled by Bootstrap, but we can add extra functionality
    var dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(function(item) {
        item.addEventListener('click', function() {
            TrustAgency.announceToScreenReader('选择: ' + this.textContent);
        });
    });
};

/* ============================================
   Smooth Scroll for Anchor Links
   ============================================ */
TrustAgency.initializeSmoothScroll = function() {
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var targetId = this.getAttribute('href');
            var target = document.querySelector(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
                TrustAgency.announceToScreenReader('导航到: ' + (target.textContent || targetId));
            }
        });
    });
};

/* ============================================
   Search Functionality
   ============================================ */
TrustAgency.setupSearch = function() {
    var searchForm = document.getElementById('search-form');
    if (!searchForm) return;
    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var query = this.querySelector('input[type="search"]').value;
        if (query.trim()) {
            TrustAgency.announceToScreenReader('搜索: ' + query);
            // Redirect to search results page
            // window.location.href = '/search?q=' + encodeURIComponent(query);
            console.log('Search query:', query);
        }
    });
};

/* ============================================
   Lazy Load Images
   ============================================ */
TrustAgency.initializeLazyLoad = function() {
    if ('IntersectionObserver' in window) {
        var images = document.querySelectorAll('img[data-src]');
        if (images.length === 0) return;
        
        var imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    // Add loaded class for animation
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        images.forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        var images = document.querySelectorAll('img[data-src]');
        images.forEach(function(img) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
};

/* ============================================
   Dark Mode Toggle
   ============================================ */
TrustAgency.setupDarkModeToggle = function() {
    var darkModeToggle = document.getElementById('dark-mode-toggle');
    if (!darkModeToggle) return;
    
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var savedTheme = localStorage.getItem('theme');
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.setAttribute('data-bs-theme', 'dark');
        darkModeToggle.setAttribute('aria-pressed', 'true');
    }
    
    darkModeToggle.addEventListener('click', function() {
        var isDark = document.body.getAttribute('data-bs-theme') === 'dark';
        if (isDark) {
            document.body.removeAttribute('data-bs-theme');
            localStorage.setItem('theme', 'light');
            darkModeToggle.setAttribute('aria-pressed', 'false');
            TrustAgency.announceToScreenReader('切换到亮色模式');
        } else {
            document.body.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            darkModeToggle.setAttribute('aria-pressed', 'true');
            TrustAgency.announceToScreenReader('切换到深色模式');
        }
    });
};

/* ============================================
   Responsive Table Helper
   ============================================ */
TrustAgency.makeTableResponsive = function(tableSelector) {
    var tables = document.querySelectorAll(tableSelector || 'table');
    tables.forEach(function(table) {
        if (!table.closest('.table-responsive')) {
            var wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
};

/* ============================================
   Utility: Log
   ============================================ */
TrustAgency.log = function(message, level) {
    if (!TrustAgency.config.debug) return;
    
    level = level || 'info';
    var timestamp = new Date().toISOString();
    
    switch(level) {
        case 'error':
            console.error('[' + timestamp + '] ERROR:', message);
            break;
        case 'warn':
            console.warn('[' + timestamp + '] WARN:', message);
            break;
        default:
            console.log('[' + timestamp + '] INFO:', message);
    }
};

/* ============================================
   Public API Export
   ============================================ */
window.TrustAgency = TrustAgency;

// Backward compatibility
window.trustagency = {
    announceToScreenReader: TrustAgency.announceToScreenReader,
    setupLazyLoad: TrustAgency.initializeLazyLoad,
    setupDarkModeToggle: TrustAgency.setupDarkModeToggle,
    setupSearch: TrustAgency.setupSearch
};
