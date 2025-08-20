from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class QueueLengthRecord(Base):
    __tablename__ = "queue_length_records"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    length = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    model = relationship("Model")