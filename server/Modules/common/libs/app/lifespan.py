"""
FastAPI 应用生命周期管理
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..celery import get_celery_service
from ..config.registry import ConfigRegistry
from ..database import (
    close_db_engine,
    close_redis_clients,
    init_db_engine,
    init_redis_clients,
    init_session_maker,
)
from ..log import setup_logging
from ..time import init_timezone


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期入口

    启动顺序：
    1. 加载并校验所有配置
    2. 读取关键配置（确保可用）
    3. 初始化全局资源（日志 / DB / Redis）

    关闭顺序：
    1. 释放全局资源
    """

    # ------------------------------------------------------------------
    # 启动阶段
    # ------------------------------------------------------------------

    #  加载所有配置（只执行一次）
    ConfigRegistry.load()

    #  初始化日志（示例）
    setup_logging()

    #  初始化数据库 / Redis

    # 初始化数据库引擎
    init_db_engine()

    # 初始化数据库会话工厂
    init_session_maker()

    # 初始化 Redis 客户端
    init_redis_clients()

    # 初始化时区
    init_timezone()

    # 初始化并验证 Celery 连接
    celery_service = get_celery_service()
    await celery_service.verify_connection()

    # 将 Celery 附加到 FastAPI state
    celery_service.init_fastapi_celery(app)

    #  应用正式启动
    yield

    # ------------------------------------------------------------------
    # 关闭阶段
    # ------------------------------------------------------------------

    # 释放数据库连接

    # 关闭数据库引擎
    await close_db_engine()

    # 关闭 Redis 客户端
    await close_redis_clients()
