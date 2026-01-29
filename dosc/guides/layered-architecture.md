# 分层架构说明

本文档详细介绍 Py Small Admin 的分层架构设计。

## 概述

Py Small Admin 采用经典的四层架构：路由层、控制器层、服务层、模型层。这种分层设计使得代码结构清晰、职责明确、易于维护。

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    客户端                             │
│              (Web / Mobile / API)                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP 请求
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  路由层 (Routes)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • 接口定义                                   │  │
│  │  • 路由绑定                                   │  │
│  │  • 参数声明                                   │  │
│  │  • 响应模型                                   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                控制器层 (Controllers)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • 参数验证                                   │  │
│  │  • 业务协调                                   │  │
│  │  • 调用服务层                                 │  │
│  │  • 返回响应                                   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 服务层 (Services)                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • 业务逻辑                                   │  │
│  │  • 数据处理                                   │  │
│  │  • 调用模型层                                 │  │
│  │  • 事务管理                                   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 模型层 (Models)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • 数据模型                                   │  │
│  │  • 表结构定义                                 │  │
│  │  • 关系映射                                   │  │
│  │  • 数据验证                                   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  数据库 (Database)                     │
│              MySQL / Redis / RabbitMQ                 │
└─────────────────────────────────────────────────────────┘
```

## 各层详解

### 1. 路由层 (Routes)

#### 职责

- 定义 API 接口
- 处理 HTTP 请求路由
- 指定请求方法、路径、参数
- 定义响应模型

#### 特点

- **轻量级**: 只负责接口定义，不包含业务逻辑
- **声明式**: 使用装饰器定义路由
- **自动文档**: 自动生成 OpenAPI 文档
- **类型安全**: 支持类型提示

#### 示例代码

```python
from fastapi import APIRouter
from Modules.admin.controllers.v1.admin_controller import AdminController

router = APIRouter(prefix="/admin", tags=["管理员管理"])
controller = AdminController()

# 定义路由
router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取管理员列表",
)(controller.index)

router.post(
    "/add",
    response_model=dict[str, Any],
    summary="管理员添加",
)(controller.add)
```

#### 最佳实践

1. **保持简单**: 路由层只做路由定义，不包含业务逻辑
2. **使用装饰器**: 利用 FastAPI 的装饰器语法
3. **清晰的路径**: 使用 RESTful 风格的路径
4. **文档注释**: 添加 summary 和 description 提供文档

### 2. 控制器层 (Controllers)

#### 职责

- 接收并验证请求参数
- 调用服务层处理业务逻辑
- 返回统一格式的响应

#### 特点

- **参数验证**: 使用 Pydantic 模型验证参数
- **业务协调**: 协调多个服务的调用
- **轻量级**: 不包含复杂业务逻辑
- **错误处理**: 统一的错误处理

#### 示例代码

```python
from fastapi import Body, Path, Query
from fastapi.responses import JSONResponse
from Modules.admin.services.admin_service import AdminService
from Modules.admin.validators.admin_validator import AdminAddRequest
from Modules.common.libs.validation.decorators import validate_request_data

class AdminController:
    def __init__(self):
        self.admin_service = AdminService()

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

#### 最佳实践

1. **参数验证**: 使用装饰器进行参数验证
2. **类型提示**: 使用类型提示提高代码可读性
3. **描述清晰**: 为参数添加 description
4. **错误处理**: 统一的错误处理机制

### 3. 服务层 (Services)

#### 职责

- 实现核心业务逻辑
- 处理数据库操作
- 协调多个模型的操作
- 管理事务

#### 特点

- **业务逻辑**: 包含所有业务逻辑
- **可复用**: 服务方法可被多个控制器调用
- **继承基类**: 继承 BaseService 获得通用功能
- **事务管理**: 管理数据库事务

#### 示例代码

```python
from Modules.common.services.base_service import BaseService

class AdminService(BaseService):
    """管理员服务"""

    async def add(self, data: dict) -> JSONResponse:
        """管理员添加"""
        # 业务逻辑
        # 1. 检查用户名是否存在
        # 2. 加密密码
        # 3. 保存到数据库
        return await self.common_add(
            data=data,
            model_class=AdminAdmin,
            pre_operation_callback=self._pre_add,
        )

    async def _pre_add(self, data: dict, session):
        """添加前置操作"""
        # 检查用户名
        # 加密密码
        return data, session
```

#### 最佳实践

1. **单一职责**: 每个服务方法只做一件事
2. **复用基类**: 使用 BaseService 的通用方法
3. **回调函数**: 使用回调函数处理前置/后置操作
4. **事务管理**: 正确管理数据库事务

### 4. 模型层 (Models)

#### 职责

- 定义数据模型
- 建立数据库表结构
- 定义模型之间的关系
- 数据验证

#### 特点

- **类型安全**: 使用 SQLModel 的类型提示
- **自动验证**: Pydantic 自动验证
- **关系映射**: 支持一对多、多对多关系
- **继承基类**: 继承 BaseTableModel

#### 示例代码

```python
from sqlmodel import Field, Relationship
from Modules.common.models.base_model import BaseTableModel

class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    __table_comment__ = "管理员表"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(default="", index=True)
    password: str = Field(default="")
    status: int = Field(default=1)

    # 关系
    group: Mapped["AdminGroup"] = Relationship(back_populates="admins")
```

