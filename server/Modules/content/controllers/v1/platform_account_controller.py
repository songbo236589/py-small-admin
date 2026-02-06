"""
Content 平台账号管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Form, Path, Query
from fastapi.responses import JSONResponse

from Modules.common.libs.validation.decorators import (
    validate_request_data,
)
from Modules.common.libs.validation.pagination_validator import (
    IdRequest,
    PaginationRequest,
)
from Modules.content.services.platform_account_service import PlatformAccountService
from Modules.content.validators.platform_account_validator import (
    PlatformAccountAddUpdateRequest,
)


class PlatformAccountController:
    """Content平台账号管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化平台账号管理控制器"""
        self.platform_account_service = PlatformAccountService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        platform: str | None = Query(None, description="平台标识"),
        account_name: str | None = Query(None, description="账号名称"),
        status: int | None = Query(None, description="状态"),
        sort: str | None = Query(None, description="排序规则"),
        created_at_start: str | None = Query(
            None, alias="created_at[start]", description="创建时间开始"
        ),
        created_at_end: str | None = Query(
            None, alias="created_at[end]", description="创建时间结束"
        ),
        updated_at_start: str | None = Query(
            None, alias="updated_at[start]", description="更新时间开始"
        ),
        updated_at_end: str | None = Query(
            None, alias="updated_at[end]", description="更新时间结束"
        ),
    ) -> JSONResponse:
        """获取平台账号列表或搜索平台账号（统一接口）"""
        return await self.platform_account_service.index(
            {
                "page": page,
                "limit": limit,
                "platform": platform,
                "account_name": account_name,
                "status": status,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(PlatformAccountAddUpdateRequest)
    async def add(
        self,
        platform: str = Form(..., description="平台标识：zhihu, juejin, csdn等"),
        account_name: str = Form(..., description="账号名称"),
        cookies: str = Form(..., description="Cookie信息（JSON格式）"),
        user_agent: str | None = Form(None, description="浏览器UA"),
        status: int = Form(1, description="状态"),
    ) -> JSONResponse:
        """平台账号添加"""
        return await self.platform_account_service.add(
            {
                "platform": platform,
                "account_name": account_name,
                "cookies": cookies,
                "user_agent": user_agent,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="平台账号ID")) -> JSONResponse:
        """获取平台账号信息（用于编辑）"""
        return await self.platform_account_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(PlatformAccountAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="平台账号ID"),
        platform: str = Form(..., description="平台标识：zhihu, juejin, csdn等"),
        account_name: str = Form(..., description="账号名称"),
        cookies: str = Form(..., description="Cookie信息（JSON格式）"),
        user_agent: str | None = Form(None, description="浏览器UA"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """更新平台账号信息"""
        return await self.platform_account_service.update(
            id,
            {
                "platform": platform,
                "account_name": account_name,
                "cookies": cookies,
                "user_agent": user_agent,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="平台账号ID"),
    ) -> JSONResponse:
        """平台账号删除"""
        return await self.platform_account_service.destroy(id)

    @validate_request_data(IdRequest)
    async def verify(
        self,
        id: int = Path(..., description="平台账号ID"),
    ) -> JSONResponse:
        """验证平台账号Cookie有效性"""
        return await self.platform_account_service.verify(id)
