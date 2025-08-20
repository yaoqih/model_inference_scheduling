import logging
import httpx
from sqlalchemy.orm import Session
from urllib.parse import quote

from ..database import SessionLocal
from ..models.model import Model
from ..models.queue_length_record import QueueLengthRecord
from ..config import settings

logger = logging.getLogger(__name__)

async def record_queue_lengths():
    """
    定时任务：记录所有已配置模型的RabbitMQ队列长度。
    """
    logger.info("开始执行记录队列长度的定时任务")
    db: Session = SessionLocal()
    try:
        models = db.query(Model).filter(Model.rabbitmq_host.isnot(None), Model.rabbitmq_queue_name.isnot(None)).all()
        
        async with httpx.AsyncClient() as client:
            for model in models:
                if not all([model.rabbitmq_username, model.rabbitmq_password]):
                    logger.warning(f"模型 '{model.model_name}' (ID: {model.id}) 的RabbitMQ管理配置不完整，跳过此模型。")
                    continue

                vhost = quote(model.rabbitmq_vhost or '/', safe='')
                queue_name = quote(model.rabbitmq_queue_name, safe='')
                api_url = f"http://{model.rabbitmq_host}:{model.rabbitmq_port}/api/queues/{vhost}/{queue_name}"

                try:
                    response = await client.get(
                        api_url,
                        auth=(model.rabbitmq_username, model.rabbitmq_password),
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        queue_length = data.get("messages", 0)
                        
                        # 1. 创建并保存新的记录
                        new_record = QueueLengthRecord(model_id=model.id, length=queue_length)
                        db.add(new_record)
                        db.commit()
                        logger.info(f"成功记录模型 '{model.model_name}' 的队列长度: {queue_length}")

                        # 2. 清理旧的记录
                        record_count = db.query(QueueLengthRecord).filter(QueueLengthRecord.model_id == model.id).count()
                        if record_count > settings.QUEUE_HISTORY_MAX_LENGTH:
                            num_to_delete = record_count - settings.QUEUE_HISTORY_MAX_LENGTH
                            oldest_records = db.query(QueueLengthRecord).filter(QueueLengthRecord.model_id == model.id).order_by(QueueLengthRecord.timestamp.asc()).limit(num_to_delete).all()
                            for record in oldest_records:
                                db.delete(record)
                            db.commit()
                            logger.info(f"为模型 '{model.model_name}' 清理了 {num_to_delete} 条旧的队列长度记录。")

                    else:
                        logger.warning(f"请求模型 '{model.model_name}' 的队列信息失败，状态码: {response.status_code}")

                except httpx.RequestError as e:
                    logger.error(f"请求模型 '{model.model_name}' 的队列信息时发生网络错误: {e}")
                except Exception as e:
                    logger.error(f"处理模型 '{model.model_name}' 时发生未知错误: {e}")
                    db.rollback()

    finally:
        db.close()
    logger.info("记录队列长度的定时任务执行完毕")