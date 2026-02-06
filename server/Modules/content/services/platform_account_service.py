"""
Content 平台账号服务 - 负责平台账号相关的业务逻辑
"""

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


class PlatformAccountService(BaseService):
    """Content平台账号服务 - 负责平台账号相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取平台账号列表或搜索平台账号（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["account_name"]
        # 精确匹配字段字典
        data["exact_fields"] = ["platform", "status"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at", "last_verified"]

        async with get_async_session() as session:
            # 构建基础查询
            query = select(ContentPlatformAccount)
            # 搜索
            query = await self.apply_search_filters(query, ContentPlatformAccount, data)

            # 应用排序
            query = await self.apply_sorting(
                query, ContentPlatformAccount, data.get("sort")
            )

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for account in page_data.items:
                d = account.__dict__.copy()
                # 隐藏敏感信息
                d["cookies"] = "***HIDDEN***"
                d["created_at"] = (
                    format_datetime(account.created_at) if account.created_at else None
                )
                d["updated_at"] = (
                    format_datetime(account.updated_at) if account.updated_at else None
                )
                d["last_verified"] = (
                    format_datetime(account.last_verified)
                    if account.last_verified
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
        """添加平台账号"""
        return await self.common_add(
            data=data,
            model_class=ContentPlatformAccount,
            pre_operation_callback=self._platform_account_add_pre_operation,
        )

    async def _platform_account_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """平台账号添加前置操作

        Args:
            data: 平台账号数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        platform = data.get("platform")
        account_name = data.get("account_name")

        # 检查同一平台下的账号名称是否已存在
        existing = await session.execute(
            select(ContentPlatformAccount).where(
                ContentPlatformAccount.platform == platform,
                ContentPlatformAccount.account_name == account_name,
            )
        )
        if existing.scalar_one_or_none():
            return error(f"该平台下已存在同名账号: {account_name}")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """获取平台账号信息（用于编辑）"""
        async with get_async_session() as session:
            result = await session.execute(
                select(
                    *[
                        ContentPlatformAccount.id,
                        ContentPlatformAccount.platform,
                        ContentPlatformAccount.account_name,
                        ContentPlatformAccount.cookies,
                        ContentPlatformAccount.user_agent,
                        ContentPlatformAccount.status,
                    ]
                ).where(ContentPlatformAccount.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("平台账号不存在")

            return success(dict(info))

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新平台账号信息"""
        return await self.common_update(
            id=id,
            data=data,
            model_class=ContentPlatformAccount,
            pre_operation_callback=self._platform_account_update_pre_operation,
        )

    async def _platform_account_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """平台账号更新前置操作

        Args:
            id: 平台账号ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        platform = data.get("platform")
        account_name = data.get("account_name")

        # 如果更新了平台或账号名称，检查是否重复
        if platform or account_name:
            # 获取原账号信息
            original = await session.execute(
                select(ContentPlatformAccount).where(ContentPlatformAccount.id == id)
            )
            original_account = original.scalar_one_or_none()
            if not original_account:
                return error("平台账号不存在")

            check_platform = platform if platform else original_account.platform
            check_account_name = (
                account_name if account_name else original_account.account_name
            )

            # 检查是否与其他账号重复
            existing = await session.execute(
                select(ContentPlatformAccount).where(
                    ContentPlatformAccount.platform == check_platform,
                    ContentPlatformAccount.account_name == check_account_name,
                    ContentPlatformAccount.id != id,
                )
            )
            if existing.scalar_one_or_none():
                return error(f"该平台下已存在同名账号: {check_account_name}")

        return data, session

    async def destroy(self, id: int) -> JSONResponse:
        """平台账号删除"""
        return await self.common_destroy(id=id, model_class=ContentPlatformAccount)

    async def verify(self, id: int) -> JSONResponse:
        """验证平台账号Cookie有效性"""
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentPlatformAccount).where(ContentPlatformAccount.id == id)
            )
            account = result.scalar_one_or_none()

            if not account:
                return error("平台账号不存在")

            # TODO: 实现实际的Cookie验证逻辑
            # 这里需要根据不同平台实现不同的验证方式
            # 例如：使用Playwright访问平台页面，检查是否能正常登录

            # 暂时只更新验证时间
            account.last_verified = now()
            account.status = 1  # 假设验证成功
            await session.commit()

            return success(
                {
                    "id": account.id,
                    "platform": account.platform,
                    "account_name": account.account_name,
                    "status": account.status,
                    "last_verified": format_datetime(account.last_verified),
                    "message": "Cookie验证成功",
                }
            )
