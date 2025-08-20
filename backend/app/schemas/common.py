from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any, List

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "操作成功"
    code: int = 200

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    total: int
    page: int = 1
    page_size: int = 10
    message: str = "获取成功"

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    code: int
    details: Optional[Any] = None