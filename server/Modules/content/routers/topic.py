"""
Content 话题管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.topic_controller import TopicController

# 创建路由器
router = APIRouter(prefix="/topics", tags=["话题管理"])
# 创建控制器实例
controller = TopicController()


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取话题列表",
)(controller.index)


router.post(
    "/fetch",
    response_model=dict[str, Any],
    summary="抓取平台推荐话题",
)(controller.fetch)


router.get(
    "/detail/{id}",
    response_model=dict[str, Any],
    summary="获取话题详情",
)(controller.detail)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="话题状态",
)(controller.set_status)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="删除话题",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除",
)(controller.destroy_all)
