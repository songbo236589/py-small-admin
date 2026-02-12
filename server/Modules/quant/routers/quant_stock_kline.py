"""
股票K线数据路由 - 定义股票K线数据同步相关的API路由
"""

from typing import Any

from fastapi import APIRouter

from Modules.quant.controllers.v1.quant_stock_kline_controller import (
    QuantStockKlineController,
)

# 创建路由器
router = APIRouter(prefix="/kline", tags=["股票K线数据"])

# 创建控制器实例
controller = QuantStockKlineController()


# ==================== K线数据同步接口 ====================

router.post(
    "/sync_kline_1d",
    response_model=dict[str, Any],
    summary="同步所有股票日K线数据",
)(controller.sync_kline_1d)


router.post(
    "/sync_single_kline_1d",
    response_model=dict[str, Any],
    summary="同步单个股票日K线数据",
)(controller.sync_single_kline_1d)
