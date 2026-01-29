# 路由开发指南

本文档详细介绍如何开发路由层。

## 概述

路由层负责定义 API 接口，处理 HTTP 请求路由。路由层只负责接口定义，不包含业务逻辑。

## 路由定义

### 基本语法

使用 FastAPI 的 `APIRouter` 和装饰器定义路由：

```python
from fastapi import APIRouter
from typing import Any

router = APIRouter(prefix="/admin", tags=["管理员管理"])

@router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取管理员列表",
)
async def index():
    pass
```

### 路由参数

#### prefix

路由前缀，所有路由都会加上这个前缀：

```python
router = APIRouter(prefix="/admin", tags=["管理员管理"])

# 实际路径: /admin/index
@router.get("/index")
async def index():
    pass
```

#### tags

标签，用于在 API 文档中分组：

```python
router = APIRouter(tags=["管理员管理"])
```

#### response_model

响应模型，用于生成 API 文档：

```python
@router.get(
    "/index",
    response_model=dict[str, Any],
)
async def index():
    return {"code": 200, "message": "success", "data": {}}
```

#### summary

接口摘要，显示在 API 文档中：

```python
@router.get(
    "/index",
    summary="获取管理员列表",
)
async def index():
    pass
```

#### description

接口描述，显示在 API 文档中：

```python
@router.get(
    "/index",
    summary="获取管理员列表",
    description="分页获取管理员列表，支持搜索和排序",
)
async def index():
    pass
```

## HTTP 方法

### GET

用于获取资源：

```python
@router.get("/index")
async def index():
    pass
```

### POST

用于创建资源：

```python
@router.post("/add")
async def add():
    pass
```

### PUT

用于更新资源：

```python
@router.put("/update/{id}")
async def update(id: int):
    pass
```

### DELETE

用于删除资源：

```python
@router.delete("/destroy/{id}")
async def destroy(id: int):
    pass
```

### PATCH

用于部分更新资源：

```python
@router.patch("/patch/{id}")
async def patch(id: int):
    pass
```

## 路径参数

### 路径参数

在路径中定义参数：

```python
from fastapi import Path

@router.get("/edit/{id}")
async def edit(id: int = Path(..., description="管理员ID")):
    pass
```

### 查询参数

在查询字符串中定义参数：

```python
from fastapi import Query

@router.get("/index")
async def index(
    page: int = Query(1, description="页码"),
    limit: int = Query(20, description="每页数量"),
    keyword: str | None = Query(None, description="关键词"),
):
    pass
```

### 请求体参数

在请求体中定义参数：

```python
from fastapi import Body

@router.post("/add")
async def add(
    username: str = Body(..., description="用户名"),
    password: str = Body(..., description="密码"),
):
    pass
```

### 表单参数

在表单中定义参数：

```python
from fastapi import Form

@router.post("/add")
async def add(
    username: str = Form(..., description="用户名"),
    password: str = Form(..., description="密码"),
):
    pass
```

## 路由注册

### 在模块中注册

```python
# Modules/admin/routes/__init__.py
from fastapi import APIRouter
from Modules.admin.routes.admin import router as admin_router

main_router = APIRouter()
main_router.include_router(admin_router)
```

### 在应用中注册

```python
# Modules/main.py
from Modules.admin.routes import main_router as admin_router

app.include_router(admin_router, prefix=Config.get("app.api_prefix", ""))
```

## RESTful 设计

### 资源命名

使用名词复数形式：

```python
# ✅ 正确
router = APIRouter(prefix="/admins")

# ❌ 错误
router = APIRouter(prefix="/admin")
```

### HTTP 方法使用

| 操作     | HTTP 方法 | 路由示例            |
| -------- | --------- | ------------------- |
| 获取列表 | GET       | GET /admins         |
| 获取详情 | GET       | GET /admins/{id}    |
| 创建     | POST      | POST /admins        |
| 更新     | PUT       | PUT /admins/{id}    |
| 部分更新 | PATCH     | PATCH /admins/{id}  |
| 删除     | DELETE    | DELETE /admins/{id} |

## 路由分组

### 按功能分组

```python
# 管理员路由
admin_router = APIRouter(prefix="/admin", tags=["管理员管理"])

# 角色路由
group_router = APIRouter(prefix="/group", tags=["角色管理"])

# 权限路由
rule_router = APIRouter(prefix="/rule", tags=["权限管理"])
```

### 按版本分组

```python
# v1 路由
v1_router = APIRouter(prefix="/v1", tags=["v1"])

# v2 路由
v2_router = APIRouter(prefix="/v2", tags=["v2"])
```

## 最佳实践

### 1. 保持简单

路由层只做路由定义，不包含业务逻辑：

```python
# ✅ 正确
@router.get("/index")
async def index(page: int, limit: int):
    return await controller.index({"page": page, "limit": limit})

# ❌ 错误
@router.get("/index")
async def index(page: int, limit: int):
    # 包含业务逻辑
    async with get_async_session() as session:
        query = select(AdminAdmin)
        result = await paginate(session, query, ...)
    return result
```

### 2. 使用描述

为所有参数添加描述：

```python
@router.get("/index")
async def index(
    page: int = Query(1, description="页码，从1开始"),
    limit: int = Query(20, description="每页数量，最大100"),
):
    pass
```

### 3. 使用类型提示

使用类型提示提高代码可读性：

```python
from typing import Any

@router.get("/index", response_model=dict[str, Any])
async def index() -> JSONResponse:
    pass
```

### 4. 使用标签

使用标签在 API 文档中分组：

```python
router = APIRouter(tags=["管理员管理"])
```

## 常见问题

### 1. 如何定义可选参数？

```python
from fastapi import Query

@router.get("/index")
async def index(
    keyword: str | None = Query(None, description="关键词"),
):
    pass
```

### 2. 如何定义默认值？

```python
@router.get("/index")
async def index(
    page: int = Query(1, description="页码"),
):
    pass
```

### 3. 如何定义多个路径参数？

```python
@router.get("/edit/{id}/{type}")
async def edit(
    id: int = Path(..., description="ID"),
    type: str = Path(..., description="类型"),
):
    pass
```

## 相关链接

- [控制器开发指南](./controller-guide.md)
- [服务层开发指南](./service-guide.md)
- [模型开发指南](./model-guide.md)
- [验证器开发指南](./validator-guide.md)
- [第一个接口开发](../first-api.md)

---

通过遵循路由开发指南，您可以定义清晰、规范的 API 接口。
