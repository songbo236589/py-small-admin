"""
行业日志路由 - 定义行业日志相关的API路由
"""

from typing import Any

from fastapi import APIRouter

from Modules.quant.controllers.v1.quant_industry_log_controller import (
    QuantIndustryLogController,
)

# 创建路由器
router = APIRouter(prefix="/industry_log", tags=["行业日志管理"])

# 创建控制器实例
controller = QuantIndustryLogController()


# ==================== 行业日志列表 ====================

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取行业日志列表",
)(controller.index)


# ==================== 批量删除操作 ====================

router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除行业日志",
)(controller.destroy_all)
