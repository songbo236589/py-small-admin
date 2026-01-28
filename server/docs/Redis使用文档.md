# Redis 使用文档

## 概述

本项目中的 Redis 模块提供了完整的 Redis 客户端管理和操作功能，支持同步和异步操作，以及连接池管理。该模块基于 `redis-py` 库实现，封装了 Redis 连接的创建、管理和使用。

该模块主要包含以下文件：

- `Modules/common/libs/database/redis/client.py`: Redis 客户端管理类
- `Modules/common/libs/database/redis/__init__.py`: Redis 模块导出接口
- `config/database.py`: Redis 数据库配置类

## 主要功能

- 支持 Redis 客户端的创建和管理
- 同步和异步客户端支持
- 连接池管理和配置
- 多 Redis 实例支持
- 完整的连接参数配置
- FastAPI 依赖注入支持
- 资源管理和优雅关闭

## 安装与导入

```python
from Modules.common.libs.database.redis import (
    # 客户端管理类
    RedisClientManager,
    redis_manager,
    
    # 便捷函数
    init_redis_clients,
    get_redis_client,
    get_async_redis_client,
    get_redis,
    close_redis_clients,
)
```

## Redis 配置

### 基本配置

Redis 配置通过 `DatabaseConfig` 类管理，支持环境变量配置：

```python
from config.database import DatabaseConfig

# 获取数据库配置
config = DatabaseConfig()
redis_config = config.redis["default"]
print(redis_config)  # 默认 Redis 连接配置
```

### 环境变量配置

可以通过环境变量配置 Redis：

```bash
# Redis 基本配置
DB_REDIS__DEFAULT__HOST=127.0.0.1
DB_REDIS__DEFAULT__PORT=6379
DB_REDIS__DEFAULT__PASSWORD=mypassword
DB_REDIS__DEFAULT__DATABASE=0

# Redis 连接池配置
DB_REDIS__DEFAULT__MAX_CONNECTIONS=50
DB_REDIS__DEFAULT__RETRY_ON_TIMEOUT=true
DB_REDIS__DEFAULT__SOCKET_TIMEOUT=5
DB_REDIS__DEFAULT__SOCKET_CONNECT_TIMEOUT=5
DB_REDIS__DEFAULT__HEALTH_CHECK_INTERVAL=30

# Redis 键名前缀
DB_REDIS__DEFAULT__PREFIX=redis_default_
```

### 多实例配置

支持配置多个 Redis 实例：

```python
# config/database.py 中的配置示例
redis: dict[str, Any] = {
    "default": {
        "host": "127.0.0.1",
        "port": 6379,
        "database": 0,
        "password": None,
        "prefix": "redis_default_",
        "max_connections": 50,
    },
    "cache": {
        "host": "127.0.0.1",
        "port": 6379,
        "database": 1,
        "password": None,
        "prefix": "redis_cache_",
        "max_connections": 100,
    },
    "session": {
        "host": "127.0.0.1",
        "port": 6380,
        "database": 0,
        "password": "session_password",
        "prefix": "redis_session_",
        "max_connections": 20,
    },
}
```

## Redis 客户端管理

### RedisClientManager 类

`RedisClientManager` 是核心的 Redis 客户端管理器，负责创建和管理多个 Redis 连接实例。

#### 初始化 Redis 客户端

```python
from Modules.common.libs.database.redis import redis_manager

# 初始化所有 Redis 客户端
redis_manager.init_clients()

# 获取同步客户端
sync_client = redis_manager.get_client("default")

# 获取异步客户端
async_client = redis_manager.get_async_client("default")
```

#### 获取特定实例的客户端

```python
# 获取默认 Redis 客户端
default_client = redis_manager.get_client("default")
default_async_client = redis_manager.get_async_client("default")

# 获取缓存专用 Redis 客户端
cache_client = redis_manager.get_client("cache")
cache_async_client = redis_manager.get_async_client("cache")

# 获取会话专用 Redis 客户端
session_client = redis_manager.get_client("session")
session_async_client = redis_manager.get_async_client("session")
```

#### 关闭客户端

```python
# 关闭所有 Redis 客户端和连接池
redis_manager.close_clients()
```

## 便捷函数

