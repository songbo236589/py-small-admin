# 第一个接口开发

本文档将指导您从零开始创建一个完整的 CRUD 接口。

## 概述

我们将创建一个简单的"文章管理"模块，包含完整的增删改查功能。

## 学习目标

完成本教程后，您将学会：

- 如何创建新的模块
- 如何定义数据模型
- 如何创建验证器
- 如何实现服务层逻辑
- 如何创建控制器
- 如何定义路由
- 如何测试接口

## 前置要求

- 已完成 [开发环境搭建](./development-setup.md)
- 已启动数据库服务
- 已运行数据库迁移

## 步骤一：创建模块

### 方式一：使用命令工具（推荐）

```bash
# 使用命令工具创建模块
python -m commands.create_module article
```

这将自动创建完整的模块结构：

```
Modules/article/
├── __init__.py
├── controllers/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── article_controller.py
├── services/
│   ├── __init__.py
│   └── article_service.py
├── models/
│   ├── __init__.py
│   └── article_model.py
├── routes/
│   ├── __init__.py
│   └── article.py
├── validators/
│   ├── __init__.py
│   └── article_validator.py
├── migrations/
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── seeds/
    ├── __init__.py
    └── article_seed.py
```

### 方式二：手动创建

如果手动创建，请确保目录结构完整，并创建所有必要的 `__init__.py` 文件。

## 步骤二：定义数据模型

编辑 `Modules/article/models/article_model.py`：

```python
"""
文章模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class Article(BaseTableModel, table=True):
    """
    文章模型

    对应数据库表：articles
    """

    # 表注释
    __table_comment__ = "文章表"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 文章标题
    title: str | None = Field(
        sa_column=Column(
            String(200), nullable=False, server_default="", comment="文章标题"
        ),
        default="",
    )

    # 文章内容
    content: str | None = Field(
        sa_column=Column(Text, nullable=False, comment="文章内容"),
        default="",
    )

    # 作者
    author: str | None = Field(
        sa_column=Column(
            String(100), nullable=False, server_default="", comment="作者"
        ),
        default="",
    )

    # 状态: 0=草稿, 1=已发布
    status: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="状态:0=草稿,1=已发布",
            index=True,
        ),
        default=0,
    )

    # 浏览量
    views: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="浏览量",
        ),
        default=0,
    )

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )
```

## 步骤三：创建验证器

编辑 `Modules/article/validators/article_validator.py`：

```python
"""
文章验证器
"""

from pydantic import BaseModel, Field


class ArticleAddRequest(BaseModel):
    """文章添加请求"""

    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容")
    author: str = Field(..., min_length=1, max_length=100, description="作者")
    status: int = Field(default=0, ge=0, le=1, description="状态:0=草稿,1=已发布")


class ArticleUpdateRequest(BaseModel):
    """文章更新请求"""

    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容")
    author: str = Field(..., min_length=1, max_length=100, description="作者")
    status: int = Field(default=0, ge=0, le=1, description="状态:0=草稿,1=已发布")
```

## 步骤四：创建服务层

编辑 `Modules/article/services/article_service.py`：

```python
"""
文章服务 - 负责文章相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from Modules.article.models.article_model import Article
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService


class ArticleService(BaseService):
    """文章服务 - 负责文章相关的业务逻辑"""

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取文章列表或搜索文章（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 设置文本搜索字段
        data["text_fields"] = ["title", "author"]
        # 精确匹配字段字典
        data["exact_fields"] = ["status"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at"]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(Article)
            # 搜索
            query = await self.apply_search_filters(query, Article, data)

            # 应用排序
            query = await self.apply_sorting(query, Article, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for article in page_data.items:
                d = article.__dict__.copy()
                d["created_at"] = (
                    format_datetime(article.created_at) if article.created_at else None
                )
                d["updated_at"] = (
                    format_datetime(article.updated_at) if article.updated_at else None
                )
                items.append(d)
            return success(
                jsonable_encoder(
                    {
                        "items": items,
                        "total": page_data.total,
                        "page": page_data.page,
                        "size": page_data.size,
                        "pages": page_data.pages,
                    }
                )
            )

    async def add(self, data: dict[str, Any]) -> JSONResponse:
        """文章添加"""
        return await self.common_add(
            data=data,
            model_class=Article,
            success_message="文章添加成功",
        )

    async def edit(self, id: int) -> JSONResponse:
        """获取文章信息（用于编辑）"""
        async with get_async_session() as session:
            result = await session.execute(
                select(Article).where(Article.id == id)
            )
            article = result.scalar_one_or_none()

            if not article:
                return error("文章不存在")

            return success({
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "author": article.author,
                "status": article.status,
            })

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新文章信息"""
        return await self.common_update(
            id=id,
            data=data,
            model_class=Article,
            success_message="文章更新成功",
        )

    async def destroy(self, id: int) -> JSONResponse:
        """文章删除"""
        return await self.common_destroy(
            id=id,
            model_class=Article,
        )

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """文章批量删除"""
        return await self.common_destroy_all(
            id_array=id_array,
            model_class=Article,
        )
```

