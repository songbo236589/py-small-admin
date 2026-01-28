"""
Admin 菜单管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Form, Path
from fastapi.responses import JSONResponse

from Modules.admin.services.rule_service import RuleService
from Modules.admin.validators.rule_validator import RuleAddUpdateRequest
from Modules.common.libs.validation.decorators import (
    validate_request_data,
)
from Modules.common.libs.validation.pagination_validator import (
    IdRequest,
    ListSortRequest,
    ListStatusRequest,
)


class RuleController:
    """Admin菜单管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化菜单管理控制器"""
        self.rule_service = RuleService()

    async def index(self) -> JSONResponse:
        """获取菜单列表"""
        return await self.rule_service.index()

    @validate_request_data(RuleAddUpdateRequest)
    async def add(
        self,
        name: str = Form(..., description="菜单名称"),
        path: str | None = Form("", description="路由路径"),
        component: str | None = Form("", description="组件路径"),
        redirect: str | None = Form("", description="重定向路径"),
        type: int = Form(1, description="菜单类型:1=模块,2=目录,3=菜单"),
        status: int = Form(1, description="侧边栏显示状态:0=隐藏,1=显示"),
        icon: str | None = Form("", description="图标"),
        pid: int = Form(0, description="父级ID"),
        sort: int = Form(1, description="排序"),
        target: str | None = Form("", description="链接打开方式：_self/_blank"),
    ) -> JSONResponse:
        """菜单添加"""
        return await self.rule_service.add(
            {
                "name": name,
                "path": path,
                "component": component,
                "redirect": redirect,
                "type": type,
                "status": status,
                "icon": icon,
                "pid": pid,
                "sort": sort,
                "target": target,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="菜单ID")) -> JSONResponse:
        """获取菜单信息（用于编辑）"""
        return await self.rule_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(RuleAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="菜单ID"),
        name: str = Form(..., description="菜单名称"),
        path: str | None = Form("", description="路由路径"),
        component: str | None = Form("", description="组件路径"),
        redirect: str | None = Form("", description="重定向路径"),
        type: int = Form(1, description="菜单类型:1=模块,2=目录,3=菜单"),
        status: int = Form(1, description="侧边栏显示状态:0=隐藏,1=显示"),
        icon: str | None = Form("", description="图标"),
        pid: int = Form(0, description="父级ID"),
        sort: int = Form(1, description="排序"),
        target: str | None = Form("", description="链接打开方式：_self/_blank"),
    ) -> JSONResponse:
        """更新菜单信息"""
        return await self.rule_service.update(
            id,
            {
                "name": name,
                "path": path,
                "component": component,
                "redirect": redirect,
                "type": type,
                "status": status,
                "icon": icon,
                "pid": pid,
                "sort": sort,
                "target": target,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="菜单ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """菜单状态"""
        return await self.rule_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListSortRequest)
    async def set_sort(
        self,
        id: int = Path(..., description="菜单ID"),
        sort: int = Form(..., description="排序"),
    ) -> JSONResponse:
        """菜单状态"""
        return await self.rule_service.set_sort(
            id,
            {
                "sort": sort,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="菜单ID"),
    ) -> JSONResponse:
        """菜单删除"""
        return await self.rule_service.destroy(id)
