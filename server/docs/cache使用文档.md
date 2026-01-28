# Cache 使用文档

## 概述

本项目的 Cache 模块提供了统一的缓存操作接口，基于 Redis 实现，支持同步和异步操作。该模块封装了 Redis 的底层操作，提供类型安全、错误处理和日志记录功能。

该模块主要包含以下文件：

- `Modules/common/libs/cache/cache.py`: 缓存服务类（同步和异步）
- `config/cache.py`: 缓存配置类

## 主要功能

- 支持同步和异步缓存操作
- 自动序列化和反序列化（支持 JSON）
- 键名前缀管理
- 默认 TTL（过期时间）配置
- 批量操作支持
- 原子操作（setnx）
- 工厂函数模式（get_or_set）
- 数值递增/递减操作
- 完整的错误处理和日志记录
- 单例模式的全局服务实例

## 安装与导入

```python
from Modules.common.libs.cache import (
    # 服务类
    SyncCacheService,
    AsyncCacheService,
    
    # 获取服务实例
    get_sync_cache_service,
    get_async_cache_service,
    
    # 同步便捷函数
    sync_cache_get,
    sync_cache_set,
    sync_cache_setnx,
    sync_cache_delete,
    sync_cache_exists,
    sync_cache_expire,
    sync_cache_ttl,
    sync_cache_get_many,
    sync_cache_set_many,
    sync_cache_delete_many,
    sync_cache_increment,
    sync_cache_decrement,
    sync_cache_clear,
    sync_cache_keys,
    sync_cache_get_or_set,
    
    # 异步便捷函数
    async_cache_get,
    async_cache_set,
    async_cache_delete,
    async_cache_exists,
    async_cache_expire,
    async_cache_ttl,
    async_cache_get_many,
    async_cache_set_many,
    async_cache_delete_many,
    async_cache_increment,
    async_cache_decrement,
    async_cache_clear,
    async_cache_keys,
    async_cache_get_or_set,
)
```

## Cache 配置

### 基本配置

Cache 配置通过 `CacheConfig` 类管理，支持环境变量配置：

```python
from config.cache import CacheConfig

# 获取缓存配置
config = CacheConfig()
print(f"连接名称: {config.connection}")
print(f"默认 TTL: {config.default_ttl}")
print(f"键名前缀: {config.key_prefix}")
```

### 环境变量配置

可以通过环境变量配置缓存：

```bash
# Redis 连接名称（对应 config/database.py 中的 redis 配置）
CACHE_CONNECTION=cache

# 默认 TTL（秒）
CACHE_DEFAULT_TTL=3600

# 键名前缀
CACHE_KEY_PREFIX=myapp_cache_
```

### 配置说明

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `connection` | Redis 连接名称（对应 database.py 中的 redis 配置） | cache |
| `default_ttl` | 默认缓存过期时间（秒） | 3600 |
| `key_prefix` | 缓存键名前缀 | "" |

## 同步缓存服务

### SyncCacheService 类

`SyncCacheService` 提供同步的缓存操作接口。

#### 基本操作

```python
from Modules.common.libs.cache import SyncCacheService

# 创建服务实例
cache = SyncCacheService()

# 设置缓存
cache.set("user:1", {"name": "张三", "age": 30}, ttl=3600)

# 获取缓存
user = cache.get("user:1")
print(user)  # {'name': '张三', 'age': 30}

# 获取不存在的键（返回默认值）
user = cache.get("user:999", default=None)
print(user)  # None

# 删除缓存
cache.delete("user:1")

# 检查缓存是否存在
exists = cache.exists("user:1")
print(exists)  # False
```

#### 过期时间管理

```python
from Modules.common.libs.cache import SyncCacheService

cache = SyncCacheService()

# 设置缓存（使用默认 TTL）
cache.set("key1", "value1")

# 设置缓存（指定 TTL）
cache.set("key2", "value2", ttl=1800)  # 30分钟

# 设置过期时间
cache.expire("key1", 7200)  # 2小时

# 获取剩余过期时间
ttl = cache.ttl("key2")
print(f"剩余时间: {ttl}秒")  # 剩余时间: 1799秒
```

#### 原子操作

