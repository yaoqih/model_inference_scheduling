from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    inference_time = Column(Float, nullable=True)
    average_inference_time = Column(Float, nullable=True, comment="平均推理时间(秒)")
    username = Column(String(100), nullable=True)
    password = Column(String(100), nullable=True)
    port = Column(Integer, nullable=True)
    rabbitmq_queue_name = Column(String(100), nullable=True)
    rabbitmq_host = Column(String(255), nullable=True)
    rabbitmq_port = Column(Integer, default=15672)
    rabbitmq_username = Column(String(100), nullable=True)
    rabbitmq_password = Column(String(100), nullable=True)
    rabbitmq_vhost = Column(String(100), default="/")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    environment = relationship("Environment", back_populates="models")