## 步骤五：创建控制器

编辑 `Modules/article/controllers/v1/article_controller.py`：

```python
"""
文章管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Body, Path, Query
from fastapi.responses import JSONResponse

from Modules.article.services.article_service import ArticleService
from Modules.article.validators.article_validator import (
    ArticleAddRequest,
    ArticleUpdateRequest,
)
from Modules.common.libs.validation.decorators import (
    validate_body_data,
    validate_request_data,
)
from Modules.common.libs.validation.pagination_validator import (
    IdArrayRequest,
    IdRequest,
    ListStatusRequest,
    PaginationRequest,
)


class ArticleController:
    """文章管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化文章管理控制器"""
        self.article_service = ArticleService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        title: str | None = Query(None, description="文章标题"),
        author: str | None = Query(None, description="作者"),
        status: int | None = Query(None, description="状态"),
        sort: str | None = Query(None, description="排序规则"),
        created_at_start: str | None = Query(
            None, alias="created_at[start]", description="创建时间开始"
        ),
        created_at_end: str | None = Query(
            None, alias="created_at[end]", description="创建时间结束"
        ),
        updated_at_start: str | None = Query(
            None, alias="updated_at[start]", description="更新时间开始"
        ),
        updated_at_end: str | None = Query(
            None, alias="updated_at[end]", description="更新时间结束"
        ),
    ) -> JSONResponse:
        """获取文章列表或搜索文章（统一接口）"""
        return await self.article_service.index(
            {
                "page": page,
                "limit": limit,
                "title": title,
                "author": author,
                "status": status,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(ArticleAddRequest)
    async def add(
        self,
        title: str = Body(..., description="文章标题"),
        content: str = Body(..., description="文章内容"),
        author: str = Body(..., description="作者"),
        status: int = Body(0, description="状态"),
    ) -> JSONResponse:
        """文章添加"""
        return await self.article_service.add(
            {
                "title": title,
                "content": content,
                "author": author,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="文章ID")) -> JSONResponse:
        """获取文章信息（用于编辑）"""
        return await self.article_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(ArticleUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="文章ID"),
        title: str = Body(..., description="文章标题"),
        content: str = Body(..., description="文章内容"),
        author: str = Body(..., description="作者"),
        status: int = Body(0, description="状态"),
    ) -> JSONResponse:
        """更新文章信息"""
        return await self.article_service.update(
            id,
            {
                "title": title,
                "content": content,
                "author": author,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="文章ID"),
    ) -> JSONResponse:
        """文章删除"""
        return await self.article_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """文章批量删除"""
        return await self.article_service.destroy_all(request.id_array)
```

## 步骤六：定义路由

编辑 `Modules/article/routes/article.py`：

```python
"""
文章管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.article.controllers.v1.article_controller import ArticleController

# 创建路由器
router = APIRouter(prefix="/article", tags=["文章管理"])
# 创建控制器实例
controller = ArticleController()

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取文章列表或搜索文章（统一接口）",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="文章添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="文章编辑页面数据",
)(controller.edit)


router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="文章编辑",
)(controller.update)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="文章删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="文章批量删除",
)(controller.destroy_all)
```

## 步骤七：注册路由

编辑 `Modules/article/routes/__init__.py`：

```python
"""
文章模块路由
"""

from fastapi import APIRouter

from Modules.article.routes.article import router as article_router

# 创建主路由
main_router = APIRouter()

# 注册子路由
main_router.include_router(article_router)
```

