"""
Content 浏览器扩展控制器 - 处理浏览器扩展相关请求
"""

from typing import Any

from fastapi import Body
from fastapi.responses import JSONResponse

from Modules.content.services.extension_service import ExtensionService


class ExtensionController:
    """浏览器扩展控制器 - 处理浏览器扩展相关请求"""

    def __init__(self):
        """初始化浏览器扩展控制器"""
        self.extension_service = ExtensionService()

    async def get_platform_list(self) -> JSONResponse:
        """
        获取平台列表

        返回所有支持的平台配置，包含平台标识、名称、域名等信息
        """
        return await self.extension_service.get_platform_list()

    async def import_cookies(
        self,
        data: dict[str, Any] = Body(..., description="Cookie数据和User-Agent"),
    ) -> JSONResponse:
        """从浏览器扩展导入Cookies

        接收浏览器扩展发送的Cookie数据，自动识别平台并更新或创建平台账号。

        Args:
            data: 包含 cookies 和 userAgent 的字典
                {
                    "cookies": [...],  # Cookie 数组
                    "userAgent": "Mozilla/5.0..."  # 浏览器 User-Agent
                }
        """
        cookies_data = data.get("cookies", [])
        user_agent = data.get("userAgent")
        # TODO: 从认证信息中获取当前用户ID
        user_id = 1  # 暂时使用固定用户ID
        return await self.extension_service.import_cookies(
            cookies_data, user_id, user_agent
        )
