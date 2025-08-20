from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./model_scheduling.db"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Model Inference Scheduling Platform"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 调度器配置
    NODE_STATUS_REFRESH_INTERVAL: int = 30  # 节点状态刷新间隔（秒）
    ENABLE_SCHEDULER: bool = True

    # 队列历史记录配置
    QUEUE_HISTORY_MAX_LENGTH: int = 1000  # 每个队列保留的历史记录条数

    class Config:
        env_file = ".env"

settings = Settings()