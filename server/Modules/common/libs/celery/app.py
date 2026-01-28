"""
Celery 应用实例

供 Celery CLI 使用的应用实例入口

使用示例:
    # 启动 Worker
    celery -A Modules.common.libs.celery.app worker --loglevel=info

    # 启动 Beat (定时任务)
    celery -A Modules.common.libs.celery.app beat --loglevel=info

    # 启动 Flower (监控)
    celery -A Modules.common.libs.celery.app flower

    # 查看已注册的任务
    celery -A Modules.common.libs.celery.app inspect registered

    # 查看定时任务配置
    celery -A Modules.common.libs.celery.app inspect beat
"""

# Celery Worker 启动时需要初始化数据库等资源
# 这里执行与 FastAPI 应用相同的初始化流程

# 导入所有需要的模块
import asyncio
import atexit
import signal
import sys

from celery.signals import worker_shutdown

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
from .celery_service import get_celery_service

# 按顺序执行初始化
# 1. 加载所有配置
ConfigRegistry.load()

# 2. 初始化日志
setup_logging()

# 3. 初始化数据库引擎
init_db_engine()

# 4. 初始化数据库会话工厂
init_session_maker()

# 5. 初始化 Redis 客户端
init_redis_clients()

# 6. 初始化时区
init_timezone()

# 7. 创建 Celery 应用实例供 CLI 使用
celery = get_celery_service().app


# 8. 注册 Celery Worker 退出时的资源清理函数
def cleanup_resources():
    """
    Celery Worker 退出时的资源清理函数

    关闭数据库连接和 Redis 客户端，避免资源泄漏
    """
    try:
        # 获取当前事件循环
        loop = asyncio.get_event_loop()

        # 如果事件循环未关闭，则执行清理
        if not loop.is_closed():
            # 关闭数据库引擎
            loop.run_until_complete(close_db_engine())

            # 关闭 Redis 客户端
            loop.run_until_complete(close_redis_clients())

    except Exception:
        # 捕获异常，避免清理失败影响 Worker 退出
        import traceback

        traceback.print_exc()


# 注册 worker_shutdown 信号处理


@worker_shutdown.connect
def on_worker_shutdown(sender, **kwargs):
    """
    Celery Worker 退出时的信号处理函数

    当 Worker 接收到 shutdown 信号时，执行资源清理
    """
    cleanup_resources()


# 注册系统信号处理（用于强制退出场景）
def signal_handler(signum, frame):
    """
    系统信号处理函数

    当收到 SIGTERM 或 SIGINT 信号时，执行资源清理并退出
    """
    cleanup_resources()
    sys.exit(0)


# 注册系统信号
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# 注册 atexit 钩子（作为最后的保障）


atexit.register(cleanup_resources)
