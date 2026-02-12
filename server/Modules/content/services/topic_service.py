"""
Content 话题服务 - 负责话题抓取和管理的业务逻辑
"""

import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime, now
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.content.models.content_platform_account import ContentPlatformAccount
from Modules.content.models.content_topic import ContentTopic
from Modules.content.services.publisher import ZhihuHandler


class TopicService(BaseService):
    """Content话题服务 - 负责话题抓取和管理的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def fetch_topics(
        self, platform: str, platform_account_id: int, limit: int = 20
    ) -> JSONResponse:
        """从指定平台获取推荐话题（同步执行）

        Args:
            platform: 平台标识（zhihu）
            platform_account_id: 平台账号ID
            limit: 获取数量

        Returns:
            JSONResponse: 抓取结果
        """
        # 1. 验证平台账号
        async with get_async_session() as session:
            account_result = await session.execute(
                select(ContentPlatformAccount).where(
                    ContentPlatformAccount.id == platform_account_id,
                    ContentPlatformAccount.platform == platform,
                    ContentPlatformAccount.status == 1,  # 1=有效
                )
            )
            account = account_result.scalar_one_or_none()

            if not account:
                return error("平台账号不存在或已失效")

            # 2. 解析 Cookies
            try:
                cookies = json.loads(account.cookies) if account.cookies else []
            except json.JSONDecodeError:
                return error("Cookie 格式错误，无法解析")

            # 3. 获取对应的处理器
            handlers = {
                "zhihu": ZhihuHandler,
            }

            handler_class = handlers.get(platform)
            if not handler_class:
                return error(f"不支持的平台: {platform}")

            # 4. 执行抓取（同步等待完成）
            try:
                handler = handler_class(cookies=cookies, user_agent=account.user_agent)
                questions = await handler.fetch_recommended_questions(limit=limit)

                # 5. 存储到数据库（去重）
                created_count = 0
                updated_count = 0
                skipped_count = 0

                for q in questions:
                    # 检查是否已存在
                    existing = await session.execute(
                        select(ContentTopic).where(
                            ContentTopic.platform == platform,
                            ContentTopic.platform_question_id == q["question_id"],
                        )
                    )
                    existing_topic = existing.scalar_one_or_none()

                    topic_data = {
                        "platform": platform,
                        "platform_question_id": q["question_id"],
                        "title": q["title"],
                        "description": q.get("description"),
                        "url": q.get("url"),
                        "view_count": q.get("view_count", 0),
                        "answer_count": q.get("answer_count", 0),
                        "follower_count": q.get("follower_count", 0),
                        "category": q.get("category"),
                        "hot_score": q.get("hot_score"),
                        "author_name": q.get("author_name"),
                        "author_url": None,
                        "fetched_at": now(),
                    }

                    if existing_topic:
                        # 更新已存在的话题
                        for key, value in topic_data.items():
                            setattr(existing_topic, key, value)
                        updated_count += 1
                    else:
                        # 创建新话题
                        new_topic = ContentTopic(**topic_data)
                        new_topic.created_at = now()
                        session.add(new_topic)
                        created_count += 1

                await session.commit()

                return success(
                    {
                        "total": len(questions),
                        "created": created_count,
                        "updated": updated_count,
                        "skipped": skipped_count,
                        "platform": platform,
                        "message": f"成功抓取 {len(questions)} 个话题（新增 {created_count} 个，更新 {updated_count} 个）",
                    }
                )

            except Exception as e:
                return error(f"抓取失败: {str(e)}")

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取话题列表或搜索话题（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["title", "category", "author_name"]
        # 精确匹配字段字典
        data["exact_fields"] = ["platform", "status"]
        # 应用范围筛选
        data["range_fields"] = ["hot_score", "view_count", "answer_count", "fetched_at"]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(ContentTopic)

            # 搜索
            query = await self.apply_search_filters(query, ContentTopic, data)

            # 应用排序（默认按热度降序）
            if not data.get("sort"):
                query = query.order_by(ContentTopic.hot_score.desc())  # type: ignore
            else:
                query = await self.apply_sorting(query, ContentTopic, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for topic in page_data.items:
                d = topic.__dict__.copy()
                d["fetched_at"] = (
                    format_datetime(topic.fetched_at) if topic.fetched_at else None
                )
                d["created_at"] = (
                    format_datetime(topic.created_at) if topic.created_at else None
                )
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

    async def detail(self, id: int) -> JSONResponse:
        """获取话题详情"""
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

            info = {
                "id": topic.id,
                "platform": topic.platform,
                "platform_question_id": topic.platform_question_id,
                "title": topic.title,
                "description": topic.description,
                "url": topic.url,
                "view_count": topic.view_count,
                "answer_count": topic.answer_count,
                "follower_count": topic.follower_count,
                "category": topic.category,
                "hot_score": topic.hot_score,
                "author_name": topic.author_name,
                "author_url": topic.author_url,
                "status": topic.status,
                "fetched_at": format_datetime(topic.fetched_at)
                if topic.fetched_at
                else None,
                "created_at": format_datetime(topic.created_at)
                if topic.created_at
                else None,
            }

            return success(info)

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """话题状态"""
        return await self.common_update(id=id, data=data, model_class=ContentTopic)

    async def destroy(self, id: int) -> JSONResponse:
        """删除话题"""
        return await self.common_destroy(id=id, model_class=ContentTopic)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """批量删除话题"""
        return await self.common_destroy_all(
            id_array=id_array, model_class=ContentTopic
        )
