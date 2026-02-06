"""
Content 发布服务 - 负责文章发布相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.content.models.content_article import ContentArticle
from Modules.content.models.content_platform_account import ContentPlatformAccount
from Modules.content.models.content_publish_log import ContentPublishLog


class PublishService(BaseService):
    """Content发布服务 - 负责文章发布相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def publish_article(self, data: dict[str, Any]) -> JSONResponse:
        """发布单篇文章到指定平台

        Args:
            data: 包含 platform, account_id, article_id 的字典

        Returns:
            JSONResponse: 发布结果
        """
        platform = data.get("platform")
        account_id = data.get("account_id", 0)
        article_id = data.get("article_id", 0)

        async with get_async_session() as session:
            # 验证文章是否存在
            article_result = await session.execute(
                select(ContentArticle).where(ContentArticle.id == article_id)
            )
            article = article_result.scalar_one_or_none()
            if not article:
                return error("文章不存在")

            # 验证平台账号是否存在且匹配
            account_result = await session.execute(
                select(ContentPlatformAccount).where(
                    ContentPlatformAccount.id == account_id,
                    ContentPlatformAccount.platform == platform,
                )
            )
            account = account_result.scalar_one_or_none()
            if not account:
                return error("平台账号不存在或不匹配")

            # 检查是否已有待发布或发布中的任务
            existing_log = await session.execute(
                select(ContentPublishLog).where(
                    ContentPublishLog.article_id == article_id,
                    ContentPublishLog.platform == platform,
                    ContentPublishLog.status.in_(  # type: ignore
                        [0, 1]
                    ),  # 0=待发布, 1=发布中
                )
            )
            if existing_log.scalar_one_or_none():
                return error("该文章已有正在进行的发布任务")

            # 创建发布日志
            publish_log = ContentPublishLog(
                article_id=article_id,
                platform=platform,  # type: ignore
                status=0,  # 待发布
            )
            session.add(publish_log)
            await session.commit()
            await session.refresh(publish_log)

            # TODO: 创建异步发布任务
            # 这里需要调用 Celery 任务队列进行异步发布
            # 示例：
            # from Modules.content.queues.publish_queue import publish_article_task
            # task = publish_article_task.delay(publish_log.id, article_id, platform, account_id)
            # publish_log.task_id = task.id
            # await session.commit()

            return success(
                {
                    "log_id": publish_log.id,
                    "article_id": article_id,
                    "platform": platform,
                    "status": publish_log.status,
                    "message": "发布任务已创建，正在排队处理",
                }
            )

    async def publish_batch(self, data: dict[str, Any]) -> JSONResponse:
        """批量发布多篇文章

        Args:
            data: 包含 platform, article_ids 的字典

        Returns:
            JSONResponse: 批量发布结果
        """
        platform = data.get("platform")
        article_ids = data.get("article_ids", [])

        async with get_async_session() as session:
            # 验证所有文章是否存在
            articles_result = await session.execute(
                select(ContentArticle.id, ContentArticle.title).where(
                    ContentArticle.id.in_(article_ids)  # type: ignore
                )
            )
            articles = articles_result.all()

            if len(articles) != len(article_ids):
                return error("部分文章不存在")

            # 查找该平台可用的账号
            account_result = await session.execute(
                select(ContentPlatformAccount).where(
                    ContentPlatformAccount.platform == platform,
                    ContentPlatformAccount.status == 1,  # 有效状态
                )
            )
            accounts = account_result.scalars().all()

            if not accounts:
                return error("该平台没有可用的账号，请先添加平台账号")

            # 创建发布日志
            logs = []
            for article_id, _article_title in articles:
                # 检查是否已有待发布或发布中的任务
                existing_log = await session.execute(
                    select(ContentPublishLog).where(
                        ContentPublishLog.article_id == article_id,
                        ContentPublishLog.platform == platform,
                        ContentPublishLog.status.in_([0, 1]),  # type: ignore
                    )
                )
                if existing_log.scalar_one_or_none():
                    continue

                publish_log = ContentPublishLog(
                    article_id=article_id,
                    platform=platform,  # type: ignore
                    status=0,  # 待发布
                )
                session.add(publish_log)
                logs.append(publish_log)

            await session.commit()

            # TODO: 创建批量异步发布任务
            # 示例：
            # from Modules.content.queues.publish_queue import publish_batch_task
            # task = publish_batch_task.delay([log.id for log in logs], platform, account.id)
            # for log in logs:
            #     log.task_id = task.id
            # await session.commit()

            return success(
                {
                    "total": len(articles),
                    "created": len(logs),
                    "skipped": len(articles) - len(logs),
                    "platform": platform,
                    "message": f"已创建 {len(logs)} 个发布任务",
                }
            )

    async def logs(self, data: dict[str, Any]) -> JSONResponse:
        """获取发布记录列表"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 精确匹配字段字典
        data["exact_fields"] = ["platform", "status", "article_id"]
        # 应用范围筛选
        data["range_fields"] = ["created_at"]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(ContentPublishLog)
            # 搜索
            query = await self.apply_search_filters(query, ContentPublishLog, data)

            # 应用排序（默认按创建时间倒序）
            if not data.get("sort"):
                query = query.order_by(ContentPublishLog.created_at.desc())  # type: ignore
            else:
                query = await self.apply_sorting(
                    query, ContentPublishLog, data.get("sort")
                )

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for log in page_data.items:
                d = log.__dict__.copy()
                d["created_at"] = (
                    format_datetime(log.created_at) if log.created_at else None
                )
                # 获取文章标题
                article_result = await session.execute(
                    select(ContentArticle.title).where(
                        ContentArticle.id == log.article_id
                    )
                )
                d["article_title"] = article_result.scalar_one_or_none()
                items.append(d)
            return success(
                jsonable_encoder(
                    {
                        "items": items,
                        "total": page_data.total,
                        "page": page_data.page,
                        "size": page_data.size,
                        "pages": page_data.pages,
                    }
                )
            )

    async def log_detail(self, id: int) -> JSONResponse:
        """获取发布记录详情"""
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentPublishLog).where(ContentPublishLog.id == id)
            )
            log = result.scalar_one_or_none()

            if not log:
                return error("发布记录不存在")

            # 获取文章信息
            article_result = await session.execute(
                select(ContentArticle.id, ContentArticle.title).where(
                    ContentArticle.id == log.article_id
                )
            )
            article = article_result.first()

            info = {
                "id": log.id,
                "article_id": log.article_id,
                "article_title": article[1] if article else None,
                "platform": log.platform,
                "platform_article_id": log.platform_article_id,
                "platform_url": log.platform_url,
                "status": log.status,
                "error_message": log.error_message,
                "retry_count": log.retry_count,
                "task_id": log.task_id,
                "created_at": format_datetime(log.created_at)
                if log.created_at
                else None,
            }

            return success(info)

    async def retry(self, id: int) -> JSONResponse:
        """重试失败的发布

        Args:
            id: 发布日志ID

        Returns:
            JSONResponse: 重试结果
        """
        async with get_async_session() as session:
            # 获取发布日志
            log_result = await session.execute(
                select(ContentPublishLog).where(ContentPublishLog.id == id)
            )
            log = log_result.scalar_one_or_none()

            if not log:
                return error("发布记录不存在")

            # 检查状态，只有失败的任务才能重试
            if log.status != 3:  # 3=失败
                return error("只能重试失败的发布任务")

            # 检查重试次数
            if log.retry_count >= 3:
                return error("重试次数已达上限，请检查配置或手动处理")

            # 更新状态为待发布
            log.status = 0  # 待发布
            log.retry_count += 1
            log.error_message = None
            await session.commit()

            # TODO: 创建重试发布任务
            # 示例：
            # from Modules.content.queues.publish_queue import publish_article_task
            # task = publish_article_task.delay(log.id, log.article_id, log.platform, account_id)
            # log.task_id = task.id
            # await session.commit()

            return success(
                {
                    "log_id": log.id,
                    "retry_count": log.retry_count,
                    "message": "重试任务已创建",
                }
            )
