# 查询优化指南

本文档详细介绍如何优化数据库查询。

## 概述

查询优化是提高系统性能的关键，通过合理的索引、查询优化和缓存可以显著提升性能。

## 索引优化

### 添加索引

为常用查询字段添加索引：

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    username: str = Field(default="", index=True)
    status: int = Field(default=1, index=True)
    created_at: datetime = Field(default=None, index=True)
```

### 复合索引

为多个字段的组合查询添加复合索引：

```python
from sqlalchemy import Index

class Article(BaseTableModel, table=True):
    """文章模型"""

    __table_args__ = (
        Index("idx_author_status", "author_id", "status"),
    )
```

### 唯一索引

为唯一字段添加唯一索引：

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""

    username: str = Field(default="", unique=True)
```

## 查询优化

### 只查询需要的字段

```python
# ✅ 正确 - 只查询需要的字段
query = select(
    AdminAdmin.id,
    AdminAdmin.username,
    AdminAdmin.name,
)

# ❌ 错误 - 查询所有字段
query = select(AdminAdmin)
```

### 使用 limit

```python
# ✅ 正确 - 使用 limit
query = select(AdminAdmin).limit(10)

# ❌ 错误 - 查询所有数据
query = select(AdminAdmin)
```

### 使用预加载

```python
# ✅ 正确 - 使用预加载
query = select(AdminAdmin).options(selectinload(AdminAdmin.group))

# ❌ 错误 - N+1 问题
query = select(AdminAdmin)
```

### 避免子查询

```python
# ✅ 正确 - 使用 join
query = select(AdminAdmin).join(AdminGroup)

# ❌ 错误 - 使用子查询
query = select(AdminAdmin).where(
    AdminAdmin.group_id.in_(
        select(AdminGroup.id).where(AdminGroup.status == 1)
    )
)
```

## 缓存优化

### 使用 Redis 缓存

```python
async def get_admin(id: int):
    cache_key = f"admin:{id}"

    # 先从缓存获取
    redis = await get_redis_client("cache")
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 缓存不存在，从数据库获取
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.id == id)
        )
        admin = result.scalar_one_or_none()

    # 写入缓存
    if admin:
        await redis.setex(cache_key, 3600, json.dumps(admin.__dict__))

    return admin
```

### 缓存失效

```python
async def update_admin(id: int, data: dict):
    # 更新数据库
    async with get_async_session() as session:
        admin = await session.get(AdminAdmin, id)
        for key, value in data.items():
            setattr(admin, key, value)
        await session.commit()

    # 删除缓存
    redis = await get_redis_client("cache")
    await redis.delete(f"admin:{id}")
```

## 分页优化

### 使用游标分页

```python
async def get_admin_list(cursor: str | None = None, limit: int = 20):
    async with get_async_session() as session:
        query = select(AdminAdmin).order_by(AdminAdmin.id)

        if cursor:
            query = query.where(AdminAdmin.id > int(cursor))

        query = query.limit(limit)
        result = await session.execute(query)
        admins = result.scalars().all()

        # 获取下一个游标
        next_cursor = str(admins[-1].id) if admins else None

        return {
            "items": admins,
            "next_cursor": next_cursor,
        }
```

## 批量操作

### 批量插入

```python
async def batch_insert_admins(admins: list[dict]):
    async with get_async_session() as session:
        for admin_data in admins:
            admin = AdminAdmin(**admin_data)
            session.add(admin)
        await session.commit()
```

### 批量更新

```python
async def batch_update_admins(updates: list[dict]):
    async with get_async_session() as session:
        for update in updates:
            admin = await session.get(AdminAdmin, update["id"])
            for key, value in update.items():
                if key != "id":
                    setattr(admin, key, value)
        await session.commit()
```

## 最佳实践

### 1. 使用 explain 分析查询

```python
from sqlalchemy import text

async def analyze_query():
    async with get_async_session() as session:
        result = await session.execute(
            text("EXPLAIN SELECT * FROM admin_admins")
        )
        print(result.fetchall())
```

### 2. 监控慢查询

```python
import logging

logger = logging.getLogger(__name__)

async def get_admin_list():
    start_time = time.time()

    async with get_async_session() as session:
        result = await session.execute(select(AdminAdmin))
        admins = result.scalars().all()

    elapsed_time = time.time() - start_time

    # 记录慢查询
    if elapsed_time > 1.0:
        logger.warning(f"慢查询: 耗时 {elapsed_time:.2f} 秒")

    return admins
```

### 3. 定期优化索引

定期检查和优化索引：

```bash
# 查看索引使用情况
SHOW INDEX FROM admin_admins;

# 分析表
ANALYZE TABLE admin_admins;
```

## 常见问题

### 1. 如何优化 like 查询？

```python
# ✅ 正确 - 使用前缀索引
query = select(AdminAdmin).where(
    AdminAdmin.username.like("admin%")
)

# ❌ 错误 - 无法使用索引
query = select(AdminAdmin).where(
    AdminAdmin.username.like("%admin%")
)
```

### 2. 如何优化 count 查询？

```python
# ✅ 正确 - 使用缓存
cache_key = "admin_count"
count = await redis.get(cache_key)
if not count:
    async with get_async_session() as session:
        result = await session.execute(
            select(func.count(AdminAdmin.id))
        )
        count = result.scalar()
        await redis.setex(cache_key, 3600, count)

# ❌ 错误 - 每次都查询
async with get_async_session() as session:
    result = await session.execute(
        select(func.count(AdminAdmin.id))
    )
    count = result.scalar()
```

## 相关链接

- [数据库使用指南](./database-guide.md)
- [关系映射指南](./relationship-guide.md)
- [分表使用指南](./sharding-guide.md)

---

通过遵循查询优化指南，您可以显著提升系统性能。
