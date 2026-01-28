"""
Redis 模块

提供 Redis 客户端管理和操作功能。
"""

from .client import (
    RedisClientManager,
    close_redis_clients,
    close_redis_clients_sync,
    get_async_redis_client,
    get_redis,
    get_redis_client,
    init_redis_clients,
    redis_manager,
)

__all__ = [
    # 客户端管理类
    "RedisClientManager",
    "redis_manager",
    # 便捷函数
    "init_redis_clients",
    "get_redis_client",
    "get_async_redis_client",
    "get_redis",
    "close_redis_clients",
    "close_redis_clients_sync",
]