```python
from Modules.common.libs.cache import SyncCacheService

cache = SyncCacheService()

# 原子设置（仅当键不存在时设置）
result = cache.setnx("counter:views", 0)
print(result)  # True（设置成功）

# 再次尝试设置（键已存在）
result = cache.setnx("counter:views", 100)
print(result)  # False（跳过设置）

# 递增
count = cache.increment("counter:views")
print(count)  # 1

# 批量递增
count = cache.increment("counter:views", delta=10)
print(count)  # 11

# 递减
count = cache.decrement("counter:views")
print(count)  # 10
```

#### 批量操作

```python
from Modules.common.libs.cache import SyncCacheService

cache = SyncCacheService()

# 批量设置
cache.set_many({
    "user:1": {"name": "张三"},
    "user:2": {"name": "李四"},
    "user:3": {"name": "王五"},
}, ttl=3600)

# 批量获取
users = cache.get_many(["user:1", "user:2", "user:3"])
print(users)
# {'user:1': {'name': '张三'}, 'user:2': {'name': '李四'}, 'user:3': {'name': '王五'}}

# 批量删除
deleted = cache.delete_many(["user:1", "user:2"])
print(f"删除数量: {deleted}")  # 删除数量: 2
```

#### 工厂函数模式

```python
from Modules.common.libs.cache import SyncCacheService

cache = SyncCacheService()

# 定义数据获取函数
def fetch_user_data(user_id: int) -> dict:
    # 模拟从数据库获取数据
    print(f"从数据库获取用户 {user_id} 的数据")
    return {"id": user_id, "name": f"用户{user_id}"}

# 使用 get_or_set
user = cache.get_or_set("user:123", fetch_user_data, ttl=3600)
print(user)
# 从数据库获取用户 123 的数据
# {'id': 123, 'name': '用户123'}

# 再次获取（从缓存）
user = cache.get_or_set("user:123", fetch_user_data, ttl=3600)
print(user)
# {'id': 123, 'name': '用户123'}（不会打印数据库查询）
```

#### 键管理

```python
from Modules.common.libs.cache import SyncCacheService

cache = SyncCacheService()

# 设置一些缓存
cache.set("user:1", "张三")
cache.set("user:2", "李四")
cache.set("config:theme", "dark")

# 获取所有键
all_keys = cache.keys()
print(all_keys)  # ['user:1', 'user:2', 'config:theme']

# 获取匹配模式的键
user_keys = cache.keys("user:*")
print(user_keys)  # ['user:1', 'user:2']

# 清空所有缓存（带前缀）
cache.clear()
```

## 异步缓存服务

### AsyncCacheService 类

`AsyncCacheService` 提供异步的缓存操作接口，API 与同步版本类似。

#### 基本操作

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio

async def async_example():
    # 创建服务实例
    cache = AsyncCacheService()
    
    # 设置缓存
    await cache.set("user:1", {"name": "张三", "age": 30}, ttl=3600)
    
    # 获取缓存
    user = await cache.get("user:1")
    print(user)  # {'name': '张三', 'age': 30}
    
    # 删除缓存
    await cache.delete("user:1")

# 运行异步示例
asyncio.run(async_example())
```

#### 异步工厂函数

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio

async def async_factory_example():
    cache = AsyncCacheService()
    
    # 同步工厂函数
    def sync_fetch():
        print("同步获取数据")
        return {"data": "value"}
    
    # 异步工厂函数
    async def async_fetch():
        print("异步获取数据")
        await asyncio.sleep(0.1)
        return {"data": "value"}
    
    # 使用同步工厂函数
    data1 = await cache.get_or_set("key1", sync_fetch, ttl=3600)
    print(data1)
    
    # 使用异步工厂函数
    data2 = await cache.get_or_set("key2", async_fetch, ttl=3600)
    print(data2)

asyncio.run(async_factory_example())
```

## 便捷函数

### 同步便捷函数

```python
from Modules.common.libs.cache import (
    sync_cache_get,
    sync_cache_set,
    sync_cache_delete,
    sync_cache_exists,
    sync_cache_get_or_set,
)

# 设置缓存
sync_cache_set("key", "value", ttl=3600)

# 获取缓存
value = sync_cache_get("key")

# 删除缓存
sync_cache_delete("key")

# 检查是否存在
exists = sync_cache_exists("key")

# 获取或设置
value = sync_cache_get_or_set("key", lambda: "default", ttl=3600)
```

