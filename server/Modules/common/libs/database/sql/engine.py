"""
数据库引擎管理

负责创建和管理数据库引擎，支持多种数据库类型和连接池配置。
"""

from typing import Any

from loguru import logger
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ...config import Config


class DatabaseEngineManager:
    """数据库引擎管理器类"""

    def __init__(self):
        """初始化数据库引擎管理器"""
        self._engines: dict[str, Engine] = {}
        self._async_engines: dict[str, AsyncEngine] = {}

    @staticmethod
    def _build_database_url(config: dict[str, Any]) -> str:
        """
        根据配置构建数据库连接 URL

        Args:
            config: 数据库配置字典

        Returns:
            str: 数据库连接 URL
        """
        # 如果提供了完整的 URL，直接使用
        if config.get("url"):
            return config["url"]

        # 否则根据配置构建 URL
        driver = config.get("driver", "mysql")
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 3306)
        database = config.get("database", "forge")
        username = config.get("username", "forge")
        password = config.get("password", "")

        # 构建基础 URL
        if driver == "mysql":
            # MySQL 使用 mysqlclient 驱动
            url = f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}"
        elif driver == "pgsql":
            # PostgreSQL
            url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
        elif driver == "sqlite":
            # SQLite
            url = f"sqlite:///{database}"
        elif driver == "sqlsrv":
            # SQL Server
            url = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库驱动: {driver}")

        # 添加额外参数
        params = []
        if driver == "mysql":
            charset = config.get("charset", "utf8mb4")
            params.append(f"charset={charset}")

            # 添加时区配置
            # try:
            #     timezone_str = Config.get("app.timezone", "Asia/Shanghai")
            #     if timezone_str == "Asia/Shanghai":
            #         params.append("time_zone='+08:00'")
            #     elif timezone_str == "UTC":
            #         params.append("time_zone='+00:00'")
            #     # 可以根据需要添加更多时区映射
            # except Exception as e:
            #     logger.warning(f"获取时区配置失败，跳过数据库时区设置: {e}")

        if params:
            url += "?" + "&".join(params)

        return url

    def init_db_engine(self) -> None:
        """
        初始化数据库引擎

        从配置中读取数据库连接信息，创建相应的数据库引擎。
        支持同步和异步两种引擎。
        """
        logger.info("正在初始化数据库引擎...")

        # 获取默认连接名称
        default_connection = Config.get("database.default")
        connections = Config.get("database.connections")

        # 获取数据库配置
        if not connections:
            logger.error("数据库配置不存在")
            return

        # 为每个连接创建引擎
        for name, config in connections.items():
            if default_connection != name:
                continue
            try:
                # 构建数据库 URL
                database_url = self._build_database_url(config)
                logger.info(f"正在创建数据库引擎 '{name}': {database_url}")

                # 创建同步引擎
                engine = create_engine(
                    database_url,
                    # 连接池配置
                    pool_size=config.get("pool_size", 10),
                    max_overflow=config.get("max_overflow", 20),
                    pool_timeout=config.get("pool_timeout", 30),
                    # 减少连接回收时间，避免MySQL服务器先关闭连接
                    pool_recycle=config.get("pool_recycle", 1800),  # 30分钟
                    # 启用连接预检查，在获取连接前测试连接有效性
                    pool_pre_ping=True,
                    # 其他配置
                    echo=config.get("echo", False),
                    future=True,
                )
                self._engines[name] = engine

                # 创建异步引擎
                # 对于异步引擎，需要使用相应的异步驱动
                async_url = database_url.replace("mysql+mysqldb", "mysql+aiomysql")
                async_url = async_url.replace(
                    "postgresql+asyncpg", "postgresql+asyncpg"
                )
                print(async_url)
                async_engine = create_async_engine(
                    async_url,
                    # 连接池配置
                    pool_size=config.get("pool_size", 10),
                    max_overflow=config.get("max_overflow", 20),
                    pool_timeout=config.get("pool_timeout", 30),
                    # 减少连接回收时间，避免MySQL服务器先关闭连接
                    pool_recycle=config.get("pool_recycle", 1800),  # 30分钟
                    # 启用连接预检查，在获取连接前测试连接有效性
                    pool_pre_ping=True,
                    # 其他配置
                    echo=True,
                )
                self._async_engines[name] = async_engine

                logger.info(f"数据库引擎 '{name}' 创建成功")

            except Exception as e:
                logger.error(f"创建数据库引擎 '{name}' 失败: {e}")
                continue

        logger.info("数据库引擎初始化完成")

    def get_db_engine(self, name: str | None = None) -> Engine:
        """
        获取数据库引擎（同步）

        Args:
            name: 连接名称，如果为 None 则使用默认连接

        Returns:
            Engine: 数据库引擎实例

        Raises:
            ValueError: 当指定的连接不存在时
        """
        if name is None:
            name = Config.get("database.default", "mysql")

        if name not in self._engines:
            raise ValueError(f"数据库引擎 '{name}' 不存在")

        return self._engines[name]

    def get_async_db_engine(self, name: str | None = None) -> AsyncEngine:
        """
        获取数据库引擎（异步）

        Args:
            name: 连接名称，如果为 None 则使用默认连接

        Returns:
            AsyncEngine: 异步数据库引擎实例

        Raises:
            ValueError: 当指定的连接不存在时
        """
        if name is None:
            name = Config.get("database.default", "mysql")

        if name not in self._async_engines:
            raise ValueError(f"异步数据库引擎 '{name}' 不存在")

        return self._async_engines[name]

    async def close_db_engine(self) -> None:
        """
        关闭所有数据库引擎

        释放所有数据库连接和连接池资源。
        这是一个异步方法，应在异步上下文中调用。
        """
        logger.info("正在关闭数据库引擎...")

        # 关闭同步引擎
        for name, engine in self._engines.items():
            try:
                engine.dispose()
                logger.info(f"同步数据库引擎 '{name}' 已关闭")
            except Exception as e:
                logger.error(f"关闭同步数据库引擎 '{name}' 失败: {e}")

        # 关闭异步引擎
        for name, engine in self._async_engines.items():
            try:
                # 对于异步引擎，直接使用 await
                await engine.dispose()
                logger.info(f"异步数据库引擎 '{name}' 已关闭")
            except Exception as e:
                logger.error(f"关闭异步数据库引擎 '{name}' 失败: {e}")

        # 清空引擎字典
        self._engines.clear()
        self._async_engines.clear()

        logger.info("数据库引擎关闭完成")

    def close_db_engine_sync(self) -> None:
        """
        关闭所有数据库引擎（同步版本）

        释放所有数据库连接和连接池资源。
        这是一个同步方法，可以在同步上下文中调用。
        """
        import asyncio

        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，创建一个任务
            loop.create_task(self.close_db_engine())
            logger.info("已在事件循环中创建关闭数据库引擎任务")
        except RuntimeError:
            # 没有运行的事件循环，可以直接运行
            asyncio.run(self.close_db_engine())
            logger.info("数据库引擎关闭完成（同步方式）")


# 全局数据库引擎管理器实例
db_engine_manager = DatabaseEngineManager()


# 为了保持向后兼容性，提供函数接口
def init_db_engine() -> None:
    """初始化数据库引擎（函数接口）"""
    return db_engine_manager.init_db_engine()


def get_db_engine(name: str | None = None) -> Engine:
    """获取数据库引擎（函数接口）"""
    return db_engine_manager.get_db_engine(name)


def get_async_db_engine(name: str | None = None) -> AsyncEngine:
    """获取异步数据库引擎（函数接口）"""
    return db_engine_manager.get_async_db_engine(name)


async def close_db_engine() -> None:
    """关闭数据库引擎（函数接口，异步）"""
    return await db_engine_manager.close_db_engine()


def close_db_engine_sync() -> None:
    """关闭数据库引擎（函数接口，同步）"""
    return db_engine_manager.close_db_engine_sync()
