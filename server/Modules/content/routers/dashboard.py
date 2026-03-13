"""
Content Dashboard 路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.dashboard_controller import DashboardController

# 创建路由器
router = APIRouter(prefix="/dashboard", tags=["Dashboard 统计"])
# 创建控制器实例
controller = DashboardController()


router.get(
    "/statistics",
    response_model=dict[str, Any],
    summary="获取内容统计数据",
)(controller.statistics)
