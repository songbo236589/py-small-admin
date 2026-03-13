"""
Content 话题管理控制器 - 负责参数验证和业务逻辑协调
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
from Modules.content.services.topic_service import TopicService
from Modules.content.validators.topic_validator import (
    BatchUpdateCategoryRequest,
    GenerateDescriptionRequest,
    UpdateCategoryRequest,
    UpdateDescriptionRequest,
)


class TopicController:
    """Content话题管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化话题管理控制器"""
        self.topic_service = TopicService()

    @validate_request_data(PaginationRequest)
    async def index(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        platform: str | None = Query(None, description="平台标识"),
        status: int | None = Query(None, description="状态"),
        category: str | None = Query(None, description="分类"),
        category_id: str | int | None = Query(None, description="分类ID"),
        has_description: str | None = Query(None, description="描述状态：all/has/none"),
        sort: str | None = Query(None, description="排序规则"),
    ) -> JSONResponse:
        """获取话题列表或搜索话题（统一接口）"""
        return await self.topic_service.index(
            {
                "page": page,
                "limit": limit,
                "platform": platform,
                "status": status,
                "category": category,
                "category_id": category_id,
                "has_description": has_description,
                "sort": sort,
            }
        )

    async def fetch(
        self,
        platform: str = Form(..., description="平台标识"),
        platform_account_id: int = Form(..., description="平台账号ID"),
        limit: int = Form(20, description="抓取数量"),
    ) -> JSONResponse:
        """抓取平台推荐话题（同步执行，预计耗时 10-30 秒）"""
        return await self.topic_service.fetch_topics(
            platform, platform_account_id, limit
        )

    @validate_request_data(IdRequest)
    async def detail(self, id: int = Path(..., description="话题ID")) -> JSONResponse:
        """获取话题详情"""
        return await self.topic_service.detail(id)

    @validate_request_data(IdRequest)
    @validate_request_data(ListStatusRequest)
    async def set_status(
        self,
        id: int = Path(..., description="话题ID"),
        status: int = Form(..., description="状态"),
    ) -> JSONResponse:
        """话题状态"""
        return await self.topic_service.set_status(
            id,
            {
                "status": status,
            },
        )

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="话题ID"),
    ) -> JSONResponse:
        """删除话题"""
        return await self.topic_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """批量删除话题"""
        return await self.topic_service.destroy_all(request.id_array)

    @validate_body_data(BatchUpdateCategoryRequest)
    async def batch_update_category(
        self,
        request: BatchUpdateCategoryRequest = Body(...),
    ) -> JSONResponse:
        """批量更新话题分类"""
        return await self.topic_service.batch_update_category(
            request.id_array, request.category_id
        )

    @validate_request_data(IdRequest)
    @validate_request_data(GenerateDescriptionRequest)
    async def generate_description(
        self,
        id: int = Path(..., description="话题ID"),
        model: str | None = Form(None, description="AI 模型（可选）"),
    ) -> JSONResponse:
        """AI 生成话题描述"""
        return await self.topic_service.generate_and_update_description(id, model)

    @validate_request_data(IdRequest)
    @validate_request_data(UpdateDescriptionRequest)
    async def update_description(
        self,
        id: int = Path(..., description="话题ID"),
        description: str = Form(..., description="描述内容"),
    ) -> JSONResponse:
        """更新话题描述"""
        return await self.topic_service.update_description(id, description)

    @validate_request_data(IdRequest)
    @validate_request_data(UpdateCategoryRequest)
    async def update_category(
        self,
        id: int = Path(..., description="话题ID"),
        category_id: int | None = Form(None, description="分类ID"),
    ) -> JSONResponse:
        """更新话题分类"""
        return await self.topic_service.update_category(id, category_id)

    @validate_request_data(IdRequest)
    @validate_request_data(GenerateDescriptionRequest)
    async def generate_category(
        self,
        id: int = Path(..., description="话题ID"),
        model: str | None = Form(None, description="AI 模型（可选）"),
    ) -> JSONResponse:
        """AI 生成话题分类"""
        return await self.topic_service.generate_and_update_category(id, model)

    @validate_request_data(IdRequest)
    async def fetch_zhihu_content(
        self,
        id: int = Path(..., description="话题ID"),
    ) -> JSONResponse:
        """手动抓取知乎问题内容"""
        return await self.topic_service.fetch_zhihu_content(id)
