import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import settings
from .scheduler import init_scheduler, start_scheduler, shutdown_scheduler
from .api.v1.api import api_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Model Inference Scheduling Platform",
    description="A platform for managing model inference nodes and scheduling",
    version="1.0.0",
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 调度器生命周期事件
@app.on_event("startup")
async def startup_event():
    if settings.ENABLE_SCHEDULER:
        init_scheduler()
        start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    if settings.ENABLE_SCHEDULER:
        shutdown_scheduler()

# 全局异常处理器
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # 记录详细的异常信息，包括堆栈跟踪
    logger.error(f"Unhandled exception for request {request.method} {request.url}: {exc}")
    logger.error("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"An unexpected error occurred: {exc}",
            "data": None
        },
    )

@app.get("/")
def read_root():
    return {
        "message": "Model Inference Scheduling Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}