from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QueueInfo(BaseModel):
    """RabbitMQ队列信息"""
    name: str
    messages: int
    consumers: int
    idle_since: Optional[str] = None

    class Config:
        from_attributes = True


class QueueLengthRecordBase(BaseModel):
    length: int


class QueueLengthRecordCreate(QueueLengthRecordBase):
    model_id: int


class QueueLengthRecord(QueueLengthRecordBase):
    id: int
    model_id: int
    timestamp: datetime

    class Config:
        from_attributes = True