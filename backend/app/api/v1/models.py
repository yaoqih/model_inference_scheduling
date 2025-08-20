import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models.model import Model
from ...models.environment import Environment
from ...schemas.model import Model as ModelSchema, ModelCreate, ModelUpdate
from ...schemas.common import APIResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=APIResponse[List[ModelSchema]])
def get_models(
    environment_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有模型"""
    logger.info(f"获取模型列表: environment_id={environment_id}, skip={skip}, limit={limit}")
    query = db.query(Model)
    if environment_id:
        query = query.filter(Model.environment_id == environment_id)
    
    models = query.offset(skip).limit(limit).all()
    return APIResponse(
        data=models,
        message=f"成功获取 {len(models)} 个模型配置"
    )

@router.post("/", response_model=APIResponse[ModelSchema])
def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db)
):
    """创建新模型配置"""
    logger.info(f"创建新模型: name='{model.model_name}', environment_id={model.environment_id}")
    # 检查环境是否存在
    environment = db.query(Environment).filter(Environment.id == model.environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="指定的环境不存在")
    
    # 检查模型名称在同一环境中是否已存在
    existing = db.query(Model).filter(
        Model.environment_id == model.environment_id,
        Model.model_name == model.model_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"模型 '{model.model_name}' 在环境 '{environment.name}' 中已存在"
        )
    
    # 创建新模型配置
    db_model = Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return APIResponse(
        data=db_model,
        message=f"模型 '{model.model_name}' 配置创建成功"
    )

@router.get("/{model_id}", response_model=APIResponse[ModelSchema])
def get_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """获取指定模型详情"""
    logger.info(f"获取模型详情: id={model_id}")
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    return APIResponse(
        data=model,
        message="模型配置详情获取成功"
    )

@router.put("/{model_id}", response_model=APIResponse[ModelSchema])
def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db)
):
    """更新模型配置"""
    logger.info(f"更新模型: id={model_id}, data={model_update.dict(exclude_unset=True)}")
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    # 检查模型名称是否与同环境其他模型冲突
    if model_update.model_name and model_update.model_name != model.model_name:
        existing = db.query(Model).filter(
            Model.environment_id == model.environment_id,
            Model.model_name == model_update.model_name,
            Model.id != model_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"模型名称 '{model_update.model_name}' 在当前环境中已存在"
            )
    
    # 更新模型配置
    update_data = model_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    
    return APIResponse(
        data=model,
        message=f"模型 '{model.model_name}' 配置更新成功"
    )

@router.delete("/{model_id}", response_model=APIResponse[dict])
def delete_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """删除模型配置"""
    logger.info(f"删除模型: id={model_id}")
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    model_name = model.model_name
    db.delete(model)
    db.commit()
    
    return APIResponse(
        data={"deleted_id": model_id},
        message=f"模型 '{model_name}' 配置删除成功"
    )

@router.get("/environment/{environment_id}", response_model=APIResponse[List[ModelSchema]])
def get_models_by_environment(
    environment_id: int,
    db: Session = Depends(get_db)
):
    """获取指定环境的所有模型"""
    logger.info(f"按环境ID获取模型: environment_id={environment_id}")
    # 检查环境是否存在
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    models = db.query(Model).filter(Model.environment_id == environment_id).all()
    return APIResponse(
        data=models,
        message=f"成功获取环境 '{environment.name}' 的 {len(models)} 个模型配置"
    )