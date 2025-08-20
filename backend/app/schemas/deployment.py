from pydantic import BaseModel, Field
from typing import List, Optional

class DeployedModelInfo(BaseModel):
    """单个部署模型的信息"""
    model_name: str
    status: str

class GPUDeploymentStatus(BaseModel):
    """单个GPU的部署状态和负载"""
    gpu_id: int
    deployed_model: Optional[DeployedModelInfo] = None
    gpu_load: Optional[float] = Field(None, description="GPU aio_load in percentage")
    memory_used: Optional[float] = Field(None, description="Memory used in MB")
    memory_total: Optional[float] = Field(None, description="Total memory in MB")
    power_usage: Optional[float] = Field(None, description="Power usage in Watts")
    power_limit: Optional[float] = Field(None, description="Power limit in Watts")

class NodeDeploymentStatus(BaseModel):
    """单个节点的完整部署状态"""
    node_id: int
    node_ip: str
    node_port: int
    available_models: List[str] = []
    available_gpu_ids: List[int] = []
    gpus: List[GPUDeploymentStatus] = []

class ModelDeploymentStat(BaseModel):
    """单个模型的部署数量统计"""
    model_name: str
    count: int

class DeploymentSummary(BaseModel):
    """部署页面的聚合数据结构"""
    model_stats: List[ModelDeploymentStat]
    deployment_statuses: List[NodeDeploymentStatus]