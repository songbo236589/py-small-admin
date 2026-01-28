"""
行业同步队列任务

包含行业-股票关联关系同步相关的队列任务
"""

from Modules.common.libs.celery.celery_service import get_celery_service
from Modules.quant.services.quant_industry_service import QuantIndustryService

# 获取 Celery 应用实例
celery_app = get_celery_service().app


@celery_app.task(
    name="Modules.quant.queues.industry_queues.sync_industry_relation_queue",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def sync_industry_relation_queue(
    self,
    industry_id: int,
    industry_code: str,
) -> dict:
    """
    同步单个行业的股票关联关系任务

    Args:
        industry_id: 行业ID
        industry_code: 行业代码

    Returns:
        dict: 同步结果统计
    """
    # 使用同步版本的方法
    service = QuantIndustryService()
    return service.sync_single_industry_relation_sync(industry_id, industry_code)