模块提供了一系列便捷函数，简化 Redis 操作：

```python
from Modules.common.libs.database.redis import (
    init_redis_clients,
    get_redis_client,
    get_async_redis_client,
    get_redis,
    close_redis_clients,
)

# 初始化 Redis 客户端
init_redis_clients()

# 获取同步客户端
sync_client = get_redis_client("default")

# 获取异步客户端
async_client = get_async_redis_client("default")

# FastAPI 依赖注入方式获取异步客户端
# 在路由函数中使用:
# async def some_route(redis_client=Depends(get_redis)):
#     await redis_client.set("key", "value")

# 关闭所有客户端
close_redis_clients()
```

## 实际应用场景

### 1. 基本 Redis 操作

```python
from Modules.common.libs.database.redis import get_async_redis_client

async def basic_redis_operations():
    """基本 Redis 操作示例"""
    # 获取异步客户端
    redis_client = get_async_redis_client("default")
    
    # 设置键值
    await redis_client.set("user:1", "张三")
    
    # 获取值
    name = await redis_client.get("user:1")
    print(f"用户名: {name}")  # 用户名: 张三
    
    # 设置带过期时间的键值
    await redis_client.setex("session:abc123", 1800, "user_session_data")  # 30分钟过期
    
    # 检查键是否存在
    exists = await redis_client.exists("user:1")
    print(f"键是否存在: {exists}")  # 键是否存在: 1
    
    # 删除键
    deleted = await redis_client.delete("user:1")
    print(f"删除的键数量: {deleted}")  # 删除的键数量: 1
    
    # 设置哈希
    await redis_client.hset("profile:123", mapping={
        "name": "李四",
        "age": 30,
        "email": "lisi@example.com"
    })
    
    # 获取哈希字段
    name = await redis_client.hget("profile:123", "name")
    print(f"姓名: {name}")  # 姓名: 李四
    
    # 获取整个哈希
    profile = await redis_client.hgetall("profile:123")
    print(f"完整资料: {profile}")
```

### 2. 使用同步客户端

```python
from Modules.common.libs.database.redis import get_redis_client

def sync_redis_operations():
    """同步 Redis 操作示例"""
    # 获取同步客户端
    redis_client = get_redis_client("default")
    
    # 设置键值
    redis_client.set("counter:views", 0)
    
    # 递增计数器
    count = redis_client.incr("counter:views")
    print(f"访问次数: {count}")  # 访问次数: 1
    
    # 批量递增
    count = redis_client.incrby("counter:views", 10)
    print(f"访问次数: {count}")  # 访问次数: 11
    
    # 操作列表
    redis_client.lpush("recent_users", "user1", "user2", "user3")
    users = redis_client.lrange("recent_users", 0, -1)
    print(f"最近用户: {users}")
    
    # 操作集合
    redis_client.sadd("online_users", "user1", "user2", "user3")
    is_online = redis_client.sismember("online_users", "user2")
    print(f"user2 是否在线: {is_online}")
```

### 3. 缓存应用

```python
from Modules.common.libs.database.redis import get_async_redis_client
import json
import asyncio

async def cache_user_data(user_id: int, user_data: dict, ttl: int = 3600):
    """缓存用户数据"""
    redis_client = get_async_redis_client("cache")
    cache_key = f"user:{user_id}"
    
    # 将字典序列化为 JSON 字符串
    serialized_data = json.dumps(user_data)
    
    # 设置缓存
    await redis_client.setex(cache_key, ttl, serialized_data)

async def get_cached_user_data(user_id: int):
    """获取缓存的用户数据"""
    redis_client = get_async_redis_client("cache")
    cache_key = f"user:{user_id}"
    
    # 获取缓存数据
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        # 反序列化 JSON 字符串
        return json.loads(cached_data)
    
    return None

# 使用示例
async def example_usage():
    user_id = 123
    user_data = {
        "id": user_id,
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 30
    }
    
    # 缓存用户数据（1小时）
    await cache_user_data(user_id, user_data, ttl=3600)
    
    # 获取缓存数据
    cached_user = await get_cached_user_data(user_id)
    print(f"缓存用户数据: {cached_user}")
```

### 4. 会话管理

