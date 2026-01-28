"""
缓存服务类

提供统一的缓存操作接口，基于 Redis 和内存实现。
支持同步和异步操作，提供类型安全、错误处理和日志记录。
"""

import asyncio
import json
from collections.abc import Callable
from typing import Any

from loguru import logger

from ..config import Config
from ..database.redis.client import get_async_redis_client, get_redis_client


class _BaseCacheService:
    """
    缓存服务基类

    提供通用的缓存操作逻辑，支持序列化和键名前缀处理。
    """

    def __init__(self):
        """
        初始化缓存服务
        """
        self._config_loaded = False
        self._default_ttl: int = 3600
        self._key_prefix: str = ""
        self._connection_name: str = "cache"

    def _init_config(self) -> None:
        """初始化配置"""
        if not self._config_loaded:
            try:
                self._default_ttl = Config.get("cache.default_ttl", 3600)
                self._key_prefix = Config.get("cache.key_prefix", "")
                self._connection_name = Config.get("cache.connection", "cache")
                self._config_loaded = True
            except Exception as e:
                logger.error(f"缓存配置加载失败 - error: {e}")
                raise ValueError("缓存配置加载失败") from e

    def _build_key(self, key: str) -> str:
        """
        构建完整的缓存键

        Args:
            key: 原始键名

        Returns:
            带前缀的完整键名
        """
        if self._key_prefix:
            return f"{self._key_prefix}{key}"
        return key

    def _serialize(self, value: Any) -> str:
        """
        序列化值

        Args:
            value: 要序列化的值

        Returns:
            序列化后的字符串
        """
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        return json.dumps(value, ensure_ascii=False)

    def _deserialize(self, value: str | bytes | None) -> Any:
        """
        反序列化值

        Args:
            value: 要反序列化的值

        Returns:
            反序列化后的值
        """
        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        # 尝试解析为 JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # 如果不是 JSON，直接返回字符串
            return value


