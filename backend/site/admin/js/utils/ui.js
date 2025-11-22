/**
 * UI 组件工具函数
 */

/**
 * 显示Toast提示
 */
export function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // 样式
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 24px',
        borderRadius: '4px',
        color: '#fff',
        fontSize: '14px',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease-out',
        minWidth: '200px',
        maxWidth: '400px',
        boxShadow: '0 2px 12px rgba(0,0,0,0.15)'
    });
    
    // 根据类型设置背景色
    const colors = {
        info: '#409EFF',
        success: '#67C23A',
        warning: '#E6A23C',
        error: '#F56C6C'
    };
    toast.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(toast);
    
    // 自动移除
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, duration);
}

/**
 * 显示确认对话框
 */
export function showConfirm(message, options = {}) {
    const {
        title = '确认',
        confirmText = '确定',
        cancelText = '取消',
        type = 'warning'
    } = options;
    
    return new Promise((resolve) => {
        // 创建遮罩
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        Object.assign(overlay.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            right: '0',
            bottom: '0',
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: '9998'
        });
        
        // 创建对话框
        const modal = document.createElement('div');
        modal.className = 'modal';
        Object.assign(modal.style, {
            backgroundColor: '#fff',
            borderRadius: '4px',
            padding: '20px',
            minWidth: '300px',
            maxWidth: '500px',
            boxShadow: '0 2px 12px rgba(0,0,0,0.3)'
        });
        
        // 标题
        const titleEl = document.createElement('h3');
        titleEl.textContent = title;
        Object.assign(titleEl.style, {
            margin: '0 0 15px 0',
            fontSize: '18px',
            fontWeight: 'bold'
        });
        
        // 消息
        const messageEl = document.createElement('p');
        messageEl.textContent = message;
        Object.assign(messageEl.style, {
            margin: '0 0 20px 0',
            fontSize: '14px',
            lineHeight: '1.5'
        });
        
        // 按钮容器
        const btnContainer = document.createElement('div');
        Object.assign(btnContainer.style, {
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '10px'
        });
        
        // 取消按钮
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = cancelText;
        cancelBtn.className = 'btn btn-default';
        Object.assign(cancelBtn.style, {
            padding: '8px 20px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            cursor: 'pointer',
            backgroundColor: '#fff'
        });
        
        // 确定按钮
        const confirmBtn = document.createElement('button');
        confirmBtn.textContent = confirmText;
        confirmBtn.className = `btn btn-${type}`;
        Object.assign(confirmBtn.style, {
            padding: '8px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            backgroundColor: type === 'warning' ? '#E6A23C' : '#409EFF',
            color: '#fff'
        });
        
        // 事件处理
        const close = (result) => {
            document.body.removeChild(overlay);
            resolve(result);
        };
        
        cancelBtn.onclick = () => close(false);
        confirmBtn.onclick = () => close(true);
        overlay.onclick = (e) => {
            if (e.target === overlay) close(false);
        };
        
        // 组装
        btnContainer.appendChild(cancelBtn);
        btnContainer.appendChild(confirmBtn);
        modal.appendChild(titleEl);
        modal.appendChild(messageEl);
        modal.appendChild(btnContainer);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
    });
}

/**
 * 显示Loading
 */
export function showLoading(message = '加载中...') {
    const loading = document.createElement('div');
    loading.className = 'loading-overlay';
    loading.id = 'global-loading';
    
    Object.assign(loading.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        right: '0',
        bottom: '0',
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: '9999'
    });
    
    // Loading图标
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    Object.assign(spinner.style, {
        width: '40px',
        height: '40px',
        border: '4px solid rgba(255,255,255,0.3)',
        borderTop: '4px solid #fff',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
    });
    
    // 消息
    const text = document.createElement('p');
    text.textContent = message;
    Object.assign(text.style, {
        color: '#fff',
        marginTop: '15px',
        fontSize: '14px'
    });
    
    loading.appendChild(spinner);
    loading.appendChild(text);
    document.body.appendChild(loading);
    
    // 添加动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    if (!document.querySelector('#ui-animations')) {
        style.id = 'ui-animations';
        document.head.appendChild(style);
    }
    
    return loading;
}

/**
 * 隐藏Loading
 */
export function hideLoading() {
    const loading = document.getElementById('global-loading');
    if (loading) {
        document.body.removeChild(loading);
    }
}

/**
 * 显示进度条
 */
export class ProgressBar {
    constructor() {
        this.bar = null;
        this.progress = 0;
    }
    
    show() {
        if (this.bar) return;
        
        this.bar = document.createElement('div');
        this.bar.className = 'progress-bar';
        Object.assign(this.bar.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            height: '3px',
            width: '0%',
            backgroundColor: '#409EFF',
            transition: 'width 0.3s',
            zIndex: '10000'
        });
        
        document.body.appendChild(this.bar);
    }
    
    set(percent) {
        if (!this.bar) this.show();
        this.progress = Math.min(Math.max(percent, 0), 100);
        this.bar.style.width = this.progress + '%';
    }
    
    inc(amount = 5) {
        this.set(this.progress + amount);
    }
    
    done() {
        this.set(100);
        setTimeout(() => this.hide(), 300);
    }
    
    hide() {
        if (this.bar) {
            document.body.removeChild(this.bar);
            this.bar = null;
            this.progress = 0;
        }
    }
}

/**
 * 创建分页器
 */
export function createPagination(container, options = {}) {
    const {
        total = 0,
        page = 1,
        pageSize = 20,
        onChange = () => {}
    } = options;
    
    const totalPages = Math.ceil(total / pageSize);
    
    container.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // 上一页
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = page === 1;
    prevBtn.onclick = () => onChange(page - 1);
    container.appendChild(prevBtn);
    
    // 页码
    const maxVisible = 7;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === page ? 'active' : '';
        pageBtn.onclick = () => onChange(i);
        container.appendChild(pageBtn);
    }
    
    // 下一页
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = page === totalPages;
    nextBtn.onclick = () => onChange(page + 1);
    container.appendChild(nextBtn);
}

// 导出单例进度条
export const progressBar = new ProgressBar();
