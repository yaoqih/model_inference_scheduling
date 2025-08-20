"""
节点操作API - 与节点端Model Inference Client API集成
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ...database import get_db
from ...models.node import Node
from ...services.node_client import node_manager
from ...schemas.common import APIResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{node_id}/gpu-status", response_model=APIResponse[List[Dict[str, Any]]])
async def get_node_gpu_status(
    node_id: int,
    db: Session = Depends(get_db)
):
    """获取节点GPU状态"""
    logger.info(f"获取节点GPU状态: node_id={node_id}")
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
    logger.info(f"获取节点模型状态: node_id={node_id}")
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

@router.post("/{node_id}/models/{model_name}/start", response_model=APIResponse[Dict[str, Any]])
async def start_model_on_node(
    node_id: int,
    model_name: str,
    gpu_id: int,
    config: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """在节点上启动模型"""
    logger.info(f"在节点上启动模型: node_id={node_id}, model_name='{model_name}', gpu_id={gpu_id}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 获取节点客户端并启动模型
        client = node_manager.get_client(node.node_ip, node.node_port)
        result = await client.start_model(model_name, gpu_id, config)
        
        return APIResponse(
            data=result,
            message=f"成功在节点 {node.node_ip}:{node.node_port} 上启动模型 {model_name}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"启动模型失败: {str(e)}"
        )

@router.post("/{node_id}/models/{model_name}/stop", response_model=APIResponse[Dict[str, Any]])
async def stop_model_on_node(
    node_id: int,
    model_name: str,
    gpu_id: int,
    db: Session = Depends(get_db)
):
    """在节点上停止模型"""
    logger.info(f"在节点上停止模型: node_id={node_id}, model_name='{model_name}', gpu_id={gpu_id}")
    # 获取节点信息
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    try:
        # 获取节点客户端并停止模型
        client = node_manager.get_client(node.node_ip, node.node_port)
        result = await client.stop_model(model_name, gpu_id)
        
        return APIResponse(
            data=result,
            message=f"成功在节点 {node.node_ip}:{node.node_port} 上停止模型 {model_name}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"停止模型失败: {str(e)}"
        )

@router.post("/{node_id}/processes/{pid}/kill", response_model=APIResponse[Dict[str, Any]])
async def kill_process_on_node(
    node_id: int,
    pid: int,
    db: Session = Depends(get_db)
):
    """在节点上终止进程"""
    logger.info(f"在节点上终止进程: node_id={node_id}, pid={pid}")
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

@router.get("/batch/health-check", response_model=APIResponse[Dict[str, bool]])
async def batch_health_check(
    environment_id: int = None,
    db: Session = Depends(get_db)
):
    """批量健康检查"""
    logger.info(f"批量健康检查: environment_id={environment_id}")
    # 获取节点列表
    query = db.query(Node)
    if environment_id:
        query = query.filter(Node.environment_id == environment_id)
    
    nodes = query.all()
    if not nodes:
        return APIResponse(
            data={},
            message="没有找到节点"
        )
    
    try:
        # 转换为字典格式
        node_dicts = [
            {
                "node_ip": node.node_ip,
                "node_port": node.node_port
            }
            for node in nodes
        ]
        
        # 批量健康检查
        health_status = await node_manager.batch_health_check(node_dicts)
        
        return APIResponse(
            data=health_status,
            message=f"完成 {len(nodes)} 个节点的健康检查"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"批量健康检查失败: {str(e)}"
        )

@router.get("/batch/gpu-status", response_model=APIResponse[Dict[str, List[Dict[str, Any]]]])
async def batch_get_gpu_status(
    environment_id: int = None,
    db: Session = Depends(get_db)
):
    """批量获取GPU状态"""
    logger.info(f"批量获取GPU状态: environment_id={environment_id}")
    # 获取节点列表
    query = db.query(Node)
    if environment_id:
        query = query.filter(Node.environment_id == environment_id)
    
    nodes = query.all()
    if not nodes:
        return APIResponse(
            data={},
            message="没有找到节点"
        )
    
    try:
        # 转换为字典格式
        node_dicts = [
            {
                "node_ip": node.node_ip,
                "node_port": node.node_port
            }
            for node in nodes
        ]
        
        # 批量获取GPU状态
        gpu_status = await node_manager.batch_get_gpu_status(node_dicts)
        
        return APIResponse(
            data=gpu_status,
            message=f"完成 {len(nodes)} 个节点的GPU状态获取"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"批量获取GPU状态失败: {str(e)}"
        )

@router.get("/batch/model-status", response_model=APIResponse[Dict[str, List[Dict[str, Any]]]])
async def batch_get_model_status(
    environment_id: int = None,
    db: Session = Depends(get_db)
):
    """批量获取模型状态"""
    logger.info(f"批量获取模型状态: environment_id={environment_id}")
    # 获取节点列表
    query = db.query(Node)
    if environment_id:
        query = query.filter(Node.environment_id == environment_id)
    
    nodes = query.all()
    if not nodes:
        return APIResponse(
            data={},
            message="没有找到节点"
        )
    
    try:
        # 转换为字典格式
        node_dicts = [
            {
                "node_ip": node.node_ip,
                "node_port": node.node_port
            }
            for node in nodes
        ]
        
        # 批量获取模型状态
        model_status = await node_manager.batch_get_model_status(node_dicts)
        
        return APIResponse(
            data=model_status,
            message=f"完成 {len(nodes)} 个节点的模型状态获取"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"批量获取模型状态失败: {str(e)}"
        )