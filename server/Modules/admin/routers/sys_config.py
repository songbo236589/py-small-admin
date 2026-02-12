"""
Admin 系统配置路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.admin.controllers.v1.sys_config_controller import SysConfigController

# 创建路由器
router = APIRouter(prefix="/sys_config", tags=["系统配置"])
# 创建控制器实例
controller = SysConfigController()


router.get(
    "/edit/{group_code}",
    response_model=dict[str, Any],
    summary="配置编辑页面数据",
)(controller.edit)

router.put(
    "/update/{group_code}",
    response_model=dict[str, Any],
    summary="配置编辑",
)(controller.update)
