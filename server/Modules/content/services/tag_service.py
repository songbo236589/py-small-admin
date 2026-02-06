"""
Content 文章标签服务 - 负责文章标签相关的业务逻辑
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
from Modules.content.models.content_tag import ContentTag


class TagService(BaseService):
    """Content文章标签服务 - 负责文章标签相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取标签列表或搜索标签（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["name", "slug"]
        # 精确匹配字段字典
        data["exact_fields"] = ["status"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at"]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(ContentTag)
            # 搜索
            query = await self.apply_search_filters(query, ContentTag, data)

            # 应用排序
            query = await self.apply_sorting(query, ContentTag, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for tag in page_data.items:
                d = tag.__dict__.copy()
                d["created_at"] = (
                    format_datetime(tag.created_at) if tag.created_at else None
                )
                d["updated_at"] = (
                    format_datetime(tag.updated_at) if tag.updated_at else None
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

    async def add(self, data: dict[str, Any]) -> JSONResponse:
        """添加标签"""
        return await self.common_add(
            data=data,
            model_class=ContentTag,
            pre_operation_callback=self._tag_add_pre_operation,
        )

    async def _tag_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """标签添加前置操作

        Args:
            data: 标签数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        name = data.get("name")
        slug = data.get("slug")

        # 检查标签名称是否已存在
        existing_name = await session.execute(
            select(ContentTag).where(ContentTag.name == name)
        )
        if existing_name.scalar_one_or_none():
            return error("标签名称已存在")

        # 检查标签别名是否已存在
        existing_slug = await session.execute(
            select(ContentTag).where(ContentTag.slug == slug)
        )
        if existing_slug.scalar_one_or_none():
            return error("标签别名已存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """获取标签信息（用于编辑）"""
        async with get_async_session() as session:
            result = await session.execute(
                select(
                    *[
                        ContentTag.id,
                        ContentTag.name,
                        ContentTag.slug,
                        ContentTag.color,
                        ContentTag.sort,
                        ContentTag.status,
                    ]
                ).where(ContentTag.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("标签不存在")

            return success(dict(info))

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新标签信息"""
        return await self.common_update(
            id=id,
            data=data,
            model_class=ContentTag,
            pre_operation_callback=self._tag_update_pre_operation,
        )

    async def _tag_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """标签更新前置操作

        Args:
            id: 标签ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        name = data.get("name")
        slug = data.get("slug")

        # 检查标签名称是否已被其他标签使用
        if name:
            existing_name = await session.execute(
                select(ContentTag).where(ContentTag.name == name)
            )
            tag_with_name = existing_name.scalar_one_or_none()
            if tag_with_name and tag_with_name.id != id:
                return error("标签名称已存在")

        # 检查标签别名是否已被其他标签使用
        if slug:
            existing_slug = await session.execute(
                select(ContentTag).where(ContentTag.slug == slug)
            )
            tag_with_slug = existing_slug.scalar_one_or_none()
            if tag_with_slug and tag_with_slug.id != id:
                return error("标签别名已存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """标签状态"""
        return await self.common_update(id=id, data=data, model_class=ContentTag)

    async def set_sort(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """标签排序"""
        return await self.common_update(id=id, data=data, model_class=ContentTag)

    async def destroy(self, id: int) -> JSONResponse:
        """标签删除"""
        return await self.common_destroy(
            id=id,
            model_class=ContentTag,
            pre_operation_callback=self._tag_destroy_pre_operation,
        )

    async def _tag_destroy_pre_operation(
        self, id: int, session: Any
    ) -> tuple[Any] | JSONResponse:
        """标签删除前置操作 - 检查是否有关联文章

        Args:
            id: 标签ID
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(session,)
        """
        from Modules.content.models.content_article_tag import ContentArticleTag

        # 检查是否有关联的文章
        articles = await session.execute(
            select(ContentArticleTag).where(ContentArticleTag.tag_id == id)
        )
        if articles.scalar_one_or_none():
            return error("该标签已关联文章，无法删除")

        return (session,)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """标签批量删除"""
        return await self.common_destroy_all(
            id_array=id_array,
            model_class=ContentTag,
            pre_operation_callback=self._tag_destroy_all_pre_operation,
        )

    async def _tag_destroy_all_pre_operation(
        self, id_array: list[int], session: Any
    ) -> tuple[list[int], Any] | JSONResponse:
        """标签批量删除前置操作 - 检查是否有关联文章

        Args:
            id_array: 标签ID数组
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(id_array, session)
        """
        from Modules.content.models.content_article_tag import ContentArticleTag

        # 检查是否有关联的文章
        articles = await session.execute(
            select(ContentArticleTag).where(ContentArticleTag.tag_id.in_(id_array))  # type: ignore
        )
        if articles.scalar_one_or_none():
            return error("所选标签中已关联文章，无法删除")

        return id_array, session
