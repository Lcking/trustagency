/**
 * API 配置管理
 */

// API 基础配置
export const API_CONFIG = {
    BASE_URL: (() => {
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const port = window.location.port;
        
        if (host === 'localhost' || host === '127.0.0.1') {
            return `${protocol}//${host}:8001`;
        }
        return port ? `${protocol}//${host}:${port}` : `${protocol}//${host}`;
    })(),
    TIMEOUT: 30000,
    RETRY_TIMES: 3,
    RETRY_DELAY: 1000
};

// 存储键名
export const STORAGE_KEYS = {
    TOKEN: 'token',
    USER: 'currentUser',
    THEME: 'theme',
    LANGUAGE: 'language'
};

// 用户角色
export const USER_ROLES = {
    SUPER_ADMIN: 'superadmin',
    ADMIN: 'admin',
    EDITOR: 'editor',
    VIEWER: 'viewer'
};

// 任务状态
export const TASK_STATUS = {
    PENDING: 'pending',
    PROCESSING: 'processing',
    COMPLETED: 'completed',
    FAILED: 'failed',
    CANCELLED: 'cancelled'
};

// 任务状态显示映射
export const TASK_STATUS_MAP = {
    pending: { text: '待处理', class: 'badge-warning' },
    processing: { text: '处理中', class: 'badge-info' },
    completed: { text: '已完成', class: 'badge-success' },
    failed: { text: '失败', class: 'badge-danger' },
    cancelled: { text: '已取消', class: 'badge-secondary' }
};

// 文章状态
export const ARTICLE_STATUS = {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    ARCHIVED: 'archived'
};

// 分页配置
export const PAGINATION = {
    DEFAULT_PAGE: 1,
    DEFAULT_SIZE: 20,
    MAX_SIZE: 100
};

// UI 动画时长
export const ANIMATION = {
    DURATION_FAST: 150,
    DURATION_NORMAL: 300,
    DURATION_SLOW: 500
};

// HTTP 状态码
export const HTTP_STATUS = {
    OK: 200,
    CREATED: 201,
    NO_CONTENT: 204,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_ERROR: 500,
    SERVICE_UNAVAILABLE: 503
};

// 错误消息
export const ERROR_MESSAGES = {
    NETWORK_ERROR: '网络连接失败，请检查网络',
    TIMEOUT_ERROR: '请求超时，请稍后重试',
    AUTH_ERROR: '认证失败，请重新登录',
    PERMISSION_ERROR: '权限不足',
    NOT_FOUND: '请求的资源不存在',
    SERVER_ERROR: '服务器错误，请稍后重试',
    UNKNOWN_ERROR: '未知错误，请稍后重试'
};

// 成功消息
export const SUCCESS_MESSAGES = {
    CREATE: '创建成功',
    UPDATE: '更新成功',
    DELETE: '删除成功',
    SAVE: '保存成功',
    LOGIN: '登录成功',
    LOGOUT: '退出成功'
};