```python
from Modules.common.libs.database.redis import get_async_redis_client
import uuid
import json
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.redis_client = get_async_redis_client("session")
        self.session_ttl = 1800  # 30分钟
    
    async def create_session(self, user_id: int, user_data: dict) -> str:
        """创建用户会话"""
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            **user_data
        }
        
        # 存储会话数据
        await self.redis_client.setex(
            session_key, 
            self.session_ttl, 
            json.dumps(session_data)
        )
        
        return session_id
    
    async def get_session(self, session_id: str) -> dict | None:
        """获取会话数据"""
        session_key = f"session:{session_id}"
        session_data = await self.redis_client.get(session_key)
        
        if session_data:
            # 更新最后访问时间
            session = json.loads(session_data)
            session["last_accessed"] = datetime.now().isoformat()
            await self.redis_client.setex(
                session_key,
                self.session_ttl,
                json.dumps(session)
            )
            return session
        
        return None
    
    async def destroy_session(self, session_id: str) -> bool:
        """销毁会话"""
        session_key = f"session:{session_id}"
        result = await self.redis_client.delete(session_key)
        return result > 0

# 使用示例
async def session_example():
    session_manager = SessionManager()
    
    # 创建会话
    session_id = await session_manager.create_session(
        user_id=123,
        user_data={"name": "张三", "role": "admin"}
    )
    print(f"创建会话: {session_id}")
    
    # 获取会话
    session = await session_manager.get_session(session_id)
    print(f"会话数据: {session}")
    
    # 销毁会话
    success = await session_manager.destroy_session(session_id)
    print(f"会话销毁: {success}")
```

### 5. 分布式锁

```python
from Modules.common.libs.database.redis import get_async_redis_client
import asyncio
import uuid

class DistributedLock:
    def __init__(self, name: str, ttl: int = 10):
        self.name = name
        self.ttl = ttl
        self.redis_client = get_async_redis_client("default")
        self.identifier = str(uuid.uuid4())
        self.lock_key = f"lock:{name}"
    
    async def acquire(self) -> bool:
        """获取锁"""
        # 使用 SET NX EX 原子操作获取锁
        result = await self.redis_client.set(
            self.lock_key,
            self.identifier,
            ex=self.ttl,
            nx=True
        )
        return result is not None
    
    async def release(self) -> bool:
        """释放锁"""
        # 使用 Lua 脚本确保只有锁的持有者才能释放锁
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await self.redis_client.eval(lua_script, 1, self.lock_key, self.identifier)
        return result == 1
    
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
```

### 6. 限流器

```python
from Modules.common.libs.database.redis import get_async_redis_client
import time

class RateLimiter:
    def __init__(self, key_prefix: str = "rate_limit"):
        self.redis_client = get_async_redis_client("default")
        self.key_prefix = key_prefix
    
    async def is_allowed(
        self, 
        identifier: str, 
        limit: int, 
        window: int
    ) -> tuple[bool, int]:
        """
        检查是否允许请求
        
        Args:
            identifier: 标识符（如用户ID、IP地址）
            limit: 限制次数
            window: 时间窗口（秒）
            
        Returns:
            (是否允许, 当前计数)
        """
        key = f"{self.key_prefix}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window
        
        # 使用有序集合记录请求时间
        await self.redis_client.zadd(key, {str(current_time): current_time})
        
        # 移除时间窗口外的记录
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # 获取当前时间窗口内的请求数
        current_count = await self.redis_client.zcard(key)
        
        # 设置键的过期时间
        await self.redis_client.expire(key, window)
        
        # 检查是否超过限制
        if current_count > limit:
            return False, current_count
        
        return True, current_count

# 使用示例
async def rate_limiter_example():
    rate_limiter = RateLimiter()
    
    user_id = "user123"
    
    # 检查用户是否可以在1分钟内请求10次
    for i in range(12):
        allowed, count = await rate_limiter.is_allowed(user_id, limit=10, window=60)
        print(f"请求 {i+1}: {'允许' if allowed else '拒绝'}, 当前计数: {count}")
        
        if not allowed:
            print("请求过于频繁，请稍后再试")
            break
```

### 7. FastAPI 集成

