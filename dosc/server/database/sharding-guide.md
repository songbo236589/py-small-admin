# 分表使用指南

本文档详细介绍如何使用分表功能。

## 概述

当数据量很大时，分表可以提高查询性能和数据管理效率。

## 分表策略

### 按时间分表

按时间分表是最常见的分表策略：

```python
class QuantStockKlines1d(BaseTableModel, table=True):
    """日线K线"""
    __table_comment__ = "日线K线表"

    stock_id: int = Field(default=0, index=True)
    trade_date: datetime = Field(default=None, index=True)


class QuantStockKlines1w(BaseTableModel, table=True):
    """周线K线"""
    __table_comment__ = "周线K线表"

    stock_id: int = Field(default=0, index=True)
    trade_date: datetime = Field(default=None, index=True)
```

### 按业务分表

按业务逻辑分表：

```python
class Article2023(BaseTableModel, table=True):
    """2023年文章表"""
    __tablename__ = "articles_2023"


class Article2024(BaseTableModel, table=True):
    """2024年文章表"""
    __tablename__ = "articles_2024"
```

### 按哈希分表

按哈希值分表：

```python
class Article0(BaseTableModel, table=True):
    """文章表0"""
    __tablename__ = "articles_0"


class Article1(BaseTableModel, table=True):
    """文章表1"""
    __tablename__ = "articles_1"
```

## 分表实现

### 定义分表模型

```python
from sqlmodel import Field
from Modules.common.models.base_model import BaseTableModel

class QuantStockKlines1d(BaseTableModel, table=True):
    """日线K线"""
    __table_comment__ = "日线K线表"

    stock_id: int = Field(default=0, index=True)
    trade_date: datetime = Field(default=None, index=True)
    open: float = Field(default=0.0)
    high: float = Field(default=0.0)
    low: float = Field(default=0.0)
    close: float = Field(default=0.0)
    volume: int = Field(default=0)
```

### 分表路由

根据条件路由到不同的表：

```python
async def get_kline(stock_id: int, period: str):
    # 根据周期选择表
    if period == "1d":
        model_class = QuantStockKlines1d
    elif period == "1w":
        model_class = QuantStockKlines1w
    else:
        raise ValueError(f"不支持的周期: {period}")

    async with get_async_session() as session:
        result = await session.execute(
            select(model_class).where(model_class.stock_id == stock_id)
        )
        return result.scalars().all()
```

### 分表查询

跨分表查询：

```python
async def get_kline_range(stock_id: int, start_date: datetime, end_date: datetime):
    # 查询多个分表
    models = [
        QuantStockKlines1d,
        QuantStockKlines1w,
    ]

    results = []
    for model_class in models:
        async with get_async_session() as session:
            result = await session.execute(
                select(model_class)
                .where(model_class.stock_id == stock_id)
                .where(model_class.trade_date >= start_date)
                .where(model_class.trade_date <= end_date)
            )
            results.extend(result.scalars().all())

    return results
```

## 分表迁移

### 创建分表

```python
from sqlalchemy import text

async def create_sharded_table(table_name: str):
    async with get_async_session() as session:
        await session.execute(
            text(f"CREATE TABLE IF NOT EXISTS {table_name} LIKE articles")
        )
        await session.commit()
```

### 数据迁移

```python
async def migrate_data(source_table: str, target_table: str):
    async with get_async_session() as session:
        await session.execute(
            text(f"INSERT INTO {target_table} SELECT * FROM {source_table}")
        )
        await session.commit()
```

## 最佳实践

### 1. 使用统一的基础模型

```python
# ✅ 正确 - 继承基础模型
class QuantStockKlines1d(BaseTableModel, table=True):
    pass

# ❌ 错误 - 不继承基础模型
class QuantStockKlines1d(SQLModel, table=True):
    pass
```

### 2. 使用分表路由器

```python
# ✅ 正确 - 使用路由器
class ShardingRouter:
    def get_table(self, period: str):
        tables = {
            "1d": QuantStockKlines1d,
            "1w": QuantStockKlines1w,
        }
        return tables.get(period)

# ❌ 错误 - 硬编码表名
if period == "1d":
    model_class = QuantStockKlines1d
```

### 3. 使用分表缓存

```python
async def get_kline_with_cache(stock_id: int, period: str):
    cache_key = f"kline:{stock_id}:{period}"

    # 先从缓存获取
    redis = await get_redis_client("cache")
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 缓存不存在，从数据库获取
    router = ShardingRouter()
    model_class = router.get_table(period)

    async with get_async_session() as session:
        result = await session.execute(
            select(model_class).where(model_class.stock_id == stock_id)
        )
        klines = result.scalars().all()

    # 写入缓存
    if klines:
        await redis.setex(cache_key, 3600, json.dumps([k.__dict__ for k in klines]))

    return klines
```

## 常见问题

### 1. 如何选择分表策略？

根据业务场景选择：

- **按时间分表**: 适合时间序列数据
- **按业务分表**: 适合有明显业务区分的数据
- **按哈希分表**: 适合均匀分布的数据

### 2. 如何处理跨表查询？

```python
# 使用 UNION 查询
async def get_all_articles():
    async with get_async_session() as session:
        result = await session.execute(
            text("""
                SELECT * FROM articles_2023
                UNION
                SELECT * FROM articles_2024
            """)
        )
        return result.fetchall()
```

### 3. 如何迁移历史数据？

```python
# 使用批量插入
async def migrate_historical_data():
    batch_size = 1000
    offset = 0

    while True:
        async with get_async_session() as session:
            result = await session.execute(
                text(f"SELECT * FROM articles LIMIT {batch_size} OFFSET {offset}")
            )
            articles = result.fetchall()

            if not articles:
                break

            # 插入到分表
            for article in articles:
                await session.execute(
                    text("INSERT INTO articles_2024 VALUES (...)")
                )

            await session.commit()
            offset += batch_size
```

## 相关链接

- [数据库使用指南](./database-guide.md)
- [查询优化指南](./query-optimization.md)
- [分表使用文档](../../server/docs/分表使用文档.md)

---

通过遵循分表使用指南，您可以高效管理大量数据。
