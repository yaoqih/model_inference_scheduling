from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    node_ip = Column(String(45), nullable=False)
    node_port = Column(Integer, default=6004, nullable=False)
    available_gpu_ids = Column(Text, nullable=True)  # JSON格式存储 ["0", "1", "2"]
    available_models = Column(Text, nullable=True)   # JSON格式存储 ["MAM", "FastFitAll"]
    status = Column(String(20), default="unknown")   # online, offline, error, unknown
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    environment = relationship("Environment", back_populates="nodes")
    model_instances = relationship("ModelInstance", back_populates="node")