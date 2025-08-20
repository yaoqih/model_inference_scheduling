from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import re

class NodeBase(BaseModel):
    environment_id: int = Field(..., description="环境ID")
    node_ip: str = Field(..., description="节点IP地址")
    node_port: int = Field(default=6004, ge=1, le=65535, description="节点端口")
    available_gpu_ids: Optional[List[str]] = Field(default_factory=list, description="可用GPU ID列表")
    available_models: Optional[List[str]] = Field(default_factory=list, description="可用模型列表")

    @classmethod
    def validate_ip(cls, v):
        # 简单的IP地址验证
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('无效的IP地址格式')
        return v

class NodeCreate(NodeBase):
    pass

class NodeUpdate(BaseModel):
    node_ip: Optional[str] = Field(None, description="节点IP地址")
    node_port: Optional[int] = Field(None, ge=1, le=65535, description="节点端口")
    available_gpu_ids: Optional[List[str]] = Field(None, description="可用GPU ID列表")
    available_models: Optional[List[str]] = Field(None, description="可用模型列表")

    @classmethod
    def validate_ip(cls, v):
        if v is not None:
            ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
            if not re.match(ip_pattern, v):
                raise ValueError('无效的IP地址格式')
        return v

class Node(NodeBase):
    id: int
    status: str = Field(description="节点状态: online, offline, error, unknown")
    last_heartbeat: Optional[datetime] = Field(None, description="最后心跳时间")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 节点状态更新
class NodeStatusUpdate(BaseModel):
    status: str = Field(..., description="节点状态")
    available_gpu_ids: Optional[List[str]] = Field(None, description="可用GPU ID列表")
    available_models: Optional[List[str]] = Field(None, description="可用模型列表")

# GPU信息
class GPUInfo(BaseModel):
    id: int
    memory_usage: float
    power_draw: float
    processes: List[dict]

# 模型实例信息
class ModelInstanceInfo(BaseModel):
    model_name: str
    gpu_id: int
    status: str
    pid: Optional[int] = None
    port: Optional[int] = None