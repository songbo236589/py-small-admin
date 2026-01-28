"""
数据库模块

提供数据库和 Redis 的统一访问接口。
"""

# SQL 数据库相关
# Redis 相关
from .redis import (
    RedisClientManager,
    close_redis_clients,
    close_redis_clients_sync,
    get_async_redis_client,
    get_redis,
    get_redis_client,
    init_redis_clients,
    redis_manager,
)
from .sql import (
    close_db_engine,
    close_db_engine_sync,
    get_async_db_engine,
    get_async_session,
    get_async_session_maker,
    get_db_engine,
    get_db_session,
    get_session_maker,
    get_sync_session,
    init_db_engine,
    init_session_maker,
)

__all__ = [
    # SQL 数据库
    "init_db_engine",
    "get_db_engine",
    "get_async_db_engine",
    "close_db_engine",
    "close_db_engine_sync",
    "init_session_maker",
    "get_session_maker",
    "get_async_session_maker",
    "get_async_session",
    "get_db_session",
    "get_sync_session",
    # Redis
    "RedisClientManager",
    "redis_manager",
    "init_redis_clients",
    "get_redis_client",
    "get_async_redis_client",
    "get_redis",
    "close_redis_clients",
    "close_redis_clients_sync",
]
