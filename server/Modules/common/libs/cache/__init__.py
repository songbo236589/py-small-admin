"""
缓存模块

提供统一的缓存操作接口，支持同步和异步操作。
基于 Redis 实现，提供类型安全、错误处理和日志记录。
"""

from .cache import (
    # 服务类
    AsyncCacheService,
    SyncCacheService,
    # 异步便捷函数
    async_cache_clear,
    async_cache_decrement,
    async_cache_delete,
    async_cache_delete_many,
    async_cache_exists,
    async_cache_expire,
    async_cache_get,
    async_cache_get_many,
    async_cache_get_or_set,
    async_cache_increment,
    async_cache_keys,
    async_cache_set,
    async_cache_set_many,
    async_cache_ttl,
    # 服务获取函数
    get_async_cache_service,
    get_sync_cache_service,
    # 同步便捷函数
    sync_cache_clear,
    sync_cache_decrement,
    sync_cache_delete,
    sync_cache_delete_many,
    sync_cache_exists,
    sync_cache_expire,
    sync_cache_get,
    sync_cache_get_many,
    sync_cache_get_or_set,
    sync_cache_increment,
    sync_cache_keys,
    sync_cache_set,
    sync_cache_set_many,
    sync_cache_setnx,
    sync_cache_ttl,
)

# 导出主要接口
__all__ = [
    # 服务类
    "SyncCacheService",
    "AsyncCacheService",
    # 服务获取函数
    "get_sync_cache_service",
    "get_async_cache_service",
    # 同步便捷函数
    "sync_cache_get",
    "sync_cache_set",
    "sync_cache_setnx",
    "sync_cache_delete",
    "sync_cache_exists",
    "sync_cache_expire",
    "sync_cache_ttl",
    "sync_cache_get_many",
    "sync_cache_set_many",
    "sync_cache_delete_many",
    "sync_cache_increment",
    "sync_cache_decrement",
    "sync_cache_clear",
    "sync_cache_keys",
    "sync_cache_get_or_set",
    # 异步便捷函数
    "async_cache_get",
    "async_cache_set",
    "async_cache_delete",
    "async_cache_exists",
    "async_cache_expire",
    "async_cache_ttl",
    "async_cache_get_many",
    "async_cache_set_many",
    "async_cache_delete_many",
    "async_cache_increment",
    "async_cache_decrement",
    "async_cache_clear",
    "async_cache_keys",
    "async_cache_get_or_set",
]