### 异步便捷函数

```python
from Modules.common.libs.cache import (
    async_cache_get,
    async_cache_set,
    async_cache_delete,
    async_cache_exists,
    async_cache_get_or_set,
)
import asyncio

async def example():
    # 设置缓存
    await async_cache_set("key", "value", ttl=3600)
    
    # 获取缓存
    value = await async_cache_get("key")
    
    # 删除缓存
    await async_cache_delete("key")
    
    # 检查是否存在
    exists = await async_cache_exists("key")
    
    # 获取或设置
    value = await async_cache_get_or_set("key", lambda: "default", ttl=3600)

asyncio.run(example())
```

## 实际应用场景

### 1. 用户数据缓存

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio

class UserService:
    def __init__(self):
        self.cache = AsyncCacheService()
    
    async def get_user(self, user_id: int) -> dict | None:
        """获取用户信息（带缓存）"""
        cache_key = f"user:{user_id}"
        
        # 从缓存获取
        user = await self.cache.get(cache_key)
        if user:
            return user
        
        # 从数据库获取（模拟）
        user = await self._fetch_user_from_db(user_id)
        if user:
            # 缓存用户数据（1小时）
            await self.cache.set(cache_key, user, ttl=3600)
        
        return user
    
    async def _fetch_user_from_db(self, user_id: int) -> dict:
        """从数据库获取用户（模拟）"""
        # 实际项目中这里会查询数据库
        return {
            "id": user_id,
            "name": f"用户{user_id}",
            "email": f"user{user_id}@example.com"
        }
    
    async def update_user(self, user_id: int, data: dict) -> bool:
        """更新用户信息"""
        # 更新数据库（模拟）
        print(f"更新数据库用户 {user_id}")
        
        # 清除缓存
        cache_key = f"user:{user_id}"
        await self.cache.delete(cache_key)
        
        return True

# 使用示例
async def user_cache_example():
    service = UserService()
    
    # 第一次获取（从数据库）
    user = await service.get_user(123)
    print(f"用户: {user}")
    
    # 第二次获取（从缓存）
    user = await service.get_user(123)
    print(f"用户: {user}")
    
    # 更新用户（清除缓存）
    await service.update_user(123, {"name": "新名字"})
    
    # 再次获取（从数据库）
    user = await service.get_user(123)
    print(f"用户: {user}")

asyncio.run(user_cache_example())
```

### 2. API 响应缓存

```python
from fastapi import FastAPI, Depends
from Modules.common.libs.cache import AsyncCacheService
from functools import wraps
import json
import hashlib

app = FastAPI()

def cache_response(ttl: int = 300):
    """API 响应缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = AsyncCacheService()
            
            # 生成缓存键
            cache_key = f"api:{func.__name__}:{hashlib.md5(json.dumps(kwargs).encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

@app.get("/api/products")
@cache_response(ttl=600)
async def get_products():
    """获取产品列表（缓存10分钟）"""
    # 模拟数据库查询
    return [
        {"id": 1, "name": "产品1", "price": 100},
        {"id": 2, "name": "产品2", "price": 200},
    ]

@app.get("/api/products/{product_id}")
@cache_response(ttl=3600)
async def get_product(product_id: int):
    """获取产品详情（缓存1小时）"""
    # 模拟数据库查询
    return {"id": product_id, "name": f"产品{product_id}", "price": product_id * 100}
```

### 3. 计数器缓存

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio

class CounterService:
    def __init__(self):
        self.cache = AsyncCacheService()
    
    async def increment_view(self, article_id: int) -> int:
        """增加文章浏览次数"""
        cache_key = f"article:views:{article_id}"
        count = await self.cache.increment(cache_key)
        
        # 设置过期时间（1天）
        if count == 1:
            await self.cache.expire(cache_key, 86400)
        
        return count
    
    async def get_views(self, article_id: int) -> int:
        """获取文章浏览次数"""
        cache_key = f"article:views:{article_id}"
        count = await self.cache.get(cache_key, default=0)
        return count
    
    async def increment_daily_api_calls(self, user_id: int) -> int:
        """增加用户每日 API 调用次数"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"api_calls:{user_id}:{today}"
        
        count = await self.cache.increment(cache_key)
        
        # 设置过期时间（到当天结束）
        if count == 1:
            await self.cache.expire(cache_key, 86400)
        
        return count

