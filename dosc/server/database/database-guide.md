# 数据库使用指南

本文档详细介绍如何使用数据库。

## 概述

Py Small Admin 使用 MySQL 作为主数据库，通过 SQLModel 和 SQLAlchemy 进行数据库操作。

## 数据库连接

### 配置连接

在 `.env` 文件中配置数据库连接：

```env
DB_CONNECTIONS__MYSQL__HOST=localhost
DB_CONNECTIONS__MYSQL__PORT=3306
DB_CONNECTIONS__MYSQL__USER=root
DB_CONNECTIONS__MYSQL__PASSWORD=your_password
DB_CONNECTIONS__MYSQL__DATABASE=py_small_admin
```

### 获取会话

```python
from Modules.common.libs.database.sql.session import get_async_session

async def get_admin(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

## 数据库操作

### 查询数据

#### 查询单条记录

```python
async def get_by_id(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

#### 查询多条记录

```python
async def get_list():
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin)
        )
        return result.scalars().all()
```

#### 条件查询

```python
async def get_by_status(status: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.status == status)
        )
        return result.scalars().all()
```

### 添加数据

```python
async def add_admin(data: dict):
    async with get_async_session() as session:
        admin = AdminAdmin(**data)
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin
```

### 更新数据

```python
async def update_admin(id: int, data: dict):
    async with get_async_session() as session:
        admin = await session.get(AdminAdmin, id)
        if admin:
            for key, value in data.items():
                setattr(admin, key, value)
            await session.commit()
            await session.refresh(admin)
        return admin
```

### 删除数据

```python
async def delete_admin(id: int):
    async with get_async_session() as session:
        admin = await session.get(AdminAdmin, id)
        if admin:
            await session.delete(admin)
            await session.commit()
        return True
    return False
```

## 关系查询

### 预加载关系

```python
from sqlalchemy.orm import selectinload

async def get_admin_with_group(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin)
            .options(selectinload(AdminAdmin.group))
            .where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

### 使用关系

```python
async def get_admin_with_group(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin)
            .options(selectinload(AdminAdmin.group))
            .where(AdminAdmin.id == id)
        )
        admin = result.scalar_one_or_none()

        # 访问关系
        if admin and admin.group:
            return {
                "id": admin.id,
                "username": admin.username,
                "group_name": admin.group.name,
            }
        return None
```

## 事务处理

### 基本事务

```python
async def transfer_money(from_id: int, to_id: int, amount: int):
    async with get_async_session() as session:
        try:
            # 扣款
            from_account = await session.get(Account, from_id)
            from_account.balance -= amount

            # 加款
            to_account = await session.get(Account, to_id)
            to_account.balance += amount

            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e
```

### 嵌套事务

```python
async def complex_operation():
    async with get_async_session() as session:
        try:
            # 操作 1
            # 操作 2
            # 操作 3
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
```

## 查询优化

### 使用索引

```python
class AdminAdmin(BaseTableModel, table=True):
    """管理员模型"""
    username: str = Field(default="", index=True)
    status: int = Field(default=1, index=True)
    created_at: datetime = Field(default=None, index=True)
```

### 只查询需要的字段

```python
async def get_admin_list():
    async with get_async_session() as session:
        result = await session.execute(
            select(
                AdminAdmin.id,
                AdminAdmin.username,
                AdminAdmin.name,
            )
        )
        return result.mappings().all()
```

### 使用 limit

```python
async def get_admin_list(limit: int = 10):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).limit(limit)
        )
        return result.scalars().all()
```

## 最佳实践

### 1. 使用异步操作

```python
# ✅ 正确
async with get_async_session() as session:
    result = await session.execute(select(AdminAdmin))

# ❌ 错误
with get_session() as session:
    result = session.execute(select(AdminAdmin))
```

### 2. 使用事务

```python
# ✅ 正确
async with get_async_session() as session:
    try:
        # 操作
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e

# ❌ 错误 - 没有事务
async with get_async_session() as session:
    # 操作
    await session.commit()
```

### 3. 关闭会话

使用 `async with` 自动关闭会话：

```python
# ✅ 正确
async with get_async_session() as session:
    result = await session.execute(select(AdminAdmin))

# ❌ 错误 - 忘记关闭
session = get_async_session()
result = await session.execute(select(AdminAdmin))
# 忘记关闭会话
```

## 常见问题

### 1. 如何处理连接超时？

在配置中设置连接超时：

```env
DB_CONNECTIONS__MYSQL__CONNECT_TIMEOUT=10
```

### 2. 如何处理连接池？

在配置中设置连接池参数：

```env
DB_CONNECTIONS__MYSQL__POOL_SIZE=10
DB_CONNECTIONS__MYSQL__MAX_OVERFLOW=20
```

### 3. 如何查看 SQL 日志？

在配置中启用 SQL 日志：

```env
DB_ECHO=true
```

## 相关链接

- [数据库迁移指南](./migration-guide.md)
- [关系映射指南](./relationship-guide.md)
- [查询优化指南](./query-optimization.md)
- [分表使用指南](./sharding-guide.md)

---

通过遵循数据库使用指南，您可以高效、安全地使用数据库。
