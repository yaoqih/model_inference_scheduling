import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from urllib.parse import quote
from typing import List

from ...database import get_db
from ...models.model import Model
from ...models.queue_length_record import QueueLengthRecord
from ...schemas.queue import QueueInfo, QueueLengthRecord as QueueLengthRecordSchema
from ...schemas.common import APIResponse
from ...config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{model_id}", response_model=APIResponse[QueueInfo])
async def get_queue_info(
    model_id: int,
    db: Session = Depends(get_db)
):
    """通过RabbitMQ Management API获取指定模型关联的队列信息"""
    logger.info(f"开始通过HTTP API获取模型 {model_id} 的队列信息")

    # 1. 从数据库获取模型配置
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        logger.warning(f"模型 {model_id} 未在数据库中找到")
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    logger.info(f"成功获取到模型 '{model.model_name}' 的配置")

    # 2. 检查必要的RabbitMQ配置
    required_configs = [
        model.rabbitmq_host, 
        model.rabbitmq_queue_name,
        model.rabbitmq_username,
        model.rabbitmq_password
    ]
    if not all(required_configs):
        logger.warning(f"模型 '{model.model_name}' (ID: {model_id}) 的RabbitMQ管理配置不完整")
        raise HTTPException(status_code=400, detail="模型未配置完整的RabbitMQ连接信息（包括用户名和密码）")

    # 3. 构建RabbitMQ Management API的URL
    # URL编码虚拟主机和队列名称，以防包含特殊字符（例如 "/")
    vhost = quote(model.rabbitmq_vhost or '/', safe='')
    queue_name = quote(model.rabbitmq_queue_name, safe='')
    
    api_url = (
        f"http://{model.rabbitmq_host}:{model.rabbitmq_port}/api/queues/{vhost}/{queue_name}"
    )
    
    logger.info(f"准备请求RabbitMQ Management API: {api_url}")

    # 4. 使用httpx异步请求API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                auth=(model.rabbitmq_username, model.rabbitmq_password),
                timeout=10.0
            )

            # 检查响应状态码
            if response.status_code == 200:
                data = response.json()
                queue_info = QueueInfo(
                    name=data.get("name"),
                    messages=data.get("messages", 0),
                    consumers=data.get("consumers", 0),
                    idle_since=data.get("idle_since")
                )
                logger.info(f"成功从API获取队列 '{queue_info.name}' 的信息")
                return APIResponse(
                    data=queue_info,
                    message="队列信息获取成功"
                )
            elif response.status_code == 404:
                logger.warning(f"队列 '{model.rabbitmq_queue_name}' 在RabbitMQ中未找到 (404)")
                raise HTTPException(status_code=404, detail=f"队列 '{model.rabbitmq_queue_name}' 不存在")
            elif response.status_code == 401:
                logger.error("RabbitMQ管理API认证失败 (401)")
                raise HTTPException(status_code=401, detail="RabbitMQ管理用户认证失败")
            else:
                logger.error(f"请求RabbitMQ管理API时返回了非预期的状态码: {response.status_code}, 响应: {response.text}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"请求RabbitMQ管理API失败: {response.text}"
                )

    except httpx.ConnectError as e:
        logger.error(f"无法连接到RabbitMQ Management API: {e}", exc_info=True)
        raise HTTPException(
            status_code=504,
            detail=f"无法连接到RabbitMQ管理服务在 {model.rabbitmq_host}:{model.rabbitmq_port}"
        )
    except httpx.TimeoutException as e:
        logger.error(f"请求RabbitMQ Management API超时: {e}", exc_info=True)
        raise HTTPException(status_code=504, detail="请求RabbitMQ管理服务超时")
    except Exception as e:
        logger.error(f"获取队列信息时发生未知错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取队列信息时发生未知错误: {e}"
        )

@router.get("/{model_id}/history", response_model=APIResponse[List[QueueLengthRecordSchema]])
async def get_queue_length_history(
    model_id: int,
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数量"),
    db: Session = Depends(get_db)
):
    """获取指定模型的队列长度历史记录"""
    logger.info(f"开始获取模型 {model_id} 的队列长度历史记录，限制 {limit} 条")

    # 检查模型是否存在
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        logger.warning(f"模型 {model_id} 未在数据库中找到")
        raise HTTPException(status_code=404, detail="模型不存在")

    # 查询历史记录
    history = (
        db.query(QueueLengthRecord)
        .filter(QueueLengthRecord.model_id == model_id)
        .order_by(QueueLengthRecord.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    logger.info(f"成功获取模型 {model_id} 的 {len(history)} 条队列长度历史记录")
    
    return APIResponse(
        data=history,
        message="队列长度历史记录获取成功"
    )