# 使用示例
async def counter_example():
    service = CounterService()
    
    # 增加浏览次数
    views = await service.increment_view(123)
    print(f"浏览次数: {views}")  # 1
    
    views = await service.increment_view(123)
    print(f"浏览次数: {views}")  # 2
    
    # 获取浏览次数
    views = await service.get_views(123)
    print(f"总浏览次数: {views}")  # 2
    
    # API 调用计数
    calls = await service.increment_daily_api_calls(456)
    print(f"今日 API 调用: {calls}")  # 1

asyncio.run(counter_example())
```

### 4. 分布式锁

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio
import uuid

class DistributedLock:
    """分布式锁实现"""
    
    def __init__(self, lock_name: str, ttl: int = 30):
        self.cache = AsyncCacheService()
        self.lock_name = f"lock:{lock_name}"
        self.ttl = ttl
        self.identifier = str(uuid.uuid4())
    
    async def acquire(self) -> bool:
        """获取锁"""
        # 使用 setnx 实现原子性获取锁
        result = await self.cache.setnx(self.lock_name, self.identifier, ttl=self.ttl)
        return result
    
    async def release(self) -> bool:
        """释放锁"""
        # 检查是否是锁的持有者
        current_value = await self.cache.get(self.lock_name)
        if current_value == self.identifier:
            await self.cache.delete(self.lock_name)
            return True
        return False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        while not await self.acquire():
            await asyncio.sleep(0.1)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.release()

# 使用示例
async def distributed_lock_example():
    # 使用上下文管理器
    async with DistributedLock("resource_name", ttl=30) as lock:
        print("获取到锁，执行临界区代码")
        # 执行需要互斥的操作
        await asyncio.sleep(2)
        print("临界区代码执行完毕")
    
    # 手动获取和释放锁
    lock = DistributedLock("another_resource", ttl=30)
    if await lock.acquire():
        try:
            print("手动获取到锁，执行操作")
            # 执行操作
        finally:
            await lock.release()
            print("手动释放锁")

asyncio.run(distributed_lock_example())
```

### 5. 配置缓存

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio

class ConfigService:
    """配置服务（带缓存）"""
    
    def __init__(self):
        self.cache = AsyncCacheService()
    
    async def get_config(self, config_key: str) -> str | None:
        """获取配置值"""
        cache_key = f"config:{config_key}"
        
        # 从缓存获取
        value = await self.cache.get(cache_key)
        if value is not None:
            return value
        
        # 从数据库获取（模拟）
        value = await self._fetch_config_from_db(config_key)
        if value is not None:
            # 缓存配置（1小时）
            await self.cache.set(cache_key, value, ttl=3600)
        
        return value
    
    async def set_config(self, config_key: str, value: str) -> bool:
        """设置配置值"""
        # 更新数据库（模拟）
        print(f"更新数据库配置: {config_key} = {value}")
        
        # 更新缓存
        cache_key = f"config:{config_key}"
        await self.cache.set(cache_key, value, ttl=3600)
        
        return True
    
    async def clear_config_cache(self, config_key: str) -> bool:
        """清除配置缓存"""
        cache_key = f"config:{config_key}"
        await self.cache.delete(cache_key)
        return True
    
    async def _fetch_config_from_db(self, config_key: str) -> str | None:
        """从数据库获取配置（模拟）"""
        # 模拟配置数据
        configs = {
            "site_name": "我的网站",
            "site_description": "这是一个很棒的网站",
            "max_upload_size": "10485760",
        }
        return configs.get(config_key)

# 使用示例
async def config_example():
    service = ConfigService()
    
    # 获取配置（第一次从数据库）
    site_name = await service.get_config("site_name")
    print(f"网站名称: {site_name}")
    
    # 获取配置（从缓存）
    site_name = await service.get_config("site_name")
    print(f"网站名称: {site_name}")
    
    # 更新配置
    await service.set_config("site_name", "新网站名称")
    
    # 获取更新后的配置
    site_name = await service.get_config("site_name")
    print(f"网站名称: {site_name}")

