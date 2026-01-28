"""
量化数据同步定时任务

包含股票和概念数据的定时同步任务，用于自动化数据更新
"""

import asyncio

from loguru import logger

from Modules.common.libs.celery.celery_service import get_celery_service
from Modules.quant.services.quant_concept_service import QuantConceptService
from Modules.quant.services.quant_stock_service import QuantStockService

# 获取 Celery 应用实例
celery_app = get_celery_service().app


# ==================== 股票数据同步任务 ====================


@celery_app.task(
    name="Modules.quant.tasks.quant_tasks.sync_stock_list_task",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def sync_stock_list_task(market: int = 1):
    """
    定时同步股票列表任务

    Args:
        market: 市场类型（1=上海、2=深圳、4=港股、5=美股）

    调度建议：
        - 每天凌晨 2:00 执行
        - crontab(hour=2, minute=0)

    Returns:
        dict: 执行结果
    """
    logger.info(f"开始同步股票列表，市场类型: {market}")

    try:
        # 创建服务实例
        service = QuantStockService()

        # 使用 asyncio.run 执行异步方法
        result = asyncio.run(service.sync_stock_list(market))

        # 解析结果
        if result.status_code == 200:
            logger.info(f"股票列表同步完成，市场类型: {market}")
            return {"market": market, "status": "success"}
        else:
            logger.error(f"股票列表同步失败: {result.body.decode()}")
            raise Exception(f"同步失败: {result.body.decode()}")
    except Exception as e:
        logger.error(f"股票列表同步任务执行失败: {e}")
        raise


# ==================== 概念数据同步任务 ====================


@celery_app.task(
    name="Modules.quant.tasks.quant_tasks.sync_concept_list_task",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def sync_concept_list_task():
    """
    定时同步概念列表任务

    调度建议：
        - 每周日凌晨 3:00 执行
        - crontab(day_of_week=0, hour=3, minute=0)

    Returns:
        dict: 执行结果
    """
    logger.info("开始同步概念列表")

    try:
        # 创建服务实例
        service = QuantConceptService()

        # 使用 asyncio.run 执行异步方法
        result = asyncio.run(service.sync_list())

        # 解析结果
        if result.status_code == 200:
            logger.info("概念列表同步完成")
            return {"status": "success"}
        else:
            logger.error(f"概念列表同步失败: {result.body.decode()}")
            raise Exception(f"同步失败: {result.body.decode()}")
    except Exception as e:
        logger.error(f"概念列表同步任务执行失败: {e}")
        raise


@celery_app.task(
    name="Modules.quant.tasks.quant_tasks.sync_stock_concept_task",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def sync_stock_concept_task():
    """
    定时同步股票-概念关联关系任务

    调度建议：
        - 每天凌晨 3:00 执行
        - crontab(hour=3, minute=0)

    Returns:
        dict: 执行结果
    """
    logger.info("开始同步股票-概念关联关系")

    try:
        # 创建服务实例
        service = QuantConceptService()

        # 使用 asyncio.run 执行异步方法
        result = asyncio.run(service.sync_relation())

        # 解析结果
        if result.status_code == 200:
            logger.info("股票-概念关联关系同步完成")
            return {"status": "success"}
        else:
            logger.error(f"股票-概念关联关系同步失败: {result.body.decode()}")
            raise Exception(f"同步失败: {result.body.decode()}")
    except Exception as e:
        logger.error(f"股票-概念关联关系同步任务执行失败: {e}")
        raise
