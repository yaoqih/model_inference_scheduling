import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models.environment import Environment
from ...schemas.environment import Environment as EnvironmentSchema, EnvironmentCreate, EnvironmentUpdate
from ...schemas.common import APIResponse, PaginatedResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=APIResponse[List[EnvironmentSchema]])
def get_environments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有环境"""
    logger.info(f"获取环境列表: skip={skip}, limit={limit}")
    environments = db.query(Environment).offset(skip).limit(limit).all()
    return APIResponse(
        data=environments,
        message=f"成功获取 {len(environments)} 个环境"
    )

@router.post("/", response_model=APIResponse[EnvironmentSchema])
def create_environment(
    environment: EnvironmentCreate,
    db: Session = Depends(get_db)
):
    """创建新环境"""
    logger.info(f"创建新环境: name='{environment.name}'")
    # 检查环境名称是否已存在
    existing = db.query(Environment).filter(Environment.name == environment.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"环境名称 '{environment.name}' 已存在")
    
    # 创建新环境
    db_environment = Environment(**environment.dict())
    db.add(db_environment)
    db.commit()
    db.refresh(db_environment)
    
    return APIResponse(
        data=db_environment,
        message=f"环境 '{environment.name}' 创建成功"
    )

@router.get("/{environment_id}", response_model=APIResponse[EnvironmentSchema])
def get_environment(
    environment_id: int,
    db: Session = Depends(get_db)
):
    """获取指定环境详情"""
    logger.info(f"获取环境详情: id={environment_id}")
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    return APIResponse(
        data=environment,
        message="环境详情获取成功"
    )

@router.put("/{environment_id}", response_model=APIResponse[EnvironmentSchema])
def update_environment(
    environment_id: int,
    environment_update: EnvironmentUpdate,
    db: Session = Depends(get_db)
):
    """更新环境信息"""
    logger.info(f"更新环境: id={environment_id}, data={environment_update.dict(exclude_unset=True)}")
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    # 检查名称是否与其他环境冲突
    if environment_update.name and environment_update.name != environment.name:
        existing = db.query(Environment).filter(
            Environment.name == environment_update.name,
            Environment.id != environment_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"环境名称 '{environment_update.name}' 已存在")
    
    # 更新环境信息
    update_data = environment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(environment, field, value)
    
    db.commit()
    db.refresh(environment)
    
    return APIResponse(
        data=environment,
        message=f"环境 '{environment.name}' 更新成功"
    )

@router.delete("/{environment_id}", response_model=APIResponse[dict])
def delete_environment(
    environment_id: int,
    db: Session = Depends(get_db)
):
    """删除环境"""
    logger.info(f"删除环境: id={environment_id}")
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    # 检查是否有关联的模型或节点
    if environment.models or environment.nodes:
        raise HTTPException(
            status_code=400, 
            detail="无法删除环境：存在关联的模型或节点，请先删除相关资源"
        )
    
    environment_name = environment.name
    db.delete(environment)
    db.commit()
    
    return APIResponse(
        data={"deleted_id": environment_id},
        message=f"环境 '{environment_name}' 删除成功"
    )