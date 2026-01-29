# 服务层开发指南

本文档详细介绍如何开发服务层。

## 概述

服务层负责核心业务逻辑处理，是控制器层和模型层之间的桥梁。

## 服务层结构

### 基本结构

```python
from Modules.common.services.base_service import BaseService

class AdminService(BaseService):
    """管理员服务"""

    def __init__(self):
        """初始化服务"""
        super().__init__()
        self.password_service = PasswordService()

    async def add(self, data: dict) -> JSONResponse:
        """管理员添加"""
        pass
```

### 继承 BaseService

继承 BaseService 获得通用功能：

```python
from Modules.common.services.base_service import BaseService

class AdminService(BaseService):
    """管理员服务"""

    async def add(self, data: dict) -> JSONResponse:
        """管理员添加"""
        return await self.common_add(
            data=data,
            model_class=AdminAdmin,
        )
```

## 通用方法

### common_add

通用添加方法：

```python
async def add(self, data: dict) -> JSONResponse:
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

### common_update

通用更新方法：

```python
async def update(self, id: int, data: dict) -> JSONResponse:
    return await self.common_update(
        id=id,
        data=data,
        model_class=AdminAdmin,
        pre_operation_callback=self._pre_update,
        field_update_callback=self._field_update,
    )

async def _pre_update(self, id: int, data: dict, session):
    """更新前置操作"""
    # 检查用户名
    return data, session

def _field_update(self, admin: AdminAdmin, data: dict):
    """字段更新"""
    admin.username = data.get("username", admin.username)
    admin.name = data.get("name", admin.name)
```

### common_destroy

通用删除方法：

```python
async def destroy(self, id: int) -> JSONResponse:
    return await self.common_destroy(
        id=id,
        model_class=AdminAdmin,
    )
```

### common_destroy_all

通用批量删除方法：

```python
async def destroy_all(self, id_array: list[int]) -> JSONResponse:
    return await self.common_destroy_all(
        id_array=id_array,
        model_class=AdminAdmin,
    )
```

## 搜索功能

### 应用搜索过滤器

```python
async def index(self, data: dict) -> JSONResponse:
    page = data.get("page", 1)
    size = data.get("limit", 20)

    # 设置文本搜索字段
    data["text_fields"] = ["username", "name"]
    # 精确匹配字段
    data["exact_fields"] = ["status", "group_id"]
    # 范围字段
    data["range_fields"] = ["created_at", "updated_at"]

    async with get_async_session() as session:
        query = select(AdminAdmin)
        # 应用搜索过滤器
        query = await self.apply_search_filters(query, AdminAdmin, data)
        # 应用排序
        query = await self.apply_sorting(query, AdminAdmin, data.get("sort"))

        page_data = await paginate(session, query, CustomParams(page=page, size=size))
        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
        })
```

### 文本搜索

```python
async def apply_search_filters(self, query, model_class, search_params):
    text_fields = search_params.get("text_fields", [])

    for field in text_fields:
        value = search_params.get(field)
        if value and value.strip():
            field_attr = getattr(model_class, field)
            query = query.filter(field_attr.like(f"%{value.strip()}%"))

    return query
```

### 精确匹配

```python
async def apply_search_filters(self, query, model_class, search_params):
    exact_fields = search_params.get("exact_fields", {})

    for field in exact_fields:
        value = search_params.get(field)
        if value is not None:
            field_attr = getattr(model_class, field)
            query = query.filter(field_attr == value)

    return query
```

### 范围搜索

```python
async def apply_search_filters(self, query, model_class, search_params):
    range_fields = search_params.get("range_fields", {})

    for field in range_fields:
        field_attr = getattr(model_class, field)
        start_date = search_params.get(f"{field}_start")
        if start_date:
            query = query.filter(field_attr >= start_date)
        end_date = search_params.get(f"{field}_end")
        if end_date:
            query = query.filter(field_attr <= end_date)

    return query
```

## 排序功能

### 应用排序

```python
async def apply_sorting(self, query, model_class, sort_param):
    if not sort_param:
        # 默认排序
        if hasattr(model_class, "id"):
            query = query.order_by(model_class.id.desc())
        return query

    # 解析排序参数
    if isinstance(sort_param, str):
        try:
            sort_data = json.loads(sort_param)
        except:
            sort_field, sort_direction = sort_param.split(" ")
    else:
        sort_data = sort_param

    # 应用排序
    if isinstance(sort_data, dict):
        sort_field = list(sort_data.keys())[0]
        sort_direction = sort_data[sort_field]
    else:
        sort_field, sort_direction = sort_param.split(" ")

    if hasattr(model_class, sort_field):
        if sort_direction.lower() == "desc":
            query = query.order_by(getattr(model_class, sort_field).desc())
        else:
            query = query.order_by(getattr(model_class, sort_field).asc())

    return query
```

## 回调函数

### 前置操作回调

```python
async def add(self, data: dict) -> JSONResponse:
    return await self.common_add(
        data=data,
        model_class=AdminAdmin,
        pre_operation_callback=self._pre_add,
    )

