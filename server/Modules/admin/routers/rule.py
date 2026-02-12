"""
Admin 用户管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.admin.controllers.v1.rule_controller import RuleController

# 创建路由器
router = APIRouter(prefix="/rule", tags=["菜单管理"])
# 创建控制器实例
controller = RuleController()


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取菜单列表",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="菜单添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="菜单编辑页面数据",
)(controller.edit)

router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="菜单编辑",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="菜单状态",
)(controller.set_status)


router.put(
    "/set_sort/{id}",
    response_model=dict[str, Any],
    summary="菜单排序",
)(controller.set_sort)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="菜单删除",
)(controller.destroy)
