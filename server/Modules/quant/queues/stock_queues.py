"""
股票K线同步队列任务

包含股票K线数据同步相关的队列任务
"""

from Modules.common.libs.celery.celery_service import get_celery_service
from Modules.quant.services.quant_stock_kline_service import QuantStockKlineService

# 获取 Celery 应用实例
celery_app = get_celery_service().app


@celery_app.task(
    name="Modules.quant.queues.stock_queues.sync_stock_kline_1d_queue",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=1800,  # 最大重试间隔 30 分钟，避免频繁重试触发限流
    retry_jitter=True,
    max_retries=5,  # 增加重试次数，提高成功率
    acks_late=False,
    reject_on_worker_lost=True,
    time_limit=300,  # 5分钟，防止长时间挂起
    soft_time_limit=180,  # 3分钟
)
def sync_stock_kline_1d_queue(
    self,
    stock_id: int,
    stock_code: str,
    stock_name: str,
) -> dict:
    """
    同步单个股票的日K线数据任务

    Args:
        stock_id: 股票ID
        stock_code: 股票代码
        stock_name: 股票名称

    Returns:
        dict: 同步结果统计
    """
    # 使用同步版本的方法
    service = QuantStockKlineService()
    return service.sync_single_stock_kline_1d_sync(stock_id, stock_code, stock_name)
