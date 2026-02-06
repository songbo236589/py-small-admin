"""
Content 文章分类服务 - 负责文章分类相关的业务逻辑
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
from Modules.content.models.content_category import ContentCategory


class CategoryService(BaseService):
    """Content文章分类服务 - 负责文章分类相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def tree(self, status: int | None = None) -> JSONResponse:
        """获取分类树形结构

        Args:
            status: 可选，1=只返回启用的分类，0=只返回禁用的分类，None=返回所有分类（默认）
        """
        async with get_async_session() as session:
            # 构建查询
            query = select(ContentCategory).order_by(ContentCategory.sort.asc())  # type: ignore

            # 根据 status 参数过滤
            if status is not None:
                query = query.where(ContentCategory.status == status)  # type: ignore

            result = await session.execute(query)
            categories = list(result.scalars().all())

            # 将所有分类转换为字典格式，便于处理
            category_dict = {}
            for category in categories:
                category_dict[category.id] = {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "parent_id": category.parent_id,
                    "sort": category.sort,
                    "status": category.status,
                    "description": category.description,
                    "created_at": format_datetime(category.created_at)
                    if category.created_at
                    else None,
                    "updated_at": format_datetime(category.updated_at)
                    if category.updated_at
                    else None,
                    "value": category.id,
                    "key": category.id,
                    "title": category.name,
                    "children": [],
                }

            # 构建树形结构：遍历所有分类，将子节点添加到父节点的children中
            tree_data = []
            for category in category_dict.values():
                parent_id = category["parent_id"]
                if parent_id is None or parent_id == 0:
                    # 顶级节点，直接添加到树中
                    tree_data.append(category)
                else:
                    # 子节点，添加到父节点的children中
                    if parent_id in category_dict:
                        category_dict[parent_id]["children"].append(category)

            # 移除空的children数组
            def remove_empty_children(node):
                if not node["children"]:
                    del node["children"]
                else:
                    for child in node["children"]:
                        remove_empty_children(child)

            for node in tree_data:
                remove_empty_children(node)

            return success(jsonable_encoder(tree_data))
    """Content文章分类服务 - 负责文章分类相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取分类列表或搜索分类（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["name", "slug", "description"]
        # 精确匹配字段字典
        data["exact_fields"] = ["status", "parent_id"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at"]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(ContentCategory)
            # 搜索
            query = await self.apply_search_filters(query, ContentCategory, data)

            # 应用排序
            query = await self.apply_sorting(query, ContentCategory, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for category in page_data.items:
                d = category.__dict__.copy()
                d["created_at"] = (
                    format_datetime(category.created_at)
                    if category.created_at
                    else None
                )
                d["updated_at"] = (
                    format_datetime(category.updated_at)
                    if category.updated_at
                    else None
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
        """添加分类"""
        return await self.common_add(
            data=data,
            model_class=ContentCategory,
            pre_operation_callback=self._category_add_pre_operation,
        )

    async def _category_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """分类添加前置操作

        Args:
            data: 分类数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        name = data.get("name")
        slug = data.get("slug")

        # 检查分类名称是否已存在
        existing_name = await session.execute(
            select(ContentCategory).where(ContentCategory.name == name)
        )
        if existing_name.scalar_one_or_none():
            return error("分类名称已存在")

        # 检查分类别名是否已存在
        existing_slug = await session.execute(
            select(ContentCategory).where(ContentCategory.slug == slug)
        )
        if existing_slug.scalar_one_or_none():
            return error("分类别名已存在")

        # 检查父分类是否存在
        parent_id = data.get("parent_id")
        if parent_id and parent_id > 0:
            parent = await session.execute(
                select(ContentCategory).where(ContentCategory.id == parent_id)
            )
            if not parent.scalar_one_or_none():
                return error("父分类不存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """获取分类信息（用于编辑）"""
        async with get_async_session() as session:
            result = await session.execute(
                select(
                    *[
                        ContentCategory.id,
                        ContentCategory.name,
                        ContentCategory.slug,
                        ContentCategory.parent_id,
                        ContentCategory.sort,
                        ContentCategory.status,
                        ContentCategory.description,
                    ]
                ).where(ContentCategory.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("分类不存在")

            return success(dict(info))

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新分类信息"""
        return await self.common_update(
            id=id,
            data=data,
            model_class=ContentCategory,
            pre_operation_callback=self._category_update_pre_operation,
        )

    async def _category_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """分类更新前置操作

        Args:
            id: 分类ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        name = data.get("name")
        slug = data.get("slug")
        parent_id = data.get("parent_id")

        # 检查分类名称是否已被其他分类使用
        if name:
            existing_name = await session.execute(
                select(ContentCategory).where(ContentCategory.name == name)
            )
            category_with_name = existing_name.scalar_one_or_none()
            if category_with_name and category_with_name.id != id:
                return error("分类名称已存在")

        # 检查分类别名是否已被其他分类使用
        if slug:
            existing_slug = await session.execute(
                select(ContentCategory).where(ContentCategory.slug == slug)
            )
            category_with_slug = existing_slug.scalar_one_or_none()
            if category_with_slug and category_with_slug.id != id:
                return error("分类别名已存在")

        # 检查父分类是否存在，且不能设置自己为父分类
        if parent_id is not None:
            if parent_id == id:
                return error("不能将自己设置为父分类")
            if parent_id > 0:
                parent = await session.execute(
                    select(ContentCategory).where(ContentCategory.id == parent_id)
                )
                if not parent.scalar_one_or_none():
                    return error("父分类不存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """分类状态"""
        return await self.common_update(id=id, data=data, model_class=ContentCategory)

    async def set_sort(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """分类排序"""
        return await self.common_update(id=id, data=data, model_class=ContentCategory)

    async def destroy(self, id: int) -> JSONResponse:
        """分类删除（递归删除所有子分类）"""
        # 获取当前分类及其所有子分类的ID
        id_array = await self._get_all_children_ids(id)

        # 检查是否有关联的文章
        async with get_async_session() as session:
            from Modules.content.models.content_article import ContentArticle

            articles = await session.execute(
                select(ContentArticle).where(
                    ContentArticle.category_id.in_(id_array)  # type: ignore
                )
            )
            if articles.scalar_one_or_none():
                return error("所选分类中存在文章，无法删除")

        return await self.common_destroy_all(id_array=id_array, model_class=ContentCategory)

    async def _get_all_children_ids(self, parent_id: int) -> list[int]:
        """递归获取父分类及其所有子分类的ID

        Args:
            parent_id: 父分类ID

        Returns:
            包含父分类ID及其所有子分类ID的列表
        """
        async with get_async_session() as session:
            # 初始化结果数组，包含父分类ID
            result_ids = [parent_id]

            # 查询所有直接子分类
            query = select(ContentCategory.id).where(ContentCategory.parent_id == parent_id)
            children_result = await session.execute(query)
            children_ids = children_result.scalars().all()

            # 递归获取每个子分类的所有子分类ID
            for child_id in children_ids:
                grandchildren_ids = await self._get_all_children_ids(child_id)
                result_ids.extend(grandchildren_ids)

            return result_ids

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """分类批量删除（递归删除所有子分类）"""
        # 获取所有分类及其子分类的ID
        all_ids = []
        for category_id in id_array:
            children_ids = await self._get_all_children_ids(category_id)
            all_ids.extend(children_ids)

        # 去重
        all_ids = list(set(all_ids))

        # 检查是否有关联的文章
        async with get_async_session() as session:
            from Modules.content.models.content_article import ContentArticle

            articles = await session.execute(
                select(ContentArticle).where(
                    ContentArticle.category_id.in_(all_ids)  # type: ignore
                )
            )
            if articles.scalar_one_or_none():
                return error("所选分类中存在文章，无法删除")

        return await self.common_destroy_all(id_array=all_ids, model_class=ContentCategory)
