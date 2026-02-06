"""
Content 发布管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.publish_controller import PublishController

# 创建路由器
router = APIRouter(prefix="/publish", tags=["发布管理"])
# 创建控制器实例
controller = PublishController()


router.post(
    "/article/{id}",
    response_model=dict[str, Any],
    summary="发布文章到指定平台",
)(controller.publish_article)


router.post(
    "/batch",
    response_model=dict[str, Any],
    summary="批量发布多篇文章",
)(controller.publish_batch)


router.get(
    "/logs",
    response_model=dict[str, Any],
    summary="发布记录列表",
)(controller.logs)


router.get(
    "/logs/{id}",
    response_model=dict[str, Any],
    summary="发布记录详情",
)(controller.log_detail)


router.put(
    "/retry/{id}",
    response_model=dict[str, Any],
    summary="重试失败发布",
)(controller.retry)
