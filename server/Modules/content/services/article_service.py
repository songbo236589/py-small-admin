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
from Modules.common.libs.time.utils import format_datetime
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService
from Modules.content.models.content_article import ContentArticle
from Modules.content.models.content_article_tag import ContentArticleTag
from Modules.content.models.content_category import ContentCategory
from Modules.content.models.content_tag import ContentTag


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
        data["exact_fields"] = ["status", "category_id", "author_id"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at", "published_at"]

        async with get_async_session() as session:
            # 构建基础查询，使用 selectinload 预加载关联数据，只加载需要的字段
            query = select(ContentArticle).options(
                selectinload(ContentArticle.category).load_only(
                    *[ContentCategory.id, ContentCategory.name]
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
        tag_ids = data.get("tag_ids")
        if tag_ids and len(tag_ids) > 0:
            # 创建文章标签关联
            for tag_id in tag_ids:
                article_tag = ContentArticleTag(article_id=instance.id, tag_id=tag_id)  # type: ignore
                session.add(article_tag)
            await session.commit()

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
        """文章更新后置操作 - 更新标签关联

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

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """文章状态"""
        return await self.common_update(id=id, data=data, model_class=ContentArticle)

    async def destroy(self, id: int) -> JSONResponse:
        """文章删除"""
        return await self.common_destroy(id=id, model_class=ContentArticle)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """文章批量删除"""
        return await self.common_destroy_all(
            id_array=id_array, model_class=ContentArticle
        )
