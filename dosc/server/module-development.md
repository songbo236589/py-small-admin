# 模块开发指南

本文档介绍如何创建和开发新模块。

## 概述

Py Small Admin 采用模块化设计，每个功能模块都遵循统一的目录结构和开发规范。

## 模块结构

### 标准模块结构

```
Modules/{module_name}/
├── __init__.py
├── controllers/               # 控制器层
│   ├── __init__.py
│   └── v1/                 # API 版本
│       ├── __init__.py
│       └── {name}_controller.py
├── services/                 # 服务层
│   ├── __init__.py
│   └── {name}_service.py
├── models/                   # 模型层
│   ├── __init__.py
│   └── {name}_model.py
├── routes/                   # 路由层
│   ├── __init__.py
│   └── {name}.py
├── validators/               # 验证器层
│   ├── __init__.py
│   └── {name}_validator.py
├── middleware/               # 中间件（可选）
│   ├── __init__.py
│   └── {name}_middleware.py
├── migrations/               # 数据库迁移
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/            # 迁移版本
├── seeds/                   # 数据填充
│   ├── __init__.py
│   └── {name}_seed.py
├── queues/                  # 队列（可选）
│   ├── __init__.py
│   └── {name}_queues.py
└── tasks/                   # 异步任务（可选）
    ├── __init__.py
    └── {name}_tasks.py
```

## 创建新模块

### 方式一：使用命令工具（推荐）

```bash
# 使用命令工具创建模块
python -m commands.create_module article
```

这将自动创建完整的模块结构。

### 方式二：手动创建

如果手动创建，请按照以下步骤：

#### 1. 创建目录结构

```bash
# 创建模块目录
mkdir -p Modules/article/controllers/v1
mkdir -p Modules/article/services
mkdir -p Modules/article/models
mkdir -p Modules/article/routes
mkdir -p Modules/article/validators
mkdir -p Modules/article/migrations/versions
mkdir -p Modules/article/seeds
```

#### 2. 创建 **init**.py 文件

在每个目录中创建 `__init__.py` 文件：

```python
# Modules/article/__init__.py
"""文章模块"""
```

#### 3. 创建模型

```python
# Modules/article/models/article_model.py
from sqlmodel import Field
from Modules.common.models.base_model import BaseTableModel

class Article(BaseTableModel, table=True):
    """文章模型"""
    __table_comment__ = "文章表"

    title: str = Field(default="", index=True)
    content: str = Field(default="")
    status: int = Field(default=1)
```

#### 4. 创建验证器

```python
# Modules/article/validators/article_validator.py
from pydantic import BaseModel, Field

class ArticleAddRequest(BaseModel):
    """文章添加请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    status: int = Field(default=1, ge=0, le=1)
```

#### 5. 创建服务

```python
# Modules/article/services/article_service.py
from Modules.common.services.base_service import BaseService

class ArticleService(BaseService):
    """文章服务"""

    async def add(self, data: dict):
        """文章添加"""
        return await self.common_add(
            data=data,
            model_class=Article,
        )
```

#### 6. 创建控制器

```python
# Modules/article/controllers/v1/article_controller.py
from fastapi import Body
from fastapi.responses import JSONResponse
from Modules.article.services.article_service import ArticleService
from Modules.article.validators.article_validator import ArticleAddRequest

class ArticleController:
    """文章控制器"""

    def __init__(self):
        self.article_service = ArticleService()

    async def add(
        self,
        title: str = Body(..., description="标题"),
        content: str = Body(..., description="内容"),
    ) -> JSONResponse:
        """文章添加"""
        return await self.article_service.add({
            "title": title,
            "content": content,
        })
```

#### 7. 创建路由

```python
# Modules/article/routes/article.py
from fastapi import APIRouter
from Modules.article.controllers.v1.article_controller import ArticleController

router = APIRouter(prefix="/article", tags=["文章管理"])
controller = ArticleController()

router.post("/add", summary="文章添加")(controller.add)
```

#### 8. 注册路由

```python
# Modules/article/routes/__init__.py
from fastapi import APIRouter
from Modules.article.routes.article import router as article_router

main_router = APIRouter()
main_router.include_router(article_router)
```

```python
# Modules/main.py
from Modules.article.routes import main_router as article_router

# 注册路由
app.include_router(article_router, prefix=Config.get("app.api_prefix", ""))
```

#### 9. 运行数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "添加文章表"

