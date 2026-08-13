// 开发: 直接连接到后端特定端口 (8001 或 8000)
// 生产: 使用相对根路径，由 Nginx 反向代理
const getAPIUrl = () => {
    const protocol = window.location.protocol;
    const host = window.location.hostname;
    const port = window.location.port;
    
    // 如果有显式端口（开发环境通常是 8001），直接连接到后端
    if (port === '8001' || port === '8000') {
        return `${protocol}//${host}:${port}`;
    }
    
    // 否则使用相对根路径（生产环境，由 Nginx 代理）
    return window.location.origin;
};

const API_URL = getAPIUrl();

// 调试模式：显示API URL
if (localStorage.getItem('debugMode') === 'true') {
    console.log('API_URL:', API_URL);
    console.log('Location:', window.location);
}

let token = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');

// ============= Token 管理和全局 Fetch 拦截器 =============
/**
 * 发送认证 API 请求并自动处理 401 错误（token 过期）
 * @param {string} url - API 地址
 * @param {object} options - fetch 选项
 * @returns {Promise<Response>}
 */
async function authenticatedFetch(url, options = {}) {
    const headers = options.headers || {};
    
    // 如果 token 存在，添加到请求头
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const fetchOptions = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(url, fetchOptions);
        
        // 如果返回 401（Unauthorized），token 可能已过期
        if (response.status === 401) {
            console.warn('Token 已过期或无效，请重新登录');
            // 清除无效的 token
            localStorage.removeItem('token');
            localStorage.removeItem('currentUser');
            token = null;
            currentUser = {};
            // 显示登录页面
            showLoginPage();
            showNotification('登录已过期，请重新登录', 'warning');
            return response;
        }
        
        return response;
    } catch (error) {
        console.error('API 请求失败:', error);
        throw error;
    }
}

// 全局 Fetch 拦截器 - 自动为所有 fetch 调用添加 token 和处理 401 错误
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const [resource, options = {}] = args;
    
    // 跳过登录请求（不需要 token）
    if (typeof resource === 'string' && resource.includes('/api/admin/login')) {
        return originalFetch.apply(this, args);
    }
    
    // 为其他 API 调用添加 token
    const modifiedOptions = { ...options };
    const headers = modifiedOptions.headers || {};
    
    if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    modifiedOptions.headers = headers;
    
    return originalFetch.call(this, resource, modifiedOptions).then(async response => {
        // 处理 401 错误 - token 过期
        if (response.status === 401 && typeof resource === 'string' && resource.includes('/api/')) {
            console.warn('Token 已过期或无效，请重新登录');
            localStorage.removeItem('token');
            localStorage.removeItem('currentUser');
            token = null;
            currentUser = {};
            
            // 如果当前显示的不是登录页面，则显示登录页面
            if (document.getElementById('mainPage') && document.getElementById('mainPage').style.display !== 'none') {
                showLoginPage();
                if (typeof showNotification === 'function') {
                    showNotification('登录已过期，请重新登录', 'warning');
                }
            }
        }
        
        return response;
    });
};

// 页面加载