async def _pre_add(self, data: dict, session):
    """添加前置操作"""
    username = data.get("username")

    # 检查用户名是否已存在
    existing_admin = await session.execute(
        select(AdminAdmin).where(AdminAdmin.username == username)
    )
    if existing_admin.scalar_one_or_none():
        return error("用户名已存在")

    # 加密密码
    password = data.get("password")
    hashed_password = self.password_service.hash_password(password)
    data["password"] = hashed_password

    return data, session
```

### 字段更新回调

```python
async def update(self, id: int, data: dict) -> JSONResponse:
    return await self.common_update(
        id=id,
        data=data,
        model_class=AdminAdmin,
        field_update_callback=self._field_update,
    )

def _field_update(self, admin: AdminAdmin, data: dict):
    """字段更新"""
    updatable_fields = ["username", "name", "phone", "status"]

    for field in updatable_fields:
        if field in data and data[field] is not None:
            setattr(admin, field, data[field])
```

## 数据库操作

### 使用异步会话

```python
from Modules.common.libs.database.sql.session import get_async_session

async def add(self, data: dict) -> JSONResponse:
    async with get_async_session() as session:
        instance = AdminAdmin(**data)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)

        return success({"id": instance.id})
```

### 查询单条记录

```python
async def get_by_id(self, id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

### 查询多条记录

```python
async def get_list(self, page: int = 1, size: int = 20):
    async with get_async_session() as session:
        query = select(AdminAdmin)
        page_data = await paginate(session, query, CustomParams(page=page, size=size))
        return page_data
```

### 关系加载

```python
from sqlalchemy.orm import selectinload

async def get_with_group(self, id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin)
            .options(selectinload(AdminAdmin.group))
            .where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

## 最佳实践

### 1. 使用通用方法

使用 BaseService 的通用方法：

```python
# ✅ 正确
async def add(self, data: dict) -> JSONResponse:
    return await self.common_add(
        data=data,
        model_class=AdminAdmin,
    )

# ❌ 错误
async def add(self, data: dict) -> JSONResponse:
    async with get_async_session() as session:
        instance = AdminAdmin(**data)
        session.add(instance)
        await session.commit()
        return success(None)
```

### 2. 使用回调函数

使用回调函数处理前置操作：

```python
# ✅ 正确
async def add(self, data: dict) -> JSONResponse:
    return await self.common_add(
        data=data,
        model_class=AdminAdmin,
        pre_operation_callback=self._pre_add,
    )

async def _pre_add(self, data: dict, session):
    # 前置操作
    return data, session

# ❌ 错误
async def add(self, data: dict) -> JSONResponse:
    # 所有逻辑都在一个方法中
    # 检查用户名
    # 加密密码
    # 保存数据
    pass
```

### 3. 使用事务

使用事务确保数据一致性：

```python
# ✅ 正确
async def transfer(self, from_id: int, to_id: int, amount: int):
    async with get_async_session() as session:
        try:
            # 扣款
            from_account = await session.get(Account, from_id)
            from_account.balance -= amount

            # 加款
            to_account = await session.get(Account, to_id)
            to_account.balance += amount

            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

# ❌ 错误 - 没有事务
async def transfer(self, from_id: int, to_id: int, amount: int):
    from_account = await session.get(Account, from_id)
    from_account.balance -= amount

    to_account = await session.get(Account, to_id)
    to_account.balance += amount
```

## 常见问题

### 1. 如何处理业务逻辑错误？

返回错误响应：

```python
async def add(self, data: dict) -> JSONResponse:
    # 检查用户名
    if await self.check_username_exists(data["username"]):
        return error("用户名已存在")

    # 调用通用方法
    return await self.common_add(data, AdminAdmin)
```

### 2. 如何使用缓存？

使用 Redis 缓存：

```python
async def get_config(self, key: str):
    redis = await get_redis_client("cache")
    # 先从缓存获取
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)

    # 缓存不存在，从数据库获取
    config = await self._get_from_db(key)
    # 写入缓存
    await redis.setex(key, 3600, json.dumps(config))
    return config
```

### 3. 如何处理复杂查询？

使用 SQLAlchemy 的查询构建器：

```python
async def complex_query(self, filters: dict):
    async with get_async_session() as session:
        query = select(AdminAdmin)

        # 添加多个条件
        if filters.get("username"):
            query = query.where(AdminAdmin.username.like(f"%{filters['username']}%"))
        if filters.get("status"):
            query = query.where(AdminAdmin.status == filters["status"])

        # 添加排序
        query = query.order_by(AdminAdmin.id.desc())

        # 执行查询
        result = await session.execute(query)
        return result.scalars().all()
```

## 相关链接

- [控制器开发指南](./controller-guide.md)
- [模型开发指南](./model-guide.md)
- [BaseService 源码](../../server/Modules/common/services/base_service.py)
- [第一个接口开发](../first-api.md)

---

通过遵循服务层开发指南，您可以编写清晰、可复用的服务代码。