asyncio.run(config_example())
```

### 6. 会话缓存

```python
from Modules.common.libs.cache import AsyncCacheService
import uuid
from datetime import datetime
import asyncio

class SessionService:
    """会话服务"""
    
    def __init__(self):
        self.cache = AsyncCacheService()
        self.session_ttl = 1800  # 30分钟
    
    async def create_session(self, user_id: int, user_data: dict) -> str:
        """创建会话"""
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            **user_data
        }
        
        # 存储会话数据
        await self.cache.set(session_key, session_data, ttl=self.session_ttl)
        
        return session_id
    
    async def get_session(self, session_id: str) -> dict | None:
        """获取会话"""
        session_key = f"session:{session_id}"
        session_data = await self.cache.get(session_key)
        
        if session_data:
            # 更新最后访问时间
            session_data["last_accessed"] = datetime.now().isoformat()
            await self.cache.set(session_key, session_data, ttl=self.session_ttl)
            return session_data
        
        return None
    
    async def destroy_session(self, session_id: str) -> bool:
        """销毁会话"""
        session_key = f"session:{session_id}"
        await self.cache.delete(session_key)
        return True
    
    async def refresh_session(self, session_id: str) -> bool:
        """刷新会话"""
        session_key = f"session:{session_id}"
        exists = await self.cache.exists(session_key)
        if exists:
            await self.cache.expire(session_key, self.session_ttl)
            return True
        return False

# 使用示例
async def session_example():
    service = SessionService()
    
    # 创建会话
    session_id = await service.create_session(
        user_id=123,
        user_data={"name": "张三", "role": "admin"}
    )
    print(f"创建会话: {session_id}")
    
    # 获取会话
    session = await service.get_session(session_id)
    print(f"会话数据: {session}")
    
    # 刷新会话
    await service.refresh_session(session_id)
    print("会话已刷新")
    
    # 销毁会话
    await service.destroy_session(session_id)
    print("会话已销毁")

asyncio.run(session_example())
```

## 最佳实践

### 1. 合理设置 TTL

根据数据的更新频率和业务需求设置合适的 TTL：

```python
# 静态数据（如配置）：较长的 TTL
await cache.set("config:theme", "dark", ttl=3600)  # 1小时

# 动态数据（如用户信息）：中等 TTL
await cache.set("user:123", user_data, ttl=1800)  # 30分钟

# 实时数据（如计数器）：较短 TTL 或不设置 TTL
await cache.set("counter:views", count, ttl=60)  # 1分钟
```

### 2. 使用键名前缀

使用键名前缀避免键名冲突，便于管理和清理：

```python
# 在配置中设置前缀
# config/cache.py
key_prefix: str = "myapp_cache_"

# 实际键名会自动添加前缀
cache.set("user:123", data)  # 实际键: myapp_cache_user:123
```

### 3. 使用 get_or_set 模式

使用 `get_or_set` 模式简化缓存逻辑，避免缓存穿透：

```python
# 不推荐：手动检查缓存
def get_user(user_id):
    user = cache.get(f"user:{user_id}")
    if user is None:
        user = db.query_user(user_id)
        cache.set(f"user:{user_id}", user)
    return user

# 推荐：使用 get_or_set
def get_user(user_id):
    return cache.get_or_set(
        f"user:{user_id}",
        lambda: db.query_user(user_id),
        ttl=3600
    )
```

### 4. 批量操作优化

对于多个键的操作，使用批量方法提高性能：

```python
# 不推荐：多次单独操作
for user_id in user_ids:
    user = await cache.get(f"user:{user_id}")

# 推荐：批量获取
users = await cache.get_many([f"user:{uid}" for uid in user_ids])
```

### 5. 错误处理

缓存操作应该有适当的错误处理和降级策略：

```python
from Modules.common.libs.cache import AsyncCacheService
from loguru import logger

async def safe_cache_get(key: str, default=None):
    """安全的缓存获取"""
    try:
        cache = AsyncCacheService()
        return await cache.get(key, default=default)
    except Exception as e:
        logger.error(f"缓存获取失败 - key: {key}, error: {e}")
        return default

async def safe_cache_set(key: str, value, ttl: int = 3600) -> bool:
    """安全的缓存设置"""
    try:
        cache = AsyncCacheService()
        return await cache.set(key, value, ttl=ttl)
    except Exception as e:
        logger.error(f"缓存设置失败 - key: {key}, error: {e}")
        return False
