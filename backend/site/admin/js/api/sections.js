/**
 * API 服务模块 - 栏目管理
 */

import apiClient from '../api-client.js';

class SectionsAPI {
    /**
     * 获取栏目列表
     */
    async getList() {
        return apiClient.get('/api/sections');
    }

    /**
     * 获取栏目详情
     */
    async getById(id) {
        return apiClient.get(`/api/sections/${id}`);
    }

    /**
     * 创建栏目
     */
    async create(section) {
        return apiClient.post('/api/sections', section);
    }

    /**
     * 更新栏目
     */
    async update(id, section) {
        return apiClient.put(`/api/sections/${id}`, section);
    }

    /**
     * 删除栏目
     */
    async delete(id) {
        return apiClient.delete(`/api/sections/${id}`);
    }
}

export default new SectionsAPI();
