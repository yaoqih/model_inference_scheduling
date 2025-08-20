# 项目概述
这是一个用于管理AI模型推理节点和调度的管理平台，支持多环境管理、模型配置管理、节点资源管理和实时监控。

# 技术栈
- **后端**: FastAPI, SQLAlchemy, SQLite, Pydantic
- **前端**: React, TypeScript, Ant Design

# 数据库设计
- **核心表结构**:
  - `environments`: 环境配置表
  - `models`: 模型配置表
  - `nodes`: 节点信息表
  - `model_instances`: 模型实例状态表

# API接口
提供了多种API接口用于管理环境、模型和节点。