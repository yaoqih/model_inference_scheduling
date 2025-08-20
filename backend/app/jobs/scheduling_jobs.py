import logging
import json
from sqlalchemy.orm import Session
from backend.app import models, database
from backend.app.services import node_client
from sqlalchemy import func, and_
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def apply_scheduling_strategies():
    logger.info("开始应用调度策略...")
    db: Session = next(database.get_db())
    
    active_strategies = db.query(models.SchedulingStrategy).filter(models.SchedulingStrategy.is_active == True).all()
    
    if not active_strategies:
        logger.info("没有活动的调度策略。")
        return

    for strategy in active_strategies:
        if strategy.name == "busy_queue_scaling":
            await apply_busy_queue_scaling_strategy(db)

async def apply_busy_queue_scaling_strategy(db: Session):
    logger.info("应用 'busy_queue_scaling' 策略...")

    # 在单次调度运行中跟踪已分配的GPU，格式为 {node_key: {gpu_id}}
    gpus_allocated_this_run = {}

    # 统计最近 5 分钟内各模型的平均队列长度，用于后续判断请求活跃度
    now = datetime.utcnow()
    recent_threshold = now - timedelta(minutes=5)
    recent_stats_query = db.query(
        models.QueueLengthRecord.model_id,
        func.avg(models.QueueLengthRecord.length).label('avg_len')
    ).filter(
        models.QueueLengthRecord.timestamp >= recent_threshold
    ).group_by(
        models.QueueLengthRecord.model_id
    ).all()
    # 转换为 {model_id: avg_len}
    recent_stats = {mid: avg for mid, avg in recent_stats_query}

    # 1. 找出繁忙的模型
    models_with_stats = db.query(
        models.Model,
        func.avg(models.QueueLengthRecord.length).label('avg_queue_length')
    ).join(models.QueueLengthRecord, models.Model.id == models.QueueLengthRecord.model_id)\
    .group_by(models.Model.id)\
    .having(func.count(models.QueueLengthRecord.id) >= 10)\
    .all()

    busy_models = []
    for model, avg_queue_length in models_with_stats:
        if (avg_queue_length * model.average_inference_time) > 300:
            busy_models.append(model)

    if busy_models:
        logger.info(f"检测到繁忙的模型: {[m.model_name for m in busy_models]}")
        # 2. 获取所有在线节点和它们的状态
        online_nodes = db.query(models.Node).filter(models.Node.status == "online").all()
        
        # 获取所有节点的模型和GPU状态
        node_dicts = [{"node_ip": n.node_ip, "node_port": n.node_port} for n in online_nodes]
        model_status_map, gpu_status_map = await node_client.node_manager.batch_get_status(node_dicts)

        # 统计当前所有运行中的模型实例数量
        running_instances = {}
        for instances in model_status_map.values():
            for ins in instances:
                mname = ins.get("model_name")
                running_instances[mname] = running_instances.get(mname, 0) + 1

        # 为后续快速查找，构造繁忙模型字典
        busy_model_map = {m.model_name: m for m in busy_models}

        # 构造候选模型列表：无实例且最近 5 分钟平均队列长度>0，按请求量倒序
        candidate_models = sorted(
            [
                m for m in busy_models
                if running_instances.get(m.model_name, 0) == 0 and recent_stats.get(m.id, 0) > 0
            ],
            key=lambda mm: recent_stats.get(mm.id, 0),
            reverse=True
        )

        # 3. 寻找空闲的GPU并部署繁忙模型
        for node in online_nodes:
            node_key = f"{node.node_ip}:{node.node_port}"
            gpu_statuses = gpu_status_map.get(node_key, [])
            model_statuses = model_status_map.get(node_key, [])
            
            # 获取已占用的GPU ID
            used_gpu_ids = {ms['gpu_id'] for ms in model_statuses}
            
            # 获取节点可用的GPU ID
            try:
                # 解析JSON字符串并转换为整数集合
                gpu_ids_str = json.loads(node.available_gpu_ids)
                available_gpu_ids = {int(gid) for gid in gpu_ids_str}
            except (json.JSONDecodeError, TypeError, ValueError):
                available_gpu_ids = set()
            
            # 找出真正空闲的GPU
            free_gpu_ids = available_gpu_ids - used_gpu_ids - gpus_allocated_this_run.get(node_key, set())

            for gpu_id in free_gpu_ids:
                # 若没有候选模型可启动则跳出
                if not candidate_models:
                    break
                # 选择请求量最高的候选模型
                model_to_deploy = candidate_models.pop(0)

                # 节点需支持该模型
                if model_to_deploy.model_name not in node.available_models:
                    continue

                logger.info(f"在节点 {node.node_ip} 的 GPU {gpu_id} 上启动繁忙模型 {model_to_deploy.model_name}")
                try:
                    client = node_client.node_manager.get_client(node.node_ip, node.node_port)
                    await client.start_model(model_to_deploy.model_name, gpu_id)

                    # 记录本次运行已分配的GPU
                    if node_key not in gpus_allocated_this_run:
                        gpus_allocated_this_run[node_key] = set()
                    gpus_allocated_this_run[node_key].add(gpu_id)
                except Exception as e:
                    logger.error(f"启动模型 {model_to_deploy.model_name} 失败: {e}")

            # ---------------- GPU 替换逻辑 ----------------
            # 如果仍有候选模型未部署，且当前节点 GPU 上存在近 5 分钟无请求的模型实例，则进行替换
            if candidate_models:
                for inst in list(model_statuses):
                    inst_model_name = inst.get("model_name")
                    inst_gpu_id = inst.get("gpu_id")
                    if inst_model_name is None or inst_gpu_id is None:
                        continue

                    running_model_obj = busy_model_map.get(inst_model_name)
                    running_model_id = running_model_obj.id if running_model_obj else None
                    # 近 5 分钟平均队列长度为 0 视为闲置
                    if recent_stats.get(running_model_id, 0) == 0 and candidate_models:
                        new_model = candidate_models.pop(0)
                        # 节点需支持新模型
                        if new_model.model_name not in node.available_models:
                            continue
                        try:
                            logger.info(f"在节点 {node.node_ip} 的 GPU {inst_gpu_id} 上将空闲模型 {inst_model_name} 替换为 {new_model.model_name}")
                            client = node_client.node_manager.get_client(node.node_ip, node.node_port)
                            await client.stop_model(inst_model_name, inst_gpu_id)
                            await client.start_model(new_model.model_name, inst_gpu_id)

                            # 记录本次运行已分配的GPU
                            if node_key not in gpus_allocated_this_run:
                                gpus_allocated_this_run[node_key] = set()
                            gpus_allocated_this_run[node_key].add(inst_gpu_id)
                        except Exception as e:
                            logger.error(f"替换模型失败: {e}")
                        if not candidate_models:
                            break

    # 4. 保证每个模型至少有一个实例
    all_models = db.query(models.Model).all()
    
    # 优化：一次性获取所有在线节点的状态
    online_nodes = db.query(models.Node).filter(models.Node.status == "online").all()
    if not online_nodes:
        logger.info("没有在线节点，跳过保底实例检查。")
        return

    node_dicts = [{"node_ip": n.node_ip, "node_port": n.node_port} for n in online_nodes]
    model_status_map, gpu_status_map = await node_client.node_manager.batch_get_status(node_dicts)

    # 将实时状态转换为更易于查询的结构
    running_instances = {}
    for node_key, instances in model_status_map.items():
        for instance in instances:
            model_name = instance.get('model_name')
            if model_name not in running_instances:
                running_instances[model_name] = 0
            running_instances[model_name] += 1

    for model in all_models:
        logger.info(f"检查模型 '{model.model_name}' 的实例数量 (使用实时数据)...")
        
        # 使用从节点获取的实时数据检查实例数量
        instance_count = running_instances.get(model.model_name, 0)
        
        if instance_count == 0:
            logger.info(f"模型 {model.model_name} 没有任何实例，尝试为其启动一个。")
            model_deployed = False
            for node in online_nodes:
                if model.model_name in node.available_models:
                    node_key = f"{node.node_ip}:{node.node_port}"
                    model_statuses = model_status_map.get(node_key, [])
                    used_gpu_ids = {ms['gpu_id'] for ms in model_statuses}
                    try:
                        # 解析JSON字符串并转换为整数集合
                        gpu_ids_str = json.loads(node.available_gpu_ids)
                        available_gpu_ids = {int(gid) for gid in gpu_ids_str}
                    except (json.JSONDecodeError, TypeError, ValueError):
                        available_gpu_ids = set()
                    
                    # 同样需要检查本次运行中已分配的GPU
                    free_gpu_ids = available_gpu_ids - used_gpu_ids - gpus_allocated_this_run.get(node_key, set())

                    if free_gpu_ids:
                        gpu_to_use = free_gpu_ids.pop()
                        logger.info(f"在节点 {node.node_ip} 的 GPU {gpu_to_use} 上为 {model.model_name} 启动保底实例")
                        try:
                            client = node_client.node_manager.get_client(node.node_ip, node.node_port)
                            await client.start_model(model.model_name, gpu_to_use)
                            
                            # 记录本次运行已分配的GPU
                            if node_key not in gpus_allocated_this_run:
                                gpus_allocated_this_run[node_key] = set()
                            gpus_allocated_this_run[node_key].add(gpu_to_use)

                            model_deployed = True
                            break  # 已为该模型启动实例，继续下一个模型
                        except Exception as e:
                            logger.error(f"启动保底实例失败: {e}")
            if model_deployed:
                continue