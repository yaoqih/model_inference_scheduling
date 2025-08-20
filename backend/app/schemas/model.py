from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ModelBase(BaseModel):
    environment_id: int = Field(..., description="环境ID")
    model_name: str = Field(..., max_length=100, description="模型名称")
    inference_time: Optional[float] = Field(None, ge=0, description="推理时间(秒)")
    average_inference_time: Optional[float] = Field(None, ge=0, description="平均推理时间(秒)")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    port: Optional[int] = Field(None, ge=1, le=65535, description="端口")
    rabbitmq_queue_name: Optional[str] = Field(None, description="RabbitMQ队列名")
    rabbitmq_host: Optional[str] = Field(None, description="RabbitMQ主机")
    rabbitmq_port: int = Field(default=15672, ge=1, le=65535, description="RabbitMQ端口")
    rabbitmq_username: Optional[str] = Field(None, description="RabbitMQ用户名")
    rabbitmq_password: Optional[str] = Field(None, description="RabbitMQ密码")
    rabbitmq_vhost: str = Field(default="/", description="RabbitMQ虚拟主机")

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    model_name: Optional[str] = Field(None, max_length=100, description="模型名称")
    inference_time: Optional[float] = Field(None, ge=0, description="推理时间(秒)")
    average_inference_time: Optional[float] = Field(None, ge=0, description="平均推理时间(秒)")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    port: Optional[int] = Field(None, ge=1, le=65535, description="端口")
    rabbitmq_queue_name: Optional[str] = Field(None, description="RabbitMQ队列名")
    rabbitmq_host: Optional[str] = Field(None, description="RabbitMQ主机")
    rabbitmq_port: Optional[int] = Field(None, ge=1, le=65535, description="RabbitMQ端口")
    rabbitmq_username: Optional[str] = Field(None, description="RabbitMQ用户名")
    rabbitmq_password: Optional[str] = Field(None, description="RabbitMQ密码")
    rabbitmq_vhost: Optional[str] = Field(None, description="RabbitMQ虚拟主机")

class Model(ModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True