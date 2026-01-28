"""
股票K线数据控制器 - 负责股票K线数据同步相关的API接口
"""

from fastapi import Form
from fastapi.responses import JSONResponse

from Modules.quant.services.quant_stock_kline_service import QuantStockKlineService


class QuantStockKlineController:
    """股票K线数据控制器 - 负责股票K线数据同步相关的API接口"""

    def __init__(self):
        """初始化股票K线控制器"""
        self.service = QuantStockKlineService()

    async def sync_kline_1d(self) -> JSONResponse:
        """
        同步所有股票日K线数据

        Returns:
            JSONResponse: 同步结果统计
        """
        return await self.service.sync_kline_1d()

    async def sync_single_kline_1d(
        self,
        id: int = Form(..., description="股票ID"),
    ) -> JSONResponse:
        """
        同步单个股票日K线数据

        Args:
            id: 股票ID

        Returns:
            JSONResponse: 同步结果统计
        """
        return await self.service.sync_single_kline_1d(id)
