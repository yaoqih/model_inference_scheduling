# 项目交接文档（Handover）- Model Inference Scheduling Platform

本文档面向接手本项目的工程师，覆盖系统架构、运行与运维、配置、数据模型、API、调度与定时任务、前端结构、常见问题与排障、上线与安全要点、交接清单与验收步骤等内容。配合总览请参考 [README](README.md) 与客户端调用说明 [model_inference_client_api_documentation.md](model_inference_client_api_documentation.md)。


## 1. 系统总览

- 后端：FastAPI + SQLAlchemy + APScheduler，入口 [backend/app/main.py](backend/app/main.py)，路由聚合 [backend/app/api/v1/api.py](backend/app/api/v1/api.py)，调度器 [backend/app/scheduler.py](backend/app/scheduler.py)。
- 前端：React + TypeScript + Ant Design，入口与路由 [frontend/src/App.tsx](frontend/src/App.tsx)，主布局 [frontend/src/components/Layout/MainLayout.tsx](frontend/src/components/Layout/MainLayout.tsx)。
- 数据库：默认 SQLite，本地文件 model_scheduling.db；模型定义见 [backend/app/models/](backend/app/models/)；Pydantic 模型见 [backend/app/schemas/](backend/app/schemas/)。
- 运行脚本：本地开发使用 [run_dev.py](run_dev.py)。


## 2. 运行与开发环境

前提：
- Python 3.8+，pip 可用
- Node.js 16+（前端开发与本地预览）

后端启动：

