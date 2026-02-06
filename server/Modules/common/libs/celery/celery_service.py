"""
Celery 服务类

该模块提供 Celery 应用实例的完整管理功能，包括：
- Celery 应用初始化和配置
- FastAPI 集成

使用示例:
    from Modules.common.libs.celery.celery_service import get_celery_service

    # 获取 Celery 服务实例
    celery_service = get_celery_service()

    # 定义任务
    @celery_service.app.task
    def add(x, y):
        return x + y

    # 调用任务
    result = add.delay(4, 4)

启动 Worker:
    celery -A Modules.common.libs.celery.celery_service worker --loglevel=info

启动 Beat (定时任务):
    celery -A Modules.common.libs.celery.celery_service beat --loglevel=info

启动 Flower (监控):
    celery -A Modules.common.libs.celery.celery_service flower
"""

from typing import Any

from loguru import logger

from celery import Celery

from ..config import Config


class CeleryService:
    """
    Celery 服务类

    提供 Celery 应用的完整管理功能：
    - 应用初始化和配置
    - FastAPI 集成

    主要功能：
    - 封装 Celery 应用实例
    - 支持 FastAPI 应用集成
    """

    def __init__(self, config: Any = None):
        """
        初始化 Celery 服务

        Args:
            config: Celery 配置对象，如果为 None 则从 Config.get("celery") 获取
        """
        self._config = config or Config.get("celery")
        self._app: Celery | None = None

    @property
    def app(self) -> Celery:
        """
        获取 Celery 应用实例（延迟初始化）

        Returns:
            Celery: 配置好的 Celery 应用实例
        """
        if self._app is None:
            self._app = self._init_app()
        return self._app

    def _init_app(self) -> Celery:
        """
        初始化 Celery 应用实例

        Returns:
            Celery: 配置好的 Celery 应用实例
        """
        logger.info("正在初始化 Celery 应用...")

        # 创建 Celery 应用
        app = Celery(
            "py_small_admin",
            broker=self._config.broker_url,
            backend=self._config.result_backend,
            include=self._config.include,  # 从配置文件读取任务模块列表
        )

        # 加载配置
        app.conf.update(
            # ========== Broker 配置 ==========
            broker_url=self._config.broker_url,
            broker_connection_retry=self._config.broker_connection_retry,
            broker_connection_retry_on_startup=self._config.broker_connection_retry_on_startup,
            broker_connection_max_retries=self._config.broker_connection_max_retries,
            broker_connection_retry_delay=self._config.broker_connection_retry_delay,
            broker_use_ssl=self._config.broker_use_ssl,
            broker_transport_options=self._config.broker_transport_options,
            # ========== Result Backend 配置 ==========
            result_backend=self._config.result_backend,
            result_expires=self._config.result_expires,
            result_extended=self._config.result_extended,
            result_backend_transport_options=self._config.result_backend_transport_options,
            # ========== Worker 配置 ==========
            # worker_pool=self._config.worker_pool,
            worker_concurrency=self._config.worker_concurrency,
            worker_prefetch_multiplier=self._config.worker_prefetch_multiplier,
            worker_max_tasks_per_child=self._config.worker_max_tasks_per_child,
            worker_disable_rate_limits=self._config.worker_disable_rate_limits,
            worker_log_format=self._config.worker_log_format,
            worker_task_log_format=self._config.worker_task_log_format,
            # ========== 任务配置 ==========
            task_default_queue=self._config.task_default_queue,
            task_default_exchange=self._config.task_default_exchange,
            task_default_routing_key=self._config.task_default_routing_key,
            task_default_rate_limit=self._config.task_default_rate_limit,
            task_default_time_limit=self._config.task_default_time_limit,
            task_default_soft_time_limit=self._config.task_default_soft_time_limit,
            task_default_max_retries=self._config.task_default_max_retries,
            task_default_retry_delay=self._config.task_default_retry_delay,
            task_track_started=self._config.task_track_started,
            task_acks_late=self._config.task_acks_late,
            task_reject_on_worker_lost=self._config.task_reject_on_worker_lost,
            task_always_eager=self._config.task_always_eager,
            task_eager_propagates=self._config.task_eager_propagates,
            # ========== 序列化配置 ==========
            task_serializer=self._config.task_serializer,
            result_serializer=self._config.result_serializer,
            accept_content=self._config.accept_content,
            # ========== 时区配置 ==========
            timezone=self._config.timezone,
            enable_utc=self._config.enable_utc,
            # ========== 安全配置 ==========
            task_send_sent_event=self._config.task_send_sent_event,
            task_send_started_event=self._config.task_send_started_event,
            task_send_success_event=self._config.task_send_success_event,
            task_send_failure_event=self._config.task_send_failure_event,
            task_send_retry_event=self._config.task_send_retry_event,
            # ========== Beat 配置 ==========
            beat_schedule_filename=self._config.beat_schedule_filename,
            beat_max_loop_interval=self._config.beat_max_loop_interval,
            beat_loglevel=self._config.beat_loglevel,
            # ========== 任务队列配置 ==========
            task_queues=self._config.task_queues,
            task_routes=self._config.task_routes,
            # ========== 其他配置 ==========
            task_compression=self._config.task_compression,
            task_compression_threshold=self._config.task_compression_threshold,
            result_compression=self._config.result_compression,
            result_compression_threshold=self._config.result_compression_threshold,
            # ========== 定时任务配置 ==========
            beat_schedule=self._config.beat_schedule,
        )

        logger.info("Celery 应用初始化完成")
        return app

    # ========== FastAPI 集成 ==========

    def init_fastapi_celery(self, fastapi_app: Any) -> None:
        """
        将 Celery 应用集成到 FastAPI 应用中

        Args:
            fastapi_app: FastAPI 应用实例
        """
        from fastapi import FastAPI

        if not isinstance(fastapi_app, FastAPI):
            raise TypeError("fastapi_app must be a FastAPI instance")

        # 将 Celery 服务附加到 FastAPI 应用的 state 中
        # FastAPI 推荐使用 app.state 来存储应用状态
        fastapi_app.state.celery = self.app
        fastapi_app.state.celery_service = self

    async def verify_connection(self) -> None:
        """
        验证 Celery 连接

        在应用启动时调用，用于验证 Celery 是否能正常连接到 Broker

        Raises:
            RuntimeError: 当连接失败且需要严格验证时
        """
        if not self._config.verify_on_startup:
            return

        try:
            # 尝试发送一个简单的任务来验证连接
            self.app.control.ping()
            logger.info("✅ Celery 连接成功")
        except Exception as e:
            logger.warning(f"⚠️ Celery 连接失败: {e}")
            logger.warning("   请确保 RabbitMQ/Redis 服务已启动")
            # 注意：这里不抛出异常，允许应用继续启动
            # 如果需要严格验证，可以取消注释下面的代码
            # raise RuntimeError(f"Celery 连接失败: {e}")