```python
from fastapi import FastAPI, Depends, HTTPException
from Modules.common.libs.database.redis import get_redis
from typing import Annotated

app = FastAPI()

# 依赖注入类型别名
RedisDep = Annotated[AsyncRedis, Depends(get_redis)]

@app.get("/api/cache/{key}")
async def get_cache(key: str, redis: RedisDep):
    """获取缓存值"""
    value = await redis.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="缓存键不存在")
    return {"key": key, "value": value}

@app.post("/api/cache/{key}")
async def set_cache(key: str, value: str, redis: RedisDep, ttl: int = 3600):
    """设置缓存值"""
    await redis.setex(key, ttl, value)
    return {"key": key, "value": value, "ttl": ttl}

@app.delete("/api/cache/{key}")
async def delete_cache(key: str, redis: RedisDep):
    """删除缓存值"""
    deleted = await redis.delete(key)
    if not deleted:
        raise HTTPException(status_code=404, detail="缓存键不存在")
    return {"key": key, "deleted": True}

@app.get("/api/stats")
async def get_stats(redis: RedisDep):
    """获取 Redis 统计信息"""
    info = await redis.info()
    return {
        "used_memory": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
        "total_commands_processed": info.get("total_commands_processed"),
    }
```

## 最佳实践

### 1. 连接池配置

根据应用需求合理配置连接池参数：

```python
# 在 config/database.py 中配置
redis: dict[str, Any] = {
    "default": {
        "host": "127.0.0.1",
        "port": 6379,
        "database": 0,
        # 连接池配置
        "max_connections": 50,  # 最大连接数
        "retry_on_timeout": True,  # 超时重试
        "socket_timeout": 5,  # 套接字超时
        "socket_connect_timeout": 5,  # 连接超时
        "health_check_interval": 30,  # 健康检查间隔
    },
}
```

### 2. 键命名规范

使用有意义的命名规范，便于管理和调试：

```python
# 推荐的键命名规范
"user:{user_id}"                    # 用户数据
"session:{session_id}"              # 用户会话
"cache:{type}:{id}"                 # 缓存数据
"lock:{resource_name}"              # 分布式锁
"rate_limit:{identifier}"            # 限流计数器
"counter:{counter_name}"            # 计数器
"queue:{queue_name}"                # 队列
"config:{config_name}"              # 配置数据
```

### 3. 错误处理

合理处理 Redis 操作中的异常：

```python
from Modules.common.libs.database.redis import get_async_redis_client
from redis.exceptions import RedisError
from loguru import logger

async def safe_redis_operation():
    """安全的 Redis 操作示例"""
    redis_client = get_async_redis_client("default")
    
    try:
        # 执行 Redis 操作
        await redis_client.set("key", "value")
        value = await redis_client.get("key")
        return value
    except RedisError as e:
        logger.error(f"Redis 操作失败: {e}")
        # 根据业务需求进行降级处理
        return None
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise
```

### 4. 资源管理

确保在应用关闭时正确释放 Redis 资源：

```python
from Modules.common.libs.database.redis import init_redis_clients, close_redis_clients
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时初始化 Redis 客户端
    init_redis_clients()
    yield
    # 应用关闭时释放 Redis 客户端
    close_redis_clients()

app = FastAPI(lifespan=lifespan)
```

### 5. 监控和日志

添加适当的监控和日志记录：

```python
from Modules.common.libs.database.redis import get_async_redis_client
from loguru import logger
import time

async def monitored_redis_get(key: str):
    """带监控的 Redis 获取操作"""
    redis_client = get_async_redis_client("default")
    
    start_time = time.time()
    try:
        value = await redis_client.get(key)
        elapsed = time.time() - start_time
        
        logger.info(f"Redis GET 操作成功 - key: {key}, 耗时: {elapsed:.4f}s")
        return value
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Redis GET 操作失败 - key: {key}, 耗时: {elapsed:.4f}s, 错误: {e}")
        raise
```

## 常见问题

### Q: 如何处理 Redis 连接超时？

A: 可以通过调整连接池参数来处理连接超时：

```python
# 在配置中增加超时设置
redis: dict[str, Any] = {
    "default": {
        "host": "127.0.0.1",
        "port": 6379,
        "socket_timeout": 10,  # 增加套接字超时时间
        "socket_connect_timeout": 10,  # 增加连接超时时间
        "retry_on_timeout": True,  # 启用超时重试
    },
}
```

