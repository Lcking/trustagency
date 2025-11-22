/**
 * API 服务模块 - 文件上传
 */

import apiClient from '../api-client.js';

class UploadAPI {
    /**
     * 上传图片
     */
    async uploadImage(file, onProgress = null) {
        return apiClient.upload('/api/upload/image', file, {}, onProgress);
    }

    /**
     * 上传文件
     */
    async uploadFile(file, onProgress = null) {
        return apiClient.upload('/api/upload/file', file, {}, onProgress);
    }

    /**
     * 批量上传图片
     */
    async uploadImages(files, onProgress = null) {
        const promises = files.map(file => 
            this.uploadImage(file, onProgress)
        );
        return Promise.all(promises);
    }
}

export default new UploadAPI();
