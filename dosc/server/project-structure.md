# 项目结构说明

本文档详细介绍 Py Small Admin 后端项目的目录结构和各模块的职责。

## 概述

Py Small Admin 采用模块化设计，每个功能模块都遵循统一的目录结构，便于维护和扩展。

## 目录结构

```
server/
├── Modules/                      # 模块目录
│   ├── admin/                   # 管理员模块
│   │   ├── controllers/         # 控制器层
│   │   │   └── v1/             # v1 版本控制器
│   │   ├── services/            # 服务层
│   │   ├── models/              # 模型层
│   │   ├── routes/              # 路由层
│   │   ├── validators/          # 验证器层
│   │   ├── middleware/          # 中间件
│   │   ├── migrations/          # 数据库迁移
│   │   ├── seeds/              # 数据填充
│   │   ├── queues/             # 队列
│   │   └── tasks/              # 异步任务
│   ├── quant/                  # 量化数据模块（结构同 admin）
│   └── common/                 # 公共模块
│       ├── libs/               # 公共库
│       │   ├── config/         # 配置管理
│       │   ├── database/       # 数据库相关
│       │   ├── password/       # 密码加密
│       │   ├── captcha/        # 验证码
│       │   └── utils/          # 工具函数
│       ├── services/           # 基础服务
│       │   └── base_service.py # 基础服务类
│       └── models/             # 基础模型
│           └── base_model.py   # 基础模型类
├── config/                     # 配置文件
│   ├── __init__.py
│   ├── app.py                 # 应用配置
│   ├── base.py                # 基础配置
│   ├── database.py            # 数据库配置
│   ├── cache.py               # 缓存配置
│   ├── jwt.py                 # JWT 配置
│   ├── log.py                 # 日志配置
│   ├── password.py            # 密码配置
│   ├── upload.py              # 上传配置
│   ├── celery.py              # Celery 配置
│   └── captcha.py             # 验证码配置
├── commands/                   # 命令工具
│   ├── migrate.py             # 数据库迁移命令
│   ├── seed.py                # 数据填充命令
│   ├── create_module.py       # 创建模块命令
│   ├── generate_keys.py       # 密钥生成命令
│   └── celery_manager.py      # Celery 管理命令
├── docs/                       # 文档
│   ├── 环境配置说明.md
│   ├── Python环境配置完整指南.md
│   ├── config使用文档.md
│   └── ... (其他工具文档)
├── docker/                     # Docker 配置
│   ├── docker-compose.yml      # 开发环境
│   ├── docker-compose.prod.yml # 生产环境
│   ├── Dockerfile             # 服务镜像
│   ├── mysql/                 # MySQL 配置
│   ├── redis/                 # Redis 配置
│   ├── rabbitmq/              # RabbitMQ 配置
│   └── nginx/                 # Nginx 配置
├── logs/                       # 日志目录
│   └── .gitignore             # 忽略日志文件
├── uploads/                    # 上传文件目录
├── assets/                     # 静态资源
│   └── fonts/                 # 字体文件
├── run.py                      # 启动文件
├── requirements.txt            # 依赖列表
├── .env.example                # 开发环境配置示例
├── .env.production.example     # 生产环境配置示例
├── .gitignore                 # Git 忽略配置
└── README.md                  # 项目说明
```

## 模块结构详解

### 单个模块的标准结构

每个业务模块（如 `admin`、`quant`）都遵循以下标准结构：

```
Modules/{module_name}/
├── __init__.py
├── controllers/               # 控制器层
│   ├── __init__.py
│   └── v1/                  # API 版本
│       ├── __init__.py
│       └── {name}_controller.py
├── services/                  # 服务层
│   ├── __init__.py
│   └── {name}_service.py
├── models/                    # 模型层
│   ├── __init__.py
│   └── {name}_model.py
├── routes/                    # 路由层
│   ├── __init__.py
│   └── {name}.py
├── validators/                # 验证器层
│   ├── __init__.py
│   └── {name}_validator.py
├── middleware/                # 中间件（可选）
│   ├── __init__.py
│   └── {name}_middleware.py
├── migrations/                # 数据库迁移
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/             # 迁移版本
├── seeds/                    # 数据填充
│   ├── __init__.py
│   └── {name}_seed.py
├── queues/                   # 队列（可选）
│   ├── __init__.py
│   └── {name}_queues.py
└── tasks/                    # 异步任务（可选）
    ├── __init__.py
    └── {name}_tasks.py
```

## 各层职责

### 1. Routes（路由层）

**职责**：定义 API 接口，处理 HTTP 请求路由

**特点**：

- 只负责接口定义，不包含业务逻辑
- 使用 FastAPI 装饰器定义路由
- 指定请求方法、路径、参数、响应模型

**示例**：

```python
from fastapi import APIRouter
from Modules.admin.controllers.v1.admin_controller import AdminController

router = APIRouter(prefix="/admin", tags=["管理员管理"])
controller = AdminController()

router.get("/index", summary="获取管理员列表")(controller.index)
router.post("/add", summary="管理员添加")(controller.add)
```

### 2. Controllers（控制器层）

