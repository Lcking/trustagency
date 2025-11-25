# 🚀 Phase 5 启动 - 系统稳定性加固

**状态**: Phase 4 验收通过 ✅ → Phase 5 启动 🎯  
**日期**: 2025-11-23  
**周期**: 2-3 周  
**目标**: 系统连续运行 72 小时无卡顿，无数据异常  
**分支**: `refactor/admin-panel-phase5`

---

## 📊 Phase 5 概览

### 4 大核心任务

| 任务 | 目标 | 优先级 | 预计周期 |
|------|------|--------|---------|
| **5.1** 性能诊断和优化 | 消除卡顿/内存泄漏 | 🔴 最高 | 1周 |
| **5.2** 前端模块化完善 | 完整的模块加载体系 | 🔴 最高 | 1周 |
| **5.3** 监控告警系统 | 自动发现问题 | 🟠 高 | 1周 |
| **5.4** 缓存和索引 | 数据库查询优化 | 🟠 高 | 1周 |

---

## 📋 任务 5.1: 系统性能诊断和优化 (优先级: 🔴 最高)

**目标**: 找到内存泄漏、卡顿的根本原因

### 5.1.1 深度内存分析 ⏱️ 2天

#### 工作步骤
```bash
1. 打开浏览器开发者工具 → Memory 标签
2. 记录基准内存占用 (任务开始时)
3. 执行以下操作:
   - 加载首页 (记录内存)
   - 添加 5 篇文章 (记录内存)
   - 编辑 3 篇文章 (记录内存)
   - 生成 10 个 AI 任务 (记录内存)
   - 打开/关闭 10 个模态框 (记录内存)
4. 生成内存快照 (3份，间隔10分钟)
5. 对比快照，找出泄漏的对象
```

#### 输出物
- 📄 `MEMORY_PROFILING_REPORT.md` 包含:
  - 内存使用曲线图表
  - 泄漏对象分析
  - 改进方案
- 📊 工作流程: 分析 → 改进 → 验证

#### 检查清单
- [ ] 记录了基准内存占用
- [ ] 生成了 3 份内存快照
- [ ] 识别出内存泄漏的热点函数
- [ ] 提出了改进方案
- [ ] 验证改进后内存占用 < 100MB

---

### 5.1.2 前端资源加载优化 ⏱️ 2天

#### 工作步骤
```javascript
// 1. 分析当前加载时间
// 在浏览器控制台执行
performance.timing.loadEventEnd - performance.timing.navigationStart

// 2. 识别慢加载资源
// DevTools → Network 标签
// 记录所有 > 1s 的资源

// 3. 实施优化
// - 移除未使用的 CDN 库
// - 添加资源预加载
// - 压缩 HTML/CSS/JS
// - 实现图片懒加载

// 4. 验证优化效果
```

#### 检查清单
- [ ] 记录了优化前的加载时间
- [ ] 识别了 5+ 个优化点
- [ ] 实施了资源预加载策略
- [ ] 页面首屏时间 < 3s
- [ ] 验证了优化效果

#### 代码示例
```html
<!-- 预加载关键资源 -->
<link rel="preload" as="script" href="admin.js">
<link rel="prefetch" href="modal.js">

<!-- 延迟加载非关键脚本 -->
<script defer src="analytics.js"></script>
```

---

### 5.1.3 后端 API 响应时间分析 ⏱️ 2天

#### 工作步骤
```python
# 1. 添加响应时间中间件
# 在 backend/main.py 中添加

from time import time
from fastapi import Request
import logging

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time()
    response = await call_next(request)
    process_time = (time() - start) * 1000  # 转换为毫秒
    
    if process_time > 500:  # 响应 > 500ms 的请求
        logging.warning(f"{request.method} {request.url.path} - {process_time:.2f}ms")
    
    return response

# 2. 测试所有 API
# 运行压力测试或手动调用每个端点

# 3. 识别慢查询
# 找出响应 > 1s 的 API

# 4. 优化慢查询
# - 添加数据库索引
# - 实现缓存
# - 优化 SQL 查询
```

#### 检查清单
- [ ] 添加了响应时间中间件
- [ ] 测试了所有 API 端点
- [ ] 识别出 3+ 个慢查询
- [ ] 所有 API 响应 < 500ms
- [ ] 记录了改进报告

---

### 5.1.4 数据库查询优化 ⏱️ 2天