```

### 6. 缓存更新策略

根据业务需求选择合适的缓存更新策略：

```python
# 策略1：Cache-Aside（旁路缓存）
# 读取时先查缓存，未命中则查数据库并写入缓存
async def get_user(user_id):
    user = await cache.get(f"user:{user_id}")
    if user is None:
        user = await db.query_user(user_id)
        if user:
            await cache.set(f"user:{user_id}", user, ttl=3600)
    return user

# 策略2：Write-Through（写穿透）
# 写入时同时更新缓存和数据库
async def update_user(user_id, data):
    await db.update_user(user_id, data)
    await cache.set(f"user:{user_id}", data, ttl=3600)

# 策略3：Write-Behind（写回）
# 写入时只更新缓存，异步更新数据库
async def update_user(user_id, data):
    await cache.set(f"user:{user_id}", data, ttl=3600)
    asyncio.create_task(db.update_user(user_id, data))

# 策略4：失效策略
# 更新时删除缓存，下次读取时重新加载
async def update_user(user_id, data):
    await db.update_user(user_id, data)
    await cache.delete(f"user:{user_id}")
```

### 7. 监控和日志

添加适当的监控和日志记录：

```python
from Modules.common.libs.cache import AsyncCacheService
from loguru import logger
import time

async def monitored_cache_get(key: str, default=None):
    """带监控的缓存获取"""
    cache = AsyncCacheService()
    
    start_time = time.time()
    try:
        value = await cache.get(key, default=default)
        elapsed = time.time() - start_time
        
        logger.info(f"缓存GET成功 - key: {key}, 耗时: {elapsed:.4f}s, 命中: {value is not None}")
        return value
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"缓存GET失败 - key: {key}, 耗时: {elapsed:.4f}s, 错误: {e}")
        return default
```

## 常见问题

### Q: 如何处理缓存雪崩？

A: 缓存雪崩是指大量缓存同时失效，导致大量请求直接访问数据库。解决方案：

```python
import random

async def get_data_with_random_ttl(key: str):
    """使用随机 TTL 避免缓存雪崩"""
    cache = AsyncCacheService()
    
    # 基础 TTL 加上随机时间（如 3600 ± 600 秒）
    base_ttl = 3600
    random_ttl = base_ttl + random.randint(-600, 600)
    
    return await cache.get_or_set(
        key,
        lambda: fetch_data_from_db(key),
        ttl=random_ttl
    )
```

### Q: 如何处理缓存穿透？

A: 缓存穿透是指查询不存在的数据，导致请求直接访问数据库。解决方案：

```python
async def get_user_with_cache_penetration_protection(user_id: int):
    """防止缓存穿透"""
    cache = AsyncCacheService()
    cache_key = f"user:{user_id}"
    
    # 从缓存获取
    user = await cache.get(cache_key)
    if user is not None:
        # 检查是否是空值标记
        if user == "__NULL__":
            return None
        return user
    
    # 从数据库获取
    user = await db.query_user(user_id)
    
    if user is None:
        # 缓存空值标记（较短的 TTL）
        await cache.set(cache_key, "__NULL__", ttl=60)
    else:
        # 缓存实际数据
        await cache.set(cache_key, user, ttl=3600)
    
    return user
```

### Q: 如何处理缓存击穿？

A: 缓存击穿是指热点数据过期时，大量请求同时访问数据库。解决方案：

```python
from Modules.common.libs.cache import AsyncCacheService
import asyncio

async def get_hot_data_with_lock(key: str):
    """使用分布式锁防止缓存击穿"""
    cache = AsyncCacheService()
    lock_key = f"lock:{key}"
    
    # 尝试获取锁
    lock_acquired = await cache.setnx(lock_key, "1", ttl=10)
    
    if lock_acquired:
        # 获取到锁，从数据库加载数据
        try:
            data = await fetch_data_from_db(key)
            await cache.set(key, data, ttl=3600)
            return data
        finally:
            # 释放锁
            await cache.delete(lock_key)
    else:
        # 未获取到锁，等待并重试
        await asyncio.sleep(0.1)
        data = await cache.get(key)
        if data is not None:
            return data
        # 递归重试
        return await get_hot_data_with_lock(key)
