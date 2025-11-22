/**
 * API 服务模块 - AI配置管理
 */

import apiClient from '../api-client.js';

class AIConfigsAPI {
    /**
     * 获取AI配置列表
     */
    async getList() {
        return apiClient.get('/api/ai-configs');
    }

    /**
     * 获取AI配置详情
     */
    async getById(id) {
        return apiClient.get(`/api/ai-configs/${id}`);
    }

    /**
     * 创建AI配置
     */
    async create(config) {
        return apiClient.post('/api/ai-configs', config);
    }

    /**
     * 更新AI配置
     */
    async update(id, config) {
        return apiClient.put(`/api/ai-configs/${id}`, config);
    }

    /**
     * 删除AI配置
     */
    async delete(id) {
        return apiClient.delete(`/api/ai-configs/${id}`);
    }

    /**
     * 测试AI配置
     */
    async test(id) {
        return apiClient.post(`/api/ai-configs/${id}/test`);
    }
}

export default new AIConfigsAPI();
