/**
 * API 服务模块 - 认证相关
 */

import apiClient from '../api-client.js';
import { STORAGE_KEYS } from '../config.js';

class AuthAPI {
    /**
     * 用户登录
     */
    async login(username, password) {
        const response = await apiClient.post('/api/admin/login', {
            username,
            password
        });

        // 保存token和用户信息
        if (response.access_token) {
            apiClient.setToken(response.access_token);
        }
        
        if (response.user) {
            localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
        }

        return response;
    }

    /**
     * 用户登出
     */
    async logout() {
        // 清除本地存储
        apiClient.setToken(null);
        localStorage.removeItem(STORAGE_KEYS.USER);
        
        // 可以调用后端登出接口（如果有的话）
        // await apiClient.post('/api/admin/logout');
    }

    /**
     * 获取当前用户信息
     */
    getCurrentUser() {
        const userStr = localStorage.getItem(STORAGE_KEYS.USER);
        return userStr ? JSON.parse(userStr) : null;
    }

    /**
     * 检查是否已登录
     */
    isAuthenticated() {
        return !!apiClient.getToken();
    }

    /**
     * 检查是否是超级管理员
     */
    isSuperAdmin() {
        const user = this.getCurrentUser();
        return user?.is_superadmin === true;
    }

    /**
     * 修改密码
     */
    async changePassword(oldPassword, newPassword) {
        return apiClient.post('/api/admin/change-password', {
            old_password: oldPassword,
            new_password: newPassword
        });
    }
}

export default new AuthAPI();