编辑 `Modules/main.py`，在应用中注册文章模块的路由：

```python
from Modules.article.routes import main_router as article_router

# 在文件末尾添加
app.include_router(article_router, prefix=Config.get("app.api_prefix", ""))
```

## 步骤八：运行数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "添加文章表"

# 执行迁移
alembic upgrade head
```

或使用命令工具：

```bash
python -m commands.migrate
```

## 步骤九：测试接口

### 1. 启动项目

```bash
python run.py
```

### 2. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

您应该能看到"文章管理"标签下的所有接口。

### 3. 测试添加文章

使用 Swagger UI 测试：

```bash
# 请求 URL
POST /api/article/add

# 请求体
{
  "title": "我的第一篇文章",
  "content": "这是文章的内容...",
  "author": "张三",
  "status": 1
}

# 预期响应
{
  "code": 200,
  "message": "文章添加成功",
  "data": null
}
```

### 4. 测试获取列表

```bash
# 请求 URL
GET /api/article/index?page=1&limit=10

# 预期响应
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

### 5. 测试更新文章

```bash
# 请求 URL
PUT /api/article/update/1

# 请求体
{
  "title": "更新后的文章标题",
  "content": "更新后的内容",
  "author": "张三",
  "status": 1
}

# 预期响应
{
  "code": 200,
  "message": "文章更新成功",
  "data": null
}
```

### 6. 测试删除文章

```bash
# 请求 URL
DELETE /api/article/destroy/1

# 预期响应
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

## 代码说明

### 数据模型

- 继承 `BaseTableModel` 获得基础字段
- 使用 `Field` 定义字段属性
- 支持表注释和字段注释

### 验证器

- 使用 Pydantic 模型定义请求和响应
- 支持字段验证（长度、范围等）
- 自动生成 API 文档

### 服务层

- 继承 `BaseService` 获得通用 CRUD 方法
- 实现业务逻辑
- 处理数据库操作

### 控制器

- 接收和验证请求参数
- 调用服务层
- 返回统一响应

### 路由

- 使用 FastAPI 装饰器定义接口
- 指定请求方法、路径、参数
- 自动生成 OpenAPI 文档

## 进阶功能

### 添加搜索功能

服务层已经支持搜索，只需在控制器中添加搜索参数：

```python
async def index(
    self,
    title: str | None = Query(None, description="文章标题"),
    author: str | None = Query(None, description="作者"),
    ...
):
```

### 添加排序功能

```python
async def index(
    self,
    sort: str | None = Query(None, description="排序规则"),
    ...
):
```

排序参数格式：

- `{"id": "desc"}` - 按 ID 降序
- `{"created_at": "asc"}` - 按创建时间升序

### 添加分页功能

```python
async def index(
    self,
    page: int = Query(1, description="页码"),
    limit: int = Query(20, description="每页数量"),
    ...
):
```

## 常见问题

### 1. 迁移失败

**问题**：运行迁移时出现错误

**解决方案**：

- 检查数据库连接是否正常
- 确认模型定义是否正确
- 查看迁移日志定位问题

### 2. 接口 404

**问题**：访问接口时返回 404

**解决方案**：

- 确认路由是否正确注册
- 检查 API 前缀配置
- 确认请求路径是否正确

### 3. 参数验证失败

**问题**：提交数据时提示验证失败

**解决方案**：

- 检查验证器定义是否正确
- 确认请求参数格式是否匹配
- 查看 API 文档了解参数要求

## 下一步

- 📖 学习 [API 开发指南](./api-development.md) 了解更多 API 开发技巧
- 🏗️ 查看 [架构概览](../guides/architecture-overview.md) 了解系统设计
- 🔧 参考 [模块开发指南](./module-development.md) 学习模块开发
- 💡 阅读 [最佳实践](../guides/best-practices.md) 提升代码质量

## 相关链接

- [快速开始](./getting-started.md)
- [项目结构说明](./project-structure.md)
- [开发环境搭建](./development-setup.md)
- [路由开发指南](./api-development/routing-guide.md)
- [控制器开发指南](./api-development/controller-guide.md)
- [服务层开发指南](./api-development/service-guide.md)

---

恭喜您完成了第一个接口的开发！🎉
