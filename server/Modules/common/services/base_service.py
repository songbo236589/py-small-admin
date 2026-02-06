"""
基础服务类
提供所有服务类的基类，包含通用功能
"""

import json
import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlmodel import select

from Modules.common.libs.config.config import Config
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import now
from Modules.common.utils.url_helper import get_base_url


class BaseService:
    """基础服务类，所有服务类的基类"""

    def __init__(self):
        """初始化基础服务"""
        pass

    async def apply_search_filters(
        self, query, model_class, search_params: dict[str, Any]
    ) -> Any:
        """
        应用通用搜索过滤器

        Args:
            query: SQLAlchemy查询对象
            model_class: 模型类
            search_params: 搜索参数字典，包含以下可能的键：
                - text_fields: 自定义文本搜索字段列表
                - exact_fields: 精确匹配字段字典
                - range_fields: 范围字段字典

        Returns:
            SQLAlchemy查询对象
        """
        # 处理文本搜索字段（模糊匹配）
        text_fields = search_params.get("text_fields", [])

        # 应用文本搜索
        for field in text_fields:
            value = search_params.get(field)
            if value and value.strip():
                field_attr = getattr(model_class, field)
                query = query.filter(field_attr.like(f"%{value.strip()}%"))

        # 处理精确匹配字段
        exact_fields = search_params.get("exact_fields", {})

        for field in exact_fields:
            value = search_params.get(field)
            if value is not None and (not isinstance(value, bool) or value):
                field_attr = getattr(model_class, field)
                query = query.filter(field_attr == value)

        # 处理日期范围字段
        range_fields = search_params.get("range_fields", {})

        # 应用范围筛选
        for field in range_fields:
            field_attr = getattr(model_class, field)
            start_date = search_params.get(field + "_start")
            if start_date:
                query = query.filter(field_attr >= start_date)
            end_date = search_params.get(field + "_end")
            if end_date:
                query = query.filter(field_attr <= end_date)

        return query

    async def apply_sorting(self, query, model_class, sort_param: Any) -> Any:
        """
        应用排序功能

        Args:
            query: SQLAlchemy查询对象
            model_class: 模型类
            sort_param: 排序参数，可以是JSON字符串或字典，例如 {"id":"desc"} 或 "id desc"

        Returns:
            SQLAlchemy查询对象
        """
        if not sort_param:
            # 如果没有排序参数，默认使用ID倒序
            if hasattr(model_class, "id"):
                query = query.order_by(model_class.id.desc())
            return query

        try:
            # 尝试解析JSON格式的排序参数，例如 {"id":"desc"}
            sort_data = (
                json.loads(sort_param) if isinstance(sort_param, str) else sort_param
            )

            if isinstance(sort_data, dict):
                # 从字典中获取排序字段和方向
                sort_field = list(sort_data.keys())[0]
                sort_direction = sort_data[sort_field]
            else:
                # 如果不是字典，保持原来的解析方式作为后备
                sort_field, sort_direction = (
                    sort_param.split(" ", 1)
                    if " " in sort_param
                    else (sort_param, "asc")
                )
        except (json.JSONDecodeError, TypeError):
            # 如果JSON解析失败，使用原来的解析方式
            sort_field, sort_direction = (
                sort_param.split(" ", 1) if " " in sort_param else (sort_param, "asc")
            )

        # 验证排序字段是否存在
        if hasattr(model_class, sort_field):
            if sort_direction.lower() == "desc":
                query = query.order_by(getattr(model_class, sort_field).desc())
            else:
                query = query.order_by(getattr(model_class, sort_field).asc())
        else:
            # 如果排序字段不存在，默认使用ID倒序
            if hasattr(model_class, "id"):
                query = query.order_by(model_class.id.desc())

        return query

    async def common_add(
        self,
        data: dict[str, Any],
        model_class: type[Any],
        pre_operation_callback: Callable[
            [dict[str, Any], Any], Awaitable[tuple[dict[str, Any], Any] | JSONResponse]
        ]
        | None = None,
        post_operation_callback: Callable[
            [Any, dict[str, Any], Any], Awaitable[None]
        ]
        | None = None,
        success_message: str = "添加成功",
        error_message: str = "添加失败",
    ) -> JSONResponse:
        """通用添加方法

        Args:
            data: 要添加的数据
            model_class: 模型类
            pre_operation_callback: 前置操作回调函数，接收data和session参数（可选）
            post_operation_callback: 后置操作回调函数，接收instance、data和session参数（可选）
            success_message: 成功时的返回消息
            error_message: 失败时的返回消息

        Returns:
            JSONResponse: 操作结果
        """
        async with get_async_session() as session:
            # 执行前置操作回调（如果提供）
            if pre_operation_callback:
                pre_result = await pre_operation_callback(data, session)
                # 如果返回的是JSONResponse，直接返回错误信息
                if isinstance(pre_result, JSONResponse):
                    return pre_result
                # 否则，获取处理后的data和session
                data, session = pre_result

            # 维护created_at字段（如果模型有此字段且数据中没有提供）
            if hasattr(model_class, "created_at"):
                data["created_at"] = now()

            # 创建模型实例
            instance = model_class(**data)

            # 保存到数据库
            session.add(instance)
            await session.commit()
            await session.refresh(instance)

            # 执行后置操作回调（如果提供）
            if post_operation_callback:
                await post_operation_callback(instance, data, session)

            return success(None, message=success_message)

    async def common_update(
        self,
        id: int,
        data: dict[str, Any],
        model_class: type[Any],
        pre_operation_callback: Callable[
            [int, dict[str, Any], Any],
            Awaitable[tuple[dict[str, Any], Any] | JSONResponse],
        ]
        | None = None,
        field_update_callback: Callable[[Any, dict[str, Any]], None] | None = None,
        post_operation_callback: Callable[
            [Any, dict[str, Any], Any], Awaitable[None]
        ]
        | None = None,
        success_message: str = "更新成功",
        error_message: str = "记录不存在",
    ) -> JSONResponse:
        """通用更新方法

        Args:
            id: 要更新的记录ID
            data: 更新数据
            model_class: 模型类
            pre_operation_callback: 前置操作回调函数（可选）
            field_update_callback: 字段更新回调函数（可选）
            post_operation_callback: 后置操作回调函数，接收instance、data和session参数（可选）
            success_message: 成功时的返回消息
            error_message: 失败时的返回消息

        Returns:
            JSONResponse: 操作结果
        """
        async with get_async_session() as session:
            # 查询记录是否存在
            existing_record = await session.execute(
                select(model_class).where(model_class.id == id)
            )
            record = existing_record.scalar_one_or_none()

            if not record:
                return error(error_message)

            # 执行前置操作回调（如果提供）
            if pre_operation_callback:
                pre_result = await pre_operation_callback(id, data, session)
                # 如果返回的是JSONResponse，直接返回错误信息
                if isinstance(pre_result, JSONResponse):
                    return pre_result
                # 否则，获取处理后的data和session
                data, session = pre_result

            # 更新字段（如果提供了字段更新回调）
            if field_update_callback:
                field_update_callback(record, data)
            else:
                # 如果没有提供字段更新回调，直接更新提供的字段
                for key, value in data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)

            if hasattr(record, "updated_at"):
                record.updated_at = now()

            # 提交事务
            await session.commit()
            await session.refresh(record)

            # 执行后置操作回调（如果提供）
            if post_operation_callback:
                await post_operation_callback(record, data, session)

            return success(None, message=success_message)

    async def common_destroy(
        self,
        id: int,
        model_class: type[Any],
        pre_operation_callback: Callable[
            [int, Any],
            Awaitable[Any | JSONResponse],
        ]
        | None = None,
    ) -> JSONResponse:
        """通用删除方法

        Args:
            id: 要删除的记录ID
            model_class: 模型类
            pre_operation_callback: 前置操作回调函数（可选）

        Returns:
            JSONResponse: 操作结果
        """
        async with get_async_session() as session:
            # 查询记录是否存在
            existing_record = await session.execute(
                select(model_class).where(model_class.id == id)
            )
            record = existing_record.scalar_one_or_none()

            if not record:
                return error("记录不存在")

            # 执行前置操作回调（如果提供）
            if pre_operation_callback:
                pre_result = await pre_operation_callback(id, session)
                # 如果返回的是JSONResponse，直接返回错误信息
                if isinstance(pre_result, JSONResponse):
                    return pre_result

            # 删除记录
            await session.delete(record)
            await session.commit()

            return success(None, message="删除成功")

    async def common_destroy_all(
        self,
        id_array: list[int],
        model_class: type[Any],
        pre_operation_callback: Callable[
            [list[int], Any],
            Awaitable[Any | JSONResponse],
        ]
        | None = None,
    ) -> JSONResponse:
        """通用批量删除方法

        Args:
            id_array: 要删除的记录ID列表
            model_class: 模型类
            pre_operation_callback: 前置操作回调函数（可选）

        Returns:
            JSONResponse: 操作结果
        """
        async with get_async_session() as session:
            # 查询记录是否存在
            existing_records = await session.execute(
                select(model_class).where(model_class.id.in_(id_array))
            )
            records = existing_records.scalars().all()

            if not records:
                return error("没有找到可删除的记录")

            # 检查是否所有请求的ID都存在
            found_ids = [record.id for record in records]
            missing_ids = [id for id in id_array if id not in found_ids]
            if missing_ids:
                return error(f"以下ID的记录不存在: {missing_ids}")

            # 执行前置操作回调（如果提供）
            if pre_operation_callback:
                pre_result = await pre_operation_callback(id_array, session)
                # 如果返回的是JSONResponse，直接返回错误信息
                if isinstance(pre_result, JSONResponse):
                    return pre_result

            # 批量删除记录
            for record in records:
                await session.delete(record)

            await session.commit()

            return success(None, message=f"成功删除{len(records)}条记录")

    def add_upload_path_prefix_to_html(
        self,
        html_content: str,
        request: Request | None = None,
    ) -> str:
        """
        为 HTML 内容中的 src 属性添加完整的上传路径前缀

        Args:
            html_content: HTML 内容
            request: FastAPI Request 对象 可选

        Returns:
            添加了完整路径前缀的 HTML 内容

        Example:
            输入: '<img src="/image/xxx.jpg">'
            输出: '<img src="http://127.0.0.1:8009/uploads/image/xxx.jpg">'
        """
        base_url = ""
        if request:
            base_url = get_base_url(request)
        url_prefix = Config.get("upload.url_prefix", "/uploads").lstrip("/")
        full_upload_prefix = f"{base_url}/{url_prefix}"

        # 使用正则表达式将 src 属性中的相对路径添加完整上传路径前缀
        # 匹配 src="/uploads/..." 或 src='/uploads/...' 格式
        pattern = re.compile(r'(src=["\'])' + r'(/[^"\']*)')
        return pattern.sub(r"\1" + full_upload_prefix + r"\2", html_content)

    def remove_upload_path_prefix_from_html(
        self,
        html_content: str,
        request: Request | None = None,
    ) -> str:
        """
        从 HTML 内容中的 src 属性移除完整的上传路径前缀

        Args:
            html_content: HTML 内容
            request: FastAPI Request 对象 可选

        Returns:
            移除了完整路径前缀的 HTML 内容

        Example:
            输入: '<img src="http://127.0.0.1:8009/uploads/image/xxx.jpg">'
            输出: '<img src="/image/xxx.jpg">'
        """
        base_url = ""
        if request:
            base_url = get_base_url(request)
        url_prefix = Config.get("upload.url_prefix", "/uploads").lstrip("/")
        full_upload_prefix = f"{base_url}/{url_prefix}"

        # 使用正则表达式替换 src 属性中的完整上传路径前缀
        # 匹配 src="base_url/url_prefix/..." 或 src='base_url/url_prefix/...' 格式
        pattern = re.compile(
            r'(src=["\"])' + re.escape(full_upload_prefix) + r'(/[^"\']*)'
        )
        return pattern.sub(r"\1\2", html_content)
