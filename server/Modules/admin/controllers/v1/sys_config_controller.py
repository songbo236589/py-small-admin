"""
Admin 系统配置控制器 - 负责参数验证和业务逻辑协调
"""

from typing import Any

from fastapi import Body, Path, Request
from fastapi.responses import JSONResponse

from Modules.admin.services.sys_config_service import SysConfigService
from Modules.admin.validators.sys_config_validator import SysConfigGroupCodeRequest
from Modules.common.libs.validation.decorators import (
    validate_request_data,
)


class SysConfigController:
    """Admin 系统配置控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化系统配置控制器"""
        self.sys_config_service = SysConfigService()

    @validate_request_data(SysConfigGroupCodeRequest)
    async def edit(
        self, request: Request, group_code: str = Path(..., description="配置分组")
    ) -> JSONResponse:
        """获取系统配置信息（用于编辑）"""
        return await self.sys_config_service.edit(group_code, request)

    @validate_request_data(SysConfigGroupCodeRequest)
    async def update(
        self,
        request: Request,
        group_code: str = Path(..., description="配置分组"),
        data: Any = Body(...),
    ) -> JSONResponse:
        """更新系统配置信息"""
        return await self.sys_config_service.update(group_code, data, request)
