"""
Admin 用户管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.admin.controllers.v1.group_controller import GroupController

# 创建路由器
router = APIRouter(prefix="/group", tags=["角色管理"])
# 创建控制器实例
controller = GroupController()

router.get(
    "/get_group_list",
    response_model=dict[str, Any],
    summary="获取角色列表",
)(controller.get_group_list)


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取角色列表或搜索角色（统一接口）",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="角色添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="角色编辑页面数据",
)(controller.edit)

router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="角色编辑",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="角色状态",
)(controller.set_status)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="角色删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="角色批量删除",
)(controller.destroy_all)


router.get(
    "/get_access/{id}",
    response_model=dict[str, Any],
    summary="配置权限规则页面数据",
)(controller.get_access)

router.put(
    "/access_update/{id}",
    response_model=dict[str, Any],
    summary="配置权限规则",
)(controller.access_update)