```

### Q: 如何实现多级缓存？

A: 多级缓存可以结合内存缓存和 Redis 缓存：

```python
from Modules.common.libs.cache import AsyncCacheService
from functools import lru_cache
import asyncio

class MultiLevelCache:
    """多级缓存实现"""
    
    def __init__(self):
        self.redis_cache = AsyncCacheService()
        self.memory_cache = {}
    
    @lru_cache(maxsize=1000)
    def _get_from_memory(self, key: str):
        """从内存缓存获取"""
        return self.memory_cache.get(key)
    
    def _set_to_memory(self, key: str, value):
        """设置到内存缓存"""
        self.memory_cache[key] = value
    
    async def get(self, key: str):
        """多级缓存获取"""
        # L1: 内存缓存
        value = self._get_from_memory(key)
        if value is not None:
            return value
        
        # L2: Redis 缓存
        value = await self.redis_cache.get(key)
        if value is not None:
            self._set_to_memory(key, value)
            return value
        
        return None
    
    async def set(self, key: str, value, ttl: int = 3600):
        """多级缓存设置"""
        # 设置到内存缓存
        self._set_to_memory(key, value)
        
        # 设置到 Redis 缓存
        await self.redis_cache.set(key, value, ttl=ttl)
    
    async def delete(self, key: str):
        """多级缓存删除"""
        # 从内存缓存删除
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # 从 Redis 缓存删除
        await self.redis_cache.delete(key)
```

### Q: 如何监控缓存性能？

A: 可以通过日志和统计信息监控缓存性能：

```python
from Modules.common.libs.cache import AsyncCacheService
from collections import defaultdict
from loguru import logger
import time

class CacheMonitor:
    """缓存监控"""
    
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "hits": 0,
            "misses": 0,
            "total_time": 0,
            "count": 0
        })
    
    async def get(self, key: str, default=None):
        """带监控的缓存获取"""
        cache = AsyncCacheService()
        
        start_time = time.time()
        value = await cache.get(key, default=default)
        elapsed = time.time() - start_time
        
        # 更新统计信息
        stats = self.stats["get"]
        stats["total_time"] += elapsed
        stats["count"] += 1
        
        if value is not None and value != default:
            stats["hits"] += 1
            logger.info(f"缓存命中 - key: {key}, 耗时: {elapsed:.4f}s")
        else:
            stats["misses"] += 1
            logger.info(f"缓存未命中 - key: {key}, 耗时: {elapsed:.4f}s")
        
        return value
    
    def get_stats(self):
        """获取统计信息"""
        result = {}
        for operation, stats in self.stats.items():
            total_requests = stats["hits"] + stats["misses"]
            hit_rate = stats["hits"] / total_requests if total_requests > 0 else 0
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            
            result[operation] = {
                "hits": stats["hits"],
                "misses": stats["misses"],
                "hit_rate": f"{hit_rate:.2%}",
                "avg_time": f"{avg_time:.4f}s",
                "total_requests": total_requests
            }
        
        return result

# 使用示例
async def monitor_example():
    monitor = CacheMonitor()
    
    # 执行一些缓存操作
    await monitor.get("key1")
    await monitor.get("key1")
    await monitor.get("key2")
    
    # 获取统计信息
    stats = monitor.get_stats()
    print(stats)

