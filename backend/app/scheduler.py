from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.app.config import settings
from backend.app.jobs import node_jobs, queue_jobs, scheduling_jobs
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def async_apply_scheduling_strategies():
    await scheduling_jobs.apply_scheduling_strategies()

def init_scheduler():
    """初始化调度器并注册任务"""
    # 注册节点状态刷新任务
    scheduler.add_job(
        node_jobs.refresh_node_status,
        trigger=IntervalTrigger(seconds=settings.NODE_STATUS_REFRESH_INTERVAL),
        id="refresh_node_status",
        replace_existing=True
    )
    logger.info("调度器任务已注册: refresh_node_status")

    # 注册队列长度记录任务
    scheduler.add_job(
        queue_jobs.record_queue_lengths,
        trigger=IntervalTrigger(seconds=60),  # 每60秒执行一次
        id="record_queue_lengths",
        replace_existing=True
    )
    logger.info("调度器任务已注册: record_queue_lengths")

    # 注册调度策略应用任务
    scheduler.add_job(
        async_apply_scheduling_strategies,
        trigger=IntervalTrigger(minutes=1),  # 每1分钟执行一次，方便测试
        id="apply_scheduling_strategies",
        replace_existing=True
    )
    logger.info("调度器任务已注册: apply_scheduling_strategies")

def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler 已启动")

def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler 已关闭")