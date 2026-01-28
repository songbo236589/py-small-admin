"""
概念日志路由 - 定义概念日志相关的API路由
"""

from typing import Any

from fastapi import APIRouter

from Modules.quant.controllers.v1.quant_concept_log_controller import (
    QuantConceptLogController,
)

# 创建路由器
router = APIRouter(prefix="/concept_log", tags=["概念日志管理"])

# 创建控制器实例
controller = QuantConceptLogController()


# ==================== 概念日志列表 ====================

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取概念日志列表",
)(controller.index)


# ==================== 批量删除操作 ====================

router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除概念日志",
)(controller.destroy_all)