#### 工作步骤
```python
# 1. 分析当前索引
import sqlite3
conn = sqlite3.connect('trustagency.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='index'")
current_indexes = c.fetchall()
print("当前索引:", current_indexes)

# 2. 为常用查询创建索引
# 识别以下查询并添加索引:

# 查询1: 按 section_id 查询文章 → 创建索引
CREATE INDEX idx_articles_section_id ON articles(section_id);

# 查询2: 按 task_id 查询任务 → 创建索引
CREATE INDEX idx_tasks_section_id ON tasks(section_id);

# 查询3: 按 status 查询任务 → 创建索引
CREATE INDEX idx_tasks_status ON tasks(status);

# 查询4: 按 created_at 范围查询 → 创建索引
CREATE INDEX idx_articles_created_at ON articles(created_at);

# 3. 实现查询缓存
# 使用内存缓存减少数据库查询

# 4. 验证性能提升
```

#### 检查清单
- [ ] 分析了现有索引结构
- [ ] 创建了 4+ 个必要索引
- [ ] 实现了查询结果缓存
- [ ] 验证了查询性能提升
- [ ] 生成了优化报告

#### 风险防控
```bash
# 每次数据库优化前备份
cp trustagency.db "backups/before_optimization_$(date +%s).db"

# 优化后验证数据完整性
python3 << 'EOF'
import sqlite3

def check_integrity():
    conn = sqlite3.connect('trustagency.db')
    c = conn.cursor()
    
    checks = {
        'articles': 'SELECT COUNT(*) FROM articles',
        'tasks': 'SELECT COUNT(*) FROM tasks',
        'sections': 'SELECT COUNT(*) FROM sections',
        'categories': 'SELECT COUNT(*) FROM categories',
        'platforms': 'SELECT COUNT(*) FROM platforms',
    }
    
    for table, query in checks.items():
        c.execute(query)
        count = c.fetchone()[0]
        print(f"✅ {table}: {count} 条记录")
    
    conn.close()

check_integrity()
EOF
```

---

## 📋 任务 5.2: 前端模块化完善 (优先级: 🔴 最高)

**目标**: 建立完整的模块加载体系，确保系统稳定性

### 5.2.1 全局 API 暴露机制 ⏱️ 1天

#### 工作步骤
1. **创建 bridge.js** - 全局 API 桥接
```javascript
// 文件: backend/site/admin/js/bridge.js
// 用途: 暴露所有模块的公共 API

window.AppAPI = {
    // 认证模块
    auth: {
        login: window.auth?.login || (() => { throw new Error('auth module not loaded'); }),
        logout: window.auth?.logout || (() => { throw new Error('auth module not loaded'); }),
        getCurrentUser: window.auth?.getCurrentUser || (() => { throw new Error('auth module not loaded'); }),
    },
    
    // UI 模块
    ui: {
        showModal: window.ui?.showModal || (() => { throw new Error('ui module not loaded'); }),
        closeModal: window.ui?.closeModal || (() => { throw new Error('ui module not loaded'); }),
        showNotification: window.ui?.showNotification || (() => { throw new Error('ui module not loaded'); }),
    },
    
    // API 客户端
    api: {
        getArticles: window.api?.getArticles || (() => { throw new Error('api module not loaded'); }),
        createArticle: window.api?.createArticle || (() => { throw new Error('api module not loaded'); }),
        updateArticle: window.api?.updateArticle || (() => { throw new Error('api module not loaded'); }),
    },
    
    // 工具函数
    utils: {
        formatDate: window.utils?.formatDate || (() => { throw new Error('utils module not loaded'); }),
        debounce: window.utils?.debounce || (() => { throw new Error('utils module not loaded'); }),
    },
};

// 调试模式：验证所有 API 是否可用
if (window.DEBUG_MODE) {
    console.log('🔍 AppAPI 调试模式启动');
    Object.keys(window.AppAPI).forEach(module => {
        console.log(`✅ ${module}:`, window.AppAPI[module]);
    });
}
```

2. **在 index.html 中导入**
```html
<!-- 在所有模块脚本后添加 -->
<script src="js/bridge.js"></script>
```

3. **测试**
```javascript
// 在浏览器控制台执行
console.log(window.AppAPI.auth.login)        // ✅ function
console.log(window.AppAPI.ui.showModal)      // ✅ function
console.log(window.AppAPI.api.getArticles)   // ✅ function
```

#### 检查清单
- [ ] 创建了 bridge.js
- [ ] 暴露了所有关键 API
- [ ] 添加了调试模式
- [ ] 浏览器控制台能访问所有 API
- [ ] 功能测试通过

---

### 5.2.2 模块加载失败降级处理 ⏱️ 1天