**职责**：参数验证、业务逻辑协调

**特点**：

- 接收并验证请求参数
- 调用 Service 层处理业务逻辑
- 返回统一格式的响应

**示例**：

```python
from Modules.admin.services.admin_service import AdminService
from Modules.admin.validators.admin_validator import AdminAddRequest

class AdminController:
    def __init__(self):
        self.admin_service = AdminService()

    async def add(self, username: str, password: str, ...):
        # 验证参数
        # 调用服务层
        return await self.admin_service.add(data)
```

### 3. Services（服务层）

**职责**：核心业务逻辑处理

**特点**：

- 包含所有业务逻辑
- 处理数据库操作
- 继承 `BaseService` 获得通用功能

**示例**：

```python
from Modules.common.services.base_service import BaseService

class AdminService(BaseService):
    async def add(self, data: dict):
        # 业务逻辑处理
        # 数据库操作
        return await self.common_add(data, AdminAdmin)
```

### 4. Models（模型层）

**职责**：定义数据模型和数据库表结构

**特点**：

- 使用 SQLModel 定义
- 继承 `BaseTableModel`
- 支持关系映射

**示例**：

```python
from sqlmodel import Field, Relationship
from Modules.common.models.base_model import BaseTableModel

class AdminAdmin(BaseTableModel, table=True):
    __table_comment__ = "管理员表"

    username: str = Field(default="", index=True)
    password: str = Field(default="")
    status: int = Field(default=1)

    group: Mapped["AdminGroup"] = Relationship(back_populates="admins")
```

### 5. Validators（验证器层）

**职责**：定义请求和响应的数据模型

**特点**：

- 使用 Pydantic 模型
- 定义字段类型、验证规则、错误提示

**示例**：

```python
from pydantic import BaseModel, Field

class AdminAddRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    status: int = Field(default=1)
```

## 公共模块

### Common 模块

`Modules/common/` 包含所有模块共用的基础组件：

#### libs/（公共库）

- **config/**: 配置管理系统
- **database/**: 数据库连接和会话管理
- **password/**: 密码加密工具
- **captcha/**: 验证码生成
- **utils/**: 通用工具函数

#### services/（基础服务）

- **base_service.py**: 提供通用的 CRUD 操作

#### models/（基础模型）

- **base_model.py**: 所有模型的基类

## 配置文件

### config/ 目录

包含所有配置文件，使用 Pydantic 进行配置管理：

- **app.py**: 应用基础配置（名称、版本、环境等）
- **database.py**: 数据库连接配置
- **cache.py**: 缓存配置
- **jwt.py**: JWT 认证配置
- **log.py**: 日志配置
- **password.py**: 密码策略配置
- **upload.py**: 文件上传配置
- **celery.py**: Celery 任务队列配置
- **captcha.py**: 验证码配置

## 命令工具

### commands/ 目录

提供各种命令行工具：

- **migrate.py**: 数据库迁移
- **seed.py**: 数据填充
- **create_module.py**: 快速创建新模块
- **generate_keys.py**: 生成安全密钥
- **celery_manager.py**: Celery 管理

## 文档

### docs/ 目录

包含项目的所有文档：

- 环境配置说明
- 各工具使用文档
- 最佳实践
- 故障排查

## Docker 配置

### docker/ 目录

包含 Docker 相关配置：

- **docker-compose.yml**: 开发环境编排
- **docker-compose.prod.yml**: 生产环境编排
- **Dockerfile**: 应用镜像构建
- **mysql/**: MySQL 配置
- **redis/**: Redis 配置
- **rabbitmq/**: RabbitMQ 配置
- **nginx/**: Nginx 配置

## 数据流转

```
HTTP 请求
    ↓
Routes (路由层)
    ↓
Controllers (控制器层) - 参数验证
    ↓
Services (服务层) - 业务逻辑
    ↓
Models (模型层) - 数据库操作
    ↓
数据库
```

## 命名规范

### 文件命名

- **kebab-case**: `admin_controller.py`, `admin_service.py`
- **模块目录**: 小写字母，如 `admin`, `quant`

### 类命名

- **PascalCase**: `AdminController`, `AdminService`, `AdminAdmin`

### 函数/方法命名

- **snake_case**: `add_admin`, `get_user_list`

### 变量命名

- **snake_case**: `user_id`, `admin_name`

## 扩展指南

### 创建新模块

使用命令工具快速创建新模块：

```bash
python -m commands.create_module module_name
```

或参考 [模块开发指南](./module-development.md) 手动创建。

### 添加新功能

1. 在相应模块的 `models/` 中定义数据模型
2. 在 `validators/` 中定义验证器
3. 在 `services/` 中实现业务逻辑
4. 在 `controllers/` 中创建控制器
5. 在 `routes/` 中定义路由
6. 运行数据库迁移

## 相关链接

- [快速开始](./getting-started.md)
- [架构概览](../guides/architecture-overview.md)
- [分层架构说明](../guides/layered-architecture.md)
- [模块开发指南](./module-development.md)
- [第一个接口开发](./first-api.md)

---

通过理解项目结构，您可以更高效地开发和维护代码。