### Q: 如何实现 Redis 高可用？

A: 可以使用 Redis Sentinel 或 Redis Cluster：

```python
# Sentinel 配置示例
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('sentinel1', 26379),
    ('sentinel2', 26379),
    ('sentinel3', 26379),
])

master = sentinel.master_for('mymaster', socket_timeout=0.1)
slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
```

### Q: 如何处理大数据量？

A: 对于大数据量，可以考虑以下策略：

1. 使用分片存储
2. 实现数据压缩
3. 使用 Redis 的流数据结构
4. 考虑使用 Redis 的模块（如 RedisJSON）

```python
import gzip
import json

async def store_large_data(key: str, data: dict):
    """存储大数据（压缩存储）"""
    redis_client = get_async_redis_client("default")
    
    # 序列化并压缩数据
    serialized = json.dumps(data).encode('utf-8')
    compressed = gzip.compress(serialized)
    
    # 存储压缩后的数据
    await redis_client.set(key, compressed)

async def get_large_data(key: str) -> dict:
    """获取大数据（解压缩）"""
    redis_client = get_async_redis_client("default")
    
    # 获取压缩数据
    compressed = await redis_client.get(key)
    if not compressed:
        return None
    
    # 解压缩并反序列化
    decompressed = gzip.decompress(compressed)
    return json.loads(decompressed.decode('utf-8'))
```

### Q: 如何监控 Redis 性能？

A: 可以通过以下方式监控 Redis 性能：

1. 使用 Redis 的 INFO 命令获取统计信息
2. 监控慢查询日志
3. 使用监控工具（如 Redis Exporter + Prometheus）

```python
async def get_redis_stats():
    """获取 Redis 统计信息"""
    redis_client = get_async_redis_client("default")
    
    # 获取基本信息
    info = await redis_client.info()
    
    # 获取慢查询日志
    slow_log = await redis_client.slowlog_get(10)  # 获取最近10条慢查询
    
    return {
        "memory_usage": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
        "total_commands": info.get("total_commands_processed"),
        "keyspace_hits": info.get("keyspace_hits", 0),
        "keyspace_misses": info.get("keyspace_misses", 0),
        "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)),
        "slow_log": slow_log,
    }
```

## API 参考

### RedisClientManager 类方法

| 方法 | 描述 |
|------|------|
| `init_clients()` | 初始化所有 Redis 客户端 |
| `get_client(name="default")` | 获取同步 Redis 客户端 |
| `get_async_client(name="default")` | 获取异步 Redis 客户端 |
| `close_clients()` | 关闭所有 Redis 客户端和连接池 |

### 便捷函数

| 函数 | 描述 |
|------|------|
| `init_redis_clients()` | 初始化 Redis 客户端（便捷函数） |
| `get_redis_client(name="default")` | 获取同步 Redis 客户端（便捷函数） |
| `get_async_redis_client(name="default")` | 获取异步 Redis 客户端（便捷函数） |
| `get_redis(name="default")` | FastAPI 依赖注入：获取异步 Redis 客户端 |
| `close_redis_clients()` | 关闭 Redis 客户端（便捷函数） |

### 配置参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `host` | Redis 服务器地址 | 127.0.0.1 |
| `port` | Redis 服务器端口 | 6379 |
| `password` | Redis 认证密码 | None |
| `database` | Redis 数据库编号 | 0 |
| `prefix` | 键名前缀 | redis_default_ |
| `max_connections` | 连接池最大连接数 | 50 |
| `retry_on_timeout` | 连接超时是否重试 | True |
| `socket_timeout` | 套接字超时时间（秒） | 5 |
| `socket_connect_timeout` | 套接字连接超时时间（秒） | 5 |
| `health_check_interval` | 健康检查间隔（秒） | 30 |

## 版本历史

- v1.0.0: 初始版本，提供基本的 Redis 客户端管理功能
- v1.1.0: 添加多实例支持和连接池配置
- v1.2.0: 增强错误处理和资源管理
- v1.3.0: 添加 FastAPI 依赖注入支持