import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 环境相关API
export const environmentAPI = {
  // 获取所有环境
  getAll: (skip: number = 0, limit: number = 100) =>
    api.get(`/environments/?skip=${skip}&limit=${limit}`),
  
  // 根据ID获取环境
  getById: (id: number) =>
    api.get(`/environments/${id}`),
  
  // 创建环境
  create: (data: any) =>
    api.post('/environments/', data),
  
  // 更新环境
  update: (id: number, data: any) =>
    api.put(`/environments/${id}`, data),
  
  // 删除环境
  delete: (id: number) =>
    api.delete(`/environments/${id}`),
};

// 模型相关API
export const modelAPI = {
  // 获取所有模型
  getAll: (environmentId?: number, skip: number = 0, limit: number = 100) => {
    const params = new URLSearchParams();
    if (environmentId) params.append('environment_id', environmentId.toString());
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return api.get(`/models/?${params.toString()}`);
  },
  
  // 根据ID获取模型
  getById: (id: number) =>
    api.get(`/models/${id}`),
  
  // 创建模型
  create: (data: any) =>
    api.post('/models/', data),
  
  // 更新模型
  update: (id: number, data: any) =>
    api.put(`/models/${id}`, data),
  
  // 删除模型
  delete: (id: number) =>
    api.delete(`/models/${id}`),
};

// 节点相关API
export const nodeAPI = {
  // 获取所有节点
  getAll: (environmentId?: number, skip: number = 0, limit: number = 100) => {
    const params = new URLSearchParams();
    if (environmentId) params.append('environment_id', environmentId.toString());
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return api.get(`/nodes/?${params.toString()}`);
  },
  
  // 根据ID获取节点
  getById: (id: number) =>
    api.get(`/nodes/${id}`),
  
  // 创建节点
  create: (data: any) =>
    api.post('/nodes/', data),
  
  // 更新节点
  update: (id: number, data: any) =>
    api.put(`/nodes/${id}`, data),
  
  // 删除节点
  delete: (id: number) =>
    api.delete(`/nodes/${id}`),
  
  // 获取节点状态
  getStatus: (id: number) =>
    api.get(`/nodes/${id}/status`),
  
  // 获取节点模型
  getModels: (id: number) =>
    api.get(`/nodes/${id}/models`),
  
  // 加载模型到节点
  loadModel: (nodeId: number, modelId: number) =>
    api.post(`/nodes/${nodeId}/load_model`, { model_id: modelId }),
  
  // 从节点卸载模型
  unloadModel: (nodeId: number, modelId: number) =>
    api.post(`/nodes/${nodeId}/unload_model`, { model_id: modelId }),

  // 发现节点可用模型
  discoverModels: (nodeId: number) =>
    api.post(`/nodes/${nodeId}/discover_models`),

  // 获取节点模型列表
  getNodeModels: (nodeId: number) =>
    api.get(`/nodes/${nodeId}/models`),

  // 获取节点GPU状态
  getGpuStatus: (nodeId: number) =>
    api.get(`/nodes/${nodeId}/gpu-status`),

  // 获取节点模型状态
  getModelStatus: (nodeId: number) =>
    api.get(`/nodes/${nodeId}/model-status`),

  // 在节点上启动模型
  startModel: (nodeId: number, modelName:string, gpuId: number, config?: any) =>
    api.post(`/nodes/${nodeId}/models/start`, {
      model_name: modelName,
      gpu_id: gpuId,
      config: config || {}
    }, { timeout: 180000 }), // 3分钟超时

  // 在节点上停止模型
  stopModel: (nodeId: number, modelName: string, gpuId: number) =>
    api.post(`/nodes/${nodeId}/models/stop`, {
      model_name: modelName,
      gpu_id: gpuId
    }, { timeout: 180000 }), // 3分钟超时

  // 终止节点进程
  killProcess: (nodeId: number, pid: number) =>
    api.delete(`/nodes/${nodeId}/processes/${pid}`),

  // 发现节点支持的模型
  discoverSupportedModels: (nodeId: number) =>
    api.get(`/nodes/${nodeId}/models/supported`),
};

// 队列相关API
export const queueAPI = {
  // 根据模型ID获取队列信息
  getQueueInfo: (modelId: number) => api.get(`/queues/${modelId}`),

  // 根据模型ID获取队列长度历史记录
  getQueueHistory: (modelId: number, limit: number = 100) =>
    api.get(`/queues/${modelId}/history?limit=${limit}`),
};

// 部署相关API
export const deploymentAPI = {
  // 获取所有节点的部署状态
  getStatus: (environmentId?: number) => {
    const params = new URLSearchParams();
    if (environmentId) {
      params.append('environment_id', environmentId.toString());
    }
    return api.get(`/deployments/status?${params.toString()}`);
  },
};

// 调度策略相关API
export const schedulingStrategyAPI = {
  // 获取所有调度策略
  getAll: (skip: number = 0, limit: number = 100) =>
    api.get(`/scheduling-strategies/?skip=${skip}&limit=${limit}`),
  
  // 根据ID获取调度策略
  getById: (id: number) =>
    api.get(`/scheduling-strategies/${id}`),
  
  // 创建调度策略
  create: (data: { name: string; description?: string; is_active?: boolean }) =>
    api.post('/scheduling-strategies/', data),
  
  // 更新调度策略
  update: (id: number, data: { name?: string; description?: string; is_active?: boolean }) =>
    api.put(`/scheduling-strategies/${id}`, data),
  
  // 删除调度策略
  delete: (id: number) =>
    api.delete(`/scheduling-strategies/${id}`),
};

export default api;