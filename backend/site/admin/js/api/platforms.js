/**
 * API 服务模块 - 平台管理
 */

import apiClient from '../api-client.js';

class PlatformsAPI {
    /**
     * 获取平台列表
     */
    async getList() {
        return apiClient.get('/api/platforms');
    }

    /**
     * 获取平台详情
     */
    async getById(id) {
        return apiClient.get(`/api/platforms/${id}`);
    }

    /**
     * 创建平台
     */
    async create(platform) {
        return apiClient.post('/api/platforms', platform);
    }

    /**
     * 更新平台
     */
    async update(id, platform) {
        return apiClient.put(`/api/platforms/${id}`, platform);
    }

    /**
     * 删除平台
     */
    async delete(id) {
        return apiClient.delete(`/api/platforms/${id}`);
    }
}

export default new PlatformsAPI();
