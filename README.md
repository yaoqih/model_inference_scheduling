# Model Inference Scheduling Platform

一个用于管理AI模型推理节点和调度的管理平台。

## 项目概述

这是一个模型推理调度管理平台，用于统一管理多个环境下的GPU节点和AI模型，提供可视化的监控和控制界面。

### 主要功能

- **多环境管理**: 支持开发/测试/生产环境隔离
- **模型配置管理**: 每个模型独立配置RabbitMQ连接信息
- **节点资源管理**: GPU节点注册和心跳检测，实时GPU使用率监控
- **实时监控**: WebSocket实时数据推送，GPU资源使用可视化
- **远程模型控制**: 通过管理界面启动/停止模型

## 技术栈

### 后端
- **FastAPI**: 现代、高性能的Python Web框架
- **SQLAlchemy**: ORM框架
- **SQLite**: 轻量级数据库
- **Pydantic**: 数据验证
- **httpx**: 异步HTTP客户端

### 前端
- **React 18**: 现代前端框架
- **TypeScript**: 类型安全
- **Ant Design**: UI组件库

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (前端开发)

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 运行后端服务

```bash
# 方式1: 使用开发脚本
python run_dev.py

# 方式2: 直接使用uvicorn
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问服务

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 项目结构

```
model_inference_scheduling/
├── backend/                    # 后端代码
│   └── app/
│       ├── main.py            # FastAPI应用入口
│       ├── config.py          # 配置管理
│       ├── database.py        # 数据库连接
│       ├── models/            # SQLAlchemy数据模型
│       └── schemas/           # Pydantic数据验证模型
├── frontend/                  # 前端代码(待开发)
├── requirements.txt           # Python依赖
├── run_dev.py                # 开发环境启动脚本
└── README.md                 # 项目说明
```

## 数据库设计

### 核心表结构

- **environments**: 环境配置表（用于资源隔离）
- **models**: 模型配置表（包含独立的RabbitMQ配置）
- **nodes**: 节点信息表（GPU节点管理）
- **model_instances**: 模型实例状态表（运行时状态）

## API接口

### 基础接口

- `GET /`: 根路径，返回API信息
- `GET /health`: 健康检查
- `GET /docs`: API文档

### 计划中的接口

- `GET /api/v1/environments`: 获取所有环境
- `POST /api/v1/environments`: 创建环境
- `GET /api/v1/models`: 获取所有模型
- `POST /api/v1/models`: 创建模型配置
- `GET /api/v1/nodes`: 获取所有节点
- `POST /api/v1/nodes`: 添加节点

## 开发状态

### ✅ 已完成
- [x] 项目架构设计
- [x] 数据库模型设计
- [x] Pydantic数据验证模型
- [x] FastAPI基础框架
- [x] 项目目录结构

### 🚧 进行中
- [ ] API路由实现
- [ ] 数据库CRUD操作
- [ ] 节点API客户端

### 📋 待开发
- [ ] 前端React应用
- [ ] WebSocket实时通信
- [ ] RabbitMQ队列监控
- [ ] 部署文档

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。