# 🎨 前端动态配置方案

## 📋 问题

> "如果前端部署跑起来了，我如果想随时更改前端的标题怎么办呢？"

前端一旦构建成静态文件，配置就被硬编码了。每次修改都需要重新构建和部署。

---

## ✅ 解决方案：配置文件 + JavaScript 动态加载

### 方案概述

前端在运行时从后端获取配置，而不是硬编码配置。

```
┌────────────────────────┐
│   前端加载时 (SPA)      │
│  1. 发送请求到后端      │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────┐
│  后端 API 端点          │
│  /api/config/frontend   │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────┐
│  返回 JSON 配置        │
│  {                     │
│    "appTitle": "...",  │
│    "appLogo": "...",   │
│    "theme": {...}      │
│  }                     │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────┐
│  前端应用配置          │
│  动态渲染 HTML         │
│  可实时更新！          │
└────────────────────────┘
```

---

## 🔧 实现步骤

### Step 1: 后端添加配置 API

**文件**: `backend/app/routes/config.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Optional

router = APIRouter(prefix="/api/config", tags=["config"])

@router.get("/frontend")
async def get_frontend_config(db: Session = Depends(get_db)):
    """
    获取前端配置
    
    前端应用启动时调用此接口获取动态配置
    包括：应用标题、主题、菜单项等
    """
    return {
        "app": {
            "title": "TrustAgency 后台管理系统",
            "subtitle": "AI 内容生成平台",
            "logo": "/admin/assets/logo.png",
            "favicon": "/admin/assets/favicon.ico",
        },
        "theme": {
            "primary_color": "#1890ff",
            "secondary_color": "#13c2c2",
            "dark_mode": False,
        },
        "features": {
            "enable_ai_tasks": True,
            "enable_article_editor": True,
            "enable_platform_management": True,
            "enable_user_management": True,
        },
        "ui": {
            "sidebar_collapsed": False,
            "items_per_page": 20,
            "auto_save_interval": 5000,  # ms
        },
        "api": {
            "base_url": "/api",
            "timeout": 30000,  # ms
        }
    }

@router.get("/system")
async def get_system_config(db: Session = Depends(get_db)):
    """获取系统配置（版本、环境等）"""
    import os
    return {
        "version": os.getenv("API_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "debug": os.getenv("DEBUG", "False") == "True",
    }
```

**在 main.py 中注册**:

```python
from app.routes import config
app.include_router(config.router)
```

---

### Step 2: 前端添加配置加载模块

**文件**: `backend/site/admin/js/config.js`

