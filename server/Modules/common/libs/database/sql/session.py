"""
数据库会话管理

负责创建和管理数据库会话，提供上下文管理器和依赖注入支持。
"""

import asyncio
import time
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from fastapi import Depends
from loguru import logger
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

from .engine import get_async_db_engine, get_db_engine


class DatabaseSessionManager:
    """数据库会话管理器类"""

    def __init__(self):
        """初始化数据库会话管理器"""
        self._session_maker: dict[str, sessionmaker[Session]] = {}
        self._async_session_maker: dict[str, async_sessionmaker[AsyncSession]] = {}

    def init_session_maker(self) -> None:
        """
        初始化会话工厂

        为每个数据库引擎创建对应的会话工厂。
        """
        logger.info("正在初始化数据库会话工厂...")

        # 获取默认连接名称
        from ...config import Config

        default_connection = Config.get("database.default", "mysql")

        # 为默认连接创建会话工厂
        try:
            # 同步会话工厂
            engine = get_db_engine(default_connection)
            self._session_maker[default_connection] = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
                future=True,
            )

            # 异步会话工厂
            async_engine = get_async_db_engine(default_connection)
            self._async_session_maker[default_connection] = async_sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            logger.info(f"数据库会话工厂 '{default_connection}' 初始化成功")

        except Exception as e:
            logger.error(f"初始化数据库会话工厂 '{default_connection}' 失败: {e}")

    def get_session_maker(self, name: str | None = None) -> sessionmaker[Session]:
        """
        获取会话工厂（同步）

        Args:
            name: 连接名称，如果为 None 则使用默认连接

        Returns:
            sessionmaker: 会话工厂实例

        Raises:
            ValueError: 当指定的连接不存在时
        """
        if name is None:
            from ...config import Config

            name = Config.get("database.default", "mysql")

        if name not in self._session_maker:
            raise ValueError(f"会话工厂 '{name}' 不存在")

        return self._session_maker[name]

    def get_async_session_maker(
        self,
        name: str | None = None,
    ) -> async_sessionmaker[AsyncSession]:
        """
        获取会话工厂（异步）

        Args:
            name: 连接名称，如果为 None 则使用默认连接

        Returns:
            async_sessionmaker: 异步会话工厂实例

        Raises:
            ValueError: 当指定的连接不存在时
        """
        if name is None:
            from ...config import Config

            name = Config.get("database.default", "mysql")

        if name not in self._async_session_maker:
            raise ValueError(f"异步会话工厂 '{name}' 不存在")

        return self._async_session_maker[name]

    @asynccontextmanager
    async def get_async_session(
        self,
        name: str | None = None,
        max_retries: int = 2,
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        获取异步数据库会话（上下文管理器）

        Args:
            name: 连接名称，如果为 None 则使用默认连接
            max_retries: 最大重试次数，默认为2次

        Yields:
            AsyncSession: 异步数据库会话
        """
        session_maker = self.get_async_session_maker(name)
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                async with session_maker() as session:
                    try:
                        yield session
                        await session.commit()
                        return  # 成功执行，退出函数
                    except (DisconnectionError, OperationalError) as e:
                        await session.rollback()
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(
                                f"数据库连接异常，正在重试 ({attempt + 1}/{max_retries + 1}): {e}"
                            )
                            # 等待一段时间再重试
                            await asyncio.sleep(0.5 * (attempt + 1))
                            continue
                        else:
                            logger.error(f"数据库会话异常，已达到最大重试次数: {e}")
                            raise
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"数据库会话异常: {e}")
                        raise
                    finally:
                        await session.close()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(
                        f"获取数据库会话失败，正在重试 ({attempt + 1}/{max_retries + 1}): {e}"
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    logger.error(f"获取数据库会话失败，已达到最大重试次数: {e}")
                    raise

        # 如果所有重试都失败了，抛出最后一个异常
        if last_exception:
            raise last_exception

    def get_db_session(
        self,
        name: str | None = None,
        max_retries: int = 2,
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI 依赖注入：获取异步数据库会话

        Args:
            name: 连接名称，如果为 None 则使用默认连接
            max_retries: 最大重试次数，默认为2次

        Returns:
            AsyncGenerator[AsyncSession, None]: 异步数据库会话
        """

        async def _get_session() -> AsyncGenerator[AsyncSession, None]:
            async with self.get_async_session(name, max_retries) as session:
                yield session

        return Depends(_get_session)

    @contextmanager
    def get_sync_session(
        self, name: str | None = None, max_retries: int = 2
    ) -> Generator[Session, None, None]:
        """
        获取同步数据库会话（上下文管理器）

        Args:
            name: 连接名称，如果为 None 则使用默认连接
            max_retries: 最大重试次数，默认为2次

        Yields:
            Session: 同步数据库会话
        """
        session_maker = self.get_session_maker(name)
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                with session_maker() as session:
                    try:
                        yield session
                        session.commit()
                        return  # 成功执行，退出函数
                    except (DisconnectionError, OperationalError) as e:
                        session.rollback()
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(
                                f"数据库连接异常，正在重试 ({attempt + 1}/{max_retries + 1}): {e}"
                            )
                            # 等待一段时间再重试
                            time.sleep(0.5 * (attempt + 1))
                            continue
                        else:
                            logger.error(f"数据库会话异常，已达到最大重试次数: {e}")
                            raise
                    except Exception as e:
                        session.rollback()
                        logger.error(f"数据库会话异常: {e}")
                        raise
                    finally:
                        session.close()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(
                        f"获取数据库会话失败，正在重试 ({attempt + 1}/{max_retries + 1}): {e}"
                    )
                    time.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    logger.error(f"获取数据库会话失败，已达到最大重试次数: {e}")
                    raise

        # 如果所有重试都失败了，抛出最后一个异常
        if last_exception:
            raise last_exception


# 全局数据库会话管理器实例
db_session_manager = DatabaseSessionManager()


# 为了保持向后兼容性，提供函数接口
def init_session_maker() -> None:
    """初始化会话工厂（函数接口）"""
    return db_session_manager.init_session_maker()


def get_session_maker(name: str | None = None) -> sessionmaker[Session]:
    """获取会话工厂（函数接口）"""
    return db_session_manager.get_session_maker(name)


def get_async_session_maker(
    name: str | None = None,
) -> async_sessionmaker[AsyncSession]:
    """获取异步会话工厂（函数接口）"""
    return db_session_manager.get_async_session_maker(name)


@asynccontextmanager
async def get_async_session(
    name: str | None = None,
    max_retries: int = 2,
) -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话（函数接口）"""
    async with db_session_manager.get_async_session(name, max_retries) as session:
        yield session


def get_db_session(
    name: str | None = None, max_retries: int = 2
) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：获取异步数据库会话（函数接口）"""
    return db_session_manager.get_db_session(name, max_retries)


@contextmanager
def get_sync_session(
    name: str | None = None, max_retries: int = 2
) -> Generator[Session, None, None]:
    """获取同步数据库会话（函数接口）"""
    with db_session_manager.get_sync_session(name, max_retries) as session:
        yield session
