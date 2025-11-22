/**
 * 本地存储工具函数
 */

import { STORAGE_KEYS } from '../config.js';

/**
 * LocalStorage 工具类
 */
class Storage {
    /**
     * 存储数据
     */
    set(key, value, expire = null) {
        try {
            const data = {
                value,
                expire: expire ? Date.now() + expire : null
            };
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('存储失败:', error);
            return false;
        }
    }
    
    /**
     * 获取数据
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            if (!item) return defaultValue;
            
            const data = JSON.parse(item);
            
            // 检查是否过期
            if (data.expire && Date.now() > data.expire) {
                this.remove(key);
                return defaultValue;
            }
            
            return data.value;
        } catch (error) {
            console.error('读取失败:', error);
            return defaultValue;
        }
    }
    
    /**
     * 移除数据
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('移除失败:', error);
            return false;
        }
    }
    
    /**
     * 清空所有数据
     */
    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('清空失败:', error);
            return false;
        }
    }
    
    /**
     * 检查是否存在
     */
    has(key) {
        return localStorage.getItem(key) !== null;
    }
    
    /**
     * 获取所有键
     */
    keys() {
        return Object.keys(localStorage);
    }
    
    /**
     * 获取存储大小（字节）
     */
    size() {
        let total = 0;
        for (const key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                total += localStorage[key].length + key.length;
            }
        }
        return total;
    }
}

// 导出单例
export const storage = new Storage();

/**
 * 业务专用存储函数
 */

/**
 * 存储用户Token
 */
export function setToken(token) {
    return storage.set(STORAGE_KEYS.TOKEN, token);
}

/**
 * 获取用户Token
 */
export function getToken() {
    return storage.get(STORAGE_KEYS.TOKEN);
}

/**
 * 移除用户Token
 */
export function removeToken() {
    return storage.remove(STORAGE_KEYS.TOKEN);
}

/**
 * 存储用户信息
 */
export function setUserInfo(userInfo) {
    return storage.set(STORAGE_KEYS.USER_INFO, userInfo);
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
    return storage.get(STORAGE_KEYS.USER_INFO);
}

/**
 * 移除用户信息
 */
export function removeUserInfo() {
    return storage.remove(STORAGE_KEYS.USER_INFO);
}

/**
 * 存储搜索历史
 */
export function addSearchHistory(keyword, maxLength = 10) {
    const history = storage.get(STORAGE_KEYS.SEARCH_HISTORY, []);
    
    // 移除重复
    const filtered = history.filter(item => item !== keyword);
    
    // 添加到开头
    filtered.unshift(keyword);
    
    // 限制长度
    const limited = filtered.slice(0, maxLength);
    
    return storage.set(STORAGE_KEYS.SEARCH_HISTORY, limited);
}

/**
 * 获取搜索历史
 */
export function getSearchHistory() {
    return storage.get(STORAGE_KEYS.SEARCH_HISTORY, []);
}

/**
 * 清空搜索历史
 */
export function clearSearchHistory() {
    return storage.remove(STORAGE_KEYS.SEARCH_HISTORY);
}

/**
 * 存储分页设置
 */
export function setPageSize(pageSize) {
    return storage.set(STORAGE_KEYS.PAGE_SIZE, pageSize);
}

/**
 * 获取分页设置
 */
export function getPageSize(defaultSize = 20) {
    return storage.get(STORAGE_KEYS.PAGE_SIZE, defaultSize);
}

/**
 * 存储主题设置
 */
export function setTheme(theme) {
    return storage.set(STORAGE_KEYS.THEME, theme);
}

/**
 * 获取主题设置
 */
export function getTheme(defaultTheme = 'light') {
    return storage.get(STORAGE_KEYS.THEME, defaultTheme);
}

/**
 * 存储语言设置
 */
export function setLanguage(lang) {
    return storage.set(STORAGE_KEYS.LANGUAGE, lang);
}

/**
 * 获取语言设置
 */
export function getLanguage(defaultLang = 'zh-CN') {
    return storage.get(STORAGE_KEYS.LANGUAGE, defaultLang);
}

/**
 * SessionStorage 工具类
 */
class SessionStorage {
    /**
     * 存储数据
     */
    set(key, value) {
        try {
            sessionStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Session存储失败:', error);
            return false;
        }
    }
    
    /**
     * 获取数据
     */
    get(key, defaultValue = null) {
        try {
            const item = sessionStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Session读取失败:', error);
            return defaultValue;
        }
    }
    
    /**
     * 移除数据
     */
    remove(key) {
        try {
            sessionStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Session移除失败:', error);
            return false;
        }
    }
    
    /**
     * 清空所有数据
     */
    clear() {
        try {
            sessionStorage.clear();
            return true;
        } catch (error) {
            console.error('Session清空失败:', error);
            return false;
        }
    }
    
    /**
     * 检查是否存在
     */
    has(key) {
        return sessionStorage.getItem(key) !== null;
    }
}

// 导出单例
export const session = new SessionStorage();