```javascript
/**
 * 应用配置管理器
 * 从后端动态加载配置
 */

class AppConfig {
    constructor() {
        this.config = null;
        this.initialized = false;
    }
    
    /**
     * 初始化配置（在应用启动时调用）
     */
    async init() {
        try {
            // 从后端获取配置
            const response = await fetch('/api/config/frontend');
            
            if (!response.ok) {
                throw new Error(`Failed to load config: ${response.status}`);
            }
            
            this.config = await response.json();
            this.initialized = true;
            
            // 应用配置
            this.applyConfig();
            
            console.log('✅ 配置已加载:', this.config);
            return true;
        } catch (error) {
            console.error('❌ 配置加载失败:', error);
            
            // 使用默认配置
            this.setDefaults();
            return false;
        }
    }
    
    /**
     * 应用配置到页面
     */
    applyConfig() {
        if (!this.config) return;
        
        const app = this.config.app || {};
        
        // 1. 设置页面标题
        document.title = app.title || 'TrustAgency';
        
        // 2. 设置应用标题
        const titleElement = document.querySelector('[data-app-title]');
        if (titleElement) {
            titleElement.textContent = app.title;
        }
        
        // 3. 设置应用子标题
        const subtitleElement = document.querySelector('[data-app-subtitle]');
        if (subtitleElement) {
            subtitleElement.textContent = app.subtitle;
        }
        
        // 4. 设置 Logo
        const logoElement = document.querySelector('[data-app-logo]');
        if (logoElement && app.logo) {
            logoElement.src = app.logo;
        }
        
        // 5. 设置 Favicon
        let favicon = document.querySelector('link[rel="icon"]');
        if (!favicon) {
            favicon = document.createElement('link');
            favicon.rel = 'icon';
            document.head.appendChild(favicon);
        }
        if (app.favicon) {
            favicon.href = app.favicon;
        }
        
        // 6. 应用主题颜色
        this.applyTheme();
        
        // 7. 存储配置到 localStorage（备用）
        localStorage.setItem('app_config', JSON.stringify(this.config));
    }
    
    /**
     * 应用主题
     */
    applyTheme() {
        const theme = this.config.theme || {};
        
        // 使用 CSS 变量
        const root = document.documentElement;
        root.style.setProperty('--primary-color', theme.primary_color || '#1890ff');
        root.style.setProperty('--secondary-color', theme.secondary_color || '#13c2c2');
        
        // 暗黑模式
        if (theme.dark_mode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }
    
    /**
     * 获取配置值
     */
    get(path, defaultValue = null) {
        if (!this.config) return defaultValue;
        
        const keys = path.split('.');
        let value = this.config;
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    }
    
    /**
     * 设置默认配置
     */
    setDefaults() {
        this.config = {
            app: {
                title: 'TrustAgency 后台管理系统',
                subtitle: 'AI 内容生成平台',
            },
            theme: {
                primary_color: '#1890ff',
                secondary_color: '#13c2c2',
                dark_mode: false,
            },
            features: {
                enable_ai_tasks: true,
                enable_article_editor: true,
            },
            ui: {
                sidebar_collapsed: false,
                items_per_page: 20,
            },
            api: {
                base_url: '/api',
                timeout: 30000,
            }
        };
    }
}

// 全局配置实例
const appConfig = new AppConfig();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = appConfig;
}
```

---

### Step 3: 修改前端 HTML

**文件**: `backend/site/admin/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- 动态标题 -->
    <title>加载中...</title>
    
    <!-- 动态 Favicon -->
    <link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,AAABAAEAEBAAAAEAIA">
    
    <link rel="stylesheet" href="css/style.css">
    
    <!-- CSS 变量定义（主题色） -->
    <style>
        :root {
            --primary-color: #1890ff;
            --secondary-color: #13c2c2;
        }
    </style>
</head>
<body>
    <!-- 应用容器 -->
    <div id="app">
        <!-- 加载中指示器 -->
        <div class="loading-indicator">
            <div class="spinner"></div>
            <p>正在加载应用配置...</p>
        </div>
    </div>
    
    <!-- 配置管理器 -->
    <script src="js/config.js"></script>
    
    <!-- 主应用脚本 -->
    <script>
        /**
         * 应用初始化流程
         */
        async function initializeApp() {
            try {
                // 1. 加载配置
                const configLoaded = await appConfig.init();
                
                if (!configLoaded) {
                    console.warn('⚠️  使用默认配置继续...');
                }
                
                // 2. 渲染主应用
                renderApp();
                
                // 3. 初始化应用逻辑
                initAppLogic();
                
                console.log('✅ 应用已启动');
            } catch (error) {
                console.error('❌ 应用初始化失败:', error);
                document.body.innerHTML = '<h1>应用启动失败，请刷新页面</h1>';
            }
        }
        
        /**
         * 渲染应用界面
         */
        function renderApp() {
            const app = document.getElementById('app');
            
            const appConfig = window.appConfig.config;
            
            app.innerHTML = `
                <div class="header">
                    <div class="logo-container">
                        <img src="${appConfig.app.logo}" alt="logo" data-app-logo>
                        <div class="title-container">
                            <h1 data-app-title>${appConfig.app.title}</h1>
                            <p data-app-subtitle>${appConfig.app.subtitle}</p>
                        </div>
                    </div>
                </div>
                
                <div class="main-container">
                    <!-- 侧边栏和主要内容将在这里渲染 -->
                    <div id="main-content"></div>
                </div>
            `;
            
            // 移除加载指示器
            const loading = document.querySelector('.loading-indicator');
            if (loading) {
                loading.remove();
            }
        }
        
        /**
         * 初始化应用逻辑
         */
        function initAppLogic() {
            // 在这里添加你的应用逻辑
            console.log('初始化应用逻辑...');
            // ... 你的代码
        }
        
        // 页面加载完成后启动应用
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeApp);
        } else {
            initializeApp();
        }
    </script>
    
    <!-- 其他脚本 -->
    <script src="js/app.js"></script>
</body>
</html>
```

