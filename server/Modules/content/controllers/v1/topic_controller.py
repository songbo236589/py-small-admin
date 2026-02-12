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