# ========== 单例模式 ==========

_celery_service: CeleryService | None = None


def get_celery_service(config: Any = None) -> CeleryService:
    """
    获取 Celery 服务实例（单例模式）

    Args:
        config: Celery 配置对象，如果为 None 则从 Config.get("celery") 获取

    Returns:
        CeleryService: Celery 服务实例

    Example:
        >>> celery_service = get_celery_service()
        >>> celery_service.app
        <Celery: py_small_admin>
    """
    global _celery_service
    if _celery_service is None:
        _celery_service = CeleryService(config)
    return _celery_service


# ========== 便捷函数（向后兼容） ==========


# 为了向后兼容，提供便捷函数直接访问全局实例
def celery_app() -> Celery:
    """
    获取 Celery 应用实例（便捷函数）

    Returns:
        Celery: Celery 应用实例

    Example:
        >>> from Modules.common.libs.celery.celery_service import celery_app
        >>> @celery_app().task
        ... def my_task():
        ...     pass
    """
    return get_celery_service().app


def init_celery() -> Celery:
    """
    初始化 Celery 应用（向后兼容函数）

    Returns:
        Celery: Celery 应用实例

    Example:
        >>> from Modules.common.libs.celery.celery_service import init_celery
        >>> app = init_celery()
    """
    return get_celery_service().app


def init_fastapi_celery(app: Any) -> None:
    """
    将 Celery 应用集成到 FastAPI 应用中（向后兼容函数）

    Args:
        app: FastAPI 应用实例

    Example:
        >>> from fastapi import FastAPI
        >>> from Modules.common.libs.celery.celery_service import init_fastapi_celery
        >>> fastapi_app = FastAPI()
        >>> init_fastapi_celery(fastapi_app)
    """
    get_celery_service().init_fastapi_celery(app)