---

### Step 4: 前端使用配置

在任何需要配置的地方使用：

```javascript
// 获取配置值
const appTitle = appConfig.get('app.title');
const primaryColor = appConfig.get('theme.primary_color');
const enableAITasks = appConfig.get('features.enable_ai_tasks');

console.log('应用标题:', appTitle);
console.log('主题色:', primaryColor);
console.log('启用 AI 任务:', enableAITasks);
```

---

## 🔄 实时更新配置

### 方案1：管理后台配置页面

后端添加配置管理接口：

```python
@router.post("/frontend")
async def update_frontend_config(
    config: dict,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新前端配置（仅限管理员）"""
    
    # 保存到数据库或配置文件
    # 这里示例保存到环境变量或数据库
    
    return {"status": "success", "message": "配置已更新"}
```

前端定期轮询或通过 WebSocket 接收配置更新：

```javascript
// 轮询更新配置（每 30 秒）
setInterval(async () => {
    await appConfig.init();
}, 30000);

// 或使用 WebSocket 实时更新
const socket = new WebSocket('ws://localhost:8001/api/config/stream');
socket.onmessage = (event) => {
    const newConfig = JSON.parse(event.data);
    window.appConfig.config = newConfig;
    window.appConfig.applyConfig();
};
```

### 方案2：配置文件 (config.json)

后端提供一个 JSON 配置文件：

```json
{
  "app": {
    "title": "TrustAgency 后台管理系统",
    "subtitle": "AI 内容生成平台"
  },
  "theme": {
    "primary_color": "#1890ff"
  }
}
```

Nginx 配置：

```nginx
location /api/config/frontend {
    alias /opt/trustagency/config.json;
}
```

---

## 🎯 最佳实践

| 场景 | 推荐方案 |
|------|--------|
| 需要后端验证权限 | API 端点 |
| 只需要基本配置 | JSON 文件 |
| 需要实时更新 | WebSocket |
| 性能要求高 | Redis 缓存 |

---

## 📊 配置存储位置对比

| 存储位置 | 优点 | 缺点 | 适用场景 |
|---------|------|------|--------|
| **硬编码** | 性能最优 | 无法动态修改 | 开发阶段 |
| **JSON 文件** | 简单易用 | 需要重启服务 | 小型应用 |
| **环境变量** | 部署灵活 | 修改不方便 | CI/CD 部署 |
| **数据库** | 完全动态 | 性能稍差 | 大型应用 ⭐ |
| **配置服务** | 集中管理 | 复杂度高 | 微服务架构 |

---

## ✅ 总结

**使用此方案，你可以：**

- ✅ **随时修改标题** - 无需重新构建前端
- ✅ **动态切换主题** - 实时生效
- ✅ **灰度发布** - 为不同用户展示不同配置
- ✅ **A/B 测试** - 配置不同的 UI/UX
- ✅ **快速迭代** - 无需重新部署前端

**下一步行动：**

1. 在后端添加 `/api/config/frontend` 端点
2. 在前端添加 `config.js` 模块
3. 修改 `index.html` 在加载时调用配置
4. 测试配置动态应用效果

---