#### 工作步骤
```javascript
// 1. 添加加载失败检测
(function() {
    // 等待所有模块加载
    const requiredModules = ['auth', 'api', 'ui', 'utils'];
    const maxWaitTime = 5000; // 5秒
    const startTime = Date.now();
    
    const checkModules = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const missing = requiredModules.filter(m => !window[m]);
        
        if (missing.length === 0) {
            clearInterval(checkModules);
            console.log('✅ 所有模块加载成功');
            return;
        }
        
        if (elapsed > maxWaitTime) {
            clearInterval(checkModules);
            console.warn('⚠️ 部分模块加载失败:', missing);
            
            // 降级处理：加载备用脚本或显示警告
            showWarning(`系统模块加载失败: ${missing.join(', ')}`);
            
            // 加载备用脚本
            loadFallbackScript();
        }
    }, 100);
})();

// 2. 显示警告提示
function showWarning(message) {
    const warning = document.createElement('div');
    warning.className = 'system-warning';
    warning.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ffeb3b;
        color: #000;
        padding: 12px 20px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 10000;
    `;
    warning.textContent = '⚠️ ' + message;
    document.body.appendChild(warning);
    
    setTimeout(() => warning.remove(), 5000);
}

// 3. 加载备用脚本
function loadFallbackScript() {
    // 使用内联脚本作为备用
    eval(document.getElementById('fallback-script').textContent);
}
```

3. **在 HTML 中添加备用脚本**
```html
<script id="fallback-script" type="text/javascript">
// 备用的基础功能脚本
window.AppAPI = {
    auth: {},
    ui: {
        showNotification: (msg, type) => alert(msg),
    },
    api: {},
    utils: {},
};
console.log('⚠️ 使用备用脚本模式');
</script>
```

#### 检查清单
- [ ] 添加了模块加载检测
- [ ] 实现了失败降级处理
- [ ] 用户能看到友好提示
- [ ] 系统始终可用（即使部分模块失败）
- [ ] 测试模块加载失败场景

---

### 5.2.3 单元测试覆盖 ⏱️ 2天

#### 测试框架选择
```bash
# 安装 Jest
npm install --save-dev jest

# 初始化配置
npx jest --init
```

#### 测试示例 - auth.js
```javascript
// tests/auth.test.js
describe('auth module', () => {
    test('login should set token', () => {
        // 测试登录函数
        expect(window.auth.login).toBeDefined();
    });
    
    test('logout should clear token', () => {
        // 测试登出函数
        expect(window.auth.logout).toBeDefined();
    });
    
    test('getCurrentUser should return user data', () => {
        // 测试获取用户信息
        expect(window.auth.getCurrentUser).toBeDefined();
    });
});
```

#### 检查清单
- [ ] 安装并配置了测试框架
- [ ] 为 auth.js 编写了测试
- [ ] 为 api-client.js 编写了测试
- [ ] 测试覆盖率 > 70%
- [ ] 所有测试通过

---

### 5.2.4 代码清理 ⏱️ 1天

#### 工作步骤
```bash
1. 审查 index.html 文件
   - 移除未使用的脚本标签
   - 移除重复的缓存破坏器
   - 规范化事件处理器

2. 检查是否有:
   - 内联脚本超过 50 行
   - 重复的 <script> 标签
   - 无用的注释

3. 目标: HTML 文件 < 2000 行
```

#### 检查清单
- [ ] 审查了所有脚本标签
- [ ] 移除了重复的导入
- [ ] 移除了临时修复代码
- [ ] 规范化了命名
- [ ] HTML 文件 < 2000 行

---

## 📋 任务 5.3: 监控告警系统 (优先级: 🟠 高)

**目标**: 及时发现系统问题，防止事故恶化

### 5.3.1 前端性能监控 ⏱️ 1.5天

#### 监控指标
```javascript
// 创建文件: backend/site/admin/js/monitoring.js

