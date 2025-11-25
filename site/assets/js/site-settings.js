/**
 * 网站全局设置加载器
 * 自动从API获取网站设置并应用到页面
 */
(function() {
    'use strict';

    // API地址 - 自动检测开发/生产环境
    const getAPIUrl = () => {
        const port = window.location.port;
        if (port === '8001' || port === '8000') {
            return `${window.location.protocol}//${window.location.hostname}:${port}`;
        }
        return window.location.origin;
    };

    const API_URL = getAPIUrl();
    let siteSettings = null;

    // 获取网站设置
    async function fetchSiteSettings() {
        try {
            const response = await fetch(`${API_URL}/api/website-settings/`);
            if (response.ok) {
                siteSettings = await response.json();
                return siteSettings;
            }
        } catch (error) {
            console.warn('获取网站设置失败:', error);
        }
        return null;
    }

    // 更新页面标题，添加站点名称后缀
    function updatePageTitle(settings) {
        if (!settings || !settings.site_name) return;
        
        const currentTitle = document.title;
        const siteName = settings.site_name;
        
        // 如果标题已经包含站点名称，不重复添加
        if (currentTitle.includes(siteName)) return;
        
        // 如果当前标题为空或是默认标题，使用首页标题
        if (!currentTitle || currentTitle === siteName) {
            document.title = settings.site_title || siteName;
        } else {
            document.title = `${currentTitle} - ${siteName}`;
        }
    }

    // 注入统计代码到head
    function injectAnalytics(settings) {
        if (!settings) return;

        const head = document.head;

        // 百度统计
        if (settings.baidu_analytics && settings.baidu_analytics.trim()) {
            const baiduScript = document.createElement('div');
            baiduScript.innerHTML = settings.baidu_analytics;
            // 提取所有script标签并执行
            baiduScript.querySelectorAll('script').forEach(script => {
                const newScript = document.createElement('script');
                if (script.src) {
                    newScript.src = script.src;
                } else {
                    newScript.textContent = script.textContent;
                }
                head.appendChild(newScript);
            });
        }

        // Google Analytics
        if (settings.google_analytics && settings.google_analytics.trim()) {
            const gaScript = document.createElement('div');
            gaScript.innerHTML = settings.google_analytics;
            gaScript.querySelectorAll('script').forEach(script => {
                const newScript = document.createElement('script');
                if (script.src) {
                    newScript.src = script.src;
                    newScript.async = true;
                } else {
                    newScript.textContent = script.textContent;
                }
                head.appendChild(newScript);
            });
        }

        // 自定义脚本
        if (settings.custom_scripts && settings.custom_scripts.trim()) {
            const customScript = document.createElement('div');
            customScript.innerHTML = settings.custom_scripts;
            customScript.querySelectorAll('script').forEach(script => {
                const newScript = document.createElement('script');
                if (script.src) {
                    newScript.src = script.src;
                } else {
                    newScript.textContent = script.textContent;
                }
                head.appendChild(newScript);
            });
        }
    }

    // 更新页脚备案信息
    function updateFooter(settings) {
        if (!settings) return;

        // 查找或创建备案信息容器
        let icpContainer = document.getElementById('icp-info');
        
        // 如果页面没有预留容器，尝试在footer末尾添加
        if (!icpContainer) {
            const footer = document.querySelector('footer');
            if (footer) {
                icpContainer = document.createElement('div');
                icpContainer.id = 'icp-info';
                icpContainer.className = 'text-center mt-3';
                footer.appendChild(icpContainer);
            }
        }

        if (icpContainer) {
            let html = '';
            
            // 版权信息
            if (settings.company_name) {
                const year = new Date().getFullYear();
                html += `<p class="mb-1">© ${year} ${settings.company_name}. All Rights Reserved.</p>`;
            }
            
            // ICP备案号（有则显示，无则不显示）
            if (settings.icp_number && settings.icp_number.trim()) {
                html += `<p class="mb-1"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color: inherit; text-decoration: none;">${settings.icp_number}</a></p>`;
            }
            
            icpContainer.innerHTML = html;
        }
    }

    // 更新友情链接
    function updateFriendLinks(settings) {
        if (!settings || !settings.footer_links) return;

        let links = [];
        try {
            links = typeof settings.footer_links === 'string' 
                ? JSON.parse(settings.footer_links) 
                : settings.footer_links;
        } catch (e) {
            return;
        }

        if (!Array.isArray(links) || links.length === 0) return;

        // 查找友情链接容器
        let linksContainer = document.getElementById('friend-links');
        
        if (!linksContainer) {
            const footer = document.querySelector('footer');
            if (footer) {
                linksContainer = document.createElement('div');
                linksContainer.id = 'friend-links';
                linksContainer.className = 'text-center mt-2';
                footer.appendChild(linksContainer);
            }
        }

        if (linksContainer) {
            const linksHtml = links.map(link => 
                `<a href="${link.url}" target="_blank" rel="noopener" class="text-muted me-3">${link.name}</a>`
            ).join('');
            linksContainer.innerHTML = `<p class="mb-1">友情链接: ${linksHtml}</p>`;
        }
    }

    // 初始化
    async function init() {
        const settings = await fetchSiteSettings();
        if (settings) {
            updatePageTitle(settings);
            injectAnalytics(settings);
            updateFooter(settings);
            updateFriendLinks(settings);
        }
    }

    // 页面加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // 暴露给全局使用
    window.SiteSettings = {
        get: () => siteSettings,
        refresh: init
    };
})();

