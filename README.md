# Model Inference Scheduling Platform

AI 模型推理的统一管理与调度平台，支持多环境、多节点的资源编排、队列监控与自动化调度。

- 交接文档：请阅读 docs/Handover.zh-CN.md（本 README 提供快速上手与总览，交接细节与运维规范见交接文档）

## 功能概览

- 多环境管理：开发/测试/生产隔离
- 模型配置中心：按模型维护 RabbitMQ 队列与性能指标（平均推理时长）
- 节点与GPU管理：节点注册、心跳、GPU能力与已部署实例查看
- 队列监控：定时抓取 RabbitMQ 队列长度并持久化历史
- 自动化调度：基于队列压力与最近活跃度，自动部署/替换模型实例
- 可视化前端：仪表盘、环境/模型/节点、部署与调度页

## 架构与代码路径

- 后端（FastAPI + SQLAlchemy）：
  - 应用入口与中间件：[`backend/app/main.py`](backend/app/main.py)
  - 配置：[`backend/app/config.py`](backend/app/config.py)
  - 数据层与会话：[`backend/app/database.py`](backend/app/database.py)
  - 路由聚合：[`backend/app/api/v1/api.py`](backend/app/api/v1/api.py)
  - 定时调度器：[`backend/app/scheduler.py`](backend/app/scheduler.py)
  - 定时任务：[`backend/app/jobs/node_jobs.py`](backend/app/jobs/node_jobs.py), [`backend/app/jobs/queue_jobs.py`](backend/app/jobs/queue_jobs.py), [`backend/app/jobs/scheduling_jobs.py`](backend/app/jobs/scheduling_jobs.py)
  - 业务模型：[`backend/app/models/`](backend/app/models/)
  - 数据校验：[`backend/app/schemas/`](backend/app/schemas/)
  - 节点客户端：[`backend/app/services/node_client.py`](backend/app/services/node_client.py)

- 前端（React + TypeScript + Ant Design）：
  - 入口与路由：[`frontend/src/App.tsx`](frontend/src/App.tsx)
  - 主布局：[`frontend/src/components/Layout/MainLayout.tsx`](frontend/src/components/Layout/MainLayout.tsx)
  - 页面：[`frontend/src/pages/`](frontend/src/pages/)（Dashboard/Environments/Models/Nodes/Deployments/Scheduling）
  - API 服务层：[`frontend/src/services/api.ts`](frontend/src/services/api.ts)
  - 前端环境：[`frontend/.env`](frontend/.env)

- 开发脚本：
  - 一键后端开发：[`run_dev.py`](run_dev.py)

## 快速开始

### 1) 后端

环境要求：Python 3.8+

安装依赖
```bash
pip install -r requirements.txt
```

运行
```bash
# 方式1：开发脚本（自动加载 backend 包）
python run_dev.py

# 方式2：手动运行 uvicorn
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问
- OpenAPI 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 2) 前端

环境要求：Node.js 16+

```bash
cd frontend
npm install
npm start
# 默认开发端口 http://localhost:3000
```

跨域：后端允许的 CORS 源在 [`backend/app/config.py`](backend/app/config.py) 中配置，默认允许 http://localhost:3000。

### 3) 可选：环境变量（.env）

在项目根目录或运行环境中设置（见 [`backend/app/config.py`](backend/app/config.py)）：
```
DATABASE_URL=sqlite:///./model_scheduling.db
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
API_V1_STR=/api/v1
PROJECT_NAME=Model Inference Scheduling Platform
LOG_LEVEL=INFO
ENABLE_SCHEDULER=true
NODE_STATUS_REFRESH_INTERVAL=30
QUEUE_HISTORY_MAX_LENGTH=1000
```

前端 API 地址可在 [`frontend/.env`](frontend/.env) 中设置（例如 REACT_APP_API_BASE_URL）。

## API 总览

基础
- GET /             根路径信息
- GET /health       健康检查
- GET /docs         OpenAPI 文档

版本前缀：/api/v1（见 [`backend/app/api/v1/api.py`](backend/app/api/v1/api.py)）

- environments
  - GET /environments
  - POST /environments
  - GET /environments/{id}
  - PUT /environments/{id}
  - DELETE /environments/{id}

- models
  - GET /models?environment_id=
  - POST /models
  - GET /models/{id}
  - PUT /models/{id}
  - DELETE /models/{id}
  - GET /models/environment/{environment_id}

- nodes
  - GET /nodes?environment_id=&status=
  - POST /nodes
  - GET /nodes/{id}
  - PUT /nodes/{id}
  - DELETE /nodes/{id}
  - POST /nodes/{id}/heartbeat
  - POST /nodes/{id}/discover_models
  - GET /nodes/{id}/models
  - GET /nodes/{id}/status
  - GET /nodes/{id}/gpu-status
  - GET /nodes/{id}/model-status
  - POST /nodes/{id}/models/start
  - POST /nodes/{id}/models/stop
  - DELETE /nodes/{id}/processes/{pid}

- queues
  - GET /queues/{model_id}
  - GET /queues/{model_id}/history?limit=

- deployments
  - GET /deployments/status?environment_id=

- scheduling-strategies
  - GET /scheduling-strategies

更多细节见各路由文件（[`backend/app/api/v1/`](backend/app/api/v1/)）。

## 定时任务与调度

- 调度器：APScheduler（见 [`backend/app/scheduler.py`](backend/app/scheduler.py)）
- 已注册任务：
  - 刷新节点状态：每 NODE_STATUS_REFRESH_INTERVAL 秒（[`backend/app/jobs/node_jobs.py`](backend/app/jobs/node_jobs.py)）
  - 记录队列长度：每 60 秒（[`backend/app/jobs/queue_jobs.py`](backend/app/jobs/queue_jobs.py)）
  - 应用调度策略：每 1 分钟（[`backend/app/jobs/scheduling_jobs.py`](backend/app/jobs/scheduling_jobs.py)）

说明：
- 队列长度通过 RabbitMQ Management API 获取，需要在模型配置中填入 host/port/vhost/queue/name 与认证信息
- 调度策略示例 busy_queue_scaling：基于最近平均队列长度、实例运行情况与可用 GPU 动态部署/替换

## 数据库

默认 SQLite（文件位于项目根目录）。核心表：
- environments
- models（含 RabbitMQ 配置与 average_inference_time）
- nodes（含 available_gpu_ids / available_models JSON 字段）
- model_instances（运行时实例）
- queue_length_records（周期性队列长度记录）
- scheduling_strategies（策略启用状态等）

## 前端页面

- Dashboard（仪表盘）
- Environments（环境管理）
- Models（模型管理）
- Nodes（节点管理）
- Deployments（部署总览）
- Scheduling（调度与策略）

入口与路由见 [`frontend/src/App.tsx`](frontend/src/App.tsx)，布局见 [`frontend/src/components/Layout/MainLayout.tsx`](frontend/src/components/Layout/MainLayout.tsx)。

## 测试

项目包含若干 API 与客户端示例测试（例如 test_*.py）。建议：
```bash
# 安装 pytest（如未在 requirements 中）
pip install pytest

# 在项目根目录运行
pytest -q
```

## 贡献

1. Fork 仓库
2. 创建分支 `git checkout -b feature/your-feature`
3. 提交 `git commit -m "feat: your feature"`
4. 推送并创建 PR

