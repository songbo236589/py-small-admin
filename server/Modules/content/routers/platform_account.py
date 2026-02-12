"""
Content 平台账号管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.platform_account_controller import (
    PlatformAccountController,
)

# 创建控制器实例
controller = PlatformAccountController()

# 主路由器 - 包含需要认证的接口
router = APIRouter(prefix="/platform_account", tags=["平台账号管理"])

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取平台账号列表",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="添加平台账号",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="平台账号编辑页面数据",
)(controller.edit)


router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="平台账号编辑",
)(controller.update)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="平台账号删除",
)(controller.destroy)


router.post(
    "/verify/{id}",
    response_model=dict[str, Any],
    summary="验证Cookie有效性",
)(controller.verify)