document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 DOMContentLoaded fired');
    // 登录表单处理 - 必须在 DOMContentLoaded 内，确保 DOM 已加载
    const loginForm = document.getElementById('loginForm');
    console.log('📋 LoginForm element:', loginForm);
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            console.log('📨 Form submitted');
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            console.log('👤 Attempting login with:', username);

            try {
                const response = await fetch(`${API_URL}/api/admin/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                console.log('✅ Response:', response.ok, data);

                if (response.ok) {
                    token = data.access_token;
                    currentUser = data.user;
                    localStorage.setItem('token', token);
                    localStorage.setItem('currentUser', JSON.stringify(currentUser));
                    console.log('🎉 Login success');
                    showMainPage();
                    loadDashboard();
                    // 初始化批量生成表单和AI配置
                    loadTaskSections();
                    loadAIConfigsToSelect();
                } else {
                    console.error('❌ Login failed:', data.detail);
                    showError('loginError', data.detail || '登录失败');
                }
            } catch (error) {
                console.error('💥 Error:', error);
                showError('loginError', '网络错误: ' + error.message);
            }
        });
    }

    // 检查是否已登录
    if (token && currentUser.username) {
        showMainPage();
        loadDashboard();
        // 初始化批量生成表单
        loadTaskSections();
        // 初始化 AI 配置
        loadAIConfigsToSelect();
    } else {
        showLoginPage();
    }
});

// 显示页面
function showLoginPage() {
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('mainPage').style.display = 'none';
}

function showMainPage() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('mainPage').style.display = 'flex';
    document.getElementById('currentUsername').textContent = currentUser.username;
}

// 显示内容区
function showSection(section) {
    document.querySelectorAll('.content-section').forEach(el => {
        el.classList.remove('active');
    });
    document.querySelectorAll('.menu-item').forEach(el => {
        el.classList.remove('active');
    });

    document.getElementById(section).classList.add('active');
    document.querySelector(`[data-section="${section}"]`).classList.add('active');

    if (section === 'sections') loadSections();
    if (section === 'platforms') loadPlatforms();
    if (section === 'articles') loadArticles();
    if (section === 'tasks') loadTasks();
    if (section === 'ai-configs') loadAIConfigs();
    if (section === 'settings') initializeSettings();
}

// ============= 通知函数 =============
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 2000;
        max-width: 400px;
        word-wrap: break-word;
        animation: slideIn 0.3s ease-out;
    `;
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============= 栏目管理函数 =============
let currentSectionId = null;

async function loadSections() {
    try {
        const response = await fetch(`${API_URL}/api/sections`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            const sections = result.data || result;
            let html = '<div class="table-responsive"><table class="table"><thead><tr><th></th><th>栏目名</th><th>描述</th><th>需要平台</th><th>分类数</th><th>操作</th></tr></thead><tbody>';
            
            for (const section of sections) {
                const categoryCount = section.category_count || 0;
                const sectionId = section.id;
                
                // 主行
                html += `<tr id="section-row-${sectionId}">
                    <td style="width: 30px; text-align: center;">
                        <button class="expand-btn" onclick="toggleSectionDetails(${sectionId}, this)" title="展开/收起" style="border: none; background: none; cursor: pointer; font-size: 16px;">▶</button>
                    </td>
                    <td><strong>${section.name}</strong></td>
                    <td>${section.description || '-'}</td>
                    <td>${section.requires_platform ? '是' : '否'}</td>
                    <td>${categoryCount}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editSection(${sectionId})">编辑</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSection(${sectionId})">删除</button>
                    </td>
                </tr>`;
                
                // 分类详情行（初始隐藏）
                html += `<tr id="section-details-${sectionId}" style="display: none;">
                    <td colspan="6">
                        <div style="padding: 15px; background: #f9f9f9; border-radius: 4px;">
                            <h4 style="margin-top: 0;">分类列表</h4>
                            <div id="categories-list-${sectionId}" style="min-height: 100px; max-height: 300px; overflow-y: auto;">
                                <p style="color: #999;">加载中...</p>
                            </div>
                        </div>
                    </td>
                </tr>`;
            }
            
            html += '</tbody></table></div>';
            document.getElementById('sectionsContent').innerHTML = html;
        }
    } catch (error) {
        console.error('加载栏目失败:', error);
        document.getElementById('sectionsContent').innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
    }
}

// 切换栏目详情显示
async function toggleSectionDetails(sectionId, button) {
    const detailsRow = document.getElementById(`section-details-${sectionId}`);
    const isHidden = detailsRow.style.display === 'none';
    
    if (isHidden) {
        // 展开
        detailsRow.style.display = 'table-row';
        button.textContent = '▼';
        button.style.transform = 'none';
        
        // 加载分类信息
        await loadSectionCategoriesWithArticles(sectionId);
    } else {
        // 收起
        detailsRow.style.display = 'none';
        button.textContent = '▶';
        button.style.transform = 'none';
    }
}

// 加载栏目的分类及其文章数
async function loadSectionCategoriesWithArticles(sectionId) {
    try {
        // 使用新的API端点，直接获取分类及其文章数
        const categoriesResponse = await fetch(`${API_URL}/api/categories/section/${sectionId}/with-count`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!categoriesResponse.ok) {
            throw new Error(`获取分类列表失败: HTTP ${categoriesResponse.status}`);
        }
        
        const categories = await categoriesResponse.json();
        
        // 渲染添加分类的输入框和按钮
        let html = '<div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">';
        html += '<div style="display: flex; gap: 10px; margin-bottom: 10px;">';
        html += `<input type="text" id="newCategoryInput-${sectionId}" placeholder="输入新分类名称" style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">`;
        html += `<button class="btn btn-success" onclick="addCategoryToSectionDetails(${sectionId})">+ 添加分类</button>`;
        html += '</div>';
        html += '</div>';
        
        // 渲染分类表格，显示分类名、文章数和操作按钮
        html += '<table style="width: 100%; border-collapse: collapse;">';
        html += '<thead><tr style="background: #e8e8e8;"><th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">分类名</th><th style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; width: 100px;">文章数</th><th style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; width: 80px;">操作</th></tr></thead><tbody>';
        
        if (categories.length > 0) {
            for (const category of categories) {
                html += `<tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px;">${category.name}</td>
                    <td style="padding: 8px; text-align: center;"><span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">${category.article_count}</span></td>
                    <td style="padding: 8px; text-align: center;"><button class="btn btn-sm btn-danger" onclick="deleteCategoryFromDetails(${category.id}, ${sectionId})">删除</button></td>
                </tr>`;
            }
        } else {
            html += '<tr><td colspan="3" style="padding: 8px; text-align: center; color: #999;">该栏目下无分类</td></tr>';
        }
        
        html += '</tbody></table>';
        
        const listContainer = document.getElementById(`categories-list-${sectionId}`);
        if (listContainer) {
            listContainer.innerHTML = html;
        }
    } catch (error) {
        console.error('加载分类失败:', error);
        const listContainer = document.getElementById(`categories-list-${sectionId}`);
        if (listContainer) {
            listContainer.innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
        }
    }
}

// 在展开的栏目详情中添加分类
async function addCategoryToSectionDetails(sectionId) {
    const inputId = `newCategoryInput-${sectionId}`;
    const name = document.getElementById(inputId).value.trim();
    
    if (!name) {
        alert('请输入分类名称');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/categories`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                section_id: sectionId,
                is_active: true
            })
        });

        if (response.ok) {
            document.getElementById(inputId).value = '';
            // 重新加载分类列表
            await loadSectionCategoriesWithArticles(sectionId);
            showNotification('分类已添加', 'success');
        } else {
            const error = await response.json();
            alert('添加失败: ' + (error.detail || error.message || '未知错误'));
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

// 在展开的栏目详情中删除分类
async function deleteCategoryFromDetails(categoryId, sectionId) {
    if (!confirm('确定要删除此分类吗？')) return;

    try {
        const response = await fetch(`${API_URL}/api/categories/${categoryId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            // 重新加载分类列表
            await loadSectionCategoriesWithArticles(sectionId);
            showNotification('分类已删除', 'success');
        } else {
            const error = await response.json();
            alert('删除失败: ' + (error.detail || error.message || '未知错误'));
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

function showSectionForm() {
    currentSectionId = null;
    document.getElementById('sectionModalTitle').textContent = '新增栏目';
    document.getElementById('sectionForm').reset();
    document.getElementById('categoriesSection').style.display = 'none';
    document.getElementById('sectionModal').classList.add('active');
}

function closeSectionModal() {
    document.getElementById('sectionModal').classList.remove('active');
    currentSectionId = null;
}

async function editSection(sectionId) {
    try {
        const response = await fetch(`${API_URL}/api/sections/${sectionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const section = await response.json();
            currentSectionId = sectionId;
            document.getElementById('sectionModalTitle').textContent = '编辑栏目';
            document.getElementById('sectionName').value = section.name;
            document.getElementById('sectionSlug').value = section.slug;
            document.getElementById('sectionDescription').value = section.description || '';
            document.getElementById('sectionRequiresPlatform').checked = section.requires_platform || false;
            document.getElementById('sectionSortOrder').value = section.sort_order || 0;
            document.getElementById('sectionIsActive').checked = section.is_active !== false;
            document.getElementById('categoriesSection').style.display = 'block';
            loadCategoriesForSection(sectionId);
            document.getElementById('sectionModal').classList.add('active');
        }
    } catch (error) {
        alert('加载栏目失败: ' + error.message);
    }
}

async function saveSection(e) {
    e.preventDefault();
    const method = currentSectionId ? 'PUT' : 'POST';
    const url = currentSectionId ? `${API_URL}/api/sections/${currentSectionId}` : `${API_URL}/api/sections`;

    const data = {
        name: document.getElementById('sectionName').value,
        slug: document.getElementById('sectionSlug').value,
        description: document.getElementById('sectionDescription').value,
        requires_platform: document.getElementById('sectionRequiresPlatform').checked,
        sort_order: parseInt(document.getElementById('sectionSortOrder').value),
        is_active: document.getElementById('sectionIsActive').checked
    };

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showNotification(currentSectionId ? '栏目已更新' : '栏目已创建', 'success');
            closeSectionModal();
            loadSections();
        } else {
            let errorMsg = '保存失败';
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                try {
                    const error = await response.json();
                    errorMsg = error.detail || error.message || errorMsg;
                } catch (e) {
                    errorMsg = `HTTP ${response.status}`;
                }
            } else {
                errorMsg = `HTTP ${response.status}`;
            }
            showNotification(errorMsg, 'error');
        }
    } catch (error) {
        showNotification('错误: ' + error.message, 'error');
    }
}

async function deleteSection(sectionId) {
    if (!confirm('确定要删除此栏目吗？')) return;

    try {
        const response = await fetch(`${API_URL}/api/sections/${sectionId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('栏目已删除');
            loadSections();
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

async function loadCategoriesForSection(sectionId) {
    try {
        const response = await fetch(`${API_URL}/api/categories/section/${sectionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const categories = await response.json();
            let html = '';
            for (const cat of categories) {
                html += `<div style="padding: 8px; background: #f9f9f9; margin: 5px 0; border-radius: 3px; display: flex; justify-content: space-between;">
                    <span>${cat.name}</span>
                    <button class="btn btn-sm btn-danger" onclick="deleteCategory(${cat.id})">删除</button>
                </div>`;
            }
            document.getElementById('categoriesListContent').innerHTML = html || '<p>暂无分类</p>';
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

async function addCategoryToSection() {
    const name = document.getElementById('newCategoryName').value.trim();
    if (!name || !currentSectionId) {
        alert('请输入分类名称');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/categories`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                section_id: currentSectionId,
                is_active: true
            })
        });

        if (response.ok) {
            document.getElementById('newCategoryName').value = '';
            loadCategoriesForSection(currentSectionId);
        } else {
            const error = await response.json();
            alert('添加失败: ' + error.detail);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

async function deleteCategory(categoryId) {
    if (!confirm('确定要删除此分类吗？')) return;

    try {
        const response = await fetch(`${API_URL}/api/categories/${categoryId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            if (currentSectionId) {
                loadCategoriesForSection(currentSectionId);
            }
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

// 加载仪表板
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/api/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const stats = await response.json();
            document.getElementById('platformCount').textContent = stats.platforms_count;
            document.getElementById('articleCount').textContent = stats.articles_count;
            document.getElementById('publishedCount').textContent = stats.published_articles;
            document.getElementById('activeTaskCount').textContent = stats.active_tasks;
            document.getElementById('totalViews').textContent = stats.total_views;
        }

        // 检查 OpenAI 状态
        // 检查 AI 配置状态
        const aiConfigResponse = await fetch(`${API_URL}/api/ai-configs`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (aiConfigResponse.ok) {
            const result = await aiConfigResponse.json();
            const configs = result.data || result;
            const activeConfigs = configs.filter(c => c.is_active);
            const statusEl = document.getElementById('aiConfigStatusText');
            
            if (activeConfigs.length > 0) {
                // 有可用的配置
                const defaultConfig = activeConfigs.find(c => c.is_default) || activeConfigs[0];
                statusEl.innerHTML = `<span style="color: #4CAF50;">已配置 ✓</span> <small style="color: #666;">(${defaultConfig.provider})</small>`;
            } else if (configs.length > 0) {
                // 有配置但都未激活
                statusEl.innerHTML = `<span style="color: #ff9800;">未激活 ⚠</span> <small style="color: #666;">(${configs.length}个配置)</small>`;
            } else {
                // 没有配置
                statusEl.innerHTML = `<span style="color: #f44336;">未配置 ✗</span>`;
            }
        } else {
            document.getElementById('aiConfigStatusText').innerHTML = `<span style="color: #999;">无法检查</span>`;
        }
    } catch (error) {
        console.error('加载仪表板失败:', error);
    }
}

// 加载平台列表
async function loadPlatforms() {
    const search = document.getElementById('platformSearch').value;
    try {
        // 构建URL并正确编码search参数
        let url = `${API_URL}/api/platforms?skip=0&limit=20`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }
        
        console.log('加载平台列表:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            let html = '<table><thead><tr><th>名称</th><th>URL</th><th>状态</th><th>操作</th></tr></thead><tbody>';

            data.data.forEach(platform => {
                // 获取URL - 优先使用website_url，其次是url字段
                const platformUrl = platform.website_url || platform.url;
                const urlDisplay = platformUrl ? `<a href="${platformUrl}" target="_blank">${platformUrl}</a>` : '<span style="color: #999;">未设置</span>';
                
                html += `
                    <tr>
                        <td><strong>${platform.name}</strong></td>
                        <td>${urlDisplay}</td>
                        <td>${platform.is_active ? '<span class="badge badge-success">活跃</span>' : '<span class="badge badge-warning">禁用</span>'}</td>
                        <td>
                            <button class="btn btn-info btn-small" onclick="showPlatformForm(${platform.id})">编辑</button>
                            <button class="btn btn-danger btn-small" onclick="deletePlatform(${platform.id})">删除</button>
                        </td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            document.getElementById('platformsContent').innerHTML = html;
        } else {
            console.error('HTTP错误:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('响应内容:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('加载平台失败:', error);
        document.getElementById('platformsContent').innerHTML = `<p style="color: red;">加载失败: ${error.message}</p>`;
    }
}

async function deletePlatform(platformId) {
    if (!confirm('确定要删除这个平台吗？')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/platforms/${platformId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('删除成功！');
            loadPlatforms();
        } else {
            alert('删除失败');
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

// 加载文章列表
async function loadArticles() {
    const search = document.getElementById('articleSearch').value;
    try {
        const response = await fetch(
            `${API_URL}/api/articles?skip=0&limit=20${search ? '&search=' + search : ''}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );

        if (response.ok) {
            const data = await response.json();
            let html = '<table><thead><tr><th>标题</th><th>分类</th><th>浏览量</th><th>发布状态</th><th>操作</th></tr></thead><tbody>';

            data.data.forEach(article => {
                html += `
                    <tr>
                        <td><strong>${article.title}</strong></td>
                        <td>${article.category_name || article.category || '—'}</td>
                        <td>${article.view_count}</td>
                        <td>${article.is_published ? '<span class="badge badge-success">已发布</span>' : '<span class="badge badge-warning">草稿</span>'}</td>
                        <td>
                            <button class="btn btn-info btn-small" onclick="showArticleForm(${article.id})">编辑</button>
                            <button class="btn btn-secondary btn-small" onclick="viewArticleDetails(${article.id})">查看</button>
                            <a class="btn btn-success btn-small" target="_blank" href="/static/article_view.html?id=${article.id}">前台预览</a>
                            <button class="btn btn-danger btn-small" onclick="deleteArticle(${article.id})">删除</button>
                        </td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            document.getElementById('articlesContent').innerHTML = html;
        }
    } catch (error) {
        console.error('加载文章失败:', error);
    }
}

async function deleteArticle(articleId) {
    if (!confirm('确定要删除这篇文章吗？')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/articles/${articleId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('删除成功！');
            loadArticles();
        } else {
            alert('删除失败');
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

// 查看文章详情（弹窗显示全部内容）
async function viewArticleDetails(articleId) {
    try {
        const response = await fetch(`${API_URL}/api/articles/${articleId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            alert('获取文章详情失败');
            return;
        }
        const data = await response.json();
        // 构建详情弹窗
        const modalHtml = `
            <div id="articleDetailModal" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);display:flex;align-items:flex-start;justify-content:center;overflow:auto;z-index:10000;padding:40px 20px;">
                <div style="background:#fff;max-width:900px;width:100%;border-radius:8px;box-shadow:0 4px 18px rgba(0,0,0,.15);padding:24px;position:relative;font-size:14px;line-height:1.6;">
                    <h2 style="margin-top:0;margin-bottom:12px;">${data.title}</h2>
                    <div style="color:#666;font-size:12px;margin-bottom:16px;">栏目: ${data.section_id} | 分类: ${data.category || '—'} | 浏览: ${data.view_count} | 点赞: ${data.like_count} | 状态: ${data.is_published ? '已发布' : '草稿'}</div>
                    <div style="border:1px solid #eee;padding:16px;border-radius:6px;max-height:60vh;overflow:auto;" id="articleDetailContent">${data.content}</div>
                    <div style="margin-top:16px;text-align:right;">
                        <button onclick="document.getElementById('articleDetailModal').remove()" style="background:#666;color:#fff;border:none;padding:8px 14px;border-radius:4px;cursor:pointer;">关闭</button>
                        ${!data.is_published ? `<button onclick="publishArticle(${data.id})" style="background:#2d6a4f;color:#fff;border:none;padding:8px 14px;border-radius:4px;cursor:pointer;margin-left:8px;">立即发布</button>` : ''}
                    </div>
                </div>
            </div>
        `;
        // 插入到 body
        const existing = document.getElementById('articleDetailModal');
        if (existing) existing.remove();
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = modalHtml;
        document.body.appendChild(tempDiv.firstElementChild);
    } catch (error) {
        console.error('查看文章详情失败:', error);
        alert('查看失败: ' + error.message);
    }
}

// 立即发布（详情弹窗中的快捷方式）
async function publishArticle(articleId) {
    try {
        const response = await fetch(`${API_URL}/api/articles/${articleId}/publish`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            alert('发布成功');
            const detailModal = document.getElementById('articleDetailModal');
            if (detailModal) detailModal.remove();
            loadArticles();
        } else {
            alert('发布失败');
        }
    } catch (err) {
        alert('发布错误: ' + err.message);
    }
}

// ============ BUG_015 CLEAN CODE重构 ============
// 原问题：字符串拼接、缺少验证、代码重复、硬编码
// 改进：配置对象 + URLSearchParams + 验证函数 + 单一职责原则

// 配置管理
const TASK_QUERY_CONFIG = {
    DEFAULT_SKIP: 0,
    DEFAULT_LIMIT: 100,
    DATE_FORMAT: 'YYYY-MM-DD'
};

// 集中的状态映射管理（解决重复定义问题）
const TASK_STATUS_DISPLAY = {
    'PENDING': { class: 'badge-warning', label: '待处理' },
    'PROCESSING': { class: 'badge-info', label: '处理中' },
    'COMPLETED': { class: 'badge-success', label: '已完成' },
    'FAILED': { class: 'badge-danger', label: '已失败' },
    'pending': { class: 'badge-warning', label: '待处理' },
    'processing': { class: 'badge-info', label: '处理中' },
    'completed': { class: 'badge-success', label: '已完成' },
    'failed': { class: 'badge-danger', label: '已失败' }
};

// 验证函数：日期格式检查
function isValidDate(dateStr) {
    if (!dateStr) return true; // 空值有效（表示不筛选）
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(dateStr) && !isNaN(Date.parse(dateStr));
}

// 构建查询URL - 使用URLSearchParams避免字符串拼接
function buildTaskQueryUrl(filters) {
    const params = new URLSearchParams({
        skip: TASK_QUERY_CONFIG.DEFAULT_SKIP,
        limit: TASK_QUERY_CONFIG.DEFAULT_LIMIT
    });
    
    // 添加可选筛选条件
    if (filters.status && filters.status.trim()) {
        params.append('status', filters.status.trim());
    }
    if (filters.startDate) {
        if (!isValidDate(filters.startDate)) {
            console.warn('Invalid start date format:', filters.startDate);
            return null;
        }
        params.append('start_date', filters.startDate);
    }
    if (filters.endDate) {
        if (!isValidDate(filters.endDate)) {
            console.warn('Invalid end date format:', filters.endDate);
            return null;
        }
        params.append('end_date', filters.endDate);
    }
    
    return `${API_URL}/api/tasks?${params.toString()}`;
}

// 获取状态显示HTML
function getStatusBadgeHTML(status) {
    const statusConfig = TASK_STATUS_DISPLAY[status];
    if (!statusConfig) {
        return `<span class="badge">${status}</span>`;
    }
    return `<span class="badge ${statusConfig.class}">${statusConfig.label}</span>`;
}

// 加载任务列表
async function loadTasks() {
    const status = document.getElementById('taskStatus').value;
    const startDate = document.getElementById('taskStartDate').value;
    const endDate = document.getElementById('taskEndDate').value;
    
    try {
        // 验证 token 是否存在
        if (!token) {
            showNotification('⚠️ 尚未登录，请先登录', 'error');
            document.getElementById('tasksContent').innerHTML = '<div style="text-align: center; color: #f44336; padding: 20px;">❌ 尚未登录或 Token 已过期，请刷新页面重新登录</div>';
            return;
        }
        
        // 收集筛选条件
        const filters = { status, startDate, endDate };
        const apiUrl = buildTaskQueryUrl(filters);
        
        // 验证URL生成是否成功
        if (!apiUrl) {
            showNotification('❌ 筛选条件格式不正确', 'error');
            document.getElementById('tasksContent').innerHTML = '<div style="text-align: center; color: #f44336; padding: 20px;">❌ 日期格式错误，请使用 YYYY-MM-DD 格式</div>';
            return;
        }
        
        // 显示加载状态
        document.getElementById('tasksContent').innerHTML = '<div style="text-align: center; padding: 20px;"><p>📍 加载任务中...</p></div>';
        
        console.log('📍 正在查询任务:', apiUrl);
        
        const response = await fetch(apiUrl, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        console.log('📌 API 响应状态:', response.status, response.ok);

        if (response.ok) {
            const data = await response.json();
            console.log('✅ 任务数据:', data);
            
            let html = '<table style="width: 100%; border-collapse: collapse;"><thead><tr style="background: #f5f5f5; border-bottom: 2px solid #ddd;"><th style="padding: 10px; text-align: left;">批次ID</th><th style="padding: 10px;">栏目/分类</th><th style="padding: 10px;">状态</th><th style="padding: 10px;">进度</th><th style="padding: 10px;">创建时间</th><th style="padding: 10px;">操作</th></tr></thead><tbody>';

            if (data.items && data.items.length > 0) {
                data.items.forEach(task => {
                    const statusBadge = getStatusBadgeHTML(task.status);
                    const sectionCategory = task.section_name && task.category_name ? 
                        `${task.section_name} / ${task.category_name}` : 
                        '<span style="color: #999;">—</span>';
                    const progressBar = `
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="flex: 1; background: #e0e0e0; border-radius: 4px; height: 8px; overflow: hidden; min-width: 80px;">
                                <div style="width: ${task.progress || 0}%; background: #4CAF50; height: 100%;"></div>
                            </div>
                            <span style="font-size: 12px; color: #666; min-width: 50px;">${task.completed_count || 0}/${task.total_count || 0}</span>
                        </div>
                    `;

                    // 根据状态生成操作按钮
                    let actionButtons = `<button class="btn btn-info btn-small" onclick="viewTaskDetails('${task.task_id}')" title="查看详情">详情</button> `;
                    
                    if (task.status === 'pending' || task.status === 'processing') {
                        // 待处理/处理中 -> 可取消
                        actionButtons += `<button class="btn btn-warning btn-small" onclick="cancelTask('${task.task_id}')" title="取消任务">取消</button>`;
                    } else if (task.status === 'failed') {
                        // 失败 -> 可重试和删除
                        actionButtons += `<button class="btn btn-primary btn-small" onclick="retryTask('${task.task_id}')" title="重试任务">重试</button> `;
                        actionButtons += `<button class="btn btn-danger btn-small" onclick="deleteTask('${task.task_id}')" title="删除批次">删除</button>`;
                    } else if (task.status === 'completed') {
                        // 完成 -> 可删除
                        actionButtons += `<button class="btn btn-danger btn-small" onclick="deleteTask('${task.task_id}')" title="删除批次">删除</button>`;
                    }

                    html += `
                        <tr style="border-bottom: 1px solid #eee; hover: background: #f9f9f9;">
                            <td style="padding: 10px;"><code style="font-size: 11px;">${task.task_id}</code></td>
                            <td style="padding: 10px;">${sectionCategory}</td>
                            <td style="padding: 10px;">${statusBadge}</td>
                            <td style="padding: 10px;">${progressBar}</td>
                            <td style="padding: 10px;">${new Date(task.created_at).toLocaleString('zh-CN')}</td>
                            <td style="padding: 10px; white-space: nowrap;">
                                ${actionButtons}
                            </td>
                        </tr>
                    `;
                });
                showNotification(`✅ 加载成功 (${data.items.length} 个任务)`, 'success');
            } else {
                html += '<tr><td colspan="6" style="text-align: center; color: #999; padding: 20px;">暂无任务记录</td></tr>';
            }

            html += '</tbody></table>';
            document.getElementById('tasksContent').innerHTML = html;
        } else {
            // 处理 API 错误响应
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.detail || `API 错误: ${response.status}`;
            console.error('❌ API 错误:', response.status, errorMsg);
            showNotification(`❌ 加载失败: ${errorMsg}`, 'error');
            document.getElementById('tasksContent').innerHTML = `<div style="text-align: center; color: #f44336; padding: 20px;">❌ 加载任务失败<br/><small>${errorMsg}</small></div>`;
        }
    } catch (error) {
        console.error('💥 加载任务异常:', error);
        showNotification(`❌ 网络错误: ${error.message}`, 'error');
        document.getElementById('tasksContent').innerHTML = `<div style="text-align: center; color: #f44336; padding: 20px;">❌ 网络错误<br/><small>${error.message}</small></div>`;
    }
}

// 重置筛选条件 - Clean Code：单一职责原则
function resetTaskFilters() {
    document.getElementById('taskStatus').value = '';
    document.getElementById('taskStartDate').value = '';
    document.getElementById('taskEndDate').value = '';
    loadTasks();
}

async function viewTaskDetails(batchId) {
    try {
        const response = await fetch(`${API_URL}/api/tasks/${batchId}/details`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const task = await response.json();
            
            // 构建详细信息模态框HTML
            let modalHTML = `
                <div class="modal" id="taskDetailsModal" style="display: flex; align-items: center; justify-content: center; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000;">
                    <div class="modal-content" style="max-width: 900px; width: 90%; max-height: 85vh; overflow-y: auto; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                        <div style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                            <h2 style="margin: 0;">📋 任务详情</h2>
                            <span class="close" onclick="closeTaskDetailsModal()" style="cursor: pointer; font-size: 24px; color: #999;">&times;</span>
                        </div>
                        <div style="padding: 20px;">
                            <p><strong>批次ID:</strong> <code>${task.batch_id}</code></p>
                            <p><strong>栏目:</strong> ${task.section_name || '未知'}</p>
                            <p><strong>分类:</strong> ${task.category_name || '未知'}</p>
                            ${task.platform_name ? `<p><strong>平台:</strong> ${task.platform_name}</p>` : ''}
                            <p><strong>状态:</strong> 
                                ${task.status === 'pending' ? '<span class="badge badge-warning">待处理</span>' : 
                                  task.status === 'processing' ? '<span class="badge badge-info">处理中</span>' :
                                  task.status === 'completed' ? '<span class="badge badge-success">已完成</span>' :
                                  '<span class="badge badge-danger">已失败</span>'}
                            </p>
                            <p><strong>进度:</strong> ${task.completed_count || 0} / ${task.total_count || 0} (${task.progress || 0}%)</p>
                            <p><strong>创建时间:</strong> ${new Date(task.created_at).toLocaleString('zh-CN')}</p>
                        </div>

                        <h3>📝 生成的文章 (${task.total_count || 0}篇)</h3>
                        ${task.titles && task.titles.length > 0 ? `
                            <table style="width: 100%; margin-top: 10px;">
                                <thead>
                                    <tr>
                                        <th style="text-align: left; padding: 8px; background: #f0f0f0;">#</th>
                                        <th style="text-align: left; padding: 8px; background: #f0f0f0;">标题</th>
                                        <th style="text-align: left; padding: 8px; background: #f0f0f0;">状态</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${task.titles.map((title, index) => {
                                        const isCompleted = index < (task.completed_count || 0);
                                        const isFailed = task.failed_titles && task.failed_titles.includes(title);
                                        const statusText = isFailed ? '❌ 失败' : isCompleted ? '✅ 完成' : '⏳ 待处理';
                                        const statusColor = isFailed ? '#f44336' : isCompleted ? '#4CAF50' : '#999';
                                        return `
                                            <tr>
                                                <td style="padding: 8px;">${index + 1}</td>
                                                <td style="padding: 8px;">${title}</td>
                                                <td style="padding: 8px; color: ${statusColor};">${statusText}</td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        ` : '<p style="color: #999; text-align: center; padding: 20px;">无文章信息</p>'}

                        ${task.has_error && task.error_message ? `
                            <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 6px; margin-top: 20px;">
                                <h4 style="color: #856404; margin-top: 0;">⚠️ 错误信息</h4>
                                <pre style="background: white; padding: 10px; border-radius: 4px; overflow-x: auto;">${task.error_message}</pre>
                            </div>
                        ` : ''}

                        <div style="margin-top: 20px; text-align: right; border-top: 1px solid #eee; padding-top: 20px;">
                            <button class="btn btn-secondary" onclick="closeTaskDetailsModal()">关闭</button>
                        </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 将模态框添加到页面
            const existingModal = document.getElementById('taskDetailsModal');
            if (existingModal) {
                existingModal.remove();
            }
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        } else {
            alert('获取详情失败: ' + response.statusText);
        }
    } catch (error) {
        alert('获取详情失败: ' + error.message);
    }
}

function closeTaskDetailsModal() {
    const modal = document.getElementById('taskDetailsModal');
    if (modal) {
        modal.remove();
    }
}

// ============= 任务操作函数 =============

// 取消任务
async function cancelTask(taskId) {
    if (!confirm(`确定要取消任务 ${taskId} 吗？\n\n取消后任务将停止执行。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/tasks/${taskId}/cancel`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            showNotification('✅ 任务已取消', 'success');
            loadTasks(); // 刷新列表
        } else {
            const error = await response.json();
            showNotification(`❌ 取消失败: ${error.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ 网络错误: ${error.message}`, 'error');
    }
}

// 重试任务
async function retryTask(taskId) {
    if (!confirm(`确定要重试任务 ${taskId} 吗？\n\n将重新执行所有文章生成。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/tasks/${taskId}/retry`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            showNotification('✅ 任务已重新提交', 'success');
            loadTasks(); // 刷新列表
        } else {
            const error = await response.json();
            showNotification(`❌ 重试失败: ${error.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ 网络错误: ${error.message}`, 'error');
    }
}

// 删除任务
async function deleteTask(taskId) {
    if (!confirm(`确定要删除任务 ${taskId} 吗？\n\n注意：只会删除任务记录，已生成的文章不会被删除。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            showNotification('✅ 任务批次已删除', 'success');
            loadTasks(); // 刷新列表
        } else {
            const error = await response.json();
            showNotification(`❌ 删除失败: ${error.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ 网络错误: ${error.message}`, 'error');
    }
}

// 错误提示
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// ============= 平台管理函数 =============
let currentPlatformId = null;

async function showPlatformForm(platformId = null) {
    currentPlatformId = platformId;
    const modal = document.getElementById('platformModal');
    const title = document.getElementById('platformModalTitle');
    const form = document.getElementById('platformForm');
    
    if (platformId) {
        title.textContent = '编辑平台';
        
        try {
            // 先获取表单定义和平台数据
            const formDefResponse = await fetch(
                `${API_URL}/api/admin/platforms/form-definition`,
                { headers: { 'Authorization': `Bearer ${token}` } }
            );
            
            const platformDataResponse = await fetch(`${API_URL}/api/admin/platforms/${platformId}/edit`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (formDefResponse.ok && platformDataResponse.ok) {
                const formDef = await formDefResponse.json();
                const platformData = await platformDataResponse.json();
                
                // 编辑模式：传递平台数据用于隐藏空字段
                renderDynamicPlatformForm(formDef, platformData);
                populateFormFields(platformData);
            } else {
                showNotification('加载表单或数据失败', 'error');
            }
        } catch (error) {
            console.error('编辑表单错误:', error);
            showNotification('加载表单失败: ' + error.message, 'error');
        }
    } else {
        title.textContent = '新增平台';
        
        // 获取表单定义并动态渲染
        try {
            const response = await fetch(
                `${API_URL}/api/admin/platforms/create-form-definition`,
                { headers: { 'Authorization': `Bearer ${token}` } }
            );
            
            if (response.ok) {
                const formDef = await response.json();
                renderDynamicPlatformForm(formDef);
            } else {
                showNotification('获取表单定义失败，请重试', 'error');
                modal.classList.remove('active');
                return;
            }
        } catch (error) {
            console.error('获取表单定义错误:', error);
            showNotification('表单加载失败: ' + error.message, 'error');
            modal.classList.remove('active');
            return;
        }
        
        form.reset();
        // 设置默认值
        const activeCheckbox = document.getElementById('platform_is_active');
        if (activeCheckbox) {
            activeCheckbox.checked = true;
        }
    }
    modal.classList.add('active');
}

// ============ BUG_014 CLEAN CODE重构 ============
// 原问题：直接 shouldShow=true 是"头疼医头"的临时补丁，且 hasFieldValue 函数未被使用
// 改进：使用策略模式，清晰区分编辑和新增模式，考虑字段必填性，充分利用 hasFieldValue
const FIELD_VISIBILITY_RULES = {
    edit: (field = {}, data = {}) => {
        // 必填字段在编辑模式下总是显示
        if (field.required) {
            return true;
        }
        // 字段名缺失则显示（防止异常）
        if (!field.name) {
            return true;
        }
        // 修复BUG_003：编辑模式下显示所有已定义的字段，不论其是否有值
        // 这样用户可以编辑/添加原本为空的字段
        return true;
    },
    create: () => true // 新增模式显示所有字段
};

function hasFieldValue(data, fieldName) {
    // 强化判空判断，防止缺失数据或字段名时抛异常
    if (!data || !fieldName) {
        return false;
    }
    const val = data[fieldName];
    return val !== null && val !== undefined && val !== '';
}

function shouldDisplayField(field, existingData, isEditMode) {
    const rule = FIELD_VISIBILITY_RULES[isEditMode ? 'edit' : 'create'];
    return rule ? rule(field, existingData) : true;
}

function renderDynamicPlatformForm(formDefinition, existingData = null) {
    const formContainer = document.getElementById('platformForm');
    formContainer.innerHTML = '';
    const isEditMode = existingData !== null;
    
    // 为每个 section 生成表单字段
    formDefinition.sections.forEach(section => {
        // 添加 section 标题
        const sectionTitle = document.createElement('div');
        sectionTitle.className = 'form-section-title';
        sectionTitle.textContent = section.title;
        formContainer.appendChild(sectionTitle);
        
        // 添加字段
        if (section.fields && Array.isArray(section.fields)) {
            section.fields.forEach(field => {
                const shouldShow = shouldDisplayField(field, existingData, isEditMode);
                
                const fieldGroup = document.createElement('div');
                fieldGroup.className = 'form-group';
                if (!shouldShow) {
                    fieldGroup.style.display = 'none';
                }
                
                let input;
                
                // 处理 checkbox 和 boolean 类型
                if (field.type === 'checkbox' || field.type === 'boolean') {
                    input = document.createElement('input');
                    input.type = 'checkbox';
                    input.id = `platform_${field.name}`;
                    input.checked = field.default || false;
                    
                    const label = document.createElement('label');
                    label.style.display = 'flex';
                    label.style.alignItems = 'center';
                    label.style.gap = '8px';
                    label.appendChild(input);
                    label.appendChild(document.createTextNode(field.label));
                    fieldGroup.appendChild(label);
                } else {
                    // 其他字段类型
                    const label = document.createElement('label');
                    label.textContent = field.label;
                    if (field.required) {
                        label.innerHTML += ' <span style="color:red">*</span>';
                    }
                    fieldGroup.appendChild(label);
                    
                    switch(field.type) {
                        case 'text':
                            // 特殊处理 logo_url 字段：添加上传按钮
                            if (field.name === 'logo_url') {
                                const inputGroup = document.createElement('div');
                                inputGroup.className = 'input-group';
                                inputGroup.style.display = 'flex';
                                inputGroup.style.gap = '8px';
                                
                                input = document.createElement('input');
                                input.type = 'text';
                                input.id = `platform_${field.name}`;
                                input.placeholder = field.placeholder || 'https://... 或点击上传';
                                input.style.flex = '1';
                                
                                const uploadBtn = document.createElement('button');
                                uploadBtn.type = 'button';
                                uploadBtn.className = 'btn btn-outline-secondary';
                                uploadBtn.innerHTML = '📁 上传';
                                uploadBtn.onclick = () => triggerLogoUpload(input);
                                
                                const fileInput = document.createElement('input');
                                fileInput.type = 'file';
                                fileInput.id = 'logo_file_input';
                                fileInput.accept = 'image/*';
                                fileInput.style.display = 'none';
                                fileInput.onchange = (e) => handleLogoUpload(e, input);
                                
                                inputGroup.appendChild(input);
                                inputGroup.appendChild(uploadBtn);
                                inputGroup.appendChild(fileInput);
                                
                                // Logo 预览
                                const previewContainer = document.createElement('div');
                                previewContainer.id = 'logo_preview_container';
                                previewContainer.style.marginTop = '8px';
                                previewContainer.style.display = 'none';
                                previewContainer.innerHTML = `
                                    <img id="logo_preview" src="" alt="Logo预览" 
                                        style="max-width: 100px; max-height: 100px; border-radius: 8px; border: 1px solid #ddd;">
                                    <button type="button" class="btn btn-sm btn-outline-danger" style="margin-left: 8px;" 
                                        onclick="clearLogoPreview()">清除</button>
                                `;
                                
                                fieldGroup.appendChild(inputGroup);
                                fieldGroup.appendChild(previewContainer);
                                
                                // 监听输入变化更新预览
                                input.addEventListener('input', () => updateLogoPreview(input.value));
                            } else {
                                input = document.createElement('input');
                                input.type = 'text';
                                input.id = `platform_${field.name}`;
                                input.placeholder = field.placeholder || '';
                                input.required = field.required || false;
                            }
                            break;
                            
                        case 'number':
                            input = document.createElement('input');
                            input.type = 'number';
                            input.id = `platform_${field.name}`;
                            input.placeholder = field.placeholder || '';
                            if (field.min !== undefined) input.min = field.min;
                            if (field.max !== undefined) input.max = field.max;
                            input.step = field.step || '1';
                            input.required = field.required || false;
                            break;
                            
                        case 'textarea':
                            input = document.createElement('textarea');
                            input.id = `platform_${field.name}`;
                            input.placeholder = field.placeholder || '';
                            input.rows = 3;
                            input.required = field.required || false;
                            break;
                            
                        case 'select':
                            input = document.createElement('select');
                            input.id = `platform_${field.name}`;
                            input.required = field.required || false;
                            
                            const defaultOption = document.createElement('option');
                            defaultOption.value = '';
                            defaultOption.textContent = '请选择...';
                            input.appendChild(defaultOption);
                            
                            if (field.options && Array.isArray(field.options)) {
                                field.options.forEach(opt => {
                                    const option = document.createElement('option');
                                    option.value = opt.value;
                                    option.textContent = opt.label;
                                    input.appendChild(option);
                                });
                            }
                            break;
                            
                        case 'json':
                            input = document.createElement('textarea');
                            input.id = `platform_${field.name}`;
                            input.placeholder = field.placeholder || '输入 JSON 格式数据';
                            input.rows = 4;
                            input.className = 'json-editor';
                            break;
                            
                        default:
                            input = document.createElement('input');
                            input.type = 'text';
                            input.id = `platform_${field.name}`;
                            input.placeholder = field.placeholder || '';
                    }
                    
                    fieldGroup.appendChild(input);
                }
                
                formContainer.appendChild(fieldGroup);
            });
        }
    });
    
    // 添加底部按钮
    const newFooter = document.createElement('div');
    newFooter.className = 'modal-footer';
    newFooter.innerHTML = `
        <button type="button" class="btn btn-secondary" onclick="closePlatformModal()">取消</button>
        <button type="submit" class="btn btn-primary">保存</button>
    `;
    formContainer.appendChild(newFooter);
}

function populateFormFields(data) {
    // 填充所有动态生成的字段
    const fieldMapping = {
        'name': 'name',
        'slug': 'slug',
        'description': 'description',
        'website_url': 'website_url',
        'logo_url': 'logo_url',
        'rating': 'rating',
        'rank': 'rank',
        'founded_year': 'founded_year',
        'safety_rating': 'safety_rating',
        'platform_type': 'platform_type',
        'platform_source': 'platform_source',
        'is_active': 'is_active',
        'is_recommended': 'is_recommended',
        'is_regulated': 'is_regulated',
        'is_featured': 'is_featured',
        'overview_intro': 'overview_intro',
        'fee_table': 'fee_table',
        'safety_info': 'safety_info',
        'platform_badges': 'platform_badges',
        'top_badges': 'top_badges',
        'introduction': 'introduction',
        'main_features': 'main_features',
        'fee_structure': 'fee_structure',
        'why_choose': 'why_choose',
        'trading_conditions': 'trading_conditions',
        'fee_advantages': 'fee_advantages',
        'account_types': 'account_types',
        'trading_tools': 'trading_tools',
        'opening_steps': 'opening_steps',
        'security_measures': 'security_measures',
        'customer_support': 'customer_support',
        'learning_resources': 'learning_resources',
        'min_leverage': 'min_leverage',
        'max_leverage': 'max_leverage',
        'commission_rate': 'commission_rate',
        'fee_rate': 'fee_rate',
        'account_opening_link': 'account_opening_link'
    };
    
    Object.entries(fieldMapping).forEach(([fieldName, dataKey]) => {
        const elementId = `platform_${fieldName}`;
        const element = document.getElementById(elementId);
        
        if (element && data[dataKey] !== undefined) {
            const value = data[dataKey];
            
            if (element.type === 'checkbox') {
                element.checked = !!value;
            } else if (element.classList && element.classList.contains('json-editor')) {
                // JSON 字段
                element.value = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
            } else if (element.type === 'number') {
                // 0 是合法数值，不能用 || 判断，否则会把 0 当成空并在保存时写成 null
                element.value = (value === null || value === undefined) ? '' : value;
            } else {
                element.value = (value === null || value === undefined) ? '' : value;
            }
            
            // 特殊处理：Logo 预览
            if (fieldName === 'logo_url' && value) {
                updateLogoPreview(value);
            }
        }
    });
}

function closePlatformModal() {
    document.getElementById('platformModal').classList.remove('active');
    document.getElementById('platformForm').reset();
    currentPlatformId = null;
    // 清除 Logo 预览
    const previewContainer = document.getElementById('logo_preview_container');
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
}

// ============= Logo 上传相关函数 =============
function triggerLogoUpload(inputElement) {
    const fileInput = document.getElementById('logo_file_input');
    if (fileInput) {
        fileInput.click();
    }
}

async function handleLogoUpload(event, inputElement) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
        showNotification('请选择图片文件', 'error');
        return;
    }
    
    // 验证文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('图片大小不能超过 5MB', 'error');
        return;
    }
    
    try {
        showNotification('正在上传...', 'info');
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', 'logos');
        
        const response = await fetch(`${API_URL}/api/upload/image`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '上传失败');
        }
        
        const result = await response.json();
        
        // 设置 URL 到输入框
        inputElement.value = result.url;
        
        // 更新预览
        updateLogoPreview(result.url);
        
        showNotification('Logo 上传成功', 'success');
    } catch (error) {
        console.error('Logo upload error:', error);
        showNotification('上传失败: ' + error.message, 'error');
    }
    
    // 清空 file input
    event.target.value = '';
}

function updateLogoPreview(url) {
    const previewContainer = document.getElementById('logo_preview_container');
    const previewImg = document.getElementById('logo_preview');
    
    if (!previewContainer || !previewImg) return;
    
    if (url && url.trim() && !url.includes('example.com')) {
        previewImg.src = url;
        previewImg.onerror = () => {
            previewContainer.style.display = 'none';
        };
        previewImg.onload = () => {
            previewContainer.style.display = 'block';
        };
    } else {
        previewContainer.style.display = 'none';
    }
}

function clearLogoPreview() {
    const logoInput = document.getElementById('platform_logo_url');
    if (logoInput) {
        logoInput.value = '';
    }
    const previewContainer = document.getElementById('logo_preview_container');
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
}

async function savePlatform(e) {
    e.preventDefault();
    
    const platformData = {};
    
    // 收集所有动态生成的字段
    const form = document.getElementById('platformForm');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (input.id && input.id.startsWith('platform_')) {
            const fieldName = input.id.replace('platform_', '');
            
            if (input.type === 'checkbox') {
                platformData[fieldName] = input.checked;
            } else if (input.classList && input.classList.contains('json-editor')) {
                // JSON 字段 - 保持为字符串发送给后端
                // 后端 Schema 期望 Optional[str]，不是 JSON 对象
                const trimmedValue = input.value ? input.value.trim() : '';
                if (trimmedValue) {
                    // 验证是否为有效 JSON（但仍作为字符串发送）
                    try {
                        JSON.parse(trimmedValue);
                        platformData[fieldName] = trimmedValue; // 保持字符串格式
                    } catch (parseError) {
                        console.warn(`JSON格式无效 for field ${fieldName}:`, parseError);
                        // 如果不是有效 JSON，仍然作为字符串存储（后端会处理）
                        platformData[fieldName] = trimmedValue;
                    }
                } else {
                    platformData[fieldName] = null;
                }
            } else if (input.type === 'number') {
                // 空数字字段不提交，避免把 NOT NULL 列（如 commission_rate=0）误写成 null
                if (input.value !== '' && input.value !== null && input.value !== undefined) {
                    platformData[fieldName] = parseFloat(input.value);
                }
            } else {
                platformData[fieldName] = input.value;
            }
        }
    });

    try {
        const method = currentPlatformId ? 'POST' : 'POST';
        const url = currentPlatformId 
            ? `${API_URL}/api/admin/platforms/${currentPlatformId}/edit`
            : `${API_URL}/api/platforms`;

        const response = await authenticatedFetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(platformData)
        });

        if (response.ok) {
            showNotification(currentPlatformId ? '平台已更新' : '平台已创建', 'success');
            closePlatformModal();
            loadPlatforms();
        } else {
            let errorMsg = '保存失败';
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    const errorData = await response.json();
                    // 详细错误解析
                    if (errorData.detail) {
                        if (typeof errorData.detail === 'string') {
                            errorMsg = errorData.detail;
                        } else if (Array.isArray(errorData.detail)) {
                            // Pydantic 验证错误
                            errorMsg = errorData.detail.map(err => 
                                `${err.loc ? err.loc.join('.') : 'Field'}: ${err.msg}`
                            ).join('; ');
                        } else {
                            errorMsg = JSON.stringify(errorData.detail);
                        }
                    } else if (errorData.message) {
                        errorMsg = errorData.message;
                    } else {
                        errorMsg = `HTTP ${response.status}: ${JSON.stringify(errorData).substring(0, 100)}`;
                    }
                } catch (jsonError) {
                    errorMsg = `HTTP ${response.status}`;
                }
            } else {
                errorMsg = `HTTP ${response.status}`;
            }
            
            showNotification(errorMsg, 'error');
            console.error('保存失败详情:', {method, url, platformData, response});
        }
    } catch (error) {
        showNotification('错误: ' + error.message, 'error');
        console.error('保存平台异常:', error);
    }
}

// ============= 文章管理函数 =============
let currentArticleId = null;

async function loadPlatformsForSelect(selectId) {
    try {
        console.log('加载平台列表到select:', selectId);
        const response = await fetch(`${API_URL}/api/platforms?limit=100`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">选择平台...</option>';
        data.data.forEach(p => {
            select.innerHTML += `<option value="${p.id}">${p.name}</option>`;
        });
        console.log('成功加载', data.data.length, '个平台');
    } catch (error) {
        console.error('加载平台列表失败:', error);
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">加载失败</option>';
        }
    }
}

// 新增: 加载栏目列表 - 从 API 动态获取
async function loadSectionsForArticle() {
    try {
        // 从后端 API 获取栏目列表
        const response = await fetch(`${API_URL}/api/sections`);
        if (!response.ok) {
            throw new Error('Failed to fetch sections');
        }
        
        const result = await response.json();
        const sections = result.data;
        
        const select = document.getElementById('articleSection');
        select.innerHTML = '<option value="">选择栏目...</option>';
        sections.forEach(s => {
            select.innerHTML += `<option value="${s.id}" data-requires-platform="${s.requires_platform}">${s.name}</option>`;
        });
        
        console.log('栏目加载成功:', sections);
    } catch (error) {
        console.error('加载栏目失败:', error);
    }
}

async function loadCategoriesForSelect(selectId, sectionId) {
    try {
        const response = await fetch(`${API_URL}/api/categories/section/${sectionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const categories = await response.json();
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">选择分类</option>';
            categories.forEach(c => {
                select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

function updateArticlePlatformField(sectionId) {
    const sectionSelect = document.getElementById('articleSection');
    const selectedOption = sectionSelect.options[sectionSelect.selectedIndex];
    const requiresPlatform = selectedOption && selectedOption.getAttribute('data-requires-platform') === 'true';
    const platformFieldGroup = document.getElementById('articlePlatformFieldGroup');
    const platformField = document.getElementById('articlePlatform');

    if (requiresPlatform) {
        // 显示平台字段，且为必填
        platformFieldGroup.style.display = 'block';
        platformField.required = true;
        console.log('栏目需要关联平台，显示平台字段');
    } else {
        // 隐藏平台字段，且为可选
        platformFieldGroup.style.display = 'none';
        platformField.required = false;
        platformField.value = '';  // 清空选择
        console.log('栏目不需要平台，隐藏平台字段');
    }
}

// 新增: 栏目切换时的处理
function onArticleSectionChanged(options = {}) {
    const sectionSelect = document.getElementById('articleSection');
    const sectionId = sectionSelect.value;
    updateArticlePlatformField(sectionId);

    // 加载该栏目的分类
    if (!options.skipCategoryReload && sectionId) {
        loadCategoriesForSelect('articleCategory', sectionId);
    } else {
        document.getElementById('articleCategory').innerHTML = '<option value="">选择分类</option>';
    }
}

// ============= Markdown 批量导入函数 =============

let selectedMdFiles = []; // 存储选择的文件

// 显示导入模态框
async function showMarkdownImportModal() {
    const modal = document.getElementById('markdownImportModal');
    
    // 重置状态
    selectedMdFiles = [];
    updateFilesList();
    document.getElementById('importProgress').style.display = 'none';
    document.getElementById('importLog').innerHTML = '';
    document.getElementById('importSection').innerHTML = '<option value="">-- 选择栏目 --</option>';
    document.getElementById('importCategory').innerHTML = '<option value="">-- 先选择栏目 --</option>';
    document.getElementById('importPlatformGroup').style.display = 'none';
    
    // 显示模态框
    modal.classList.add('active');
    
    // 加载栏目列表
    await loadSectionsForImport();
}

// 关闭导入模态框
function closeMarkdownImportModal() {
    document.getElementById('markdownImportModal').classList.remove('active');
    selectedMdFiles = [];
}

// 加载栏目列表（用于导入）
async function loadSectionsForImport() {
    try {
        const response = await fetch(`${API_URL}/api/sections`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const result = await response.json();
            const sections = result.data;  // API返回 {data: [...]}
            const select = document.getElementById('importSection');
            select.innerHTML = '<option value="">-- 选择栏目 --</option>';
            sections.forEach(s => {
                select.innerHTML += `<option value="${s.id}" data-requires-platform="${s.requires_platform}">${s.name}</option>`;
            });
        }
    } catch (error) {
        console.error('加载栏目失败:', error);
    }
}

// 栏目变化时加载分类
async function onImportSectionChanged() {
    const sectionSelect = document.getElementById('importSection');
    const categorySelect = document.getElementById('importCategory');
    const platformGroup = document.getElementById('importPlatformGroup');
    const selectedOption = sectionSelect.options[sectionSelect.selectedIndex];
    
    categorySelect.innerHTML = '<option value="">-- 选择分类 --</option>';
    
    if (!sectionSelect.value) {
        platformGroup.style.display = 'none';
        return;
    }
    
    // 检查是否需要平台
    const requiresPlatform = selectedOption.getAttribute('data-requires-platform') === 'true';
    platformGroup.style.display = requiresPlatform ? 'block' : 'none';
    
    if (requiresPlatform) {
        await loadPlatformsForSelect('importPlatform');
    }
    
    // 加载分类 - 使用正确的API路径
    try {
        const response = await fetch(`${API_URL}/api/categories/section/${sectionSelect.value}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const categories = await response.json();
            categories.forEach(c => {
                categorySelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 处理文件拖拽
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('dropZone').style.borderColor = '#4CAF50';
    document.getElementById('dropZone').style.background = '#e8f5e9';
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('dropZone').style.borderColor = '#ccc';
    document.getElementById('dropZone').style.background = '#fafafa';
}

function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('dropZone').style.borderColor = '#ccc';
    document.getElementById('dropZone').style.background = '#fafafa';
    
    const files = Array.from(e.dataTransfer.files).filter(f => 
        f.name.endsWith('.md') || f.name.endsWith('.markdown')
    );
    addFiles(files);
}

// 处理文件选择
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
    e.target.value = ''; // 重置以便可以再次选择相同文件
}

// 添加文件到列表
function addFiles(files) {
    // 限制最多50个文件
    const remaining = 50 - selectedMdFiles.length;
    if (files.length > remaining) {
        showNotification(`⚠️ 最多只能导入50个文件，已添加前${remaining}个`, 'warning');
        files = files.slice(0, remaining);
    }
    
    // 去重
    files.forEach(file => {
        if (!selectedMdFiles.find(f => f.name === file.name)) {
            selectedMdFiles.push(file);
        }
    });
    
    updateFilesList();
}

// 更新文件列表显示
function updateFilesList() {
    const listContainer = document.getElementById('selectedFilesList');
    const listContent = document.getElementById('filesListContent');
    const countSpan = document.getElementById('selectedFilesCount');
    const importBtn = document.getElementById('startImportBtn');
    const importBtnCount = document.getElementById('importBtnCount');
    
    countSpan.textContent = selectedMdFiles.length;
    importBtnCount.textContent = selectedMdFiles.length;
    importBtn.disabled = selectedMdFiles.length === 0;
    
    if (selectedMdFiles.length === 0) {
        listContainer.style.display = 'none';
        return;
    }
    
    listContainer.style.display = 'block';
    listContent.innerHTML = selectedMdFiles.map((file, index) => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #eee;">
            <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                📄 ${file.name} <small style="color: #999;">(${(file.size / 1024).toFixed(1)}KB)</small>
            </span>
            <button type="button" onclick="removeFile(${index})" style="background: none; border: none; color: #f44336; cursor: pointer; padding: 2px 8px;">✕</button>
        </div>
    `).join('');
}

// 移除文件
function removeFile(index) {
    selectedMdFiles.splice(index, 1);
    updateFilesList();
}

// 解析 Markdown Frontmatter
function parseFrontmatter(content) {
    const frontmatterRegex = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
    const match = content.match(frontmatterRegex);
    
    if (match) {
        const frontmatter = {};
        const lines = match[1].split('\n');
        lines.forEach(line => {
            const colonIndex = line.indexOf(':');
            if (colonIndex > 0) {
                const key = line.substring(0, colonIndex).trim();
                const value = line.substring(colonIndex + 1).trim();
                frontmatter[key] = value;
            }
        });
        return {
            frontmatter,
            content: match[2]
        };
    }
    
    return { frontmatter: {}, content };
}

// 从文件名提取标题
function extractTitleFromFilename(filename) {
    return filename.replace(/\.(md|markdown)$/, '').replace(/[-_]/g, ' ');
}

// 生成 slug
function generateSlug(title) {
    return title
        .toLowerCase()
        .replace(/[^\w\s\u4e00-\u9fa5-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/^-+|-+$/g, '')
        + '-' + Date.now().toString(36);
}

// 开始导入
async function startMarkdownImport() {
    const sectionId = document.getElementById('importSection').value;
    const categoryId = document.getElementById('importCategory').value;
    const platformId = document.getElementById('importPlatform').value;
    const isPublished = document.getElementById('importAsPublished').checked;
    
    if (!sectionId || !categoryId) {
        showNotification('❌ 请选择栏目和分类', 'error');
        return;
    }
    
    // 检查是否需要平台
    const sectionSelect = document.getElementById('importSection');
    const selectedOption = sectionSelect.options[sectionSelect.selectedIndex];
    const requiresPlatform = selectedOption.getAttribute('data-requires-platform') === 'true';
    
    if (requiresPlatform && !platformId) {
        showNotification('❌ 该栏目需要选择关联平台', 'error');
        return;
    }
    
    if (selectedMdFiles.length === 0) {
        showNotification('❌ 请选择要导入的文件', 'error');
        return;
    }
    
    // 显示进度
    const progressDiv = document.getElementById('importProgress');
    const progressBar = document.getElementById('importProgressBar');
    const progressText = document.getElementById('importProgressText');
    const importLog = document.getElementById('importLog');
    const importBtn = document.getElementById('startImportBtn');
    
    progressDiv.style.display = 'block';
    importBtn.disabled = true;
    importBtn.textContent = '导入中...';
    importLog.innerHTML = '';
    
    let successCount = 0;
    let failCount = 0;
    const total = selectedMdFiles.length;
    
    for (let i = 0; i < selectedMdFiles.length; i++) {
        const file = selectedMdFiles[i];
        
        try {
            // 读取文件内容
            const text = await file.text();
            
            // 解析 frontmatter
            const { frontmatter, content } = parseFrontmatter(text);
            
            // 提取标题
            const title = frontmatter.title || extractTitleFromFilename(file.name);
            
            // 转换 Markdown 为 HTML
            const htmlContent = marked.parse(content);
            
            // 生成 slug
            const slug = generateSlug(title);
            
            // 创建文章
            const articleData = {
                title: title,
                slug: slug,
                content: htmlContent,
                summary: frontmatter.summary || frontmatter.description || '',
                section_id: parseInt(sectionId),
                category_id: parseInt(categoryId),
                platform_id: platformId ? parseInt(platformId) : null,
                tags: frontmatter.tags || '',
                is_published: isPublished,
                is_featured: false,
                meta_description: frontmatter.description || '',
                meta_keywords: frontmatter.keywords || frontmatter.tags || ''
            };
            
            const response = await fetch(`${API_URL}/api/articles`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(articleData)
            });
            
            if (response.ok) {
                successCount++;
                importLog.innerHTML += `<div style="color: #4CAF50;">✅ ${title}</div>`;
            } else {
                const error = await response.json();
                failCount++;
                importLog.innerHTML += `<div style="color: #f44336;">❌ ${title}: ${error.detail || '创建失败'}</div>`;
            }
            
        } catch (error) {
            failCount++;
            importLog.innerHTML += `<div style="color: #f44336;">❌ ${file.name}: ${error.message}</div>`;
        }
        
        // 更新进度
        const progress = ((i + 1) / total * 100).toFixed(0);
        progressBar.style.width = progress + '%';
        progressText.textContent = `${i + 1}/${total}`;
        
        // 滚动日志到底部
        importLog.scrollTop = importLog.scrollHeight;
    }
    
    // 完成
    importBtn.textContent = `开始导入 (${selectedMdFiles.length}篇)`;
    importBtn.disabled = false;
    
    showNotification(`📁 导入完成: ${successCount}篇成功, ${failCount}篇失败`, successCount > 0 ? 'success' : 'error');
    
    // 如果全部成功，刷新文章列表并关闭模态框
    if (failCount === 0) {
        setTimeout(() => {
            closeMarkdownImportModal();
            loadArticles();
        }, 1500);
    }
}

async function showArticleForm(articleId = null) {
    currentArticleId = articleId;
    const modal = document.getElementById('articleModal');
    const title = document.getElementById('articleModalTitle');
    const form = document.getElementById('articleForm');
    
    // 加载栏目
    await loadSectionsForArticle();
    await loadPlatformsForSelect('articlePlatform');
    
    if (articleId) {
        title.textContent = '编辑文章';
        fetch(`${API_URL}/api/articles/${articleId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json()).then(async data => {
            document.getElementById('articleId').value = data.id;
            document.getElementById('articleTitle').value = data.title;
            document.getElementById('articleSection').value = data.section_id || '';
            // 加载分类后设置选中值
            if (data.section_id) {
                await loadCategoriesForSelect('articleCategory', data.section_id);
            }
            const categorySelect = document.getElementById('articleCategory');
            const categoryValue = data.category_id ? String(data.category_id) : (data.category || '');
            if (categoryValue) {
                categorySelect.value = categoryValue;
            }
            document.getElementById('articlePlatform').value = data.platform_id || '';
            document.getElementById('articleSummary').value = data.summary || '';
            // 加载SEO字段
            document.getElementById('articleSeoTitle').value = data.seo_title || data.title || '';
            document.getElementById('articleSeoDescription').value = data.seo_description || data.meta_description || '';
            document.getElementById('articleSeoKeywords').value = data.seo_keywords || data.meta_keywords || '';
            // 更新SEO描述字数
            updateSeoDescCounter();
            // 🔥 修复：确保等待编辑器初始化完成后再显示内容
            await initArticleEditor(data.content || '');
            document.getElementById('articlePublished').checked = data.is_published;
            document.getElementById('articleFeatured').checked = data.is_featured;
            // 更新平台字段显示但不重新加载分类
            updateArticlePlatformField(data.section_id);
        });
    } else {
        title.textContent = '新增文章';
        form.reset();
        // 新建文章时初始化空编辑器
        await initArticleEditor('');
        updateArticlePlatformField('');
    }
    modal.classList.add('active');
}

function closeArticleModal() {
    document.getElementById('articleModal').classList.remove('active');
    document.getElementById('articleForm').reset();
    // 销毁编辑器
    if (articleEditor) {
        articleEditor.destroy();
        articleEditor = null;
    }
    currentArticleId = null;
}

// SEO字数统计
function updateSeoDescCounter() {
    const desc = document.getElementById('articleSeoDescription').value;
    const counter = document.getElementById('seoDescCounter');
    if (counter) {
        counter.textContent = desc.length;
    }
}

// 为SEO描述框添加字数统计监听
document.addEventListener('DOMContentLoaded', () => {
    const seoDescField = document.getElementById('articleSeoDescription');
    if (seoDescField) {
        seoDescField.addEventListener('input', updateSeoDescCounter);
    }
});

async function saveArticle(e) {
    e.preventDefault();
    
    // 获取编辑器内容
    let content = getEditorContent();
    
    // 如果编辑器未初始化，尝试从隐藏字段或fallback获取
    if (!content) {
        const fallbackElement = document.getElementById('articleContentFallback');
        if (fallbackElement) {
            content = fallbackElement.value;
        } else {
            content = document.getElementById('articleContent').value;
        }
    }
    
    // 获取栏目
    const sectionId = document.getElementById('articleSection').value;
    if (!sectionId) {
        alert('请选择栏目');
        return;
    }
    
    const title = document.getElementById('articleTitle').value;
    const categoryId = document.getElementById('articleCategory').value;
    
    if (!title || !categoryId || !content) {
        alert('请填写文章标题、分类和内容');
        return;
    }
    
    // 获取平台 ID（可能为空）
    const platformIdStr = document.getElementById('articlePlatform').value;
    let platformId = null;
    
    // 如果平台字段可见（表示该栏目需要平台），则验证必填
    const platformFieldGroup = document.getElementById('articlePlatformFieldGroup');
    if (platformFieldGroup.style.display !== 'none') {
        if (!platformIdStr) {
            alert('该栏目需要选择平台');
            return;
        }
        platformId = parseInt(platformIdStr);
    }
    
    const publishChecked = document.getElementById('articlePublished').checked;
    const articleData = {
        title: title,
        section_id: parseInt(sectionId),
        category_id: parseInt(categoryId),
        summary: document.getElementById('articleSummary').value || "",
        content: content,
        is_featured: document.getElementById('articleFeatured').checked,
        tags: "",
        meta_description: document.getElementById('articleSeoDescription').value || "",
        meta_keywords: document.getElementById('articleSeoKeywords').value || "",
        seo_title: document.getElementById('articleSeoTitle').value || "",
        platform_id: platformId,  // 可能为 null
        // 若为编辑模式，允许直接更新发布状态；新建则后续调用发布接口
        is_published: currentArticleId ? publishChecked : undefined
    };

    try {
        const method = currentArticleId ? 'PUT' : 'POST';
        let url = currentArticleId 
            ? `${API_URL}/api/articles/${currentArticleId}`
            : `${API_URL}/api/articles`;

        console.log('Saving article:', articleData);
        console.log('URL:', url);
        console.log('Method:', method);

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(articleData)
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Success:', result);

            // 新建且勾选“立即发布”，在保存成功后调用发布接口
            if (!currentArticleId && publishChecked) {
                try {
                    const pubResp = await fetch(`${API_URL}/api/articles/${result.id}/publish`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!pubResp.ok) {
                        console.warn('自动发布失败:', pubResp.status);
                        alert('文章已保存，但发布失败，请手动发布。');
                    }
                } catch (pubErr) {
                    console.error('自动发布异常:', pubErr);
                    alert('文章已保存，但发布请求异常，请稍后手动发布。');
                }
            }

            alert('保存成功！');
            closeArticleModal();
            loadArticles();
        } else {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            try {
                const error = JSON.parse(errorText);
                alert('保存失败: ' + (error.detail || JSON.stringify(error)));
            } catch(e) {
                alert('保存失败: ' + errorText.substring(0, 200));
            }
        }
    } catch (error) {
        console.error('Exception:', error);
        alert('错误: ' + error.message);
    }
}

// ============= AI 批量生成函数 =============
async function onTaskSectionChanged() {
    const sectionId = document.getElementById('taskSection').value;
    const platformGroup = document.getElementById('taskPlatformGroup');
    
    if (!sectionId) {
        platformGroup.style.display = 'none';
        document.getElementById('taskCategory').innerHTML = '<option value="">选择分类</option>';
        return;
    }
    
    // 加载该栏目的分类
    loadCategoriesForSelect('taskCategory', sectionId);

    try {
        const response = await fetch(`${API_URL}/api/sections/${sectionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const section = await response.json();
            
            if (section.requires_platform) {
                platformGroup.style.display = 'block';
                // 加载平台选项
                const platformResponse = await fetch(`${API_URL}/api/platforms`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (platformResponse.ok) {
                    const result = await platformResponse.json();
                    const platforms = result.data || result;  // 处理两种响应格式
                    let html = '<option value="">选择平台</option>';
                    platforms.forEach(platform => {
                        html += `<option value="${platform.id}">${platform.name}</option>`;
                    });
                    document.getElementById('taskPlatform').innerHTML = html;
                }
            } else {
                platformGroup.style.display = 'none';
                document.getElementById('taskPlatform').value = '';
            }
        }
    } catch (error) {
        console.error('加载栏目信息失败:', error);
    }
}

async function submitGenerationTask() {
    const titles = document.getElementById('taskTitles').value
        .split('\n')
        .map(t => t.trim())
        .filter(t => t.length > 0);
    
    if (titles.length === 0) {
        alert('请输入至少一个标题');
        return;
    }

    const sectionId = document.getElementById('taskSection').value;
    const categoryId = document.getElementById('taskCategory').value;
    const aiConfigId = document.getElementById('taskAIConfig').value;
    const platformId = document.getElementById('taskPlatform').value;
    const platformGroup = document.getElementById('taskPlatformGroup');

    if (!sectionId || !categoryId) {
        alert('请选择栏目和分类');
        return;
    }

    // 检查是否需要平台
    if (platformGroup.style.display !== 'none' && !platformId) {
        alert('该栏目需要选择关联平台');
        return;
    }

    try {
        const body = {
            titles: titles,
            section_id: parseInt(sectionId),
            category_id: parseInt(categoryId),
            batch_name: `Batch ${new Date().toLocaleString('zh-CN')}`
        };
        
        // 如果有平台，添加到请求中
        if (platformId) {
            body.platform_id = parseInt(platformId);
        }
        
        // 如果选择了AI配置，添加到请求中
        if (aiConfigId) {
            body.ai_config_id = parseInt(aiConfigId);
        }
        
        // 是否直接发布
        const autoPublish = document.getElementById('taskAutoPublish').checked;
        body.auto_publish = autoPublish;

        const response = await fetch(`${API_URL}/api/tasks/generate-articles`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });

        if (response.ok) {
            const result = await response.json();
            alert(`✅ 任务已提交！任务ID: ${result.task_id}`);
            document.getElementById('taskTitles').value = '';
            document.getElementById('taskSection').value = '';
            document.getElementById('taskCategory').value = '';
            document.getElementById('taskPlatform').value = '';
            loadTasks();
        } else {
            const error = await response.json();
            alert('提交失败: ' + error.detail);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

// 初始化栏目选择
async function loadTaskSections() {
    try {
        const response = await fetch(`${API_URL}/api/sections`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            const sections = result.data || result;  // 处理两种响应格式
            let html = '<option value="">选择栏目</option>';
            sections.forEach(section => {
                html += `<option value="${section.id}">${section.name}</option>`;
            });
            
            if (document.getElementById('taskSection')) {
                document.getElementById('taskSection').innerHTML = html;
            }
        }
    } catch (error) {
        console.error('加载栏目失败:', error);
    }
}

// 当栏目改变时，更新分类列表
document.addEventListener('DOMContentLoaded', function() {
    // 监听栏目变化（在表单加载完成后）
    setTimeout(() => {
        const taskSectionSelect = document.getElementById('taskSection');
        if (taskSectionSelect) {
            taskSectionSelect.addEventListener('change', async function() {
                const sectionId = this.value;
                const categorySelect = document.getElementById('taskCategory');
                
                if (!sectionId || !categorySelect) {
                    if (categorySelect) {
                        categorySelect.innerHTML = '<option value="">选择分类</option>';
                    }
                    return;
                }
                
                // 使用 loadCategoriesForSelect 函数从 categories API 获取分类
                await loadCategoriesForSelect('taskCategory', sectionId);
            });
        }
    }, 500);
});

// ============= AI配置管理函数 =============
async function loadAIConfigsToSelect() {
    try {
        const response = await fetch(`${API_URL}/api/ai-configs`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            const configs = result.data || result;
            let selectHtml = '<option value="">使用默认配置</option>';
            configs.forEach(config => {
                selectHtml += `<option value="${config.id}">${config.provider} - ${config.model_name}</option>`;
            });
            
            if (document.getElementById('taskAIConfig')) {
                document.getElementById('taskAIConfig').innerHTML = selectHtml;
            }
        }
    } catch (error) {
        console.error('加载AI配置失败:', error);
    }
}

async function loadAIConfigs() {
    try {
        const response = await fetch(`${API_URL}/api/ai-configs`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            const configs = result.data || result;
            let html = '<table class="table"><tr><th>服务商</th><th>模型</th><th>API端点</th><th>默认</th><th>操作</th></tr>';
            
            // 同时更新任务表单中的配置选择下拉框
            let selectHtml = '<option value="">使用默认配置</option>';
            configs.forEach(config => {
                selectHtml += `<option value="${config.id}">${config.provider} - ${config.model_name}</option>`;
                html += `<tr>
                    <td>${config.provider}</td>
                    <td>${config.model_name}</td>
                    <td style="word-break: break-all; max-width: 300px; font-size: 12px;">${config.api_endpoint}</td>
                    <td>
                        <input type="radio" name="default_config" ${config.is_default ? 'checked' : ''} 
                               onchange="setDefaultAIConfig(${config.id})">
                    </td>
                    <td style="white-space: nowrap;">
                        <button class="btn btn-sm btn-info" onclick="testExistingAIConfig(${config.id}, this)" title="测试连接">🧪 测试</button>
                        <button class="btn btn-sm btn-primary" onclick="editAIConfig(${config.id})">编辑</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteAIConfig(${config.id})">删除</button>
                    </td>
                </tr>`;
            });
            
            html += '</table>';
            document.getElementById('aiConfigsContent').innerHTML = html;
            
            // 更新任务表单中的下拉框
            if (document.getElementById('taskAIConfig')) {
                document.getElementById('taskAIConfig').innerHTML = selectHtml;
            }
        } else {
            document.getElementById('aiConfigsContent').innerHTML = '<p style="color: red;">加载失败</p>';
        }
    } catch (error) {
        document.getElementById('aiConfigsContent').innerHTML = '<p style="color: red;">错误: ' + error.message + '</p>';
    }
}

async function testAIConfig() {
    if (!token) {
        alert('请先登录');
        return;
    }

    const endpoint = document.getElementById('newConfigEndpoint').value;
    const apiKey = document.getElementById('newConfigAPIKey').value;
    const model = document.getElementById('newConfigModel').value;

    if (!endpoint || !apiKey || !model) {
        alert('请填写 API 端点、密钥和模型名称');
        return;
    }

    // 显示加载状态
    const testStatusDiv = document.getElementById('testStatus');
    testStatusDiv.className = 'test-status test-status-loading active';
    testStatusDiv.textContent = '⏳ 测试中...';

    try {
        const response = await fetch(`${API_URL}/api/ai-configs/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                api_endpoint: endpoint,
                api_key: apiKey,
                model_name: model
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 显示成功状态
            testStatusDiv.className = 'test-status test-status-success active';
            testStatusDiv.textContent = '✅ 连接成功！API 可正常访问';
            console.log('Test result:', data);
        } else {
            // 显示失败状态
            testStatusDiv.className = 'test-status test-status-error active';
            testStatusDiv.textContent = '❌ 连接失败: ' + (data.error || '未知错误');
            console.error('Test error:', data);
        }
    } catch (error) {
        testStatusDiv.className = 'test-status test-status-error active';
        testStatusDiv.textContent = '❌ 错误: ' + error.message;
        console.error('Test exception:', error);
    }
}

async function createAIConfig() {
    if (!token) {
        alert('请先登录');
        return;
    }

    const name = document.getElementById('newConfigName').value;
    const provider = document.getElementById('newConfigProvider').value;
    const model = document.getElementById('newConfigModel').value;
    const endpoint = document.getElementById('newConfigEndpoint').value;
    const apiKey = document.getElementById('newConfigAPIKey').value;
    const systemPrompt = document.getElementById('newConfigSystemPrompt').value;
    const temperature = parseFloat(document.getElementById('newConfigTemperature').value);
    const maxTokens = parseInt(document.getElementById('newConfigMaxTokens').value);
    const retries = parseInt(document.getElementById('newConfigRetries').value);

    if (!name || !provider || !model || !endpoint || !apiKey) {
        alert('请填写必填字段');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/ai-configs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name,
                provider,
                model_name: model,
                api_endpoint: endpoint,
                api_key: apiKey,
                system_prompt: systemPrompt,
                temperature,
                max_tokens: maxTokens,
                retry_times: retries
            })
        });

        if (response.ok) {
            alert('✅ 配置创建成功！');
            // 清空表单
            document.getElementById('newConfigName').value = '';
            document.getElementById('newConfigProvider').value = '';
            document.getElementById('newConfigModel').value = '';
            document.getElementById('newConfigEndpoint').value = '';
            document.getElementById('newConfigAPIKey').value = '';
            document.getElementById('newConfigSystemPrompt').value = '';
            document.getElementById('newConfigTemperature').value = '7';
            document.getElementById('newConfigMaxTokens').value = '2000';
            document.getElementById('newConfigRetries').value = '3';
            loadAIConfigs();
        } else {
            const error = await response.json();
            alert('创建失败: ' + error.detail);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

// 测试已存在的 AI 配置（从列表按钮点击）
async function testExistingAIConfig(configId, btnElement) {
    if (!token) {
        alert('请先登录');
        return;
    }
    
    // 保存按钮引用和原始文本（btnElement 通过参数传入）
    const btn = btnElement;
    const originalText = btn.innerHTML;
    
    try {
        // 显示正在测试的提示
        btn.innerHTML = '⏳ 测试中...';
        btn.disabled = true;
        
        // 获取配置信息
        const configResp = await fetch(`${API_URL}/api/ai-configs/${configId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!configResp.ok) {
            btn.innerHTML = originalText;
            btn.disabled = false;
            alert('❌ 获取配置失败');
            return;
        }
        
        const config = await configResp.json();
        
        // 调用测试 API
        const testResp = await fetch(`${API_URL}/api/ai-configs/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                api_endpoint: config.api_endpoint,
                api_key: config.api_key,
                model_name: config.model_name
            })
        });
        
        const result = await testResp.json();
        
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        if (result.success) {
            alert(`✅ ${config.provider} 连接成功！\n\n模型: ${config.model_name}\n响应时间: ${result.response_time || 'N/A'}ms\n\n${result.message || ''}`);
        } else {
            alert(`❌ ${config.provider} 连接失败！\n\n错误: ${result.error || result.message || '未知错误'}`);
        }
    } catch (error) {
        // 恢复按钮状态
        btn.innerHTML = originalText;
        btn.disabled = false;
        alert('测试失败: ' + error.message);
    }
}

// 在编辑弹窗中测试 AI 配置
async function testExistingAIConfigInEdit(configId, btn) {
    if (!token) {
        alert('请先登录');
        return;
    }
    
    const endpoint = document.getElementById('editApiEndpoint').value;
    const apiKey = document.getElementById('editApiKey').value;
    const model = document.getElementById('editModelName').value;
    
    if (!endpoint || !apiKey || !model) {
        alert('请填写 API 端点、密钥和模型名称');
        return;
    }
    
    // 显示正在测试（btn 通过参数传入）
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ 测试中...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/api/ai-configs/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                api_endpoint: endpoint,
                api_key: apiKey,
                model_name: model
            })
        });
        
        const result = await response.json();
        
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        if (result.success) {
            alert(`✅ 连接测试成功！\n\n响应时间: ${result.response_time || 'N/A'}ms\n\n${result.message || ''}`);
        } else {
            alert(`❌ 连接测试失败！\n\n错误: ${result.error || result.message || '未知错误'}`);
        }
    } catch (error) {
        btn.innerHTML = originalText;
        btn.disabled = false;
        alert('测试失败: ' + error.message);
    }
}

async function deleteAIConfig(configId) {
    if (!token) {
        alert('请先登录');
        return;
    }

    if (!confirm('确定要删除这个配置吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/ai-configs/${configId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('✅ 配置已删除！');
            loadAIConfigs();
        } else {
            const error = await response.json();
            alert('删除失败: ' + error.detail);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    }
}

async function editAIConfig(configId) {
    if (!token) {
        alert('请先登录');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/ai-configs/${configId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const config = await response.json();
            
            // 创建编辑模态框
            const modal = document.createElement('div');
            modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);display:flex;align-items:flex-start;justify-content:center;overflow:auto;z-index:10000;padding:40px 20px;';
            modal.id = 'aiConfigEditModal';
            
            const form = document.createElement('div');
            form.style.cssText = 'background:white;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.15);padding:30px;max-width:600px;width:100%;';
            
            // 对系统提示词内容进行安全转义
            const systemPromptValue = (config.system_prompt || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            
            form.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                    <h2 style="margin:0;">编辑 AI 配置</h2>
                    <button onclick="document.getElementById('aiConfigEditModal').remove()" style="background:none;border:none;font-size:24px;cursor:pointer;">&times;</button>
                </div>
                
                <form id="aiConfigEditForm" onsubmit="saveAIConfig(event, ${configId})">
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">配置名称</label>
                        <input type="text" id="editConfigName" value="${config.name}" readonly style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;background:#f5f5f5;" />
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">提供商</label>
                        <input type="text" id="editConfigProvider" value="${config.provider}" readonly style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;background:#f5f5f5;" />
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">模型名称</label>
                        <input type="text" id="editModelName" value="${config.model_name}" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">API 端点</label>
                        <input type="text" id="editApiEndpoint" value="${config.api_endpoint || ''}" placeholder="https://..." style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">API 密钥</label>
                        <input type="password" id="editApiKey" value="${config.api_key || ''}" placeholder="**** (仅修改时输入新密钥)" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">📝 系统提示词</label>
                        <textarea id="editSystemPrompt" rows="5" placeholder="定义AI的角色和输出风格，例如：你是一个专业的财务内容撰稿人..." style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;resize:vertical;font-family:inherit;">${systemPromptValue}</textarea>
                        <small style="color:#666;">系统提示词决定AI的角色定位和写作风格，建议包含专业领域说明</small>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:15px;">
                        <div>
                            <label style="display:block;margin-bottom:5px;font-weight:bold;">最大令牌数</label>
                            <input type="number" id="editMaxTokens" value="${config.max_tokens || 8000}" min="100" max="100000" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                            <small style="color:#666;">范围: 100-100000</small>
                        </div>
                        
                        <div>
                            <label style="display:block;margin-bottom:5px;font-weight:bold;">温度</label>
                            <input type="number" id="editTemperature" value="${config.temperature || 7}" min="0" max="100" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                            <small style="color:#666;">范围: 0-100</small>
                        </div>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:15px;">
                        <div>
                            <label style="display:block;margin-bottom:5px;font-weight:bold;">Top P 采样</label>
                            <input type="number" id="editTopP" value="${config.top_p || 90}" min="0" max="100" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                            <small style="color:#666;">范围: 0-100</small>
                        </div>
                        
                        <div>
                            <label style="display:block;margin-bottom:5px;font-weight:bold;">超时时间 (秒)</label>
                            <input type="number" id="editTimeoutSeconds" value="${config.timeout_seconds || 120}" min="10" max="600" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;" />
                        </div>
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <label style="display:block;margin-bottom:5px;font-weight:bold;">
                            <input type="checkbox" id="editIsActive" ${config.is_active ? 'checked' : ''} /> 激活此配置
                        </label>
                    </div>
                    
                    <div style="display:flex;gap:10px;justify-content:flex-end;">
                        <button type="button" class="btn btn-info" onclick="testExistingAIConfigInEdit(${configId}, this)" style="padding:10px 20px;">🧪 测试连接</button>
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('aiConfigEditModal').remove()" style="padding:10px 20px;">取消</button>
                        <button type="submit" class="btn btn-success" style="padding:10px 20px;">保存配置</button>
                    </div>
                </form>
            `;
            
            modal.appendChild(form);
            document.body.appendChild(modal);
        } else {
            alert('加载配置失败');
        }
    } catch (error) {
        alert('加载配置失败: ' + error.message);
    }
}

async function saveAIConfig(event, configId) {
    event.preventDefault();
    
    if (!token) {
        alert('请先登录');
        return;
    }
    
    const data = {
        model_name: document.getElementById('editModelName').value,
        api_endpoint: document.getElementById('editApiEndpoint').value,
        api_key: document.getElementById('editApiKey').value || undefined,  // 仅在有值时发送
        system_prompt: document.getElementById('editSystemPrompt').value || null,
        max_tokens: parseInt(document.getElementById('editMaxTokens').value),
        temperature: parseInt(document.getElementById('editTemperature').value),
        top_p: parseInt(document.getElementById('editTopP').value),
        timeout_seconds: parseInt(document.getElementById('editTimeoutSeconds').value),
        is_active: document.getElementById('editIsActive').checked
    };
    
    // 如果 api_key 为空，从数据中删除它（不修改密钥）
    if (!data.api_key) {
        delete data.api_key;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/ai-configs/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('✅ 配置已保存！');
            document.getElementById('aiConfigEditModal').remove();
            loadAIConfigs();  // 刷新列表
        } else {
            const error = await response.json();
            alert('保存失败: ' + (error.detail || '未知错误'));
        }
    } catch (error) {
        alert('保存失败: ' + error.message);
    }
}

async function setDefaultAIConfig(configId) {
    if (!token) {
        alert('请先登录');
        return;
    }

    console.log('Setting default config, token:', token ? token.substring(0, 20) + '...' : 'null');

    try {
        const response = await authenticatedFetch(`${API_URL}/api/ai-configs/${configId}/set-default`, {
            method: 'POST'
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
            alert('✅ 已设置为默认配置！');
            loadAIConfigs();
        } else {
            const error = await response.json();
            console.log('Error detail:', error);
            alert('设置失败: ' + error.detail);
        }
    } catch (error) {
        console.log('Exception:', error);
        alert('错误: ' + error.message);
    }
}

// 修改密码
async function changePassword() {
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorDiv = document.getElementById('passwordError');
    const successDiv = document.getElementById('passwordSuccess');

    // 清除之前的提示
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    // 验证
    if (!oldPassword || !newPassword || !confirmPassword) {
        errorDiv.textContent = '请填写所有字段';
        errorDiv.style.display = 'block';
        return;
    }

    if (newPassword.length < 8) {
        errorDiv.textContent = '新密码至少需要8个字符';
        errorDiv.style.display = 'block';
        return;
    }

    if (newPassword !== confirmPassword) {
        errorDiv.textContent = '两次输入的密码不一致';
        errorDiv.style.display = 'block';
        return;
    }

    if (oldPassword === newPassword) {
        errorDiv.textContent = '新密码不能与旧密码相同';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/admin/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': `Bearer ${token}`
            },
            body: new URLSearchParams({
                old_password: oldPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            successDiv.textContent = '✅ 密码修改成功，3秒后将自动退出登录';
            successDiv.style.display = 'block';
            document.getElementById('changePasswordForm').reset();
            
            // 3秒后自动退出登录
            setTimeout(() => {
                logout();
            }, 3000);
        } else {
            errorDiv.textContent = data.detail || '修改失败';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = '网络错误: ' + error.message;
        errorDiv.style.display = 'block';
    }
}

// 初始化设置页面
function initializeSettings() {
    loadWebsiteSettings();
}

// ============= 网站设置管理函数 =============

// 加载网站设置
async function loadWebsiteSettings() {
    try {
        const response = await authenticatedFetch(`${API_URL}/api/website-settings/`);
        if (response.ok) {
            const settings = await response.json();
            // 填充基本设置
            document.getElementById('siteName').value = settings.site_name || '';
            document.getElementById('siteTitle').value = settings.site_title || '';
            document.getElementById('siteDescription').value = settings.site_description || '';
            document.getElementById('siteKeywords').value = settings.site_keywords || '';
            // 填充统计代码
            document.getElementById('baiduAnalytics').value = settings.baidu_analytics || '';
            document.getElementById('googleAnalytics').value = settings.google_analytics || '';
            document.getElementById('customScripts').value = settings.custom_scripts || '';
            // 填充备案信息
            document.getElementById('icpNumber').value = settings.icp_number || '';
            document.getElementById('companyName').value = settings.company_name || '';
            document.getElementById('contactEmail').value = settings.contact_email || '';
            // 填充友情链接
            document.getElementById('footerLinks').value = settings.footer_links || '[]';
            console.log('✅ 网站设置加载成功');
        }
    } catch (error) {
        console.error('加载网站设置失败:', error);
    }
}

// 保存网站基本设置
async function saveWebsiteSettings() {
    const data = {
        site_name: document.getElementById('siteName').value,
        site_title: document.getElementById('siteTitle').value,
        site_description: document.getElementById('siteDescription').value,
        site_keywords: document.getElementById('siteKeywords').value
    };
    await updateWebsiteSettings(data, '基本设置');
}

// 保存流量统计代码
async function saveAnalyticsSettings() {
    const data = {
        baidu_analytics: document.getElementById('baiduAnalytics').value,
        google_analytics: document.getElementById('googleAnalytics').value,
        custom_scripts: document.getElementById('customScripts').value
    };
    await updateWebsiteSettings(data, '统计代码');
}

// 保存备案信息
async function saveFooterSettings() {
    const data = {
        icp_number: document.getElementById('icpNumber').value,
        company_name: document.getElementById('companyName').value,
        contact_email: document.getElementById('contactEmail').value
    };
    await updateWebsiteSettings(data, '备案信息');
}

// 保存友情链接
async function saveFooterLinks() {
    const linksText = document.getElementById('footerLinks').value.trim();
    // 验证JSON格式
    try {
        if (linksText) {
            JSON.parse(linksText);
        }
    } catch (e) {
        showNotification('友情链接格式错误，请检查JSON格式', 'error');
        return;
    }
    const data = {
        footer_links: linksText || '[]'
    };
    await updateWebsiteSettings(data, '友情链接');
}

// 更新网站设置的通用函数
async function updateWebsiteSettings(data, settingName) {
    try {
        const response = await authenticatedFetch(`${API_URL}/api/website-settings/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showNotification(`✅ ${settingName}保存成功`, 'success');
        } else {
            const errorData = await response.json();
            showNotification(`❌ 保存失败: ${errorData.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ 网络错误: ${error.message}`, 'error');
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    token = null;
    currentUser = {};
    showLoginPage();
    document.getElementById('loginForm').reset();
}

// ============= Tiptap 编辑器相关函数 =============
let articleEditor = null;

// 初始化编辑器
// 初始化编辑器 - 使用 esm.sh CDN 动态导入
async function initArticleEditor(initialContent = '', retryCount = 0) {
    const container = document.getElementById('articleEditor');
    
    if (!container) return;
    
    // 如果编辑器已存在，先销毁
    if (articleEditor) {
        try {
            articleEditor.destroy();
        } catch (e) {
            console.warn('销毁编辑器时出错:', e);
        }
    }
    
    // 清空容器
    container.innerHTML = '';
    
    try {
        // 动态导入 Tiptap 库
        console.log('📥 正在加载 Tiptap 库...');
        
        // 使用 esm.sh CDN 加载 Tiptap 使用指定版本号（官方推荐方案）
        // 参考官方文档：https://tiptap.dev/guide/install/cdn
        const { Editor } = await import('https://esm.sh/@tiptap/core@2.4.0');
        const StarterKit = (await import('https://esm.sh/@tiptap/starter-kit@2.4.0')).default;
        const ImageExt = (await import('https://esm.sh/@tiptap/extension-image@2.4.0')).default;
        const Link = (await import('https://esm.sh/@tiptap/extension-link@2.4.0')).default;
        
        console.log('✅ Tiptap 库加载成功');
        console.log('✅ Editor available:', !!Editor);
        console.log('✅ StarterKit available:', !!StarterKit);
        console.log('✅ Image available:', !!ImageExt);
        console.log('✅ Link available:', !!Link);
        
        // 验证库加载
        if (!Editor || !StarterKit) {
            throw new Error(`库加载不完整: Editor=${!!Editor}, StarterKit=${!!StarterKit}`);
        }
        
        // 构建扩展列表 (StarterKit 本身就是一个 Extension 实例/工厂的默认导出，直接放入数组即可)
        // 参考官方 CDN 示例: extensions: [StarterKit]
        const extensions = [
            StarterKit,
            // 图片：提供 setImage 命令，支持对齐属性和宽度设置
            // 修复：配置Image扩展以正确保留data-align和data-width属性
            ImageExt.extend({
                addAttributes() {
                    return {
                        ...this.parent?.(),
                        // 支持 style 属性用于控制宽度和对齐
                        style: {
                            default: null,
                            parseHTML: element => element.getAttribute('style'),
                            renderHTML: attributes => {
                                if (!attributes.style) return {};
                                return { style: attributes.style };
                            },
                        },
                    };
                },
            }).configure({
                inline: false,
                selectable: true,
                draggable: true,
                allowBase64: true,
                HTMLAttributes: {
                    style: 'max-width:100%;height:auto;display:block;',
                    class: 'editor-image',
                },
            }),
            // 链接：提供 setLink/toggleLink 命令
            Link.configure({
                openOnClick: false,
                linkOnPaste: true,
                autolink: true,
                HTMLAttributes: {
                    rel: 'noopener noreferrer nofollow',
                    target: '_blank',
                },
            }),
        ];
        
        // 修复：确保初始内容正确处理（避免null/undefined导致的丢失）
        let editorContent = initialContent;
        if (!editorContent || editorContent.trim() === '') {
            editorContent = '<p></p>';
        }
        // 确保内容是字符串且不为空
        if (typeof editorContent !== 'string' || editorContent.length === 0) {
            editorContent = '<p></p>';
        }
        console.log('📝 编辑器内容长度:', editorContent.length, '字符');
        
        // 创建编辑器实例
        articleEditor = new Editor({
            element: container,
            extensions: extensions,
            content: editorContent,
        });
        
        console.log('✅ 编辑器初始化成功');
        
        // 生成工具栏
        setTimeout(() => {
            renderEditorToolbar();
            console.log('✅ 工具栏已生成');
        }, 100);
        
    } catch (error) {
        console.error('❌ 编辑器初始化失败:', error);
        
        // 如果是网络错误，重试
        if (retryCount < 3 && (error.message.includes('Failed to fetch') || error.message.includes('404') || error.message.includes('无法加载'))) {
            console.warn(`⏳ 库加载失败，${1000 * (retryCount + 1)}ms后重试... (${retryCount + 1}/3)`);
            setTimeout(() => initArticleEditor(initialContent, retryCount + 1), 1000 * (retryCount + 1));
            return;
        }
        
        console.error('错误详情:', {
            message: error.message,
            stack: error.stack,
        });
        
        // 降级方案：显示 textarea
        container.innerHTML = '<textarea id="articleContentFallback" style="width: 100%; min-height: 300px; font-family: monospace; padding: 10px; border: 1px solid #ddd; border-radius: 4px;"></textarea>';
        const textarea = document.getElementById('articleContentFallback');
        if (textarea) {
            textarea.value = initialContent;
        }
        
        // 显示错误消息
        const toolbar = document.getElementById('articleEditorToolbar');
        if (toolbar) {
            toolbar.innerHTML = '<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 4px; border: 1px solid #ffeaa7; font-size: 12px;">⚠️ 富文本编辑器加载失败，已切换到纯文本模式。错误: ' + error.message + '</div>';
        }
    }
}

// 渲染工具栏
function renderEditorToolbar() {
    if (!articleEditor) {
        console.warn('编辑器未初始化，跳过工具栏生成');
        return;
    }
    
    const toolbar = document.getElementById('articleEditorToolbar');
    if (!toolbar) {
        console.warn('工具栏容器不存在');
        return;
    }
    
    toolbar.innerHTML = `
        <!-- 文本格式 -->
        <button class="editor-btn" onclick="toggleBold()" title="粗体 (Ctrl+B)" type="button">B</button>
        <button class="editor-btn" onclick="toggleItalic()" title="斜体 (Ctrl+I)" type="button">I</button>
        <button class="editor-btn" onclick="toggleStrike()" title="删除线" type="button">S</button>
        <button class="editor-btn" onclick="toggleCode()" title="代码" type="button">Code</button>
        <button class="editor-btn" onclick="clearFormatting()" title="清除所有样式" type="button">清除样式</button>
        
        <!-- 分隔符 -->
        <span class="editor-separator"></span>
        
        <!-- 列表 -->
        <button class="editor-btn" onclick="toggleBulletList()" title="无序列表" type="button">• 列表</button>
        <button class="editor-btn" onclick="toggleOrderedList()" title="有序列表" type="button">1. 列表</button>
        
        <!-- 分隔符 -->
        <span class="editor-separator"></span>
        
        <!-- 标题 -->
        <button class="editor-btn" onclick="setHeading(1)" title="标题1" type="button">H1</button>
        <button class="editor-btn" onclick="setHeading(2)" title="标题2" type="button">H2</button>
        <button class="editor-btn" onclick="setHeading(3)" title="标题3" type="button">H3</button>
        
        <!-- 分隔符 -->
        <span class="editor-separator"></span>
        
        <!-- 其他 -->
        <button class="editor-btn" onclick="toggleBlockquote()" title="引用" type="button">引用</button>
        <button class="editor-btn" onclick="insertCodeBlock()" title="代码块" type="button">代码块</button>
        <button class="editor-btn" onclick="insertImage()" title="插入图片" type="button">图片</button>
        <button class="editor-btn" onclick="insertLink()" title="插入链接" type="button">链接</button>
        
        <!-- 图片编辑 -->
        <span class="editor-separator"></span>
        <button class="editor-btn" onclick="alignImage('left')" title="图片居左" type="button">图左</button>
        <button class="editor-btn" onclick="alignImage('center')" title="图片居中" type="button">图中</button>
        <button class="editor-btn" onclick="alignImage('right')" title="图片居右" type="button">图右</button>
        <button class="editor-btn" onclick="setImageWidth()" title="设置图片宽度%" type="button">图宽%</button>
        <button class="editor-btn" onclick="removeImage()" title="删除图片" type="button">删图</button>
        
        <!-- 分隔符 -->
        <span class="editor-separator"></span>
        
        <!-- 撤销重做 -->
        <button class="editor-btn" onclick="undoEdit()" title="撤销" type="button">↶ 撤销</button>
        <button class="editor-btn" onclick="redoEdit()" title="重做" type="button">↷ 重做</button>
    `;
}

// 工具栏按钮处理函数
function toggleBold() {
    if (articleEditor) articleEditor.chain().focus().toggleBold().run();
}

function toggleItalic() {
    if (articleEditor) articleEditor.chain().focus().toggleItalic().run();
}

function toggleStrike() {
    if (articleEditor) articleEditor.chain().focus().toggleStrike().run();
}

function toggleCode() {
    if (articleEditor) articleEditor.chain().focus().toggleCode().run();
}

// 清除所有内联样式与块级样式：还原为普通段落
function clearFormatting() {
    if (!articleEditor) return;
    articleEditor.chain().focus()
        .unsetAllMarks()        // 去除粗体/斜体/删除线/代码等 mark
        .setParagraph()          // 设为普通段落，移除 blockquote/codeBlock/heading
        .run();
}

function toggleBulletList() {
    if (articleEditor) articleEditor.chain().focus().toggleBulletList().run();
}

function toggleOrderedList() {
    if (articleEditor) articleEditor.chain().focus().toggleOrderedList().run();
}

function setHeading(level) {
    if (articleEditor) articleEditor.chain().focus().toggleHeading({ level }).run();
}

function toggleBlockquote() {
    if (articleEditor) articleEditor.chain().focus().toggleBlockquote().run();
}

function insertCodeBlock() {
    if (articleEditor) articleEditor.chain().focus().toggleCodeBlock().run();
}

function insertImage() {
    if (!articleEditor || typeof articleEditor.commands?.setImage !== 'function') {
        alert('图片扩展未加载，请刷新页面后重试。');
        console.warn('setImage 命令不可用：Image 扩展可能未注册');
        return;
    }
    
    // 提供两种选择：上传文件或输入URL
    const choice = prompt('选择方式:\n1 = 上传本地文件\n2 = 输入图片URL\n\n请输入 1 或 2:');
    
    if (choice === '1') {
        // 上传文件 - 使用预先创建的隐藏input元素
        console.log('📁 用户选择上传本地文件');
        console.log('✓ articleEditor状态:', !!articleEditor, '支持setImage:', typeof articleEditor?.commands?.setImage);
        
        // 获取隐藏的文件输入元素
        let input = document.getElementById('imageFileInput');
        
        if (!input) {
            // 如果不存在，创建一个
            input = document.createElement('input');
            input.type = 'file';
            input.id = 'imageFileInput';
            input.accept = 'image/*';
            input.style.display = 'none';
            document.body.appendChild(input);
            console.log('⚠️ 文件输入元素不存在，已创建新的');
        }
        
        // 清除所有之前的事件处理器 - 创建全新的input元素
        const oldInput = input;
        const newInput = document.createElement('input');
        newInput.type = 'file';
        newInput.id = 'imageFileInput';
        newInput.accept = 'image/*';
        newInput.style.display = 'none';
        
        // 替换DOM中的元素
        if (oldInput.parentNode) {
            oldInput.parentNode.replaceChild(newInput, oldInput);
        } else {
            document.body.appendChild(newInput);
        }
        input = newInput;
        console.log('✓ 已创建全新的文件输入元素，确保无缓存事件监听');
        
        // 定义文件选择处理器
        async function handleFileSelect(e) {
            const file = e.target.files?.[0];
            if (!file) {
                console.log('❌ 用户取消了文件选择');
                return;
            }
            
            console.log('📤 开始上传文件:', file.name, '大小:', file.size, 'bytes');
            
            try {
                // 再次检查编辑器是否仍然存在
                if (!articleEditor) {
                    console.error('❌ 编辑器实例丢失，上传中止');
                    alert('❌ 编辑器异常，请刷新页面后重试');
                    return;
                }
                
                // 上传文件
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch(`${API_URL}/api/upload/image`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });
                
                console.log('📨 上传响应状态:', response.status);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('✅ 图片上传成功:', data.url);
                    
                    // 再次验证编辑器存在
                    if (!articleEditor) {
                        console.error('❌ 上传完成但编辑器实例丢失');
                        alert('❌ 编辑器已关闭，图片上传已取消');
                        return;
                    }
                    
                    // 插入图片到编辑器
                    articleEditor.chain().focus().setImage({ 
                        src: data.url,
                        style: 'width: 100%; height: auto; display: block; max-width: 100%;'
                    }).run();
                    console.log('✅ 图片已插入编辑器');
                    alert('✅ 图片上传成功！');
                } else {
                    const error = await response.json();
                    console.error('❌ 上传失败:', error);
                    alert('❌ 上传失败: ' + (error.detail || error.message || '未知错误'));
                }
            } catch (error) {
                console.error('❌ 上传错误:', error);
                alert('❌ 上传错误: ' + error.message);
            }
        }
        
        // 注册事件处理器
        input.addEventListener('change', handleFileSelect, { once: true });
        console.log('📁 文件选择器事件处理器已注册');
        
        // 触发文件选择对话框
        input.click();
        console.log('📁 点击文件选择对话框');
        
    } else if (choice === '2') {
        // 输入URL
        const url = prompt('输入图片URL:');
        if (url && articleEditor) {
            articleEditor.chain().focus().setImage({ 
                src: url,
                style: 'width: 100%; height: auto; display: block; max-width: 100%;'
            }).run();
            console.log('✅ 图片已从URL插入:', url);
        }
    }
}

function ensureImageSelected() {
    if (!articleEditor) return false;
    if (articleEditor.isActive('image')) {
        return true;
    }
    alert('请先点击要调整的图片，再使用该操作。');
    return false;
}

// 图片对齐
// 修复：使用style属性直接控制图片对齐，保留现有的宽度设置
function alignImage(pos) {
    if (!ensureImageSelected()) return;
    
    // 获取当前的style属性，保留现有的宽度设置
    const currentNode = articleEditor.state.selection.$anchor.nodeAfter || articleEditor.state.selection.$anchor.nodeBefore;
    let currentStyle = currentNode?.attrs?.style || '';
    
    // 提取现有的宽度值（如果有）
    const widthMatch = currentStyle.match(/width:\s*(\d+%)/);
    const currentWidth = widthMatch ? widthMatch[1] : null;
    
    let styleStr = '';
    
    if (pos === 'left') {
        // 左对齐：浮动到左边，右边有间距，文字环绕
        const width = currentWidth || '45%';
        styleStr = `float: left; margin: 0 15px 10px 0; width: ${width}; height: auto; display: block; max-width: 100%;`;
    } else if (pos === 'right') {
        // 右对齐：浮动到右边，左边有间距，文字环绕
        const width = currentWidth || '45%';
        styleStr = `float: right; margin: 0 0 10px 15px; width: ${width}; height: auto; display: block; max-width: 100%;`;
    } else if (pos === 'center') {
        // 中间对齐：不浮动，用margin自动居中
        // 如果有现有宽度，保留它；否则使用100%
        const width = currentWidth || '100%';
        styleStr = `float: none; margin: 10px auto; display: block; width: ${width}; height: auto; max-width: 100%;`;
    }
    
    if (styleStr) {
        articleEditor.chain()
            .focus()
            .updateAttributes('image', { style: styleStr })
            .run();
        console.log('✅ 设置图片对齐为:', pos, '，样式:', styleStr);
    }
}

// 设置图片宽度（百分比）
// 修复：直接修改选中图片的 style 属性，更加稳定可靠
function setImageWidth() {
    if (!ensureImageSelected()) return;
    const val = prompt('输入图片宽度(1-100)%：', '80');
    const n = parseInt(val, 10);
    if (!n || n < 1 || n > 100) {
        alert('请输入1-100之间的数字');
        return;
    }
    
    // 获取当前选中的图片节点
    const { $anchor } = articleEditor.state.selection;
    if (!$anchor) {
        console.error('❌ 无法获取选中图片的位置');
        return;
    }
    
    // 使用 updateAttributes 更新 style 属性，直接设置宽度
    articleEditor.chain()
        .focus()
        .updateAttributes('image', { 
            style: `width: ${n}%; height: auto; display: block; max-width: 100%;`
        })
        .run();
    console.log('✅ 设置图片宽度为:', n + '%');
}

// 删除当前选中的图片
function removeImage() {
    if (!ensureImageSelected()) return;
    articleEditor.chain().focus().deleteSelection().run();
}

function insertLink() {
    if (!articleEditor || typeof articleEditor.commands?.setLink !== 'function') {
        alert('链接扩展未加载，请刷新页面后重试。');
        console.warn('setLink 命令不可用：Link 扩展可能未注册');
        return;
    }
    const url = prompt('输入链接URL:');
    if (url && articleEditor) {
        articleEditor.chain().focus().setLink({ href: url }).run();
    }
}

function undoEdit() {
    if (articleEditor) articleEditor.chain().focus().undo().run();
}

function redoEdit() {
    if (articleEditor) articleEditor.chain().focus().redo().run();
}

// 获取编辑器内容（HTML格式）
function getEditorContent() {
    if (!articleEditor) return '';
    return articleEditor.getHTML();
}

// 设置编辑器内容
function setEditorContent(html) {
    if (!articleEditor) {
        initArticleEditor(html);
    } else {
        articleEditor.commands.setContent(html);
    }
}

// 清空编辑器
function clearEditor() {
    if (articleEditor) {
        articleEditor.commands.clearContent();
    }
}

// ============= Tiptap 诊断脚本 =============
window.TiptapDiagnostics = {
    check: function() {
        const checks = {
            '@tiptap/core': !!window['@tiptap/core'],
            '@tiptap/starter-kit': !!window['@tiptap/starter-kit'],
            '@tiptap/extension-image': !!window['@tiptap/extension-image'],
            '@tiptap/extension-link': !!window['@tiptap/extension-link'],
        };
        
        console.group('🔍 Tiptap 诊断信息');
        console.log('加载状态:', checks);
        
        if (window['@tiptap/core'] && window['@tiptap/core'].Editor) {
            console.log('✅ Tiptap Editor 类可用');
        } else {
            console.warn('❌ Tiptap Editor 类不可用');
        }
        
        console.table(checks);
        console.groupEnd();
        
        return checks;
    }
};

// 页面加载完毕后自动诊断
window.addEventListener('load', function() {
    setTimeout(() => TiptapDiagnostics.check(), 1000);
});
