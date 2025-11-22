/**
 * API 服务模块 - AI任务相关
 */

import apiClient from '../api-client.js';

class TasksAPI {
    /**
     * 获取任务列表
     */
    async getList(params = {}) {
        return apiClient.get('/api/tasks', params);
    }

    /**
     * 获取任务详情
     */
    async getById(id) {
        return apiClient.get(`/api/tasks/${id}`);
    }

    /**
     * 创建生成任务
     */
    async create(taskData) {
        return apiClient.post('/api/tasks/generate', taskData);
    }

    /**
     * 取消任务
     */
    async cancel(id) {
        return apiClient.post(`/api/tasks/${id}/cancel`);
    }

    /**
     * 重试失败任务
     */
    async retry(id) {
        return apiClient.post(`/api/tasks/${id}/retry`);
    }

    /**
     * 删除任务
     */
    async delete(id) {
        return apiClient.delete(`/api/tasks/${id}`);
    }

    /**
     * 获取任务进度
     */
    async getProgress(taskIds) {
        return apiClient.post('/api/tasks/progress', { task_ids: taskIds });
    }

    /**
     * 获取任务健康状态
     */
    async getHealth() {
        return apiClient.get('/api/tasks/health');
    }

    /**
     * 恢复卡住的任务
     */
    async recoverStuck() {
        return apiClient.post('/api/tasks/recovery/stuck');
    }

    /**
     * 恢复超时的任务
     */
    async recoverTimeout() {
        return apiClient.post('/api/tasks/recovery/timeout');
    }

    /**
     * 批量生成文章
     */
    async batchGenerate(data) {
        return apiClient.post('/api/tasks/batch-generate', data);
    }
}

export default new TasksAPI();
