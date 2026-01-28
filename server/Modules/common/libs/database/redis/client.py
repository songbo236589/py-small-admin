"""
Redis 客户端管理类

负责创建和管理 Redis 连接，支持多个 Redis 实例和连接池配置。
"""

from typing import Any

from loguru import logger
from redis import Redis
from redis.asyncio import ConnectionPool
from redis.asyncio import Redis as AsyncRedis

from ...config import Config


class RedisClientManager:
    """
    Redis 客户端管理器

    负责管理多个 Redis 连接实例，支持同步和异步客户端。
    """

    def __init__(self) -> None:
        # 全局 Redis 客户端实例
        self._clients: dict[str, Redis] = {}
        self._async_clients: dict[str, AsyncRedis] = {}
        self._connection_pools: dict[str, ConnectionPool] = {}

    @staticmethod
    def _build_redis_url(config: dict[str, Any]) -> str:
        """
        根据配置构建 Redis 连接 URL

        Args:
            config: Redis 配置字典

        Returns:
            str: Redis 连接 URL
        """
        # 如果提供了完整的 URL，直接使用
        if config.get("url"):
            return config["url"]

        # 否则根据配置构建 URL
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 6379)
        username = config.get("username")
        password = config.get("password")
        database = config.get("database", 0)

        # 构建 URL（支持username，用于Redis 6.0+ ACL功能）
        if username and password:
            url = f"redis://{username}:{password}@{host}:{port}/{database}"
        elif password:
            url = f"redis://:{password}@{host}:{port}/{database}"
        else:
            url = f"redis://{host}:{port}/{database}"

        return url

    def init_clients(self) -> None:
        """
        初始化 Redis 客户端

        从配置中读取 Redis 连接信息，创建相应的 Redis 客户端。
        支持同步和异步两种客户端。
        """
        logger.info("正在初始化 Redis 客户端...")

        # 获取数据库配置
        redis_configs = Config.get("database.redis")
        # logger.info(f"获取到的 Redis 配置: {redis_configs}")
        if not redis_configs:
            logger.error("Redis 配置不存在")
            return

        # 为每个连接创建客户端
        for name, config in redis_configs.items():
            try:
                # 构建连接 URL
                redis_url = self._build_redis_url(config)
                logger.info(f"正在创建 Redis 客户端 '{name}': {redis_url}")

                # 连接池配置
                pool_kwargs = {
                    "host": config.get("host", "127.0.0.1"),
                    "port": config.get("port", 6379),
                    "db": config.get("database", 0),
                    "username": config.get("username"),
                    "password": config.get("password"),
                    "max_connections": config.get("max_connections", 50),
                    "retry_on_timeout": config.get("retry_on_timeout", True),
                    "socket_timeout": config.get("socket_timeout", 5),
                    "socket_connect_timeout": config.get("socket_connect_timeout", 5),
                    "health_check_interval": config.get("health_check_interval", 30),
                }

                # 创建异步连接池
                async_pool = ConnectionPool(**pool_kwargs)
                self._connection_pools[name] = async_pool

                # 创建同步客户端
                sync_client = Redis.from_url(redis_url)
                self._clients[name] = sync_client

                # 创建异步客户端
                async_client = AsyncRedis(connection_pool=async_pool)
                self._async_clients[name] = async_client

                logger.info(f"Redis 客户端 '{name}' 创建成功")

            except Exception as e:
                logger.error(f"创建 Redis 客户端 '{name}' 失败: {e}")
                continue

        logger.info("Redis 客户端初始化完成")

    def get_client(self, name: str = "default") -> Redis:
        """
        获取 Redis 客户端（同步）

        Args:
            name: 连接名称，默认为 "default"

        Returns:
            Redis: Redis 客户端实例

        Raises:
            ValueError: 当指定的连接不存在时
        """
        if name not in self._clients:
            raise ValueError(f"Redis 客户端 '{name}' 不存在")

        return self._clients[name]

    def get_async_client(self, name: str = "default") -> AsyncRedis:
        """
        获取 Redis 客户端（异步）

        Args:
            name: 连接名称，默认为 "default"

        Returns:
            AsyncRedis: 异步 Redis 客户端实例

        Raises:
            ValueError: 当指定的连接不存在时
        """
        if name not in self._async_clients:
            raise ValueError(f"异步 Redis 客户端 '{name}' 不存在")

        return self._async_clients[name]

    async def close_clients(self) -> None:
        """
        关闭所有 Redis 客户端

        释放所有 Redis 连接和连接池资源。
        这是一个异步方法，应在异步上下文中调用。
        """
        logger.info("正在关闭 Redis 客户端...")

        # 关闭同步客户端
        for name, client in self._clients.items():
            try:
                client.close()
                logger.info(f"同步 Redis 客户端 '{name}' 已关闭")
            except Exception as e:
                logger.error(f"关闭同步 Redis 客户端 '{name}' 失败: {e}")

        # 关闭异步客户端
        for name, client in self._async_clients.items():
            try:
                await client.close()
                logger.info(f"异步 Redis 客户端 '{name}' 已关闭")
            except Exception as e:
                logger.error(f"关闭异步 Redis 客户端 '{name}' 失败: {e}")

        # 关闭连接池
        for name, pool in self._connection_pools.items():
            try:
                await pool.disconnect()
                logger.info(f"Redis 连接池 '{name}' 已关闭")
            except Exception as e:
                logger.error(f"关闭 Redis 连接池 '{name}' 失败: {e}")

        # 清空客户端字典
        self._clients.clear()
        self._async_clients.clear()
        self._connection_pools.clear()

        logger.info("Redis 客户端关闭完成")

    def close_clients_sync(self) -> None:
        """
        关闭所有 Redis 客户端（同步版本）

        释放所有 Redis 连接和连接池资源。
        这是一个同步方法，可以在同步上下文中调用。
        """
        import asyncio

        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，创建一个任务
            loop.create_task(self.close_clients())
            logger.info("已在事件循环中创建关闭任务")
        except RuntimeError:
            # 没有运行的事件循环，可以直接运行
            asyncio.run(self.close_clients())
            logger.info("Redis 客户端关闭完成（同步方式）")


# 全局 Redis 客户端管理器实例
redis_manager = RedisClientManager()


# 便捷函数，直接使用全局管理器实例
def init_redis_clients() -> None:
    """初始化 Redis 客户端（便捷函数）"""
    redis_manager.init_clients()


def get_redis_client(name: str = "default") -> Redis:
    """获取 Redis 客户端（同步，便捷函数）"""
    return redis_manager.get_client(name)


def get_async_redis_client(name: str = "default") -> AsyncRedis:
    """获取 Redis 客户端（异步，便捷函数）"""
    return redis_manager.get_async_client(name)


async def close_redis_clients() -> None:
    """关闭 Redis 客户端（便捷函数，异步）"""
    await redis_manager.close_clients()


def close_redis_clients_sync() -> None:
    """关闭 Redis 客户端（便捷函数，同步）"""
    redis_manager.close_clients_sync()


# FastAPI 依赖注入
def get_redis(name: str = "default"):
    """
    FastAPI 依赖注入：获取异步 Redis 客户端

    Args:
        name: 连接名称，默认为 "default"

    Returns:
        AsyncRedis: 异步 Redis 客户端
    """
    return get_async_redis_client(name)
