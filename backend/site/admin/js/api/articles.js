/**
 * API 服务模块 - 文章管理
 */

import apiClient from '../api-client.js';

class ArticlesAPI {
    /**
     * 获取文章列表
     */
    async getList(params = {}) {
        return apiClient.get('/api/articles', params);
    }

    /**
     * 获取文章详情
     */
    async getById(id) {
        return apiClient.get(`/api/articles/${id}`);
    }

    /**
     * 创建文章
     */
    async create(article) {
        return apiClient.post('/api/articles', article);
    }

    /**
     * 更新文章
     */
    async update(id, article) {
        return apiClient.put(`/api/articles/${id}`, article);
    }

    /**
     * 删除文章
     */
    async delete(id) {
        return apiClient.delete(`/api/articles/${id}`);
    }

    /**
     * 发布文章
     */
    async publish(id) {
        return apiClient.post(`/api/articles/${id}/publish`);
    }

    /**
     * 取消发布
     */
    async unpublish(id) {
        return apiClient.post(`/api/articles/${id}/unpublish`);
    }

    /**
     * 批量删除文章
     */
    async batchDelete(ids) {
        return apiClient.post('/api/articles/batch-delete', { ids });
    }

    /**
     * 批量发布文章
     */
    async batchPublish(ids) {
        return apiClient.post('/api/articles/batch-publish', { ids });
    }
}

export default new ArticlesAPI();
