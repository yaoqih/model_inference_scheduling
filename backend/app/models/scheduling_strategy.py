from sqlalchemy import Column, Integer, String, Boolean, Text
from ..database import Base

class SchedulingStrategy(Base):
    __tablename__ = "scheduling_strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)