"""
Content 标签管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.tag_controller import TagController

# 创建路由器
router = APIRouter(prefix="/tag", tags=["标签管理"])
# 创建控制器实例
controller = TagController()


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取标签列表",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="标签添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="标签编辑页面数据",
)(controller.edit)


router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="标签编辑",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="标签状态",
)(controller.set_status)


router.put(
    "/set_sort/{id}",
    response_model=dict[str, Any],
    summary="标签排序",
)(controller.set_sort)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="标签删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除",
)(controller.destroy_all)
