from fastapi import APIRouter

from .environments import router as environments_router
from .models import router as models_router
from .nodes import router as nodes_router
from .queues import router as queues_router
from .deployments import router as deployments_router
from .scheduling_strategies import router as scheduling_strategies_router

api_router = APIRouter()

api_router.include_router(
    environments_router,
    prefix="/environments",
    tags=["environments"]
)

api_router.include_router(
    models_router,
    prefix="/models",
    tags=["models"]
)

api_router.include_router(
    nodes_router,
    prefix="/nodes",
    tags=["nodes"]
)

api_router.include_router(
    queues_router,
    prefix="/queues",
    tags=["queues"]
)

api_router.include_router(
    deployments_router,
    prefix="/deployments",
    tags=["deployments"]
)

api_router.include_router(
    scheduling_strategies_router,
    prefix="/scheduling-strategies",
    tags=["scheduling-strategies"],
)