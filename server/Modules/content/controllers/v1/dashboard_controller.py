"""
Content Dashboard 控制器 - 负责统计数据接口
"""

from fastapi.responses import JSONResponse

from Modules.content.services.dashboard_service import DashboardService


class DashboardController:
    """Content Dashboard 控制器 - 负责统计数据接口"""

    def __init__(self):
        """初始化 Dashboard 控制器"""
        self.dashboard_service = DashboardService()

    async def statistics(self) -> JSONResponse:
        """获取内容统计数据"""
        return await self.dashboard_service.statistics()
