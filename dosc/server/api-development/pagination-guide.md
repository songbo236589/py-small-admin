# 分页开发指南

本文档详细介绍如何实现分页功能。

## 概述

分页功能用于处理大量数据的展示，提高用户体验和系统性能。

## 分页参数

### 基本参数

```python
from fastapi import Query

async def index(
    page: int = Query(1, description="页码，从1开始"),
    limit: int = Query(20, description="每页数量，最大100"),
):
    pass
```

### 分页验证器

```python
from Modules.common.libs.validation.pagination_validator import PaginationRequest

class PaginationRequest(BaseModel):
    """分页请求"""

    page: int = Field(default=1, ge=1, description="页码")
    limit: int = Field(default=20, ge=1, le=100, description="每页数量")
```

## 分页实现

### 使用 fastapi-pagination

```python
from fastapi_pagination.ext.sqlalchemy import paginate
from Modules.common.libs.validation.pagination_validator import CustomParams

async def index(self, data: dict) -> JSONResponse:
    page = data.get("page", 1)
    size = data.get("limit", 20)

    async with get_async_session() as session:
        query = select(AdminAdmin)
        page_data = await paginate(
            session, query, CustomParams(page=page, size=size)
        )

        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
            "pages": page_data.pages,
        })
```

### 自定义分页

```python
from sqlalchemy import func

async def index(self, page: int = 1, size: int = 20):
    async with get_async_session() as session:
        # 计算总数
        total_query = select(func.count(AdminAdmin.id))
        total_result = await session.execute(total_query)
        total = total_result.scalar()

        # 计算偏移量
        offset = (page - 1) * size

        # 查询数据
        query = select(AdminAdmin).offset(offset).limit(size)
        result = await session.execute(query)
        items = result.scalars().all()

        # 计算总页数
        pages = (total + size - 1) // size

        return success({
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        })
```

## 分页响应

### 标准响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

### 响应字段说明

| 字段  | 类型  | 说明             |
| ----- | ----- | ---------------- |
| items | array | 当前页的数据列表 |
| total | int   | 总记录数         |
| page  | int   | 当前页码         |
| size  | int   | 每页数量         |
| pages | int   | 总页数           |

## 搜索与分页

### 文本搜索

```python
async def index(self, page: int, limit: int, keyword: str | None):
    async with get_async_session() as session:
        query = select(AdminAdmin)

        # 添加搜索条件
        if keyword:
            query = query.where(AdminAdmin.username.like(f"%{keyword}%"))

        # 分页
        page_data = await paginate(session, query, CustomParams(page=page, size=limit))

        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
            "pages": page_data.pages,
        })
```

### 多条件搜索

```python
async def index(self, page: int, limit: int, **filters):
    async with get_async_session() as session:
        query = select(AdminAdmin)

        # 添加多个搜索条件
        if filters.get("username"):
            query = query.where(AdminAdmin.username.like(f"%{filters['username']}%"))
        if filters.get("status"):
            query = query.where(AdminAdmin.status == filters["status"])
        if filters.get("group_id"):
            query = query.where(AdminAdmin.group_id == filters["group_id"])

        # 分页
        page_data = await paginate(session, query, CustomParams(page=page, size=limit))

        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
            "pages": page_data.pages,
        })
```

## 排序与分页

### 基本排序

```python
async def index(self, page: int, limit: int, sort: str | None):
    async with get_async_session() as session:
        query = select(AdminAdmin)

        # 添加排序
        if sort:
            sort_field, sort_direction = sort.split(" ")
            if hasattr(AdminAdmin, sort_field):
                if sort_direction == "desc":
                    query = query.order_by(getattr(AdminAdmin, sort_field).desc())
                else:
                    query = query.order_by(getattr(AdminAdmin, sort_field).asc())
        else:
            query = query.order_by(AdminAdmin.id.desc())

        # 分页
        page_data = await paginate(session, query, CustomParams(page=page, size=limit))

        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
            "pages": page_data.pages,
        })
```

### JSON 格式排序

```python
async def index(self, page: int, limit: int, sort: str | None):
    async with get_async_session() as session:
        query = select(AdminAdmin)

        # 解析 JSON 格式排序
        if sort:
            try:
                sort_data = json.loads(sort)
                sort_field = list(sort_data.keys())[0]
                sort_direction = sort_data[sort_field]

                if hasattr(AdminAdmin, sort_field):
                    if sort_direction == "desc":
                        query = query.order_by(getattr(AdminAdmin, sort_field).desc())
                    else:
                        query = query.order_by(getattr(AdminAdmin, sort_field).asc())
            except:
                query = query.order_by(AdminAdmin.id.desc())
        else:
            query = query.order_by(AdminAdmin.id.desc())

        # 分页
        page_data = await paginate(session, query, CustomParams(page=page, size=limit))

        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
            "pages": page_data.pages,
        })
```

## 最佳实践

### 1. 限制每页数量

限制每页最大数量：

```python
# ✅ 正确
limit: int = Field(default=20, ge=1, le=100, description="每页数量")

# ❌ 错误
limit: int = Field(default=20, description="每页数量")
```

### 2. 验证页码

验证页码是否有效：

```python
# ✅ 正确
page: int = Field(default=1, ge=1, description="页码")

# ❌ 错误
page: int = Field(default=1, description="页码")
```

### 3. 使用缓存

缓存分页结果：

```python
async def index(self, page: int, limit: int):
    cache_key = f"admin_list:{page}:{limit}"

    # 先从缓存获取
    redis = await get_redis_client("cache")
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 缓存不存在，从数据库获取
    result = await self._get_from_db(page, limit)

    # 写入缓存
    await redis.setex(cache_key, 300, json.dumps(result))

    return result
```

## 常见问题

### 1. 如何处理空数据？

返回空数组：

```python
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "size": 20,
    "pages": 0
  }
}
```

### 2. 如何处理超大页码？

返回最后一页：

```python
async def index(self, page: int, limit: int):
    async with get_async_session() as session:
        # 计算总页数
        total = await self._get_total()
        pages = (total + limit - 1) // limit

        # 如果页码超过总页数，返回最后一页
        if page > pages:
            page = pages

        # 查询数据
        result = await self._get_data(page, limit)

        return success({
            "items": result,
            "total": total,
            "page": page,
            "size": limit,
            "pages": pages,
        })
```

### 3. 如何优化分页查询？

使用索引和优化查询：

```python
async def index(self, page: int, limit: int):
    async with get_async_session() as session:
        # 只查询需要的字段
        query = select(
            AdminAdmin.id,
            AdminAdmin.username,
            AdminAdmin.name,
        )

        # 使用索引字段排序
        query = query.order_by(AdminAdmin.id.desc())

        # 分页
        page_data = await paginate(session, query, CustomParams(page=page, size=limit))

        return success({
            "items": page_data.items,
            "total": page_data.total,
            "page": page_data.page,
            "size": page_data.size,
            "pages": page_data.pages,
        })
```

## 相关链接

- [服务层开发指南](./service-guide.md)
- [控制器开发指南](./controller-guide.md)
- [第一个接口开发](../first-api.md)

---

通过遵循分页开发指南，您可以实现高效、用户友好的分页功能。
