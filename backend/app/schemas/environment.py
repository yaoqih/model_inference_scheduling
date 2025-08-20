from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EnvironmentBase(BaseModel):
    name: str = Field(..., max_length=100, description="环境名称")
    description: Optional[str] = Field(None, description="环境描述")

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="环境名称")
    description: Optional[str] = Field(None, description="环境描述")

class Environment(EnvironmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True