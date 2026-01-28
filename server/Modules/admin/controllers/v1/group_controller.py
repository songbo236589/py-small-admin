"""
Admin 角色管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Body, Form, Path, Query
from fastapi.responses import JSONResponse

from Modules.admin.services.group_service import GroupService
from Modules.admin.validators.group_validator import (
    GroupAccessUpdateRequest,
    GroupAddUpdateRequest,
)
from Modules.common.libs.validation.decorators import (
    validate_body_data,
    validate_request_data,
)
from Modules.common.libs.validation.pagination_validator import (
    IdArrayRequest,
    IdRequest,
    ListStatusRequest,
    PaginationRequest,
)


class GroupController:
    """Admin角色管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化角色管理控制器"""
        self.group_service = GroupService()

    @validate_request_data(ListStatusRequest)
    async def get_group_list(
        self,
        status: int | None = Query(None, description="状态"),
    ) -> JSONResponse:
        """获取角色列表"""
        return await self.group_service.get_group_list({"status": status})

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录，用于控制每页显示数量"),
        name: str | None = Query(None, description="角色名称"),
        content: str | None = Query(None, description="角色描述"),
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
        """获取角色列表或搜索角色（统一接口）"""
        return await self.group_service.index(
            {
                "page": page,
                "limit": limit,
                "name": name,
                "content": content,
                "status": status,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(GroupAddUpdateRequest)
    async def add(
        self,
        name: str = Form(..., description="角色名称"),
        content: str | None = Form("", description="角色描述"),
        status: int = Form(1, description="状态"),
    ) -> JSONResponse:
        """角色添加"""
        return await self.group_service.add(
            {
                "name": name,
                "content": content,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="角色ID")) -> JSONResponse:
        """获取角色信息（用于编辑）"""
        return await self.group_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(GroupAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="角色ID"),
        name: str = Form(..., description="角色名称"),
        content: str | None = Form("", description="角色描述"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """更新角色信息"""
        return await self.group_service.update(
            id,
            {
                "name": name,
                "content": content,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="角色ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """角色状态"""
        return await self.group_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="角色ID"),
    ) -> JSONResponse:
        """角色删除"""
        return await self.group_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """角色批量删除"""
        return await self.group_service.destroy_all(request.id_array)

    @validate_request_data(IdRequest)
    async def get_access(
        self, id: int = Path(..., description="角色ID")
    ) -> JSONResponse:
        """配置权限规则页面数据"""
        return await self.group_service.get_access(id)

    @validate_request_data(IdRequest)
    @validate_body_data(GroupAccessUpdateRequest)
    async def access_update(
        self,
        id: int = Path(..., description="角色ID"),
        request: GroupAccessUpdateRequest = Body(...),
    ) -> JSONResponse:
        """配置权限规则"""
        return await self.group_service.access_update(
            id,
            request.rules,
        )