#### 最佳实践

1. **表注释**: 为表添加注释
2. **字段注释**: 为字段添加注释
3. **索引优化**: 合理使用索引
4. **关系定义**: 正确定义模型关系

## 数据流转

### 完整的数据流转过程

```
1. 客户端发送 HTTP 请求
   │
   ▼
2. 路由层接收请求
   │
   ▼
3. 控制器层验证参数
   │
   ▼
4. 服务层处理业务逻辑
   │
   ▼
5. 模型层操作数据库
   │
   ▼
6. 数据库返回结果
   │
   ▼
7. 模型层返回数据
   │
   ▼
8. 服务层处理数据
   │
   ▼
9. 控制器层返回响应
   │
   ▼
10. 路由层返回 HTTP 响应
    │
    ▼
11. 客户端接收响应
```

### 示例：添加管理员

```python
# 1. 客户端请求
POST /api/admin/add
{
  "username": "admin",
  "password": "123456",
  "name": "管理员"
}

# 2. 路由层接收
router.post("/add")(controller.add)

# 3. 控制器层验证
@validate_request_data(AdminAddRequest)
async def add(self, username, password, name):
    # 验证通过

# 4. 服务层处理
async def add(self, data):
    # 业务逻辑
    # - 检查用户名
    # - 加密密码
    # - 保存数据

# 5. 模型层操作
class AdminAdmin(BaseTableModel, table=True):
    username: str
    password: str

# 6. 数据库执行
INSERT INTO admin_admins (username, password) VALUES (?, ?)

# 7-11. 返回响应
{
  "code": 200,
  "message": "添加成功",
  "data": null
}
```

## 层与层之间的交互

### 路由层 → 控制器层

```python
# 路由层
router.post("/add")(controller.add)

# 控制器层
async def add(self, username: str, password: str):
    # 接收参数
    pass
```

**交互方式**：

- 路由层调用控制器方法
- 传递请求参数
- 控制器返回响应

### 控制器层 → 服务层

```python
# 控制器层
async def add(self, username, password):
    return await self.admin_service.add(data)

# 服务层
async def add(self, data: dict):
    # 处理业务逻辑
    pass
```

**交互方式**：

- 控制器调用服务方法
- 传递验证后的数据
- 服务返回处理结果

### 服务层 → 模型层

```python
# 服务层
async def add(self, data: dict):
    instance = AdminAdmin(**data)
    session.add(instance)
    await session.commit()

# 模型层
class AdminAdmin(BaseTableModel, table=True):
    username: str
    password: str
```

**交互方式**：

- 服务层创建模型实例
- 使用 ORM 操作数据库
- 模型层提供数据结构

## 依赖关系

### 依赖方向

```
路由层 → 控制器层 → 服务层 → 模型层 → 数据库
```

### 依赖原则

1. **单向依赖**: 上层依赖下层，下层不依赖上层
2. **接口隔离**: 每层只暴露必要的接口
3. **依赖注入**: 使用依赖注入降低耦合

## 优势

### 1. 职责清晰

每层都有明确的职责，代码结构清晰。

### 2. 易于维护

修改某一层的代码不会影响其他层。

### 3. 易于测试

可以单独测试每一层，提高测试覆盖率。

### 4. 易于扩展

添加新功能只需在相应层添加代码。

### 5. 团队协作

不同开发者可以专注于不同层。

## 注意事项

### 1. 避免跨层调用

❌ 错误示例：

```python
# 控制器直接操作数据库
async def add(self, data):
    session.add(AdminAdmin(**data))
    await session.commit()
```

✅ 正确示例：

```python
# 控制器调用服务层
async def add(self, data):
    return await self.admin_service.add(data)
```

### 2. 避免业务逻辑泄露

❌ 错误示例：

```python
# 路由层包含业务逻辑
@router.post("/add")
async def add(username: str):
    # 检查用户名
    if await check_username_exists(username):
        return error("用户名已存在")
    # 加密密码
    password = hash_password(password)
    # 保存
    return await save_admin(username, password)
```

✅ 正确示例：

```python
# 路由层只做路由定义
@router.post("/add")(controller.add)

# 业务逻辑在服务层
async def add(self, data):
    # 检查用户名
    # 加密密码
    # 保存
```

### 3. 避免重复代码

使用 BaseService 的通用方法，避免重复实现 CRUD。

## 扩展建议

### 1. 添加中间件

在路由层和控制器层之间添加中间件：

```
路由层 → 中间件层 → 控制器层 → 服务层 → 模型层
```

### 2. 添加缓存层

在服务层和模型层之间添加缓存层：

```
服务层 → 缓存层 → 模型层 → 数据库
```

### 3. 添加事件层

在服务层添加事件处理：

```
服务层 → 事件层 → 其他服务
```

## 相关链接

- [架构概览](./architecture-overview.md)
- [设计模式应用](./design-patterns.md)
- [最佳实践](./best-practices.md)
- [路由开发指南](../server/api-development/routing-guide.md)
- [控制器开发指南](../server/api-development/controller-guide.md)
- [服务层开发指南](../server/api-development/service-guide.md)
- [模型开发指南](../server/api-development/model-guide.md)

---

通过理解分层架构，您可以更好地组织代码和开发功能。
