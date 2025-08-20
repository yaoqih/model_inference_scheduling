from pydantic import BaseModel
from typing import Optional

class SchedulingStrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = False

class SchedulingStrategyCreate(SchedulingStrategyBase):
    pass

class SchedulingStrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class SchedulingStrategy(SchedulingStrategyBase):
    id: int

    class Config:
        from_attributes = True