# 系统架构

## 整体架构
该平台采用前后端分离的架构设计，后端提供RESTful API服务，前端使用React构建用户界面。

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (React)   │────│  后端 (FastAPI)  │────│  数据库 (SQLite) │
│                 │    │                 │    │                 │
│ - TypeScript    │    │ - SQLAlchemy    │    │ - 环境表         │
│ - Ant Design    │    │ - Pydantic      │    │ - 模型表         │
│ - React Router  │    │ - CORS          │    │ - 节点表         │
└─────────────────┘    └─────────────────┘    │ - 模型实例表     │
                                              └─────────────────┘
```

## 源代码路径

### 后端结构
- [`backend/app/main.py`](backend/app/main.py) - FastAPI应用入口
- [`backend/app/config.py`](backend/app/config.py) - 配置管理
- [`backend/app/database.py`](backend/app/database.py) - 数据库连接和会话管理
- [`backend/app/models/`](backend/app/models/) - SQLAlchemy数据模型
  - [`environment.py`](backend/app/models/environment.py) - 环境模型
  - [`model.py`](backend/app/models/model.py) - 模型配置模型
  - [`node.py`](backend/app/models/node.py) - 节点模型
  - [`model_instance.py`](backend/app/models/model_instance.py) - 模型实例模型
- [`backend/app/schemas/`](backend/app/schemas/) - Pydantic数据验证模型
- [`backend/app/api/v1/`](backend/app/api/v1/) - API路由
  - [`api.py`](backend/app/api/v1/api.py) - 路由聚合
  - [`environments.py`](backend/app/api/v1/environments.py) - 环境管理API
  - [`models.py`](backend/app/api/v1/models.py) - 模型管理API
  - [`nodes.py`](backend/app/api/v1/nodes.py) - 节点管理API
  - [`node_operations.py`](backend/app/api/v1/node_operations.py) - 节点操作API

### 前端结构
- [`frontend/src/App.tsx`](frontend/src/App.tsx) - 主应用组件
- [`frontend/src/components/Layout/MainLayout.tsx`](frontend/src/components/Layout/MainLayout.tsx) - 主布局组件
- [`frontend/src/pages/`](frontend/src/pages/) - 页面组件
  - [`Home.tsx`](frontend/src/pages/Home.tsx) - 首页
  - [`Environments.tsx`](frontend/src/pages/Environments.tsx) - 环境管理页面
  - [`Models.tsx`](frontend/src/pages/Models.tsx) - 模型管理页面
  - [`Nodes.tsx`](frontend/src/pages/Nodes.tsx) - 节点管理页面
- [`frontend/src/services/api.ts`](frontend/src/services/api.ts) - API服务层
- [`frontend/src/types/index.ts`](frontend/src/types/index.ts) - TypeScript类型定义

## 数据库设计

### 核心表结构
1. **environments** - 环境配置表
   - 用于资源隔离和环境管理
   - 支持开发/测试/生产环境

2. **models** - 模型配置表
   - 存储模型的RabbitMQ连接配置
   - 包含推理时间等性能指标

3. **nodes** - 节点信息表
   - GPU节点的基本信息和状态
   - 支持心跳检测和状态监控

4. **model_instances** - 模型实例状态表
   - 运行时模型实例的状态跟踪
   - 包含PID、端口、GPU分配等信息

### 表关系
- Environment 1:N Model
- Environment 1:N Node
- Node 1:N ModelInstance

## 关键技术决策

### 数据库选择
- 开发阶段使用SQLite，便于快速原型开发
- 生产环境可迁移到PostgreSQL或MySQL

### API设计
- 遵循RESTful设计原则
- 使用FastAPI自动生成OpenAPI文档
- 统一的错误处理和响应格式

### 前端架构
- 使用React Hooks进行状态管理
- Ant Design提供一致的UI体验
- TypeScript确保类型安全

## 组件关系

### 后端组件交互
```
FastAPI App
├── CORS Middleware
├── API Router (v1)
│   ├── Environments Router
│   ├── Models Router
│   ├── Nodes Router
│   └── Node Operations Router
├── Database Session
└── SQLAlchemy Models
```

### 前端组件层次
```
App
├── Router
├── MainLayout
│   ├── Sidebar Navigation
│   └── Content Area
│       ├── Home Page
│       ├── Environments Page
│       ├── Models Page
│       └── Nodes Page
└── API Service Layer
```

## 关键实现路径

### 启动流程
1. [`run_dev.py`](run_dev.py) - 开发环境启动脚本
2. [`backend/app/main.py`](backend/app/main.py) - 创建FastAPI应用
3. [`backend/app/database.py`](backend/app/database.py) - 初始化数据库连接
4. 自动创建数据库表结构

### API请求流程
1. 前端发起HTTP请求
2. FastAPI路由匹配
3. Pydantic数据验证
4. SQLAlchemy数据库操作
5. 返回JSON响应

### 数据流向
```
Frontend (React) 
    ↓ HTTP Request
Backend (FastAPI)
    ↓ SQL Query
Database (SQLite)
    ↑ Data Response
Backend Processing
    ↑ JSON Response
Frontend Update