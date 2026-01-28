"""
Admin 用户管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Body, Form, Path, Query
from fastapi.responses import JSONResponse

from Modules.admin.services.admin_service import AdminService
from Modules.admin.validators.admin_validator import AdminAddRequest, AdminUpdateRequest
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


class AdminController:
    """Admin用户管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化用户管理控制器"""
        self.admin_service = AdminService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录，用于控制每页显示数量"),
        username: str | None = Query(None, description="用户名"),
        name: str | None = Query(None, description="真实姓名"),
        phone: str | None = Query(None, description="手机号"),
        status: int | None = Query(None, description="状态"),
        group_id: int | None = Query(None, description="所属角色"),
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
        """获取用户列表或搜索用户（统一接口）"""
        return await self.admin_service.index(
            {
                "page": page,
                "limit": limit,
                "username": username,
                "name": name,
                "phone": phone,
                "status": status,
                "group_id": group_id,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(AdminAddRequest)
    async def add(
        self,
        username: str = Form(..., description="用户名"),
        name: str = Form(..., description="真实姓名"),
        password: str = Form(..., description="密码"),
        phone: str | None = Form(None, description="手机号"),
        status: int = Form(..., description="状态"),
        group_id: int = Form(..., description="所属角色"),
    ) -> JSONResponse:
        """管理员添加"""
        return await self.admin_service.add(
            {
                "username": username,
                "name": name,
                "password": password,
                "phone": phone,
                "status": status,
                "group_id": group_id,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="用户ID")) -> JSONResponse:
        """获取管理员信息（用于编辑）"""
        return await self.admin_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(AdminUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="用户ID"),
        username: str = Form(..., description="用户名"),
        name: str = Form(..., description="真实姓名"),
        phone: str | None = Form("", description="手机号"),
        status: int = Form(..., description="状态"),
        group_id: int = Form(..., description="所属角色"),
    ) -> JSONResponse:
        """更新管理员信息"""
        return await self.admin_service.update(
            id,
            {
                "username": username,
                "name": name,
                "phone": phone,
                "status": status,
                "group_id": group_id,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="用户ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """管理员状态"""
        return await self.admin_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="用户ID"),
    ) -> JSONResponse:
        """管理员删除"""
        return await self.admin_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """管理员批量删除"""
        return await self.admin_service.destroy_all(request.id_array)

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def reset_pwd(
        self,
        id: int = Path(..., description="用户ID"),
    ) -> JSONResponse:
        """管理员初始化密码"""
        return await self.admin_service.reset_pwd(id)