asyncio.run(monitor_example())
```

## API 参考

### SyncCacheService 类方法

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `get(key, default=None)` | 获取缓存值 | 缓存值或默认值 |
| `set(key, value, ttl=None)` | 设置缓存值 | bool |
| `setnx(key, value, ttl=None)` | 原子设置缓存值（仅当键不存在时） | bool |
| `delete(key)` | 删除缓存 | bool |
| `exists(key)` | 检查缓存是否存在 | bool |
| `expire(key, ttl)` | 设置缓存过期时间 | bool |
| `ttl(key)` | 获取缓存剩余过期时间 | int |
| `get_many(keys)` | 批量获取缓存值 | dict |
| `set_many(mapping, ttl=None)` | 批量设置缓存值 | bool |
| `delete_many(keys)` | 批量删除缓存 | int |
| `get_or_set(key, factory, ttl=None)` | 获取或设置缓存 | Any |
| `increment(key, delta=1)` | 递增缓存值 | int |
| `decrement(key, delta=1)` | 递减缓存值 | int |
| `clear()` | 清空所有缓存 | bool |
| `keys(pattern="*")` | 获取匹配模式的键列表 | list |

### AsyncCacheService 类方法

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `get(key, default=None)` | 获取缓存值（异步） | Any |
| `set(key, value, ttl=None)` | 设置缓存值（异步） | bool |
| `delete(key)` | 删除缓存（异步） | bool |
| `exists(key)` | 检查缓存是否存在（异步） | bool |
| `expire(key, ttl)` | 设置缓存过期时间（异步） | bool |
| `ttl(key)` | 获取缓存剩余过期时间（异步） | int |
| `get_many(keys)` | 批量获取缓存值（异步） | dict |
| `set_many(mapping, ttl=None)` | 批量设置缓存值（异步） | bool |
| `delete_many(keys)` | 批量删除缓存（异步） | int |
| `get_or_set(key, factory, ttl=None)` | 获取或设置缓存（异步） | Any |
| `increment(key, delta=1)` | 递增缓存值（异步） | int |
| `decrement(key, delta=1)` | 递减缓存值（异步） | int |
| `clear()` | 清空所有缓存（异步） | bool |
| `keys(pattern="*")` | 获取匹配模式的键列表（异步） | list |

### 全局函数

| 函数 | 描述 |
|------|------|
| `get_sync_cache_service()` | 获取同步缓存服务实例（单例） |
| `get_async_cache_service()` | 获取异步缓存服务实例（单例） |

### 同步便捷函数

| 函数 | 描述 |
|------|------|
| `sync_cache_get(key, default=None)` | 获取缓存值 |
| `sync_cache_set(key, value, ttl=None)` | 设置缓存值 |
| `sync_cache_setnx(key, value, ttl=None)` | 原子设置缓存值 |
| `sync_cache_delete(key)` | 删除缓存 |
| `sync_cache_exists(key)` | 检查缓存是否存在 |
| `sync_cache_expire(key, ttl)` | 设置缓存过期时间 |
| `sync_cache_ttl(key)` | 获取缓存剩余过期时间 |
| `sync_cache_get_many(keys)` | 批量获取缓存值 |
| `sync_cache_set_many(mapping, ttl=None)` | 批量设置缓存值 |
| `sync_cache_delete_many(keys)` | 批量删除缓存 |
| `sync_cache_increment(key, delta=1)` | 递增缓存值 |
| `sync_cache_decrement(key, delta=1)` | 递减缓存值 |
| `sync_cache_clear()` | 清空所有缓存 |
| `sync_cache_keys(pattern="*")` | 获取匹配模式的键列表 |
| `sync_cache_get_or_set(key, factory, ttl=None)` | 获取或设置缓存 |

### 异步便捷函数

| 函数 | 描述 |
|------|------|
| `async_cache_get(key, default=None)` | 获取缓存值（异步） |
| `async_cache_set(key, value, ttl=None)` | 设置缓存值（异步） |
| `async_cache_delete(key)` | 删除缓存（异步） |
| `async_cache_exists(key)` | 检查缓存是否存在（异步） |
| `async_cache_expire(key, ttl)` | 设置缓存过期时间（异步） |
| `async_cache_ttl(key)` | 获取缓存剩余过期时间（异步） |
| `async_cache_get_many(keys)` | 批量获取缓存值（异步） |
| `async_cache_set_many(mapping, ttl=None)` | 批量设置缓存值（异步） |
| `async_cache_delete_many(keys)` | 批量删除缓存（异步） |
| `async_cache_increment(key, delta=1)` | 递增缓存值（异步） |
| `async_cache_decrement(key, delta=1)` | 递减缓存值（异步） |
| `async_cache_clear()` | 清空所有缓存（异步） |
| `async_cache_keys(pattern="*")` | 获取匹配模式的键列表（异步） |
| `async_cache_get_or_set(key, factory, ttl=None)` | 获取或设置缓存（异步） |

## 版本历史

- v1.0.0: 初始版本，提供基本的缓存服务功能
- v1.1.0: 添加批量操作和原子操作支持
- v1.2.0: 增强错误处理和日志记录
- v1.3.0: 添加工厂函数模式和便捷函数
