"""
Content 文章服务 - 负责文章相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import selectinload
from sqlmodel import select

from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime, now
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.content.models.content_article import ContentArticle
from Modules.content.models.content_article_tag import ContentArticleTag
from Modules.content.models.content_category import ContentCategory
from Modules.content.models.content_tag import ContentTag
from Modules.content.models.content_topic import ContentTopic


class ArticleService(BaseService):
    """Content文章服务 - 负责文章相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取文章列表或搜索文章（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["title", "summary"]
        # 精确匹配字段字典
        data["exact_fields"] = ["status", "category_id", "topic_id", "author_id"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at", "published_at"]

        async with get_async_session() as session:
            # 构建基础查询，使用 selectinload 预加载关联数据，只加载需要的字段
            query = select(ContentArticle).options(
                selectinload(ContentArticle.category).load_only(
                    *[ContentCategory.id, ContentCategory.name]
                ),
                selectinload(ContentArticle.topic).load_only(
                    *[ContentTopic.id, ContentTopic.title]
                ),
                selectinload(ContentArticle.tags).load_only(
                    *[ContentTag.id, ContentTag.name, ContentTag.color]
                ),
            )

            # 标签筛选（需要join中间表）
            tag_id = data.get("tag_id")
            if tag_id:
                query = query.join(ContentArticleTag, ContentArticleTag.article_id == ContentArticle.id)  # type: ignore
                query = query.filter(ContentArticleTag.tag_id == tag_id)

            # 搜索
            query = await self.apply_search_filters(query, ContentArticle, data)

            # 应用排序
            query = await self.apply_sorting(query, ContentArticle, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for article in page_data.items:
                d = article.__dict__.copy()
                # 格式化时间
                d["created_at"] = (
                    format_datetime(article.created_at) if article.created_at else None
                )
                d["updated_at"] = (
                    format_datetime(article.updated_at) if article.updated_at else None
                )
                d["published_at"] = (
                    format_datetime(article.published_at)
                    if article.published_at
                    else None
                )
                # 获取分类名称
                d["category_name"] = article.category.name if article.category else None
                # 获取话题标题
                d["topic_title"] = article.topic.title if article.topic else None
                # 获取标签列表（完整对象）
                d["tags"] = [
                    {"id": tag.id, "name": tag.name, "color": tag.color}
                    for tag in article.tags
                ]
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

    async def add(self, data: dict[str, Any]) -> JSONResponse:
        """添加文章"""
        return await self.common_add(
            data=data,
            model_class=ContentArticle,
            pre_operation_callback=self._article_add_pre_operation,
            post_operation_callback=self._article_add_post_operation,
        )

    async def _article_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """文章添加前置操作

        Args:
            data: 文章数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        # 验证分类是否存在
        category_id = data.get("category_id")
        if category_id and category_id > 0:
            category = await session.execute(
                select(ContentCategory).where(ContentCategory.id == category_id)
            )
            if not category.scalar_one_or_none():
                return error("分类不存在")

        # 验证标签是否存在
        tag_ids = data.get("tag_ids")
        if tag_ids and len(tag_ids) > 0:
            tags = await session.execute(
                select(ContentTag.id).where(ContentTag.id.in_(tag_ids))  # type: ignore
            )
            valid_tag_ids = set(tags.scalars().all())
            invalid_tag_ids = set(tag_ids) - valid_tag_ids
            if invalid_tag_ids:
                return error(f"标签不存在: {', '.join(map(str, invalid_tag_ids))}")
            data["tag_ids"] = list(valid_tag_ids)

        return data, session

    async def _article_add_post_operation(
        self, instance: ContentArticle, data: dict[str, Any], session: Any
    ) -> None:
        """文章添加后置操作 - 关联标签

        Args:
            instance: 创建的文章实例
            data: 原始数据
            session: 数据库会话
        """
        from loguru import logger

        logger.info(f"[_article_add_post_operation] 开始处理文章标签, article_id={instance.id}")
        logger.debug(f"[_article_add_post_operation] 输入数据: tag_names={data.get('tag_names')}, tag_ids={data.get('tag_ids')}")

        # 优先处理 AI 生成的标签名称
        tag_names = data.get("tag_names")
        if tag_names and len(tag_names) > 0:
            logger.info(f"[_article_add_post_operation] 处理 AI 生成的标签名称: {tag_names}")
            created_count = 0
            existing_count = 0

            for tag_name in tag_names:
                # 检查标签是否已存在
                existing_tag = await session.execute(
                    select(ContentTag).where(ContentTag.name == tag_name)
                )
                tag = existing_tag.scalar_one_or_none()

                if not tag:
                    # 创建新标签
                    logger.debug(f"[_article_add_post_operation] 创建新标签: {tag_name}")
                    tag = ContentTag(
                        name=tag_name,
                        slug=tag_name,  # 直接使用 name 作为 slug
                        status=1,
                        sort=999,
                        created_at=now(),
                        updated_at=now(),
                    )
                    session.add(tag)
                    await session.commit()
                    await session.refresh(tag)
                    created_count += 1
                else:
                    logger.debug(f"[_article_add_post_operation] 使用现有标签: {tag_name} (ID: {tag.id})")
                    existing_count += 1

                # 创建文章-标签关联
                article_tag = ContentArticleTag(article_id=instance.id, tag_id=tag.id)  # type: ignore
                session.add(article_tag)
                logger.debug(f"[_article_add_post_operation] 创建文章-标签关联: article_id={instance.id}, tag_id={tag.id}")

            await session.commit()
            logger.info(f"[_article_add_post_operation] AI 标签处理完成 - 创建: {created_count}, 已存在: {existing_count}")
            return

        # 兼容原有的 tag_ids 逻辑
        tag_ids = data.get("tag_ids")
        if tag_ids and len(tag_ids) > 0:
            logger.info(f"[_article_add_post_operation] 处理手动选择的标签 IDs: {tag_ids}")
            # 创建文章标签关联
            for tag_id in tag_ids:
                article_tag = ContentArticleTag(article_id=instance.id, tag_id=tag_id)  # type: ignore
                session.add(article_tag)
                logger.debug(f"[_article_add_post_operation] 创建文章-标签关联: article_id={instance.id}, tag_id={tag_id}")
            await session.commit()
            logger.info(f"[_article_add_post_operation] 手动标签处理完成 - 数量: {len(tag_ids)}")

        # 更新话题的文章数量（如果有关联话题）
        if instance.topic_id:
            await self._update_topic_article_count(instance.topic_id, session)

    async def edit(self, id: int) -> JSONResponse:
        """获取文章信息（用于编辑）"""
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentArticle).where(ContentArticle.id == id)
            )
            article = result.scalar_one_or_none()

            if not article:
                return error("文章不存在")

            # 获取关联的标签
            tag_query = (
                select(ContentTag.id, ContentTag.name)
                .join(ContentArticleTag, ContentArticleTag.tag_id == ContentTag.id)  # type: ignore
                .where(ContentArticleTag.article_id == id)
            )
            tag_result = await session.execute(tag_query)
            tags = tag_result.all()

            info = {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "summary": article.summary,
                "cover_image_id": article.cover_image_id,
                "category_id": article.category_id,
                "status": article.status,
                "tag_ids": [tag.id for tag in tags],
                "tags": [{"id": tag.id, "name": tag.name} for tag in tags],
            }

            return success(info)

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新文章信息"""
        return await self.common_update(
            id=id,
            data=data,
            model_class=ContentArticle,
            pre_operation_callback=self._article_update_pre_operation,
            post_operation_callback=self._article_update_post_operation,
        )

    async def _article_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """文章更新前置操作

        Args:
            id: 文章ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        # 查询当前文章，保存旧的 topic_id（用于后续更新文章数量）
        article = await session.execute(select(ContentArticle).where(ContentArticle.id == id))
        article = article.scalar_one_or_none()
        if article:
            data["_old_topic_id"] = article.topic_id

        # 验证分类是否存在
        category_id = data.get("category_id")
        if category_id is not None and category_id > 0:
            category = await session.execute(
                select(ContentCategory).where(ContentCategory.id == category_id)
            )
            if not category.scalar_one_or_none():
                return error("分类不存在")

        # 验证标签是否存在
        tag_ids = data.get("tag_ids")
        if tag_ids is not None:
            if len(tag_ids) > 0:
                tags = await session.execute(
                    select(ContentTag.id).where(ContentTag.id.in_(tag_ids))  # type: ignore
                )
                valid_tag_ids = set(tags.scalars().all())
                invalid_tag_ids = set(tag_ids) - valid_tag_ids
                if invalid_tag_ids:
                    return error(f"标签不存在: {', '.join(map(str, invalid_tag_ids))}")
                data["tag_ids"] = list(valid_tag_ids)
            else:
                data["tag_ids"] = []

        return data, session

    async def _article_update_post_operation(
        self, instance: ContentArticle, data: dict[str, Any], session: Any
    ) -> None:
        """文章更新后置操作 - 更新标签关联和话题文章数量

        Args:
            instance: 更新的文章实例
            data: 原始数据
            session: 数据库会话
        """
        # 如果数据中包含 tag_ids，则更新标签关联
        if "tag_ids" in data:
            tag_ids = data.get("tag_ids", [])

            # 删除现有的标签关联
            await session.execute(
                select(ContentArticleTag).where(
                    ContentArticleTag.article_id == instance.id
                )
            )
            # 使用 delete 方式
            from sqlalchemy import delete

            await session.execute(
                delete(ContentArticleTag).where(
                    ContentArticleTag.article_id == instance.id  # type: ignore
                )
            )

            # 创建新的标签关联
            if tag_ids and len(tag_ids) > 0:
                for tag_id in tag_ids:
                    article_tag = ContentArticleTag(
                        article_id=instance.id,  # type: ignore
                        tag_id=tag_id,
                    )
                    session.add(article_tag)
            await session.commit()

        # 更新话题的文章数量（如果 topic_id 发生变化）
        if "topic_id" in data:
            old_topic_id = data.get("_old_topic_id")
            new_topic_id = instance.topic_id
            # 如果话题发生变化，需要更新旧话题和新话题的文章数量
            if old_topic_id != new_topic_id:
                if old_topic_id:
                    await self._update_topic_article_count(old_topic_id, session)
                if new_topic_id:
                    await self._update_topic_article_count(new_topic_id, session)

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """文章状态"""
        return await self.common_update(id=id, data=data, model_class=ContentArticle)

    async def _article_destroy_save_topic_id(self, id: int, session: Any) -> Any:
        """文章删除前置操作 - 保存 topic_id

        Args:
            id: 文章ID
            session: 数据库会话
        """
        # 查询文章，获取 topic_id 并保存到临时存储
        topic_id = await session.execute(
            select(ContentArticle.topic_id).where(ContentArticle.id == id)
        )
        topic_id = topic_id.scalar_one_or_none()
        if topic_id:
            # 保存到 session 的上下文中，供后置操作使用
            if not hasattr(session, '_destroy_topic_ids'):
                session._destroy_topic_ids = []
            session._destroy_topic_ids.append(topic_id)

    async def _article_destroy_post_operation(self, _id: int, session: Any) -> Any:
        """文章删除后置操作 - 更新话题文章数量

        Args:
            id: 文章ID
            session: 数据库会话
        """
        # 从临时存储中获取 topic_id 并更新
        if hasattr(session, '_destroy_topic_ids') and session._destroy_topic_ids:
            for topic_id in session._destroy_topic_ids:
                await self._update_topic_article_count(topic_id, session)
            delattr(session, '_destroy_topic_ids')

    async def destroy(self, id: int) -> JSONResponse:
        """文章删除"""
        return await self.common_destroy(
            id=id,
            model_class=ContentArticle,
            pre_operation_callback=self._article_destroy_save_topic_id,
            post_operation_callback=self._article_destroy_post_operation,
        )

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """文章批量删除"""
        return await self.common_destroy_all(
            id_array=id_array,
            model_class=ContentArticle,
            pre_operation_callback=self._article_destroy_all_save_topic_ids,
            post_operation_callback=self._article_destroy_all_post_operation,
        )

    async def _article_destroy_all_save_topic_ids(self, id_array: list[int], session: Any) -> Any:
        """文章批量删除前置操作 - 保存 topic_id

        Args:
            id_array: 文章ID列表
            session: 数据库会话
        """
        # 查询所有文章的 topic_id
        articles = await session.execute(
            select(ContentArticle.topic_id).where(ContentArticle.id.in_(id_array))
        )
        topic_ids = {row[0] for row in articles.all() if row[0]}

        # 保存到 session 的上下文中，供后置操作使用
        session._destroy_topic_ids = list(topic_ids)

    async def _article_destroy_all_post_operation(self, _id_array: list[int], session: Any) -> Any:
        """文章批量删除后置操作 - 更新话题文章数量

        Args:
            id_array: 文章ID列表
            session: 数据库会话
        """
        # 从临时存储中获取 topic_id 并更新
        if hasattr(session, '_destroy_topic_ids') and session._destroy_topic_ids:
            for topic_id in session._destroy_topic_ids:
                await self._update_topic_article_count(topic_id, session)
            delattr(session, '_destroy_topic_ids')

    async def _update_topic_article_count(self, topic_id: int, session: Any) -> None:
        """更新话题的文章数量（统计该话题下的所有文章）

        Args:
            topic_id: 话题ID
            session: 数据库会话
        """
        from sqlalchemy import func

        # 统计该话题下的文章数量
        result = await session.execute(
            select(func.count(ContentArticle.id)).where(ContentArticle.topic_id == topic_id)
        )
        count = result.scalar() or 0

        # 更新话题表的 article_count 字段
        from Modules.content.models.content_topic import ContentTopic

        topic = await session.execute(
            select(ContentTopic).where(ContentTopic.id == topic_id)
        )
        topic = topic.scalar_one_or_none()
        if topic:
            topic.article_count = count
            await session.commit()
