# 控制器开发指南

本文档详细介绍如何开发控制器层。

## 概述

控制器层负责参数验证和业务逻辑协调，是路由层和服务层之间的桥梁。

## 控制器结构

### 基本结构

```python
from fastapi import Body, Path, Query
from fastapi.responses import JSONResponse

class AdminController:
    """管理员控制器"""

    def __init__(self):
        """初始化控制器"""
        self.admin_service = AdminService()

    async def index(self, page: int, limit: int) -> JSONResponse:
        """获取管理员列表"""
        pass
```

### 完整示例

```python
from fastapi import Body, Path, Query
from fastapi.responses import JSONResponse
from Modules.admin.services.admin_service import AdminService
from Modules.admin.validators.admin_validator import AdminAddRequest
from Modules.common.libs.validation.decorators import validate_request_data
from Modules.common.libs.validation.pagination_validator import PaginationRequest

class AdminController:
    """管理员控制器"""

    def __init__(self):
        """初始化控制器"""
        self.admin_service = AdminService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页数量"),
    ) -> JSONResponse:
        """获取管理员列表"""
        return await self.admin_service.index({
            "page": page,
            "limit": limit,
        })

    @validate_request_data(AdminAddRequest)
    async def add(
        self,
        username: str = Body(..., description="用户名"),
        password: str = Body(..., description="密码"),
        name: str = Body(..., description="真实姓名"),
    ) -> JSONResponse:
        """管理员添加"""
        return await self.admin_service.add({
            "username": username,
            "password": password,
            "name": name,
        })
```

## 参数验证

### 使用验证装饰器

```python
from Modules.common.libs.validation.decorators import validate_request_data

@validate_request_data(AdminAddRequest)
async def add(self, username: str, password: str):
    # 参数已验证
    pass
```

### 使用多个验证器

```python
@validate_request_data(IdRequest)
@validate_request_data(AdminUpdateRequest)
async def update(self, id: int, username: str, password: str):
    # 参数已验证
    pass
```

### 自定义验证

```python
async def add(self, username: str, password: str):
    # 自定义验证逻辑
    if len(username) < 3:
        return error("用户名长度不能少于3个字符")
    if len(password) < 6:
        return error("密码长度不能少于6个字符")

    # 调用服务层
    return await self.admin_service.add({
        "username": username,
        "password": password,
    })
```

## 参数类型

### 路径参数

```python
from fastapi import Path

async def edit(self, id: int = Path(..., description="管理员ID")):
    pass
```

### 查询参数

```python
from fastapi import Query

async def index(
    self,
    page: int = Query(1, description="页码"),
    limit: int = Query(20, description="每页数量"),
    keyword: str | None = Query(None, description="关键词"),
):
    pass
```

### 请求体参数

```python
from fastapi import Body

async def add(
    self,
    username: str = Body(..., description="用户名"),
    password: str = Body(..., description="密码"),
):
    pass
```

### 表单参数

```python
from fastapi import Form

async def add(
    self,
    username: str = Form(..., description="用户名"),
    password: str = Form(..., description="密码"),
):
    pass
```

## 返回响应

### 使用统一响应函数

```python
from Modules.common.libs.responses.response import success, error

async def add(self, username: str, password: str):
    # 成功响应
    return success({"id": 1}, message="添加成功")

    # 错误响应
    return error("用户名已存在")
```

### 返回 JSONResponse

```python
from fastapi.responses import JSONResponse

async def add(self, username: str, password: str):
    return JSONResponse({
        "code": 200,
        "message": "添加成功",
        "data": {"id": 1}
    })
```

## 调用服务层

### 初始化服务

```python
class AdminController:
    def __init__(self):
        self.admin_service = AdminService()
```

### 调用服务方法

```python
async def add(self, username: str, password: str):
    return await self.admin_service.add({
        "username": username,
        "password": password,
    })
```

### 处理服务返回

```python
async def add(self, username: str, password: str):
    result = await self.admin_service.add({
        "username": username,
        "password": password,
    })

    # 处理返回结果
    if result.status_code == 200:
        return result
    else:
        return error("添加失败")
```

## 错误处理

### 捕获异常

```python
async def add(self, username: str, password: str):
    try:
        return await self.admin_service.add({
            "username": username,
            "password": password,
        })
    except ValueError as e:
        return error(str(e))
    except Exception as e:
        logger.error(f"添加管理员失败: {e}", exc_info=True)
        return error("系统错误")
```

### 验证错误

```python
async def add(self, username: str, password: str):
    # 验证用户名
    if not username or len(username) < 3:
        return error("用户名长度不能少于3个字符")

    # 验证密码
    if not password or len(password) < 6:
        return error("密码长度不能少于6个字符")

    # 调用服务层
    return await self.admin_service.add({
        "username": username,
        "password": password,
    })
```

## 最佳实践

### 1. 保持轻量

控制器只负责参数验证和业务协调：

```python
# ✅ 正确
async def add(self, username: str, password: str):
    return await self.admin_service.add({
        "username": username,
        "password": password,
    })

# ❌ 错误
async def add(self, username: str, password: str):
    # 包含业务逻辑
    hashed_password = self.hash_password(password)
    async with get_async_session() as session:
        instance = AdminAdmin(username=username, password=hashed_password)
        session.add(instance)
        await session.commit()
    return success(None)
```

### 2. 使用验证装饰器

使用验证装饰器进行参数验证：

```python
@validate_request_data(AdminAddRequest)
async def add(self, username: str, password: str):
    # 参数已验证
    pass
```

### 3. 使用类型提示

使用类型提示提高代码可读性：

```python
async def add(
    self,
    username: str = Body(..., description="用户名"),
    password: str = Body(..., description="密码"),
) -> JSONResponse:
    pass
```

### 4. 添加文档字符串

为所有方法添加文档字符串：

```python
async def add(self, username: str, password: str) -> JSONResponse:
    """管理员添加

    Args:
        username: 用户名
        password: 密码

    Returns:
        JSONResponse: 操作结果
    """
    pass
```

## 常见问题

### 1. 如何验证多个参数？

使用多个验证装饰器：

```python
@validate_request_data(IdRequest)
@validate_request_data(AdminUpdateRequest)
async def update(self, id: int, username: str):
    pass
```

### 2. 如何处理可选参数？

使用可选类型：

```python
async def index(
    self,
    keyword: str | None = Query(None, description="关键词"),
):
    pass
```

### 3. 如何定义默认值？

在参数定义中设置默认值：

```python
async def index(
    self,
    page: int = Query(1, description="页码"),
):
    pass
```

## 相关链接

- [路由开发指南](./routing-guide.md)
- [服务层开发指南](./service-guide.md)
- [验证器开发指南](./validator-guide.md)
- [第一个接口开发](../first-api.md)

---

通过遵循控制器开发指南，您可以编写清晰、规范的控制器代码。
