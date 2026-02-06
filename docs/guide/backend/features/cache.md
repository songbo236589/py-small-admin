# 缓存功能

本文档介绍了项目的缓存功能。

## 简介

项目使用 Redis 作为缓存后端，提供了简单易用的缓存 API。

## 基础使用

### 导入缓存服务

```python
from Modules.common.libs.cache.cache import cache
```

### 缓存操作

```python
# 设置缓存
cache.set("key", "value", ttl=3600)

# 获取缓存
value = cache.get("key")

# 删除缓存
cache.delete("key")

# 检查缓存是否存在
exists = cache.exists("key")
```

## 缓存装饰器

### 基础缓存装饰器

```python
from Modules.common.libs.cache.cache import cache

@cache(key_prefix="user", ttl=3600)
def get_user(user_id: int):
    """获取用户信息，缓存 1 小时"""
    # 数据库查询...
    return user_data

# 使用
user = get_user(1)  # 第一次调用，查询数据库
user = get_user(1)  # 第二次调用，从缓存读取
```

### 带参数的缓存

```python
@cache(key_prefix="product", ttl=1800, key_from_attr=lambda args: f"product_{args[0]}")
def get_product(product_id: int):
    """获取商品信息"""
    return product_data
```

## 缓存策略

### Cache-Aside

```python
def get_user(user_id: int):
    # 先查缓存
    cache_key = f"user:{user_id}"
    user = cache.get(cache_key)

    if user is None:
        # 缓存未命中，查询数据库
        user = db.query_user(user_id)
        # 写入缓存
        cache.set(cache_key, user, ttl=3600)

    return user
```

### Write-Through

```python
def update_user(user_id: int, data: dict):
    # 更新数据库
    db.update_user(user_id, data)
    # 同时更新缓存
    cache_key = f"user:{user_id}"
    cache.set(cache_key, data, ttl=3600)
```

### Write-Behind

```python
def update_user_async(user_id: int, data: dict):
    # 立即更新缓存
    cache_key = f"user:{user_id}"
    cache.set(cache_key, data, ttl=3600)

    # 异步更新数据库
    update_db_task.delay(user_id, data)
```

## 缓存预热

```python
def warm_up_cache():
    """缓存预热"""
    # 预加载热点数据
    hot_items = db.get_hot_items()

    for item in hot_items:
        cache.set(f"item:{item.id}", item, ttl=3600)
```

## 缓存更新

### 更新缓存

```python
def update_item(item_id: int, data: dict):
    # 更新数据库
    db.update_item(item_id, data)

    # 删除旧缓存
    cache.delete(f"item:{item_id}")

    # 或更新缓存
    cache.set(f"item:{item_id}", data, ttl=3600)
```

### 批量删除缓存

```python
def clear_category_cache(category_id: int):
    """清除分类下的所有缓存"""
    pattern = f"category:{category_id}:*"
    keys = cache.keys(pattern)

    if keys:
        cache.delete(*keys)
```

## 缓存统计

### 获取缓存信息

```python
from Modules.common.libs.database.redis import get_redis_client

redis = get_redis_client()

# 获取缓存命中率
info = redis.info('stats')
hits = info['keyspace_hits']
misses = info['keyspace_misses']
hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0

print(f"缓存命中率: {hit_rate:.2%}")
```

## 缓存配置

### 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `REDIS_HOST` | Redis 主机 | localhost |
| `REDIS_PORT` | Redis 端口 | 6379 |
| `REDIS_PASSWORD` | Redis 密码 | - |
| `REDIS_DB` | 默认数据库 | 0 |
| `REDIS_CACHE_DB` | 缓存数据库 | 1 |
| `CACHE_DEFAULT_TTL` | 默认过期时间 | 3600 |

### 配置示例

```python
# config/cache.py
CACHE_CONFIG = {
    "default_ttl": 3600,          # 默认过期时间（秒）
    "key_prefix": "app",          # 键前缀
    "enable_stats": True,         # 启用统计
    "serializer": "json",         # 序列化方式
}
```

## 最佳实践

### 1. 键命名规范

```python
# 好的命名
cache.set("user:123", data)           # 用户数据
cache.set("product:456", data)        # 商品数据
cache.set("category:789:items", data) # 分类商品

# 不好的命名
cache.set("data1", data)
cache.set("temp", data)
```

### 2. 设置合理的过期时间

```python
# 热点数据，较长过期时间
cache.set("hot_items", items, ttl=7200)

# 临时数据，较短过期时间
cache.set("verify_code", code, ttl=300)

# 永久数据
cache.set("config:site", config, ttl=None)
```

### 3. 避免缓存穿透

```python
def get_user(user_id: int):
    cache_key = f"user:{user_id}"
    user = cache.get(cache_key)

    if user is None:
        user = db.query_user(user_id)

        # 即使数据不存在也缓存，防止穿透
        if user is None:
            cache.set(cache_key, None, ttl=60)
        else:
            cache.set(cache_key, user, ttl=3600)

    return user
```

### 4. 使用缓存锁

```python
from contextlib import contextmanager

@contextmanager
def cache_lock(key: str, timeout: int = 10):
    """缓存锁"""
    lock_key = f"lock:{key}"
    lock = cache.lock(lock_key, timeout=timeout)

    try:
        lock.acquire()
        yield
    finally:
        lock.release()

# 使用
def rebuild_cache():
    with cache_lock("rebuild_cache", timeout=300):
        # 重建缓存逻辑
        pass
```

### 5. 监控缓存

```python
def log_cache_stats():
    """记录缓存统计"""
    redis = get_redis_client()
    info = redis.info('stats')

    logger.info(f"缓存命中: {info['keyspace_hits']}")
    logger.info(f"缓存未命中: {info['keyspace_misses']}")
    logger.info(f"内存使用: {info['used_memory_human']}")
```

## 相关文档

- [配置指南](../config/index.md)
- [Redis 配置](../../deploy/database/migration.md)