class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.alerts = [];
    }
    
    // 1. 页面加载时间
    recordPageLoadTime() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            this.metrics.pageLoadTime = loadTime;
            
            if (loadTime > 3000) {
                this.alert('⚠️ 页面加载过慢: ' + loadTime + 'ms');
            }
        }
    }
    
    // 2. API 调用失败监控
    monitorApiCall(url, status, duration) {
        if (status >= 400) {
            this.alert(`❌ API 失败: ${url} (${status})`);
        }
        
        if (duration > 1000) {
            this.alert(`⚠️ API 响应慢: ${url} (${duration}ms)`);
        }
    }
    
    // 3. 内存占用监控
    monitorMemory() {
        if (performance.memory) {
            const usedMemory = performance.memory.usedJSHeapSize / 1048576; // 转换为 MB
            this.metrics.memory = usedMemory;
            
            if (usedMemory > 200) {
                this.alert(`⚠️ 内存占用过高: ${usedMemory.toFixed(2)}MB`);
            }
        }
    }
    
    // 4. 错误收集
    captureErrors() {
        window.addEventListener('error', (e) => {
            this.alert(`❌ JavaScript 错误: ${e.message}`);
            this.sendErrorReport({
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
            });
        });
    }
    
    // 5. 发送告警
    alert(message) {
        console.warn(message);
        this.alerts.push({
            timestamp: new Date(),
            message: message,
        });
        
        // 可选: 发送到后端
        this.sendToBackend('/api/alerts', { message });
    }
    
    // 6. 发送数据到后端
    sendToBackend(endpoint, data) {
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        }).catch(e => console.error('上报失败:', e));
    }
    
    // 7. 获取性能报告
    getReport() {
        return {
            metrics: this.metrics,
            alerts: this.alerts,
            timestamp: new Date(),
        };
    }
}

// 初始化监控
const monitor = new PerformanceMonitor();
window.addEventListener('load', () => {
    monitor.recordPageLoadTime();
    monitor.monitorMemory();
    monitor.captureErrors();
    
    // 定期检查
    setInterval(() => {
        monitor.monitorMemory();
    }, 5000); // 每 5 秒检查一次内存
});

// 暴露接口
window.getPerformanceReport = () => monitor.getReport();
```

#### 检查清单
- [ ] 创建了 monitoring.js
- [ ] 实现了页面加载时间监控
- [ ] 实现了 API 失败监控
- [ ] 实现了内存占用监控
- [ ] 实现了错误收集
- [ ] 可以查看性能报告 (`window.getPerformanceReport()`)

---

### 5.3.2 后端健康检查 ⏱️ 1.5天

#### 创建健康检查端点
```python
# 文件: backend/health_check.py

