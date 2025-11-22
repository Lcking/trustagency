/**
 * API 服务模块 - 分类管理
 */

import apiClient from '../api-client.js';

class CategoriesAPI {
    /**
     * 获取分类列表
     */
    async getList(params = {}) {
        return apiClient.get('/api/categories', params);
    }

    /**
     * 获取分类详情
     */
    async getById(id) {
        return apiClient.get(`/api/categories/${id}`);
    }

    /**
     * 创建分类
     */
    async create(category) {
        return apiClient.post('/api/categories', category);
    }

    /**
     * 更新分类
     */
    async update(id, category) {
        return apiClient.put(`/api/categories/${id}`, category);
    }

    /**
     * 删除分类
     */
    async delete(id) {
        return apiClient.delete(`/api/categories/${id}`);
    }

    /**
     * 根据栏目获取分类
     */
    async getBySectionId(sectionId) {
        return apiClient.get('/api/categories', { section_id: sectionId });
    }
}

export default new CategoriesAPI();