```bash
pip install -r requirements.txt
python run_dev.py
# 或：
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：
- OpenAPI: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

前端启动：

```bash
cd frontend
npm install
npm start
# 打开 http://localhost:3000
```

跨域：CORS 允许来源在 [backend/app/config.py](backend/app/config.py) 中配置（默认包含 http://localhost:3000）。


## 3. 配置与环境变量

后端配置类位于 [backend/app/config.py](backend/app/config.py) 的 Settings，支持 .env 加载。关键项：

- DATABASE_URL（默认 sqlite:///./model_scheduling.db）
- CORS_ORIGINS（默认 ["http://localhost:3000","http://127.0.0.1:3000"]）
- API_V1_STR（默认 /api/v1）
- PROJECT_NAME（默认 Model Inference Scheduling Platform）
- LOG_LEVEL（默认 INFO）
- ENABLE_SCHEDULER（默认 True）
- NODE_STATUS_REFRESH_INTERVAL（默认 30 秒）
- QUEUE_HISTORY_MAX_LENGTH（默认 1000）

前端 API 基地址可在 [frontend/.env](frontend/.env) 配置（如 REACT_APP_API_BASE_URL）。


## 4. 数据库与数据模型

- 默认数据库：SQLite（文件位于项目根目录），可迁移至 PostgreSQL/MySQL（建议引入 Alembic 做迁移）。
- 核心表与模型：
  - environments：环境管理（模型见 [backend/app/models/environment.py](backend/app/models/environment.py)）
  - models：模型配置与 RabbitMQ 信息（见 [backend/app/models/model.py](backend/app/models/model.py)）
  - nodes：节点信息与可用资源（见 [backend/app/models/node.py](backend/app/models/node.py)）
  - model_instances：模型实例运行态（见 [backend/app/models/model_instance.py](backend/app/models/model_instance.py)）
  - queue_length_records：队列长度历史（见 [backend/app/models/queue_length_record.py](backend/app/models/queue_length_record.py)）
  - scheduling_strategies：调度策略与启用状态（见 [backend/app/models/scheduling_strategy.py](backend/app/models/scheduling_strategy.py)）
- 关系：Environment 1:N Model，Environment 1:N Node，Node 1:N ModelInstance。

备份/恢复（SQLite）：
- 备份：停止服务后直接拷贝 model_scheduling.db 文件
- 恢复：替换为备份文件；必要时执行 `VACUUM` 优化


## 5. 后端 API（/api/v1）

路由聚合：见 [backend/app/api/v1/api.py](backend/app/api/v1/api.py)。主要资源：

- environments：CRUD（见 [backend/app/api/v1/environments.py](backend/app/api/v1/environments.py)）
- models：CRUD 及按环境查询（见 [backend/app/api/v1/models.py](backend/app/api/v1/models.py)）
- nodes：CRUD、心跳、状态/模型/GPU 查询、模型启停、进程终止等（见 [backend/app/api/v1/nodes.py](backend/app/api/v1/nodes.py)）
- queues：RabbitMQ 队列信息与历史（见 [backend/app/api/v1/queues.py](backend/app/api/v1/queues.py)）
- deployments：部署总览（见 [backend/app/api/v1/deployments.py](backend/app/api/v1/deployments.py)）
- scheduling-strategies：策略读取（见 backend/app/api/v1/scheduling_strategies.py）

统一响应结构：见 [backend/app/schemas/common.py](backend/app/schemas/common.py) 的 APIResponse。


## 6. 调度器与定时任务

注册与启动：在应用启动事件中完成（见 [backend/app/main.py](backend/app/main.py)），配置项 ENABLE_SCHEDULER 控制启停。任务注册见 [backend/app/scheduler.py](backend/app/scheduler.py)：
- 刷新节点状态：每 NODE_STATUS_REFRESH_INTERVAL 秒（[backend/app/jobs/node_jobs.py](backend/app/jobs/node_jobs.py)）
- 记录队列长度：每 60 秒（[backend/app/jobs/queue_jobs.py](backend/app/jobs/queue_jobs.py)）
- 应用调度策略：每 1 分钟（[backend/app/jobs/scheduling_jobs.py](backend/app/jobs/scheduling_jobs.py)）

注意：调度任务多为异步（httpx/节点调用），请确保外部依赖（节点 API、RabbitMQ Management API）可达。


## 7. 节点客户端与协议

节点客户端管理位于 [backend/app/services/node_client.py](backend/app/services/node_client.py)，服务端（节点侧）需提供以下能力：
- 健康检查：health_check()
- 支持模型列表：get_supported_models()
- GPU 状态：get_gpu_status()
- 模型实例状态：get_model_status()
- 启动模型：start_model(model_name, gpu_id, config)
- 停止模型：stop_model(model_name, gpu_id)
- 终止进程：kill_process(pid)

后端通过批量接口 batch_get_status 调用节点以并行拉取状态（用于部署总览与调度）。


## 8. 队列监控与历史

队列长度抓取任务见 [backend/app/jobs/queue_jobs.py](backend/app/jobs/queue_jobs.py)，使用 RabbitMQ Management API：
- 需在模型配置表（models）中完善 rabbitmq_host/port/vhost/queue_name/username/password
- 访问 URL 形如：http://{host}:{port}/api/queues/{vhost}/{queue}
- 历史保留策略由 QUEUE_HISTORY_MAX_LENGTH 控制
- 历史查询 API：GET /api/v1/queues/{model_id}/history?limit=


## 9. 调度策略（busy_queue_scaling）

策略入口：apply_scheduling_strategies（见 [backend/app/jobs/scheduling_jobs.py](backend/app/jobs/scheduling_jobs.py)），按激活策略遍历执行。

busy_queue_scaling 要点：
- 依据最近 5 分钟平均队列长度与模型平均推理时长（models.average_inference_time）判断“繁忙”
- 空闲 GPU：节点 available_gpu_ids 与实时占用对比后得出
- 候选模型：繁忙但当前无实例、且最近 5 分钟平均队列长度 > 0，按请求量倒序
- 部署：在支持该模型的节点空闲 GPU 上启动实例；若无空闲 GPU，可将近 5 分钟无请求的实例替换为更繁忙模型
- 保底：确保每个模型至少有一个实例（再次遍历在线节点尝试部署）

扩展策略建议：
- 在 scheduling_jobs 中增加实现函数并在 apply_scheduling_strategies 中挂接
- 在 scheduling_strategies 表中插入新策略并设置 is_active = True（读取接口见 backend/app/api/v1/scheduling_strategies.py）


## 10. 前端结构

- 路由与入口：[frontend/src/App.tsx](frontend/src/App.tsx)
- 布局：[frontend/src/components/Layout/MainLayout.tsx](frontend/src/components/Layout/MainLayout.tsx)
- 页面目录：[frontend/src/pages/](frontend/src/pages/)（Dashboard、Environments、Models、Nodes、Deployments、Scheduling）
- 服务层：[frontend/src/services/api.ts](frontend/src/services/api.ts)

本地调试：确保后端允许 http://localhost:3000，前端 .env 配置 API 基地址。


## 11. 日常运维

- 启停：通过 `python run_dev.py` 启动开发后端；生产建议使用进程管理（systemd/supervisor + uvicorn/gunicorn）
- 日志：由 LOG_LEVEL 控制；FastAPI 和 APScheduler 日志输出到标准输出
- 健康检查：GET /health；基础信息 GET /
- 定时任务：调整 [backend/app/config.py](backend/app/config.py) 的相关参数并重启
- RabbitMQ：确保 Management API 已启用且账号权限正确
- 节点连通：确认节点端口开放、认证方式满足要求


## 12. 常见问题排障

- CORS 报错：将前端来源加入 [backend/app/config.py](backend/app/config.py) 的 CORS_ORIGINS
- RabbitMQ 401：核对 username/password 与 vhost 访问权限
- 请求超时：检查节点或 RabbitMQ 的网络连通与防火墙
- Scheduler 未启动：检查 ENABLE_SCHEDULER 是否为 True；查看 [backend/app/main.py](backend/app/main.py) 启动日志
- SQLite “database is locked”：减少并发写入或切换至 PostgreSQL
- 422/校验失败：参照 [backend/app/schemas/](backend/app/schemas/) 的字段定义修正入参


## 13. 安全与合规

- 不要提交 .env、凭据与密钥到代码仓库
- RabbitMQ 与节点 API 需置于可信网络或启用认证/访问控制
- 如对外提供 API，建议加上鉴权（API Key/OAuth）与速率限制


## 14. 代码规范与协作

- Python：PEP8；类型注解；建议引入 flake8/black/isort
- 前端：TypeScript + ESLint；组件分层清晰
- Git 分支：feature/*、fix/*；提交信息语义化（feat/fix/docs/refactor/chore/test）
- PR：需附上变更说明与测试步骤


## 15. 部署与发布建议

- 数据库：生产建议使用 PostgreSQL；配置 DATABASE_URL
- 应用：uvicorn/gunicorn + 进程守护；反向代理（Nginx）与 HTTPS
- 前端：`npm run build` 后由 Nginx/静态服务器托管；配置反向代理到后端 /api
- CORS：按实际域名更新 [backend/app/config.py](backend/app/config.py) 的白名单
- 监控：接入日志采集与告警（节点离线、队列异常增长等）


## 16. 交接清单（Checklist）

- 代码仓库与分支保护策略
- 环境与凭据：.env 模板、RabbitMQ 账户、节点接入方式
- 部署环境访问：服务器、端口、负载均衡/网关、域名与证书
- 数据库备份/恢复流程与计划
- 节点清单与能力（GPU/模型支持）
- 监控与告警渠道（如有）
- 测试与验收用例（见 tests/）


## 17. 验收步骤

1) 启动后端并通过 /health、/docs 验证
2) 启动前端并可访问主要页面
3) 新建一个 Environment/Model/Node 并完成 CRUD 验证
4) 为某模型配置 RabbitMQ 管理信息，验证 /queues 与 /queues/{id}/history
5) 验证 deployments/status 能返回节点与 GPU 概览
6) 打开 ENABLE_SCHEDULER 并观察调度日志与实例变化


## 18. 进一步工作（Roadmap）

- WebSocket 实时推送
- 更丰富的调度策略与权重配置
- 鉴权与多租户
- 数据可视化（前端）与节点侧 Agent 标准化
- 数据迁移与版本管理（Alembic）


如需更详细的客户端调用示例，请参考根目录的 [model_inference_client_api_documentation.md](model_inference_client_api_documentation.md) 与各 API 源码文件。