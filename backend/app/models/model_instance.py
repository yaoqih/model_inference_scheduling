from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class ModelInstance(Base):
    __tablename__ = "model_instances"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    gpu_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=True)  # STARTING, RUNNING, STOPPED, ERROR
    pid = Column(Integer, nullable=True)
    port = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    node = relationship("Node", back_populates="model_instances")