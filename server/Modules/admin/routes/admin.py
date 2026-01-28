"""
Admin 用户管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.admin.controllers.v1.admin_controller import AdminController

# 创建路由器
router = APIRouter(prefix="/admin", tags=["管理员管理"])
# 创建控制器实例
controller = AdminController()

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取管理员列表或搜索管理员（统一接口）",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="管理员添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="管理员编辑页面数据",
)(controller.edit)

router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="管理员编辑",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="管理员状态",
)(controller.set_status)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="管理员删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="管理员批量删除",
)(controller.destroy_all)

router.put(
    "/reset_pwd/{id}",
    response_model=dict[str, Any],
    summary="管理员初始化密码",
)(controller.reset_pwd)
