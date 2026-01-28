"""
缓存工具模块

提供分表相关的缓存工具类和函数。
"""

from loguru import logger

from ...cache import (
    sync_cache_delete,
    sync_cache_get,
    sync_cache_set,
    sync_cache_setnx,
)


class ShardingCacheManager:
    """
    分表缓存管理器

    提供分表相关的缓存操作，包括表存在性缓存和分布式锁。
    """

    def __init__(self, cache_ttl=300, lock_timeout=60):
        """
        初始化缓存管理器

        Args:
            cache_ttl: 缓存生存时间(秒)，默认300秒
            lock_timeout: 锁超时时间(秒)，默认60秒
        """
        self.cache_ttl = cache_ttl
        self.lock_timeout = lock_timeout
        self.cache_prefix = "sharding:table_exists:"
        self.lock_prefix = "sharding:lock:"

    def _check_cache_available(self):
        """检查缓存模块是否可用"""
        return sync_cache_get is not None

    # ==================== Redis 操作方法 ====================

    def cache_get(self, key):
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或失败返回None
        """
        if not self._check_cache_available():
            return None

        try:
            return sync_cache_get(key)
        except Exception as e:
            logger.warning(f"获取缓存失败: key={key}, 错误: {e}")
            return None

    def cache_set(self, key, value, ttl=None):
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒)，默认使用 cache_ttl

        Returns:
            bool: 是否成功
        """
        if not self._check_cache_available():
            return False

        try:
            if ttl is None:
                ttl = self.cache_ttl
            sync_cache_set(key, value, ttl=ttl)
            return True
        except Exception as e:
            logger.warning(f"设置缓存失败: key={key}, 错误: {e}")
            return False

    def cache_delete(self, key):
        """
        删除缓存值

        Args:
            key: 缓存键

        Returns:
            bool: 是否成功
        """
        if not self._check_cache_available():
            return False

        try:
            sync_cache_delete(key)
            return True
        except Exception as e:
            logger.warning(f"删除缓存失败: key={key}, 错误: {e}")
            return False

    def cache_setnx(self, key, value, ttl=None):
        """
        设置缓存值（仅当键不存在时）

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒)，默认使用 lock_timeout

        Returns:
            bool: 是否成功设置（True表示设置成功，False表示键已存在或失败）
        """
        if not self._check_cache_available():
            return False

        try:
            if ttl is None:
                ttl = self.lock_timeout
            return sync_cache_setnx(key, value, ttl=ttl)
        except Exception as e:
            logger.warning(f"设置缓存失败: key={key}, 错误: {e}")
            return False

    # ==================== 缓存可用性检查 ====================

    def is_cache_available(self):
        """
        检查缓存是否可用

        Returns:
            bool: 缓存是否可用
        """
        if not self._check_cache_available():
            return False

        try:
            # 尝试设置和获取一个测试键
            test_key = "sharding:health_check"
            self.cache_set(test_key, "1", ttl=10)
            result = self.cache_get(test_key)
            # 如果能成功设置和获取,说明缓存可用
            return str(result) == "1" or result == 1
        except Exception as e:
            logger.warning(f"缓存不可用: {e}")
            return False

    # ==================== 表存在性缓存 ====================

    def check_table_exists_with_cache(self, table_name, check_db_func):
        """
        检查表是否存在(带缓存)

        Args:
            table_name: 表名
            check_db_func: 数据库检查函数,接收table_name参数,返回bool

        Returns:
            bool: 表是否存在
        """
        cache_key = f"{self.cache_prefix}{table_name}"

        # 如果缓存可用,先查缓存
        if self.is_cache_available():
            cached = self.cache_get(cache_key)
            if cached is not None:
                return str(cached) == "1" or cached == 1

        # 查询数据库
        exists = check_db_func(table_name)

        # 如果缓存可用,写入缓存
        if self.is_cache_available():
            self.cache_set(cache_key, "1" if exists else "0")

        return exists

    # ==================== 分布式锁 ====================

    def acquire_lock(self, table_name):
        """
        获取分布式锁

        Args:
            table_name: 表名

        Returns:
            bool: 是否成功获取锁
        """
        if not self.is_cache_available():
            return False

        lock_key = f"{self.lock_prefix}{table_name}"
        return self.cache_setnx(lock_key, "1", ttl=self.lock_timeout)

    def release_lock(self, table_name):
        """
        释放分布式锁

        Args:
            table_name: 表名

        Returns:
            bool: 是否成功释放锁
        """
        if not self.is_cache_available():
            return False

        lock_key = f"{self.lock_prefix}{table_name}"
        return self.cache_delete(lock_key)
