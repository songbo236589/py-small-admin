"""
Celery 模块

提供 Celery 异步任务队列的完整支持，包括：
- Celery 应用实例初始化
- 任务定义和注册
- FastAPI 集成
"""

from .celery_service import (
    CeleryService,
    get_celery_service,
    init_celery,
    init_fastapi_celery,
)

__all__ = [
    "CeleryService",
    "get_celery_service",
    "init_celery",
    "init_fastapi_celery",
]
