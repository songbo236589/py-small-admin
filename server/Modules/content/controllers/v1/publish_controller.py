"""
Content 发布管理控制器 - 负责参数验证和业务逻辑协调
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
    PaginationRequest,
)
from Modules.content.services.publish_service import PublishService
from Modules.content.validators.publish_validator import (
    PublishArticleRequest,
    PublishBatchRequest,
)


class PublishController:
    """Content发布管理控制器 - 负责参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化发布管理控制器"""
        self.publish_service = PublishService()

    async def publish_article(
        self,
        article_id: int = Path(..., description="文章ID"),
        platform: str = Form(..., description="发布平台"),
        platform_account_id: int = Form(..., description="平台账号ID"),
    ) -> JSONResponse:
        """发布文章到指定平台"""
        # 验证参数
        request = PublishArticleRequest(
            platform=platform,
            platform_account_id=platform_account_id,
            article_id=article_id,
        )
        return await self.publish_service.publish_article(
            {
                "article_id": article_id,
                "platform": request.platform,
                "platform_account_id": request.platform_account_id,
            }
        )

    async def publish_batch(
        self,
        platform: str = Form(..., description="发布平台"),
        platform_account_id: int = Form(..., description="平台账号ID"),
        article_ids: str = Form(..., description="文章ID列表（逗号分隔）"),
    ) -> JSONResponse:
        """批量发布多篇文章"""
        # 将逗号分隔的字符串转换为列表
        article_ids_list = [
            int(aid.strip()) for aid in article_ids.split(",") if aid.strip().isdigit()
        ]

        # 验证参数
        request = PublishBatchRequest(
            platform=platform,
            platform_account_id=platform_account_id,
            article_ids=article_ids_list,
        )
        return await self.publish_service.publish_batch(
            {
                "platform": request.platform,
                "platform_account_id": request.platform_account_id,
                "article_ids": request.article_ids,
            }
        )

    @validate_request_data(PaginationRequest)
    async def logs(
        self,
        page: int = Query(1, description="页码"),
        limit: int = Query(20, description="每页返回多少条记录"),
        platform: str | None = Query(None, description="发布平台"),
        status: int | None = Query(None, description="状态"),
        article_id: int | None = Query(None, description="文章ID"),
        sort: str | None = Query(None, description="排序规则"),
        created_at_start: str | None = Query(
            None, alias="created_at[start]", description="创建时间开始"
        ),
        created_at_end: str | None = Query(
            None, alias="created_at[end]", description="创建时间结束"
        ),
    ) -> JSONResponse:
        """发布记录列表"""
        return await self.publish_service.logs(
            {
                "page": page,
                "limit": limit,
                "platform": platform,
                "status": status,
                "article_id": article_id,
                "sort": sort,
                "created_at_start": created_at_start,
                "created_at_end": created_at_end,
            }
        )

    @validate_request_data(IdRequest)
    async def log_detail(
        self, id: int = Path(..., description="发布记录ID")
    ) -> JSONResponse:
        """发布记录详情"""
        return await self.publish_service.log_detail(id)

    @validate_request_data(IdRequest)
    async def retry(
        self, id: int = Path(..., description="发布记录ID")
    ) -> JSONResponse:
        """重试失败发布"""
        return await self.publish_service.retry(id)

    @validate_request_data(IdRequest)
    async def destroy(
        self,
        id: int = Path(..., description="发布记录ID"),
    ) -> JSONResponse:
        """删除发布记录"""
        return await self.publish_service.destroy(id)

    @validate_body_data(IdArrayRequest)
    async def destroy_all(
        self,
        request: IdArrayRequest = Body(...),
    ) -> JSONResponse:
        """批量删除发布记录"""
        return await self.publish_service.destroy_all(request.id_array)
