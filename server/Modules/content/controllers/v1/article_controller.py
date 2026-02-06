"""
Content 文章管理控制器 - 负责参数验证和业务逻辑协调
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
from Modules.content.services.article_service import ArticleService
from Modules.content.validators.article_validator import ArticleAddUpdateRequest


class ArticleController:
    """Content文章管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化文章管理控制器"""
        self.article_service = ArticleService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        title: str | None = Query(None, description="文章标题"),
        summary: str | None = Query(None, description="文章摘要"),
        status: int | None = Query(None, description="状态"),
        category_id: int | None = Query(None, description="分类ID"),
        tag_id: int | None = Query(None, description="标签ID"),
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
        """获取文章列表或搜索文章（统一接口）"""
        return await self.article_service.index(
            {
                "page": page,
                "limit": limit,
                "title": title,
                "summary": summary,
                "status": status,
                "category_id": category_id,
                "tag_id": tag_id,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
                "updated_at_start": updated_at_start,
                "updated_at_end": updated_at_end,
            }
        )

    @validate_request_data(ArticleAddUpdateRequest)
    async def add(
        self,
        title: str = Form(..., description="文章标题"),
        content: str = Form(..., description="文章内容（Markdown格式）"),
        summary: str | None = Form(None, description="文章摘要"),
        cover_image_id: int | None = Form(None, description="封面图片ID"),
        category_id: int | None = Form(None, description="分类ID"),
        tag_ids: str | None = Form(None, description="标签ID列表"),
        status: int = Form(0, description="状态"),
    ) -> JSONResponse:
        """文章添加"""
        return await self.article_service.add(
            {
                "title": title,
                "content": content,
                "summary": summary,
                "cover_image_id": cover_image_id,
                "category_id": category_id,
                "tag_ids": tag_ids,
                "status": status,
            }
        )

    @validate_request_data(IdRequest)
    async def edit(self, id: int = Path(..., description="文章ID")) -> JSONResponse:
        """获取文章信息（用于编辑）"""
        return await self.article_service.edit(id)

    @validate_request_data(IdRequest)
    @validate_request_data(ArticleAddUpdateRequest)
    async def update(
        self,
        id: int = Path(..., description="文章ID"),
        title: str = Form(..., description="文章标题"),
        content: str = Form(..., description="文章内容（Markdown格式）"),
        summary: str | None = Form(None, description="文章摘要"),
        cover_image_id: int | None = Form(None, description="封面图片ID"),
        category_id: int | None = Form(None, description="分类ID"),
        tag_ids: str | None = Form(None, description="标签ID列表"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """更新文章信息"""
        return await self.article_service.update(
            id,
            {
                "title": title,
                "content": content,
                "summary": summary,
                "cover_image_id": cover_image_id,
                "category_id": category_id,
                "tag_ids": tag_ids,
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="文章ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """文章状态"""
        return await self.article_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="文章ID"),
    ) -> JSONResponse:
        """文章删除"""
        return await self.article_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """文章批量删除"""
        return await self.article_service.destroy_all(request.id_array)
