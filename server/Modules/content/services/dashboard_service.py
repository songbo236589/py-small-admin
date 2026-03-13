"""
Content Dashboard 服务 - 负责内容统计相关的业务逻辑
"""

from datetime import datetime

from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlmodel import SQLModel

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import success
from Modules.common.libs.time.utils import start_of_day
from Modules.content.models.content_article import ContentArticle
from Modules.content.models.content_category import ContentCategory
from Modules.content.models.content_platform_account import ContentPlatformAccount
from Modules.content.models.content_publish_log import ContentPublishLog
from Modules.content.models.content_tag import ContentTag
from Modules.content.models.content_topic import ContentTopic


class DashboardService:
    """Content Dashboard 服务 - 负责内容统计相关的业务逻辑"""

    def __init__(self):
        pass

    async def statistics(self) -> JSONResponse:
        """获取内容统计数据"""
        async with get_async_session() as session:
            # 获取今天的开始时间
            today_start = start_of_day()

            # 文章总数
            article_count_result = await session.execute(
                select(func.count(ContentArticle.id))
            )
            article_count = article_count_result.scalar() or 0

            # 分类数量（只统计启用的）
            category_count_result = await session.execute(
                select(func.count(ContentCategory.id)).where(ContentCategory.status == 1)
            )
            category_count = category_count_result.scalar() or 0

            # 标签数量（只统计启用的）
            tag_count_result = await session.execute(
                select(func.count(ContentTag.id)).where(ContentTag.status == 1)
            )
            tag_count = tag_count_result.scalar() or 0

            # 话题数量（只统计启用的）
            topic_count_result = await session.execute(
                select(func.count(ContentTopic.id)).where(ContentTopic.status == 1)
            )
            topic_count = topic_count_result.scalar() or 0

            # 平台账号数量
            platform_account_count_result = await session.execute(
                select(func.count(ContentPlatformAccount.id))
            )
            platform_account_count = platform_account_count_result.scalar() or 0

            # 今日发布成功数（status=2 且 completed_at 在今天）
            today_publish_result = await session.execute(
                select(func.count(ContentPublishLog.id)).where(
                    ContentPublishLog.status == 2,
                    ContentPublishLog.completed_at >= today_start,
                )
            )
            today_publish = today_publish_result.scalar() or 0

            # 待发布数（status=0）
            pending_publish_result = await session.execute(
                select(func.count(ContentPublishLog.id)).where(ContentPublishLog.status == 0)
            )
            pending_publish = pending_publish_result.scalar() or 0

            # 总发布成功数（status=2）
            total_publish_result = await session.execute(
                select(func.count(ContentPublishLog.id)).where(ContentPublishLog.status == 2)
            )
            total_publish = total_publish_result.scalar() or 0

            # 构建返回数据
            data = {
                "article_count": article_count,
                "category_count": category_count,
                "tag_count": tag_count,
                "topic_count": topic_count,
                "platform_account_count": platform_account_count,
                "publish": {
                    "today": today_publish,
                    "pending": pending_publish,
                    "total": total_publish,
                },
            }

            return success(data)