class SyncCacheService(_BaseCacheService):
    """
    同步缓存服务类

    提供同步的缓存操作接口，基于 Redis 实现。
    支持类型安全、错误处理和日志记录。

    主要功能：
    - 封装 Redis 的底层操作
    - 提供类型安全的缓存方法
    - 统一的错误处理和日志记录
    - 支持序列化和反序列化

    使用示例：
        service = SyncCacheService()
        service.set("foo", "bar", ttl=60)
        value = service.get("foo")
    """

    def __init__(self):
        """
        初始化同步缓存服务
        """
        super().__init__()
        self._redis_client: Any = None

    def _get_redis_client(self) -> Any:
        """获取 Redis 客户端（延迟初始化）"""
        if self._redis_client is None:
            self._init_config()
            self._redis_client = get_redis_client(self._connection_name)

        return self._redis_client

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值，当缓存不存在时返回

        Returns:
            缓存值或默认值
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            value = client.get(full_key)
            return self._deserialize(value) if value is not None else default
        except Exception as e:
            logger.error(f"获取缓存失败 - key: {key}, error: {e}")
            return default

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            是否设置成功
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            serialized_value = self._serialize(value)

            if ttl is None:
                ttl = self._default_ttl

            client.setex(full_key, ttl, serialized_value)
            logger.debug(f"设置缓存成功 - key: {key}, ttl: {ttl}")
            return True
        except Exception as e:
            logger.error(f"设置缓存失败 - key: {key}, error: {e}")
            return False

    def setnx(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        设置缓存值（仅当键不存在时设置，原子操作）

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            是否设置成功（True表示键不存在并设置成功，False表示键已存在）
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            serialized_value = self._serialize(value)

            if ttl is None:
                ttl = self._default_ttl

            # 使用 setnx 实现原子性设置
            result = client.setnx(full_key, serialized_value)
            if result:
                # 设置成功，设置过期时间
                client.expire(full_key, ttl)
                logger.debug(f"原子设置缓存成功 - key: {key}, ttl: {ttl}")
            else:
                logger.debug(f"键已存在，跳过设置 - key: {key}")
            return result
        except Exception as e:
            logger.error(f"原子设置缓存失败 - key: {key}, error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            client.delete(full_key)
            logger.debug(f"删除缓存成功 - key: {key}")
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 - key: {key}, error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            缓存是否存在
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            return bool(client.exists(full_key))
        except Exception as e:
            logger.error(f"检查缓存存在性失败 - key: {key}, error: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间

        Args:
            key: 缓存键
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            client.expire(full_key, ttl)
            logger.debug(f"设置缓存过期时间成功 - key: {key}, ttl: {ttl}")
            return True
        except Exception as e:
            logger.error(f"设置缓存过期时间失败 - key: {key}, error: {e}")
            return False

    def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间

        Args:
            key: 缓存键

        Returns:
            剩余过期时间（秒），-1 表示永不过期，-2 表示键不存在
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            return client.ttl(full_key)
        except Exception as e:
            logger.error(f"获取缓存 TTL 失败 - key: {key}, error: {e}")
            return -2

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """
        批量获取缓存值

        Args:
            keys: 缓存键列表

        Returns:
            缓存键值字典
        """
        try:
            client = self._get_redis_client()
            full_keys = [self._build_key(key) for key in keys]
            values = client.mget(full_keys)

            result = {}
            for key, value in zip(keys, values, strict=True):
                if value is not None:
                    result[key] = self._deserialize(value)

            logger.debug(f"批量获取缓存成功 - keys: {keys}")
            return result
        except Exception as e:
            logger.error(f"批量获取缓存失败 - keys: {keys}, error: {e}")
            return {}

    def set_many(self, mapping: dict[str, Any], ttl: int | None = None) -> bool:
        """
        批量设置缓存值

        Args:
            mapping: 键值字典
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            是否全部设置成功
        """
        try:
            client = self._get_redis_client()

            if ttl is None:
                ttl = self._default_ttl

            # Redis 的 mset 不支持设置 TTL，需要逐个设置
            for key, value in mapping.items():
                full_key = self._build_key(key)
                serialized_value = self._serialize(value)
                client.setex(full_key, ttl, serialized_value)

            logger.debug(f"批量设置缓存成功 - keys: {list(mapping.keys())}, ttl: {ttl}")
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败 - keys: {list(mapping.keys())}, error: {e}")
            return False

    def delete_many(self, keys: list[str]) -> int:
        """
        批量删除缓存

        Args:
            keys: 缓存键列表

        Returns:
            成功删除的数量
        """
        try:
            client = self._get_redis_client()
            full_keys = [self._build_key(key) for key in keys]
            result = client.delete(*full_keys)
            logger.debug(f"批量删除缓存成功 - keys: {keys}, 删除数量: {result}")
            return result
        except Exception as e:
            logger.error(f"批量删除缓存失败 - keys: {keys}, error: {e}")
            return 0

    def get_or_set(self, key: str, factory: Callable, ttl: int | None = None) -> Any:
        """
        获取缓存值，如果不存在则通过工厂函数生成并设置

        Args:
            key: 缓存键
            factory: 值工厂函数（同步函数）
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            缓存值
        """
        try:
            # 先尝试从缓存获取
            value = self.get(key)
            if value is not None:
                return value

            # 缓存不存在，调用工厂函数
            value = factory()

            # 设置缓存
            self.set(key, value, ttl=ttl)
            return value
        except Exception as e:
            logger.error(f"获取或设置缓存失败 - key: {key}, error: {e}")
            # 降级：直接调用工厂函数
            try:
                return factory()
            except Exception as factory_error:
                logger.error(f"工厂函数执行失败 - key: {key}, error: {factory_error}")
                return None

    def increment(self, key: str, delta: int = 1) -> int:
        """
        递增缓存值（仅适用于数值类型）

        Args:
            key: 缓存键
            delta: 递增量，默认为 1

        Returns:
            递增后的值
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            return client.incrby(full_key, delta)
        except Exception as e:
            logger.error(f"递增缓存失败 - key: {key}, delta: {delta}, error: {e}")
            return 0

    def decrement(self, key: str, delta: int = 1) -> int:
        """
        递减缓存值（仅适用于数值类型）

        Args:
            key: 缓存键
            delta: 递减量，默认为 1

        Returns:
            递减后的值
        """
        try:
            client = self._get_redis_client()
            full_key = self._build_key(key)
            return client.decrby(full_key, delta)
        except Exception as e:
            logger.error(f"递减缓存失败 - key: {key}, delta: {delta}, error: {e}")
            return 0

    def clear(self) -> bool:
        """
        清空所有缓存

        Returns:
            是否清空成功
        """
        try:
            client = self._get_redis_client()
            if self._key_prefix:
                # 只删除带前缀的键
                pattern = f"{self._key_prefix}*"
                keys = client.keys(pattern)
                if keys:
                    client.delete(*keys)
            else:
                # 清空整个数据库（慎用）
                client.flushdb()

            logger.info(f"清空缓存成功 - connection: {self._connection_name}")
            return True
        except Exception as e:
            logger.error(
                f"清空缓存失败 - connection: {self._connection_name}, error: {e}"
            )
            return False

    def keys(self, pattern: str = "*") -> list[str]:
        """
        获取匹配模式的键列表

        Args:
            pattern: 键匹配模式，默认为 "*"

        Returns:
            键列表
        """
        try:
            client = self._get_redis_client()
            if self._key_prefix:
                pattern = f"{self._key_prefix}{pattern}"
            full_keys = client.keys(pattern)
            # 移除前缀返回原始键名
            if self._key_prefix:
                prefix_len = len(self._key_prefix)
                return [key[prefix_len:] for key in full_keys]
            return full_keys
        except Exception as e:
            logger.error(f"获取键列表失败 - pattern: {pattern}, error: {e}")
            return []


class AsyncCacheService(_BaseCacheService):
    """
    异步缓存服务类

    提供异步的缓存操作接口，基于 Redis 实现。
    支持类型安全、错误处理和日志记录。

    主要功能：
    - 封装 Redis 的底层操作
    - 提供类型安全的缓存方法
    - 统一的错误处理和日志记录
    - 支持序列化和反序列化

    使用示例：
        service = AsyncCacheService()
        await service.set("foo", "bar", ttl=60)
        value = await service.get("foo")
    """

    def __init__(self):
        """
        初始化异步缓存服务
        """
        super().__init__()
        self._redis_client: Any = None

    async def _get_redis_client(self) -> Any:
        """获取 Redis 客户端（延迟初始化）"""
        if self._redis_client is None:
            self._init_config()
            self._redis_client = get_async_redis_client(self._connection_name)

        return self._redis_client

    async def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值，当缓存不存在时返回

        Returns:
            缓存值或默认值
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            value = await client.get(full_key)
            return self._deserialize(value) if value is not None else default
        except Exception as e:
            logger.error(f"获取缓存失败 - key: {key}, error: {e}")
            return default

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            是否设置成功
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            serialized_value = self._serialize(value)

            if ttl is None:
                ttl = self._default_ttl

            await client.setex(full_key, ttl, serialized_value)
            logger.debug(f"设置缓存成功 - key: {key}, ttl: {ttl}")
            return True
        except Exception as e:
            logger.error(f"设置缓存失败 - key: {key}, error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            await client.delete(full_key)
            logger.debug(f"删除缓存成功 - key: {key}")
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 - key: {key}, error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            缓存是否存在
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            return bool(await client.exists(full_key))
        except Exception as e:
            logger.error(f"检查缓存存在性失败 - key: {key}, error: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间

        Args:
            key: 缓存键
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            await client.expire(full_key, ttl)
            logger.debug(f"设置缓存过期时间成功 - key: {key}, ttl: {ttl}")
            return True
        except Exception as e:
            logger.error(f"设置缓存过期时间失败 - key: {key}, error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间

        Args:
            key: 缓存键

        Returns:
            剩余过期时间（秒），-1 表示永不过期，-2 表示键不存在
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            return await client.ttl(full_key)
        except Exception as e:
            logger.error(f"获取缓存 TTL 失败 - key: {key}, error: {e}")
            return -2

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """
        批量获取缓存值

        Args:
            keys: 缓存键列表

        Returns:
            缓存键值字典
        """
        try:
            client = await self._get_redis_client()
            full_keys = [self._build_key(key) for key in keys]
            values = await client.mget(full_keys)

            result = {}
            for key, value in zip(keys, values, strict=True):
                if value is not None:
                    result[key] = self._deserialize(value)

            logger.debug(f"批量获取缓存成功 - keys: {keys}")
            return result
        except Exception as e:
            logger.error(f"批量获取缓存失败 - keys: {keys}, error: {e}")
            return {}

    async def set_many(self, mapping: dict[str, Any], ttl: int | None = None) -> bool:
        """
        批量设置缓存值

        Args:
            mapping: 键值字典
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            是否全部设置成功
        """
        try:
            client = await self._get_redis_client()

            if ttl is None:
                ttl = self._default_ttl

            # Redis 的 mset 不支持设置 TTL，需要逐个设置
            for key, value in mapping.items():
                full_key = self._build_key(key)
                serialized_value = self._serialize(value)
                await client.setex(full_key, ttl, serialized_value)

            logger.debug(f"批量设置缓存成功 - keys: {list(mapping.keys())}, ttl: {ttl}")
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败 - keys: {list(mapping.keys())}, error: {e}")
            return False

    async def delete_many(self, keys: list[str]) -> int:
        """
        批量删除缓存

        Args:
            keys: 缓存键列表

        Returns:
            成功删除的数量
        """
        try:
            client = await self._get_redis_client()
            full_keys = [self._build_key(key) for key in keys]
            result = await client.delete(*full_keys)
            logger.debug(f"批量删除缓存成功 - keys: {keys}, 删除数量: {result}")
            return result
        except Exception as e:
            logger.error(f"批量删除缓存失败 - keys: {keys}, error: {e}")
            return 0

    async def get_or_set(
        self, key: str, factory: Callable, ttl: int | None = None
    ) -> Any:
        """
        获取缓存值，如果不存在则通过工厂函数生成并设置

        Args:
            key: 缓存键
            factory: 值工厂函数，可以是同步或异步函数
            ttl: 过期时间（秒），None 表示使用默认过期时间

        Returns:
            缓存值
        """
        try:
            # 先尝试从缓存获取
            value = await self.get(key)
            if value is not None:
                return value

            # 缓存不存在，调用工厂函数
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()

            # 设置缓存
            await self.set(key, value, ttl=ttl)
            return value
        except Exception as e:
            logger.error(f"获取或设置缓存失败 - key: {key}, error: {e}")
            # 如果工厂函数是同步的，直接调用作为降级
            if not asyncio.iscoroutinefunction(factory):
                try:
                    return factory()
                except Exception as factory_error:
                    logger.error(
                        f"工厂函数执行失败 - key: {key}, error: {factory_error}"
                    )
            return None

    async def increment(self, key: str, delta: int = 1) -> int:
        """
        递增缓存值（仅适用于数值类型）

        Args:
            key: 缓存键
            delta: 递增量，默认为 1

        Returns:
            递增后的值
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            return await client.incrby(full_key, delta)
        except Exception as e:
            logger.error(f"递增缓存失败 - key: {key}, delta: {delta}, error: {e}")
            return 0

    async def decrement(self, key: str, delta: int = 1) -> int:
        """
        递减缓存值（仅适用于数值类型）

        Args:
            key: 缓存键
            delta: 递减量，默认为 1

        Returns:
            递减后的值
        """
        try:
            client = await self._get_redis_client()
            full_key = self._build_key(key)
            return await client.decrby(full_key, delta)
        except Exception as e:
            logger.error(f"递减缓存失败 - key: {key}, delta: {delta}, error: {e}")
            return 0

    async def clear(self) -> bool:
        """
        清空所有缓存

        Returns:
            是否清空成功
        """
        try:
            client = await self._get_redis_client()
            if self._key_prefix:
                # 只删除带前缀的键
                pattern = f"{self._key_prefix}*"
                keys = await client.keys(pattern)
                if keys:
                    await client.delete(*keys)
            else:
                # 清空整个数据库（慎用）
                await client.flushdb()

            logger.info(f"清空缓存成功 - connection: {self._connection_name}")
            return True
        except Exception as e:
            logger.error(
                f"清空缓存失败 - connection: {self._connection_name}, error: {e}"
            )
            return False

    async def keys(self, pattern: str = "*") -> list[str]:
        """
        获取匹配模式的键列表

        Args:
            pattern: 键匹配模式，默认为 "*"

        Returns:
            键列表
        """
        try:
            client = await self._get_redis_client()
            if self._key_prefix:
                pattern = f"{self._key_prefix}{pattern}"
            full_keys = await client.keys(pattern)
            # 移除前缀返回原始键名
            if self._key_prefix:
                prefix_len = len(self._key_prefix)
                return [key[prefix_len:] for key in full_keys]
            return full_keys
        except Exception as e:
            logger.error(f"获取键列表失败 - pattern: {pattern}, error: {e}")
            return []


# ==================== 全局实例和便捷函数 ====================

# 全局缓存服务实例
_sync_cache: SyncCacheService | None = None
_async_cache: AsyncCacheService | None = None


def get_sync_cache_service() -> SyncCacheService:
    """
    获取同步缓存服务实例（单例模式）

    Returns:
        同步缓存服务实例
    """
    global _sync_cache

    if _sync_cache is None:
        _sync_cache = SyncCacheService()
    return _sync_cache


def get_async_cache_service() -> AsyncCacheService:
    """
    获取异步缓存服务实例（单例模式）

    Returns:
        异步缓存服务实例
    """
    global _async_cache

    if _async_cache is None:
        _async_cache = AsyncCacheService()
    return _async_cache


# ==================== 同步便捷函数 ====================


def sync_cache_get(key: str, default: Any = None) -> Any:
    """便捷函数：获取缓存值（同步）"""
    service = get_sync_cache_service()
    return service.get(key, default)


def sync_cache_set(key: str, value: Any, ttl: int | None = None) -> bool:
    """便捷函数：设置缓存值（同步）"""
    service = get_sync_cache_service()
    return service.set(key, value, ttl)


def sync_cache_setnx(key: str, value: Any, ttl: int | None = None) -> bool:
    """便捷函数：原子设置缓存值（仅当键不存在时设置）"""
    service = get_sync_cache_service()
    return service.setnx(key, value, ttl)


def sync_cache_delete(key: str) -> bool:
    """便捷函数：删除缓存（同步）"""
    service = get_sync_cache_service()
    return service.delete(key)


def sync_cache_exists(key: str) -> bool:
    """便捷函数：检查缓存是否存在（同步）"""
    service = get_sync_cache_service()
    return service.exists(key)


def sync_cache_expire(key: str, ttl: int) -> bool:
    """便捷函数：设置缓存过期时间（同步）"""
    service = get_sync_cache_service()
    return service.expire(key, ttl)


def sync_cache_ttl(key: str) -> int:
    """便捷函数：获取缓存剩余过期时间（同步）"""
    service = get_sync_cache_service()
    return service.ttl(key)


def sync_cache_get_many(keys: list[str]) -> dict[str, Any]:
    """便捷函数：批量获取缓存值（同步）"""
    service = get_sync_cache_service()
    return service.get_many(keys)


def sync_cache_set_many(mapping: dict[str, Any], ttl: int | None = None) -> bool:
    """便捷函数：批量设置缓存值（同步）"""
    service = get_sync_cache_service()
    return service.set_many(mapping, ttl)


def sync_cache_delete_many(keys: list[str]) -> int:
    """便捷函数：批量删除缓存（同步）"""
    service = get_sync_cache_service()
    return service.delete_many(keys)


def sync_cache_increment(key: str, delta: int = 1) -> int:
    """便捷函数：递增缓存值（同步）"""
    service = get_sync_cache_service()
    return service.increment(key, delta)


def sync_cache_decrement(key: str, delta: int = 1) -> int:
    """便捷函数：递减缓存值（同步）"""
    service = get_sync_cache_service()
    return service.decrement(key, delta)


def sync_cache_clear() -> bool:
    """便捷函数：清空所有缓存（同步）"""
    service = get_sync_cache_service()
    return service.clear()


def sync_cache_keys(pattern: str = "*") -> list[str]:
    """便捷函数：获取匹配模式的键列表（同步）"""
    service = get_sync_cache_service()
    return service.keys(pattern)


def sync_cache_get_or_set(key: str, factory: Callable, ttl: int | None = None) -> Any:
    """便捷函数：获取或设置缓存（同步）"""
    service = get_sync_cache_service()
    return service.get_or_set(key, factory, ttl)


# ==================== 异步便捷函数 ====================


async def async_cache_get(key: str, default: Any = None) -> Any:
    """便捷函数：获取缓存值（异步）"""
    service = get_async_cache_service()
    return await service.get(key, default)


async def async_cache_set(
    key: str,
    value: Any,
    ttl: int | None = None,
) -> bool:
    """便捷函数：设置缓存值（异步）"""
    service = get_async_cache_service()
    return await service.set(key, value, ttl)


async def async_cache_delete(key: str) -> bool:
    """便捷函数：删除缓存（异步）"""
    service = get_async_cache_service()
    return await service.delete(key)


async def async_cache_exists(key: str) -> bool:
    """便捷函数：检查缓存是否存在（异步）"""
    service = get_async_cache_service()
    return await service.exists(key)


async def async_cache_expire(key: str, ttl: int) -> bool:
    """便捷函数：设置缓存过期时间（异步）"""
    service = get_async_cache_service()
    return await service.expire(key, ttl)


async def async_cache_ttl(key: str) -> int:
    """便捷函数：获取缓存剩余过期时间（异步）"""
    service = get_async_cache_service()
    return await service.ttl(key)


async def async_cache_get_many(keys: list[str]) -> dict[str, Any]:
    """便捷函数：批量获取缓存值（异步）"""
    service = get_async_cache_service()
    return await service.get_many(keys)


async def async_cache_set_many(mapping: dict[str, Any], ttl: int | None = None) -> bool:
    """便捷函数：批量设置缓存值（异步）"""
    service = get_async_cache_service()
    return await service.set_many(mapping, ttl)


async def async_cache_delete_many(keys: list[str]) -> int:
    """便捷函数：批量删除缓存（异步）"""
    service = get_async_cache_service()
    return await service.delete_many(keys)


async def async_cache_increment(key: str, delta: int = 1) -> int:
    """便捷函数：递增缓存值（异步）"""
    service = get_async_cache_service()
    return await service.increment(key, delta)


async def async_cache_decrement(key: str, delta: int = 1) -> int:
    """便捷函数：递减缓存值（异步）"""
    service = get_async_cache_service()
    return await service.decrement(key, delta)


async def async_cache_clear() -> bool:
    """便捷函数：清空所有缓存（异步）"""
    service = get_async_cache_service()
    return await service.clear()


async def async_cache_keys(pattern: str = "*") -> list[str]:
    """便捷函数：获取匹配模式的键列表（异步）"""
    service = get_async_cache_service()
    return await service.keys(pattern)


async def async_cache_get_or_set(
    key: str,
    factory: Callable,
    ttl: int | None = None,
) -> Any:
    """便捷函数：获取或设置缓存（异步）"""
    service = get_async_cache_service()
    return await service.get_or_set(key, factory, ttl)
