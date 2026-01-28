"""
默认定时任务

包含系统默认的定时任务，用于测试和验证 Celery 功能
"""

from loguru import logger

from Modules.common.libs.celery.celery_service import get_celery_service

# 获取 Celery 应用实例
celery_app = get_celery_service().app


@celery_app.task(name="Modules.admin.tasks.default_tasks.print_hello_task")
def print_hello_task():
    """
    默认测试任务

    输出 "123456" 用于验证 Celery 定时任务功能是否正常工作

    Returns:
        str: 返回 "123456"
    """
    logger.info("123456")
    print("123456")
    return "123456"
