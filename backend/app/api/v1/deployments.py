import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from ...database import get_db
from ...models.node import Node
from ...services.node_client import node_manager
from ...schemas.common import APIResponse
from ...schemas.deployment import DeploymentSummary, NodeDeploymentStatus, GPUDeploymentStatus, DeployedModelInfo, ModelDeploymentStat
from collections import Counter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/status", response_model=APIResponse[DeploymentSummary])
async def get_deployment_status(
    environment_id: int = None,
    db: Session = Depends(get_db)
):
    """获取所有节点的部署状态概览，包括模型统计和GPU负载"""
    logger.info(f"获取部署状态概览: environment_id={environment_id}")
    
    query = db.query(Node)
    if environment_id:
        query = query.filter(Node.environment_id == environment_id)
    nodes = query.all()
    
    if not nodes:
        return APIResponse(data=DeploymentSummary(model_stats=[], deployment_statuses=[]), message="没有找到任何节点")

    node_dicts = [{"node_ip": n.node_ip, "node_port": n.node_port} for n in nodes]
    
    # 并行获取模型状态和GPU状态
    try:
        model_status_map, gpu_status_map = await node_manager.batch_get_status(node_dicts)
    except Exception as e:
        logger.error(f"批量获取模型或GPU状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量获取状态失败: {e}")

    deployment_statuses = []
    model_counter = Counter()

    for node in nodes:
        node_key = f"{node.node_ip}:{node.node_port}"
        running_models = model_status_map.get(node_key, [])
        gpu_loads = gpu_status_map.get(node_key, [])
        
        db_available_gpu_ids = json.loads(node.available_gpu_ids) if node.available_gpu_ids else []
        available_models = json.loads(node.available_models) if node.available_models else []

        gpu_map: Dict[int, GPUDeploymentStatus] = {}

        # 1. 基于节点返回的真实GPU列表构建map
        for gpu_stat in gpu_loads:
            gpu_id = gpu_stat.get("id")
            if gpu_id is not None:
                gpu_map[gpu_id] = GPUDeploymentStatus(gpu_id=gpu_id)
                # 真实节点返回的 memory_usage 是负载百分比
                gpu_map[gpu_id].gpu_load = gpu_stat.get("memory_usage")
                
                # 暂时硬编码总显存和功耗限制
                total_memory_mb = 24 * 1024
                power_limit_w = 450
                
                # 如果节点能提供真实数据则使用，否则使用默认值
                gpu_map[gpu_id].memory_total = gpu_stat.get("memory_total", total_memory_mb)
                gpu_map[gpu_id].power_limit = gpu_stat.get("power_limit", power_limit_w)

                # 计算实际使用的显存
                if gpu_stat.get("memory_usage") is not None:
                    gpu_map[gpu_id].memory_used = (gpu_stat.get("memory_usage") / 100) * gpu_map[gpu_id].memory_total
                
                gpu_map[gpu_id].power_usage = gpu_stat.get("power_draw") # 真实节点返回的是 power_draw

        # 2. 填充模型部署信息并统计
        for model_instance in running_models:
            gpu_id = model_instance.get("gpu_id")
            model_name = model_instance.get("model_name")
            if gpu_id is not None and gpu_id in gpu_map:
                gpu_map[gpu_id].deployed_model = DeployedModelInfo(
                    model_name=model_name,
                    status="RUNNING"
                )
                if model_name:
                    model_counter[model_name] += 1
        
        # 按gpu_id排序
        sorted_gpus = sorted(list(gpu_map.values()), key=lambda gpu: gpu.gpu_id)

        node_status = NodeDeploymentStatus(
            node_id=node.id,
            node_ip=node.node_ip,
            node_port=node.node_port,
            available_models=available_models,
            available_gpu_ids=db_available_gpu_ids, # 传递可用GPU列表
            gpus=sorted_gpus
        )
        deployment_statuses.append(node_status)

    # 格式化模型统计数据
    model_stats = [ModelDeploymentStat(model_name=name, count=count) for name, count in model_counter.items()]

    summary = DeploymentSummary(
        model_stats=model_stats,
        deployment_statuses=deployment_statuses
    )

    return APIResponse(
        data=summary,
        message=f"成功获取 {len(nodes)} 个节点的部署状态"
    )