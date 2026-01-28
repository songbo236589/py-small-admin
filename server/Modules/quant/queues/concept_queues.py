"""
概念同步队列任务

包含概念-股票关联关系同步相关的队列任务
"""

from Modules.common.libs.celery.celery_service import get_celery_service
from Modules.quant.services.quant_concept_service import QuantConceptService

# 获取 Celery 应用实例
celery_app = get_celery_service().app


@celery_app.task(
    name="Modules.quant.queues.concept_queues.sync_concept_relation_queue",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def sync_concept_relation_queue(
    self,
    concept_id: int,
    concept_code: str,
) -> dict:
    """
    同步单个概念的股票关联关系任务

    Args:
        concept_id: 概念ID
        concept_code: 概念代码

    Returns:
        dict: 同步结果统计
    """
    # 使用同步版本的方法
    service = QuantConceptService()
    return service.sync_single_concept_relation_sync(concept_id, concept_code)