# 执行迁移
alembic upgrade head
```

## 模块开发规范

### 1. 命名规范

- **模块名**: 小写字母，如 `article`、`product`
- **类名**: PascalCase，如 `ArticleService`、`ArticleController`
- **文件名**: kebab-case，如 `article_service.py`、`article_controller.py`

### 2. 代码组织

- **控制器**: 只负责参数验证和业务协调
- **服务**: 包含所有业务逻辑
- **模型**: 只定义数据结构
- **路由**: 只负责接口定义

### 3. 依赖管理

- 服务层依赖模型层
- 控制器层依赖服务层
- 路由层依赖控制器层

### 4. 数据库迁移

- 每个模块有独立的迁移目录
- 迁移文件命名规范：`{timestamp}_{description}.py`

## 模块间通信

### 调用其他模块的服务

```python
# 在当前模块中调用其他模块的服务
from Modules.admin.services.admin_service import AdminService

class ArticleService(BaseService):
    def __init__(self):
        self.admin_service = AdminService()

    async def get_article_author(self, author_id: int):
        return await self.admin_service.get_by_id(author_id)
```

### 共享模型

```python
# 在当前模块中引用其他模块的模型
from Modules.admin.models.admin_admin import AdminAdmin

class Article(BaseTableModel, table=True):
    author_id: int = Field(default=0, foreign_key="admin_admins.id")
    author: Mapped["AdminAdmin"] = Relationship()
```

## 模块测试

### 单元测试

```python
# tests/test_article_service.py
import pytest
from Modules.article.services.article_service import ArticleService

@pytest.mark.asyncio
async def test_add_article():
    service = ArticleService()
    result = await service.add({
        "title": "测试文章",
        "content": "测试内容",
    })
    assert result.status_code == 200
```

### 集成测试

```python
# tests/test_article_api.py
from fastapi.testclient import TestClient
from Modules.main import app

client = TestClient(app)

def test_add_article_api():
    response = client.post(
        "/api/article/add",
        json={
            "title": "测试文章",
            "content": "测试内容",
        }
    )
    assert response.status_code == 200
```

## 模块文档

### API 文档

为模块的 API 编写文档：

```python
@router.post(
    "/add",
    response_model=dict[str, Any],
    summary="文章添加",
    description="添加新文章",
)
async def add(...):
    pass
```

### 模块说明文档

创建模块说明文档：

```markdown
# 文章模块

## 功能

文章管理模块提供文章的增删改查功能。

## 接口

- POST /api/article/add - 添加文章
- GET /api/article/index - 获取文章列表
- PUT /api/article/update/{id} - 更新文章
- DELETE /api/article/destroy/{id} - 删除文章
```

## 常见问题

### 1. 如何在模块中使用缓存？

```python
from Modules.common.libs.database.redis.client import get_redis_client

async def get_article(self, id: int):
    redis = await get_redis_client("cache")
    cached = await redis.get(f"article:{id}")
    if cached:
        return json.loads(cached)

    article = await self._get_from_db(id)
    await redis.setex(f"article:{id}", 3600, json.dumps(article))
    return article
```

### 2. 如何在模块中使用 Celery 任务？

```python
# Modules/article/tasks/article_tasks.py
from celery import shared_task

@shared_task
def send_article_notification(article_id: int):
    # 发送文章通知
    pass

# 在服务中调用任务
from Modules.article.tasks.article_tasks import send_article_notification

async def add(self, data: dict):
    result = await self.common_add(data, Article)
    # 异步发送通知
    send_article_notification.delay(result.id)
    return result
```

### 3. 如何在模块中使用中间件？

```python
# Modules/article/middleware/article_middleware.py
from fastapi import Request

async def article_middleware(request: Request, call_next):
    # 前置处理
    response = await call_next(request)
    # 后置处理
    return response

# 在 main.py 中注册中间件
from Modules.article.middleware.article_middleware import article_middleware
app.middleware("http")(article_middleware)
```

## 最佳实践

### 1. 保持模块独立

- 模块之间低耦合
- 模块内部高内聚
- 避免循环依赖

### 2. 使用基类

- 服务继承 BaseService
- 模型继承 BaseTableModel
- 复用通用功能

### 3. 统一错误处理

- 使用统一的错误响应格式
- 记录错误日志
- 提供友好的错误提示

### 4. 编写测试

- 为关键功能编写单元测试
- 为 API 编写集成测试
- 保持高测试覆盖率

## 相关链接

- [第一个接口开发](./first-api.md)
- [项目结构说明](./project-structure.md)
- [Admin 模块详解](./admin-module.md)
- [Quant 模块详解](./quant-module.md)
- [Common 模块详解](./common-module.md)

---

通过遵循模块开发指南，您可以快速创建高质量的功能模块。
