"""
Content 文章分类管理控制器 - 负责参数验证和业务逻辑协调
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
from Modules.content.services.category_service import CategoryService
from Modules.content.validators.category_validator import CategoryAddUpdateRequest


class CategoryController:
    """Content文章分类管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化文章分类管理控制器"""
        self.category_service = CategoryService()

    async def tree(
        self,
        status: int | None = Query(None, description="状态过滤：1=启用，0=禁用，None=全部")
    ) -> JSONResponse:
        """获取分类树形结构"""
        return await self.category_service.tree(status)

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        name: str | None = Query(None, description="分类名称"),
        slug: str | None = Query(None, description="分类别名"),
        status: int | None = Query(None, description="状态"),
        parent_id: int | None = Query(None, description="父分类ID"),
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
        """获取分类列表或搜索分类（统一接口）"""
        return await self.category_service.index(
            {
                "page": page,
                "limit": limit,
                "name": name,
                "slug": slug,
                "status": status,
                "parent_id": parent_id,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(CategoryAddUpdateRequest)
    async def add(
        self,
        name: str = Form(..., description="分类名称"),
        slug: str = Form(..., description="分类别名"),
        parent_id: int | None = Form(None, description="父分类ID"),
        sort: int = Form(0, description="排序"),
        status: int = Form(1, description="状态"),
        description: str | None = Form(None, description="分类描述"),
    ) -> JSONResponse:
        """分类添加"""
        return await self.category_service.add(
            {
                "name": name,
                "slug": slug,
                "parent_id": parent_id,
                "sort": sort,
                "status": status,
                "description": description,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="分类ID")) -> JSONResponse:
        """获取分类信息（用于编辑）"""
        return await self.category_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(CategoryAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="分类ID"),
        name: str = Form(..., description="分类名称"),
        slug: str = Form(..., description="分类别名"),
        parent_id: int | None = Form(None, description="父分类ID"),
        sort: int = Form(..., description="排序"),
        status: int = Form(..., description="状态"),
        description: str | None = Form(None, description="分类描述"),
    ) -> JSONResponse:
        """更新分类信息"""
        return await self.category_service.update(
            id,
            {
                "name": name,
                "slug": slug,
                "parent_id": parent_id,
                "sort": sort,
                "status": status,
                "description": description,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="分类ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """分类状态"""
        return await self.category_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_sort(
        self,
        id: int = Path(..., description="分类ID"),
        sort: int = Form(..., description="排序"),
    ) -> JSONResponse:
        """分类排序"""
        return await self.category_service.set_sort(
            id,
            {
                "sort": sort,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="分类ID"),
    ) -> JSONResponse:
        """分类删除"""
        return await self.category_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """分类批量删除"""
        return await self.category_service.destroy_all(request.id_array)
