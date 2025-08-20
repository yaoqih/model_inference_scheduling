// 环境类型定义
export interface Environment {
  id?: number;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

// 模型类型定义
export interface Model {
  id?: number;
  model_name: string;
  description?: string;
  environment_id: number;
  average_inference_time?: number;
  rabbitmq_host?: string;
  rabbitmq_port?: number;
  rabbitmq_username?: string;
  rabbitmq_password?: string;
  rabbitmq_queue_name?: string;
  queue_length?: number;
  created_at?: string;
  updated_at?: string;
}

// 节点类型定义
export interface Node {
  id?: number;
  environment_id: number;
  node_ip: string;
  node_port: number;
  available_gpu_ids?: string[];
  available_models?: string[];
  status?: 'online' | 'offline' | 'unknown' | 'error';
  last_heartbeat?: string;
  created_at?: string;
  updated_at?: string;
}

// API响应类型
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// RabbitMQ队列信息类型
export interface QueueInfo {
  name: string;
  message_count: number;
  consumer_count: number;
  status: string;
}

// 部署状态相关类型
export interface DeployedModelInfo {
  model_name: string;
  status: string;
}

export interface GPUDeploymentStatus {
  gpu_id: number;
  deployed_model?: DeployedModelInfo;
  gpu_load?: number;
  memory_used?: number;
  memory_total?: number;
  power_usage?: number;
  power_limit?: number;
}

export interface NodeDeploymentStatus {
  node_id: number;
  node_ip: string;
  node_port: number;
  available_models: string[];
  available_gpu_ids: number[];
  gpus: GPUDeploymentStatus[];
}

export interface ModelDeploymentStat {
  model_name: string;
  count: number;
}

export interface DeploymentSummary {
  model_stats: ModelDeploymentStat[];
  deployment_statuses: NodeDeploymentStatus[];
}

// 队列长度历史记录类型
export interface QueueLengthRecord {
  id: number;
  model_id: number;
  length: number;
  timestamp: string;
}

// 调度策略类型定义
export interface SchedulingStrategy {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export {};