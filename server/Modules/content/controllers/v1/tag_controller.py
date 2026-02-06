"""
Content 文章标签管理控制器 - 负责参数验证和业务逻辑协调
"""

from fastapi import Body, Form, Path, Query
from fastapi.responses import JSONResponse

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
from Modules.content.services.tag_service import TagService
from Modules.content.validators.tag_validator import TagAddUpdateRequest


class TagController:
    """Content文章标签管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化文章标签管理控制器"""
        self.tag_service = TagService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        name: str | None = Query(None, description="标签名称"),
        slug: str | None = Query(None, description="标签别名"),
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
        """获取标签列表或搜索标签（统一接口）"""
        return await self.tag_service.index(
            {
                "page": page,
                "limit": limit,
                "name": name,
                "slug": slug,
                "status": status,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(TagAddUpdateRequest)
    async def add(
        self,
        name: str = Form(..., description="标签名称"),
        slug: str = Form(..., description="标签别名"),
        color: str | None = Form(None, description="标签颜色"),
        sort: int = Form(0, description="排序"),
        status: int = Form(1, description="状态"),
    ) -> JSONResponse:
        """标签添加"""
        return await self.tag_service.add(
            {
                "name": name,
                "slug": slug,
                "color": color,
                "sort": sort,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="标签ID")) -> JSONResponse:
        """获取标签信息（用于编辑）"""
        return await self.tag_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(TagAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="标签ID"),
        name: str = Form(..., description="标签名称"),
        slug: str = Form(..., description="标签别名"),
        color: str | None = Form(None, description="标签颜色"),
        sort: int = Form(..., description="排序"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """更新标签信息"""
        return await self.tag_service.update(
            id,
            {
                "name": name,
                "slug": slug,
                "color": color,
                "sort": sort,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="标签ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """标签状态"""
        return await self.tag_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_sort(
        self,
        id: int = Path(..., description="标签ID"),
        sort: int = Form(..., description="排序"),
    ) -> JSONResponse:
        """标签排序"""
        return await self.tag_service.set_sort(
            id,
            {
                "sort": sort,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="标签ID"),
    ) -> JSONResponse:
        """标签删除"""
        return await self.tag_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """标签批量删除"""
        return await self.tag_service.destroy_all(request.id_array)
