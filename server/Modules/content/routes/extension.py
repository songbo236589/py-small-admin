"""
Content 浏览器扩展路由 - 浏览器扩展专用公开接口
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.extension_controller import (
    ExtensionController,
)

# 创建控制器实例
controller = ExtensionController()

# 扩展路由器 - 浏览器扩展专用公开接口（不需要认证）
extension_router = APIRouter(prefix="/extension", tags=["浏览器扩展"])

# 获取平台列表
extension_router.get(
    "/platform/index",
    response_model=dict[str, Any],
    summary="获取平台列表",
)(controller.get_platform_list)

# 导入Cookies
extension_router.post(
    "/platform_account/import_cookies",
    response_model=dict[str, Any],
    summary="从浏览器扩展导入Cookies",
)(controller.import_cookies)
