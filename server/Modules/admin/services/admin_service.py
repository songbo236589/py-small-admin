"""
Admin 用户服务 - 负责用户相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import load_only, selectinload
from sqlmodel import select

from Modules.admin.models.admin_admin import AdminAdmin
from Modules.admin.models.admin_group import AdminGroup
from Modules.common.libs.config.config import Config
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.password.password import PasswordService
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService


class AdminService(BaseService):
    """Admin用户服务 - 负责用户相关的业务逻辑"""

    def __init__(self):
        super().__init__()
        self.password_service = PasswordService()

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取用户列表或搜索用户（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)

        # 设置文本搜索字段
        data["text_fields"] = [
            "username",
            "name",
            "phone",
        ]
        # 精确匹配字段字典
        data["exact_fields"] = ["status", "group_id"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at"]

        async with get_async_session() as session:
            # 构建基础查询，使用关系映射加载AdminGroup
            query = select(AdminAdmin).options(
                load_only(
                    *[
                        AdminAdmin.id,
                        AdminAdmin.name,
                        AdminAdmin.username,
                        AdminAdmin.phone,
                        AdminAdmin.status,
                        AdminAdmin.updated_at,
                        AdminAdmin.created_at,
                    ]
                ),
                selectinload(AdminAdmin.group).load_only(
                    *[AdminGroup.id, AdminGroup.name]
                ),
            )
            # 搜索
            query = await self.apply_search_filters(query, AdminAdmin, data)

            # 应用排序
            query = await self.apply_sorting(query, AdminAdmin, data.get("sort"))

            page_data = await paginate(
                session, query, CustomParams(page=page, size=size)
            )
            items = []
            for admin in page_data.items:
                d = admin.__dict__.copy()
                d["created_at"] = (
                    format_datetime(admin.created_at) if admin.created_at else None
                )
                d["updated_at"] = (
                    format_datetime(admin.updated_at) if admin.updated_at else None
                )
                if admin.group:
                    d["group_name"] = admin.group.name
                    d.pop("group", None)
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
        """管理员添加"""
        return await self.common_add(
            data=data,
            model_class=AdminAdmin,
            pre_operation_callback=self._admin_add_pre_operation,
        )

    async def _admin_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """管理员添加前置操作

        Args:
            data: 管理员数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        username = data.get("username")
        name = data.get("name")
        password = data.get("password")
        phone = data.get("phone")
        status = data.get("status")
        group_id = data.get("group_id")

        # 检查用户名是否已存在
        existing_admin = await session.execute(
            select(AdminAdmin).where(AdminAdmin.username == username)
        )
        if existing_admin.scalar_one_or_none():
            return error("用户名已存在")

        # 检查角色ID是否有效
        if group_id:
            existing_group = await session.execute(
                select(AdminGroup).where(AdminGroup.id == group_id)
            )
            if not existing_group.scalar_one_or_none():
                return error("指定的角色不存在")

        # 对密码进行哈希处理
        if not password:
            return error("密码不能为空")

        hashed_password = self.password_service.hash_password(password)

        # 更新数据字典，用于创建实例
        data.update(
            {
                "name": name,
                "phone": phone if phone else "",
                "password": hashed_password,
                "status": status,
                "group_id": group_id,
            }
        )

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """获取管理员信息（用于编辑）"""
        if id == 1:
            return error("无法操作")
        async with get_async_session() as session:
            # 查询管理员信息，包括关联的角色信息
            result = await session.execute(
                select(
                    *[
                        AdminAdmin.id,
                        AdminAdmin.username,
                        AdminAdmin.name,
                        AdminAdmin.phone,
                        AdminAdmin.status,
                        AdminAdmin.group_id,
                    ]
                ).where(AdminAdmin.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("管理员不存在")

            return success(dict(info))

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新管理员信息"""
        if id == 1:
            return error("无法操作")
        return await self.common_update(
            id=id,
            data=data,
            model_class=AdminAdmin,
            pre_operation_callback=self._admin_update_pre_operation,
            field_update_callback=self._admin_field_update,
        )

    async def _admin_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """管理员更新前置操作

        Args:
            id: 管理员ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        username = data.get("username")
        group_id = data.get("group_id")

        # 检查用户名是否已被其他管理员使用
        if username:
            existing_admin = await session.execute(
                select(AdminAdmin).where(AdminAdmin.username == username)
            )
            admin_with_username = existing_admin.scalar_one_or_none()

            if admin_with_username and admin_with_username.id != id:
                return error("用户名已存在")

        # 检查角色ID是否有效
        if group_id:
            existing_group = await session.execute(
                select(AdminGroup).where(AdminGroup.id == group_id)
            )
            if not existing_group.scalar_one_or_none():
                return error("指定的角色不存在")

        return data, session

    def _admin_field_update(self, admin: AdminAdmin, data: dict[str, Any]) -> None:
        """管理员字段更新

        Args:
            admin: 管理员实例
            data: 更新数据
        """
        updatable_fields = ["username", "name", "phone", "status", "group_id"]

        for field in updatable_fields:
            if field in data and data[field] is not None:
                if field == "phone":
                    setattr(admin, field, data[field] if data[field] else "")
                else:
                    setattr(admin, field, data[field])

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """管理员状态"""
        if id == 1:
            return error("无法操作")
        return await self.common_update(id=id, data=data, model_class=AdminAdmin)

    async def destroy(self, id: int) -> JSONResponse:
        """管理员删除"""
        if id == 1:
            return error("无法操作")

        return await self.common_destroy(id=id, model_class=AdminAdmin)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """管理员批量删除"""
        if id == 1:
            return error("无法操作")

        return await self.common_destroy_all(id_array=id_array, model_class=AdminAdmin)

    async def reset_pwd(self, id: int) -> JSONResponse:
        """管理员初始化密码"""
        if id == 1:
            return error("无法重置密码")
        password = Config.get("app.default_admin_password")
        data = {"password": self.password_service.hash_password(password)}
        return await self.common_update(
            id=id,
            data=data,
            model_class=AdminAdmin,
            success_message=f"密码重置成功，新密码为{password}",
        )
