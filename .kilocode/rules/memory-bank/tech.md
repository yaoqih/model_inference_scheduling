# 技术栈详细说明

## 后端技术栈

### FastAPI
- **版本**: 0.104.1
- **用途**: 构建高性能的RESTful API
- **特性**: 自动生成OpenAPI文档、类型提示支持、异步处理

### SQLAlchemy
- **版本**: 2.0.23
- **用途**: ORM框架，简化数据库操作
- **特性**: 支持多种数据库、声明式模型定义、关系映射

### Pydantic
- **版本**: 2.5.0
- **用途**: 数据验证和序列化
- **特性**: 基于Python类型提示的数据验证、自动文档生成

### 其他后端依赖
- **uvicorn**: ASGI服务器，支持异步处理
- **httpx**: 异步HTTP客户端
- **websockets**: WebSocket支持
- **python-dotenv**: 环境变量管理
- **alembic**: 数据库迁移工具

## 前端技术栈

### React
- **版本**: 18.2.0
- **用途**: 构建用户界面
- **特性**: 组件化开发、虚拟DOM、Hooks

### TypeScript
- **版本**: 4.7.4
- **用途**: 提供类型安全
- **特性**: 静态类型检查、更好的IDE支持、代码可维护性

### Ant Design
- **版本**: 5.12.8
- **用途**: UI组件库
- **特性**: 丰富的组件、一致的设计语言、国际化支持

### 其他前端依赖
- **react-router-dom**: 路由管理
- **axios**: HTTP客户端
- **recharts**: 数据可视化图表库

## 数据库

### SQLite
- **用途**: 开发和测试阶段的数据库
- **优势**: 轻量级、无需安装、文件存储
- **文件位置**: `model_scheduling.db`

### 数据库模型设计
- **Environment**: 环境配置管理
- **Model**: 模型配置和RabbitMQ连接信息
- **Node**: GPU节点信息和状态
- **ModelInstance**: 运行时模型实例状态

## 开发工具和配置

### 开发环境
- **Python**: 3.8+
- **Node.js**: 16+
- **启动脚本**: [`run_dev.py`](run_dev.py)

### 配置管理
- **后端配置**: [`backend/app/config.py`](backend/app/config.py)
- **环境变量**: 支持`.env`文件
- **CORS配置**: 允许前端跨域访问

### API文档
- **自动生成**: FastAPI自动生成OpenAPI文档
- **访问地址**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`

## 部署和运维

### 开发部署
```bash
# 后端启动
python run_dev.py

# 前端启动
cd frontend
npm start
```

### 生产部署考虑
- **数据库**: 迁移到PostgreSQL或MySQL
- **容器化**: 支持Docker部署
- **负载均衡**: 支持多实例部署
- **监控**: 集成日志和监控系统

## 技术约束和限制

### 当前限制
- 使用SQLite，不适合高并发场景
- 缺少用户认证和授权机制
- 没有实现缓存层
- 缺少完整的错误处理和日志记录

### 扩展性考虑
- 支持水平扩展
- 可插拔的存储后端
- 微服务架构支持
- API版本管理

## 代码质量和测试

### 代码规范
- Python: PEP 8
- TypeScript: ESLint配置
- 类型提示: 强制使用类型注解

### 测试策略
- 单元测试: pytest (后端)
- 集成测试: FastAPI TestClient
- 前端测试: Jest + React Testing Library
- API测试: 自动化API测试

## 性能优化

### 后端优化
- 异步处理: FastAPI原生支持
- 数据库连接池: SQLAlchemy配置
- 缓存策略: Redis集成计划

### 前端优化
- 代码分割: React.lazy
- 状态管理: React Hooks
- 打包优化: Webpack配置