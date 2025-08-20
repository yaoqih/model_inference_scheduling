import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime

from ...database import get_db
from ...models.node import Node
from ...models.environment import Environment
from ...schemas.node import Node as NodeSchema, NodeCreate, NodeUpdate, NodeStatusUpdate
from ...schemas.common import APIResponse
from ...services.node_client import node_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=APIResponse[List[NodeSchema]])
def get_nodes(
    environment_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有节点"""
    logger.info(f"获取节点列表: environment_id={environment_id}, status='{status}', skip={skip}, limit={limit}")
    query = db.query(Node)
    if environment_id:
        query = query.filter(Node.environment_id == environment_id)
    if status:
        query = query.filter(Node.status == status)
    
    nodes = query.offset(skip).limit(limit).all()
    
    # 转换JSON字段
    for node in nodes:
        if node.available_gpu_ids:
            node.available_gpu_ids = json.loads(node.available_gpu_ids)
        if node.available_models:
            node.available_models = json.loads(node.available_models)
    
    return APIResponse(
        data=nodes,
        message=f"成功获取 {len(nodes)} 个节点"
    )

@router.post("/", response_model=APIResponse[NodeSchema])
def create_node(
    node: NodeCreate,
    db: Session = Depends(get_db)
):
    """添加新节点"""
    logger.info(f"添加新节点: ip='{node.node_ip}', port={node.node_port}, env_id={node.environment_id}")
    # 检查环境是否存在
    environment = db.query(Environment).filter(Environment.id == node.environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="指定的环境不存在")
    
    # 检查节点IP和端口在同一环境中是否已存在
    existing = db.query(Node).filter(
        Node.environment_id == node.environment_id,
        Node.node_ip == node.node_ip,
        Node.node_port == node.node_port
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"节点 {node.node_ip}:{node.node_port} 在环境 '{environment.name}' 中已存在"
        )
    
    # 创建新节点
    node_data = node.dict()
    node_data['available_gpu_ids'] = json.dumps(node_data['available_gpu_ids'])
    node_data['available_models'] = json.dumps(node_data['available_models'])
    
    db_node = Node(**node_data)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    
    # 转换JSON字段用于响应
    db_node.available_gpu_ids = json.loads(db_node.available_gpu_ids)
    db_node.available_models = json.loads(db_node.available_models)
    
    return APIResponse(
        data=db_node,
        message=f"节点 {node.node_ip}:{node.node_port} 添加成功"
    )

@router.get("/{node_id}", response_model=APIResponse[NodeSchema])
def get_node(
    node_id: int,
    db: Session = Depends(get_db)
):
    """获取指定节点详情"""
    logger.info(f"获取节点详情: id={node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 转换JSON字段
    if node.available_gpu_ids:
        node.available_gpu_ids = json.loads(node.available_gpu_ids)
    if node.available_models:
        node.available_models = json.loads(node.available_models)
    
    return APIResponse(
        data=node,
        message="节点详情获取成功"
    )

@router.put("/{node_id}", response_model=APIResponse[NodeSchema])
def update_node(
    node_id: int,
    node_update: NodeUpdate,
    db: Session = Depends(get_db)
):
    """更新节点信息"""
    logger.info(f"更新节点: id={node_id}, data={node_update.dict(exclude_unset=True)}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 检查IP和端口是否与同环境其他节点冲突
    if (node_update.node_ip and node_update.node_ip != node.node_ip) or \
       (node_update.node_port and node_update.node_port != node.node_port):
        new_ip = node_update.node_ip or node.node_ip
        new_port = node_update.node_port or node.node_port
        
        existing = db.query(Node).filter(
            Node.environment_id == node.environment_id,
            Node.node_ip == new_ip,
            Node.node_port == new_port,
            Node.id != node_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"节点 {new_ip}:{new_port} 在当前环境中已存在"
            )
    
    # 更新节点信息
    update_data = node_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ['available_gpu_ids', 'available_models'] and value is not None:
            value = json.dumps(value)
        setattr(node, field, value)
    
    db.commit()
    db.refresh(node)
    
    # 转换JSON字段用于响应
    if node.available_gpu_ids:
        node.available_gpu_ids = json.loads(node.available_gpu_ids)
    if node.available_models:
        node.available_models = json.loads(node.available_models)
    
    return APIResponse(
        data=node,
        message=f"节点 {node.node_ip}:{node.node_port} 更新成功"
    )

@router.delete("/{node_id}", response_model=APIResponse[dict])
def delete_node(
    node_id: int,
    db: Session = Depends(get_db)
):
    """删除节点"""
    logger.info(f"删除节点: id={node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    node_info = f"{node.node_ip}:{node.node_port}"
    db.delete(node)
    db.commit()
    
    return APIResponse(
        data={"deleted_id": node_id},
        message=f"节点 {node_info} 删除成功"
    )

@router.post("/{node_id}/heartbeat", response_model=APIResponse[dict])
def update_node_heartbeat(
    node_id: int,
    status_update: NodeStatusUpdate,
    db: Session = Depends(get_db)
):
    """更新节点心跳和状态"""
    logger.info(f"更新节点心跳: id={node_id}, status='{status_update.status}'")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 更新心跳时间和状态
    node.last_heartbeat = datetime.utcnow()
    node.status = status_update.status
    
    if status_update.available_gpu_ids is not None:
        node.available_gpu_ids = json.dumps(status_update.available_gpu_ids)
    if status_update.available_models is not None:
        node.available_models = json.dumps(status_update.available_models)
    
    db.commit()
    
    return APIResponse(
        data={"node_id": node_id, "last_heartbeat": node.last_heartbeat},
        message=f"节点 {node.node_ip}:{node.node_port} 心跳更新成功"
    )

@router.post("/{node_id}/discover_models", response_model=APIResponse[dict])
async def discover_node_models(
    node_id: int,
    db: Session = Depends(get_db)
):
    """
    发现并更新节点可用模型列表到数据库
    """
    logger.info(f"发现并更新节点可用模型: id={node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 调用节点端API获取支持的模型
        client = node_manager.get_client(node.node_ip, node.node_port)
        supported_models = await client.get_supported_models()
        
        # 从返回的字典中提取模型名称
        discovered_models = list(supported_models.keys())
        
        # 更新节点的可用模型列表
        node.available_models = json.dumps(discovered_models)
        node.updated_at = datetime.utcnow()
        db.commit()
        
        return APIResponse(
            data={
                "node_id": node_id,
                "discovered_models": discovered_models,
                "discovery_time": datetime.utcnow()
            },
            message=f"成功发现并更新节点 {node.node_ip}:{node.node_port} 的 {len(discovered_models)} 个模型"
        )
        
    except Exception as e:
        logger.error(f"发现节点 {node_id} 模型失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"无法连接到节点 {node.node_ip}:{node.node_port} 或发现模型失败: {str(e)}"
        )

@router.get("/{node_id}/models", response_model=APIResponse[List[str]])
def get_node_models(
    node_id: int,
    db: Session = Depends(get_db)
):
    """获取节点当前可用模型列表"""
    logger.info(f"获取节点可用模型列表: id={node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    models = []
    if node.available_models:
        models = json.loads(node.available_models)
    
    return APIResponse(
        data=models,
        message=f"节点 {node.node_ip}:{node.node_port} 当前有 {len(models)} 个可用模型"
    )

@router.get("/{node_id}/status", response_model=APIResponse[dict])
async def get_node_status(
    node_id: int,
    db: Session = Depends(get_db)
):
    """检查并获取节点状态信息"""
    logger.info(f"检查并获取节点状态: id={node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 执行健康检查并更新状态
    try:
        client = node_manager.get_client(node.node_ip, node.node_port)
        is_healthy = await client.health_check()
        
        # 更新节点状态
        if is_healthy:
            node.status = "online"
            node.last_heartbeat = datetime.utcnow()
        else:
            node.status = "offline"
        
        node.updated_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # 如果健康检查失败，标记为离线
        node.status = "offline"
        node.updated_at = datetime.utcnow()
        db.commit()
    
    # 解析JSON字段
    available_gpu_ids = []
    available_models = []
    
    if node.available_gpu_ids:
        available_gpu_ids = json.loads(node.available_gpu_ids)
    if node.available_models:
        available_models = json.loads(node.available_models)
    
    status_info = {
        "node_id": node.id,
        "node_ip": node.node_ip,
        "node_port": node.node_port,
        "status": node.status,
        "last_heartbeat": node.last_heartbeat,
        "available_gpu_ids": available_gpu_ids,
        "available_models": available_models,
        "total_gpus": len(available_gpu_ids) if available_gpu_ids else 0,
        "created_at": node.created_at,
        "updated_at": node.updated_at
    }
    
    return APIResponse(
        data=status_info,
        message=f"节点 {node.node_ip}:{node.node_port} 状态检查完成，当前状态: {node.status}"
    )

@router.get("/{node_id}/gpu-status", response_model=APIResponse[List[Dict[str, Any]]])
async def get_node_gpu_status(
    node_id: int,
    db: Session = Depends(get_db)
):
    """获取节点GPU状态"""
    logger.info(f"获取节点GPU状态: id={node_id}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 获取节点客户端并查询GPU状态
        client = node_manager.get_client(node.node_ip, node.node_port)
        gpu_status = await client.get_gpu_status()
        
        return APIResponse(
            data=gpu_status,
            message=f"成功获取节点 {node.node_ip}:{node.node_port} 的GPU状态"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取节点GPU状态失败: {str(e)}"
        )

@router.get("/{node_id}/model-status", response_model=APIResponse[List[Dict[str, Any]]])
async def get_node_model_status(
    node_id: int,
    db: Session = Depends(get_db)
):
    """获取节点模型状态"""
    logger.info(f"获取节点模型状态: id={node_id}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 获取节点客户端并查询模型状态
        client = node_manager.get_client(node.node_ip, node.node_port)
        model_status = await client.get_model_status()
        
        return APIResponse(
            data=model_status,
            message=f"成功获取节点 {node.node_ip}:{node.node_port} 的模型状态"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取节点模型状态失败: {str(e)}"
        )

@router.post("/{node_id}/models/start", response_model=APIResponse[Dict[str, Any]])
async def start_model_on_node(
    node_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """在节点上启动模型"""
    logger.info(f"在节点上启动模型: id={node_id}, request={request}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 验证请求参数
        if "model_name" not in request or "gpu_id" not in request:
            raise HTTPException(status_code=400, detail="缺少必需参数: model_name, gpu_id")
        
        # 获取节点客户端并启动模型
        client = node_manager.get_client(node.node_ip, node.node_port)
        result = await client.start_model(
            request["model_name"],
            request["gpu_id"],
            request.get("config", {})
        )
        
        return APIResponse(
            data=result,
            message=f"成功在节点 {node.node_ip}:{node.node_port} 上启动模型 {request['model_name']}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"启动模型失败: {str(e)}"
        )

@router.post("/{node_id}/models/stop", response_model=APIResponse[Dict[str, Any]])
async def stop_model_on_node(
    node_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """在节点上停止模型"""
    logger.info(f"在节点上停止模型: id={node_id}, request={request}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 验证请求参数
        if "model_name" not in request or "gpu_id" not in request:
            raise HTTPException(status_code=400, detail="缺少必需参数: model_name, gpu_id")
        
        # 获取节点客户端并停止模型
        client = node_manager.get_client(node.node_ip, node.node_port)
        result = await client.stop_model(request["model_name"], request["gpu_id"])
        
        return APIResponse(
            data=result,
            message=f"成功在节点 {node.node_ip}:{node.node_port} 上停止模型 {request['model_name']}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"停止模型失败: {str(e)}"
        )

@router.delete("/{node_id}/processes/{pid}", response_model=APIResponse[Dict[str, Any]])
async def kill_process_on_node(
    node_id: int,
    pid: int,
    db: Session = Depends(get_db)
):
    """在节点上终止进程"""
    logger.info(f"在节点上终止进程: id={node_id}, pid={pid}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 获取节点客户端并终止进程
        client = node_manager.get_client(node.node_ip, node.node_port)
        result = await client.kill_process(pid)
        
        return APIResponse(
            data=result,
            message=f"成功在节点 {node.node_ip}:{node.node_port} 上终止进程 {pid}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"终止进程失败: {str(e)}"
        )

@router.get("/{node_id}/models/supported", response_model=APIResponse[Dict[str, str]])
async def get_supported_models(
    node_id: int,
    db: Session = Depends(get_db)
):
    """直接从节点获取支持的模型列表，不更新数据库"""
    logger.info(f"获取节点支持的模型列表: id={node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        client = node_manager.get_client(node.node_ip, node.node_port)
        supported_models = await client.get_supported_models()
        
        return APIResponse(
            data=supported_models,
            message=f"成功获取节点 {node.node_ip}:{node.node_port} 支持的模型列表"
        )
    except Exception as e:
        logger.error(f"获取节点 {node_id} 支持的模型失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"无法连接到节点 {node.node_ip}:{node.node_port} 或获取模型列表失败: {str(e)}"
        )