import asyncio
import sqlite3
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
async def health_check():
    """
    系统健康检查端点
    返回: 系统状态、数据库状态、最后检查时间
    """
    try:
        # 1. 检查数据库连接
        conn = sqlite3.connect("trustagency.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM articles")
        article_count = c.fetchone()[0]
        conn.close()
        
        # 2. 检查核心表
        checks = {
            "articles": article_count,
            "tasks": get_count("tasks"),
            "sections": get_count("sections"),
            "categories": get_count("categories"),
            "platforms": get_count("platforms"),
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": checks,
            "uptime": get_uptime(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

def get_count(table):
    """获取表中的行数"""
    conn = sqlite3.connect("trustagency.db")
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_uptime():
    """获取系统运行时间"""
    # 简单实现，可以从系统启动时间计算
    return "系统运行中"

# 启动服务
# python3 backend/health_check.py
# 访问: http://localhost:8001/api/health
```

#### 在主应用中集成
```python
# 在 backend/main.py 中添加

from fastapi import FastAPI
from datetime import datetime

@app.get("/api/health")
async def health_check():
    """系统健康检查"""
    try:
        conn = sqlite3.connect("trustagency.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM articles")
        count = c.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "articles": count,
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### 检查清单
- [ ] 创建了 health_check 端点
- [ ] 响应时间 < 100ms
- [ ] 能检查数据库连接
- [ ] 能验证核心表的行数
- [ ] 端点响应格式一致

---

### 5.3.3 自动备份系统 ⏱️ 1.5天

#### 创建自动备份脚本
```python
# 文件: backend/auto_backup.py

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import schedule
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def backup_database():
    """创建数据库备份"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        source = "trustagency.db"
        dest = f"{backup_dir}/trustagency_backup_{timestamp}.db"
        
        shutil.copy2(source, dest)
        logging.info(f"✅ 备份成功: {dest}")
        
        # 验证备份
        verify_backup(dest)
        
        # 清理过期备份 (保留7天)
        cleanup_old_backups(backup_dir, days=7)
        
    except Exception as e:
        logging.error(f"❌ 备份失败: {e}")

def verify_backup(backup_path):
    """验证备份的完整性"""
    try:
        conn = sqlite3.connect(backup_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM articles")
        count = c.fetchone()[0]
        conn.close()
        
        logging.info(f"✅ 备份验证通过: {count} 条记录")
        return True
    except Exception as e:
        logging.error(f"❌ 备份验证失败: {e}")
        return False

def cleanup_old_backups(backup_dir, days=7):
    """清理过期备份"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(backup_dir):
            if filename.startswith("trustagency_backup_"):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    logging.info(f"🗑️ 删除过期备份: {filename}")
    except Exception as e:
        logging.error(f"❌ 清理备份失败: {e}")

def schedule_backups():
    """定时执行备份"""
    # 每 6 小时备份一次
    schedule.every(6).hours.do(backup_database)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logging.info("🚀 启动自动备份系统")
    backup_database()  # 启动时备份一次
    schedule_backups()
```

#### 启动自动备份
```bash
# 后台运行
nohup python3 backend/auto_backup.py > /tmp/backup.log 2>&1 &

# 检查日志
tail -f /tmp/backup.log

# 查看备份文件
ls -lh backups/
```

#### 检查清单
- [ ] 创建了 auto_backup.py
- [ ] 实现了定时备份 (每 6 小时)
- [ ] 实现了备份验证
- [ ] 实现了过期备份清理
- [ ] 备份文件可恢复

---

### 5.3.4 日志收集和分析 ⏱️ 1天

#### 统一日志格式
```python
# 文件: backend/logging_config.py

import logging
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """JSON 格式的日志格式化器"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'module': record.name,
            'message': record.getMessage(),
            'filename': record.filename,
            'lineno': record.lineno,
        }
        
        return str(log_data)

# 配置日志处理器
def setup_logging():
    logger = logging.getLogger("trustagency")
    logger.setLevel(logging.DEBUG)
    
    # 文件处理器
    fh = logging.FileHandler("logs/app.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(JsonFormatter())
    
    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

#### 前端错误上报
```javascript
// 在 monitoring.js 中添加

class ErrorReporter {
    constructor() {
        this.buffer = [];
    }
    
    // 捕获错误
    captureError(error, context = {}) {
        const errorData = {
            timestamp: new Date().toISOString(),
            message: error.message,
            stack: error.stack,
            context: context,
            userAgent: navigator.userAgent,
        };
        
        this.buffer.push(errorData);
        
        // 批量发送 (每 10 个错误或 30 秒发送一次)
        if (this.buffer.length >= 10) {
            this.flush();
        }
    }
    
    // 发送错误到后端
    flush() {
        if (this.buffer.length === 0) return;
        
        fetch('/api/errors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ errors: this.buffer }),
        }).then(() => {
            console.log('✅ 错误已上报');
            this.buffer = [];
        }).catch(e => {
            console.error('❌ 错误上报失败:', e);
        });
    }
}

// 初始化
const errorReporter = new ErrorReporter();
window.addEventListener('error', (e) => {
    errorReporter.captureError(e);
});

// 定期发送
setInterval(() => {
    errorReporter.flush();
}, 30000); // 每 30 秒发送一次
```

#### 检查清单
- [ ] 建立了统一的日志格式
- [ ] 后端日志写入 logs/app.log
- [ ] 前端错误能上报到后端
- [ ] 可以查询和分析日志
- [ ] 日志系统正常运行

---

## ✅ Phase 5 验收标准

### 系统性能指标
- ✅ 页面首屏加载时间 < 3 秒
- ✅ 所有 API 响应时间 < 500ms
- ✅ 内存占用稳定 < 100MB
- ✅ 无明显内存泄漏（15 分钟内存增长 < 10MB）

### 系统可靠性
- ✅ 系统连续运行 72 小时无卡顿
- ✅ 无数据库错误或数据异常
- ✅ 所有功能正常工作
- ✅ 自动备份每 6 小时执行一次

### 代码质量
- ✅ 单元测试覆盖率 > 70%
- ✅ 所有 API 有文档说明
- ✅ 代码无明显问题或警告
- ✅ 前端 HTML 文件 < 2000 行

### 监控系统
- ✅ 能监控前端性能
- ✅ 能监控后端健康状态
- ✅ 能自动备份数据库
- ✅ 能收集和分析日志

---

## 📅 Phase 5 时间规划

| 周期 | 任务 | 完成标记 |
|------|------|---------|
| **第1周** | 5.1 性能诊断和优化 | ⏳ 进行中 |
| **第1周** | 5.2 前端模块化完善 | ⏳ 进行中 |
| **第2周** | 5.3 监控告警系统 | ⏳ 准备中 |
| **第2-3周** | 5.4 测试和验收 | ⏳ 准备中 |

---

## 🎯 立即行动清单

```bash
# 1. 创建 Phase 5 分支
git checkout -b refactor/admin-panel-phase5

# 2. 创建备份
cp trustagency.db backups/before_phase5_$(date +%s).db

# 3. 启动系统
python3 backend/main.py &
# 在另一个终端打开浏览器

# 4. 每天执行检查
bash daily_check.sh

# 5. 按照任务清单逐一完成
```

---

**🚀 Phase 5 启动完毕！**

**下一步**: 开始任务 5.1 性能诊断和优化
