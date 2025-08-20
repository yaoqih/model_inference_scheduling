import logging
from backend.app.services.node_client import NodeAPIClient
from backend.app.database import SessionLocal
from backend.app.models.node import Node

logger = logging.getLogger(__name__)

async def refresh_node_status():
    """定时刷新所有节点的状态"""
    logger.info("开始刷新节点状态...")
    db = SessionLocal()
    try:
        nodes = db.query(Node).all()
        if not nodes:
            logger.info("没有节点需要刷新")
            return

        # 适配 Node 模型字段（假设字段为 host 和 port）
        node_list = [{"node_ip": getattr(n, "node_ip", None) , "node_port": getattr(n, "node_port", None)} for n in nodes]
        node_list = [n for n in node_list if n["node_ip"] and n["node_port"]]

        if not node_list:
            logger.info("节点列表为空或缺少必要字段，跳过刷新")
            return

        # 使用全局 node_manager 调用批量状态获取
        from backend.app.services.node_client import node_manager
        model_status_map, gpu_status_map = await node_manager.batch_get_status(node_list)
        status_data = {
            "model_status": model_status_map,
            "gpu_status": gpu_status_map
        }

        # TODO: 将 status_data 更新到数据库
        logger.info(f"节点状态刷新完成: {status_data}")

    except Exception as e:
        logger.error(f"刷新节点状态时出错: {e}", exc_info=True)
    finally:
        db.close()