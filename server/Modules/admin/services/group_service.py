"""
Admin 角色服务 - 负责角色相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from Modules.admin.models.admin_group import AdminGroup
from Modules.admin.models.admin_rule import AdminRule
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime
from Modules.common.libs.validation.pagination_validator import CustomParams
from Modules.common.services.base_service import BaseService


class GroupService(BaseService):
    """Admin角色服务 - 负责角色相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def get_group_list(self, data: dict[str, Any]) -> JSONResponse:
        """获取角色列表"""
        # 精确匹配字段字典
        data["exact_fields"] = ["status"]
        async with get_async_session() as session:
            query = select(AdminGroup.id, AdminGroup.name)
            query = await self.apply_search_filters(query, AdminGroup, data)
            result = await session.execute(query)
            rows = result.all()
            groups = [{"id": r.id, "name": r.name} for r in rows]
            return success(jsonable_encoder(groups))

    async def index(self, data: dict[str, Any]) -> JSONResponse:
        """获取角色列表或搜索角色（统一接口）"""
        page = data.get("page", 1)
        size = data.get("limit", 20)
        # 模糊匹配字段字典
        data["fuzzy_fields"] = ["name", "content"]
        # 精确匹配字段字典
        data["exact_fields"] = ["status"]
        # 应用范围筛选
        data["range_fields"] = ["created_at", "updated_at"]

        async with get_async_session() as session:
            # 构建基础查询，使用关系映射加载AdminGroup
            query = select(AdminGroup)
            # 搜索
            query = await self.apply_search_filters(query, AdminGroup, data)

            # 应用排序
            query = await self.apply_sorting(query, AdminGroup, data.get("sort"))

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
        """添加角色"""
        return await self.common_add(
            data=data,
            model_class=AdminGroup,
            pre_operation_callback=self._group_add_pre_operation,
        )

    async def _group_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """角色添加前置操作

        Args:
            data: 角色数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """

        name = data.get("name")

        # 检查角色名是否已存在
        existing_group = await session.execute(
            select(AdminGroup).where(AdminGroup.name == name)
        )
        if existing_group.scalar_one_or_none():
            return error("角色已存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """获取角色信息（用于编辑）"""
        if id == 1:
            return error("无法操作")
        async with get_async_session() as session:
            # 查询管理员信息，包括关联的角色信息
            result = await session.execute(
                select(
                    *[
                        AdminGroup.id,
                        AdminGroup.name,
                        AdminGroup.content,
                        AdminGroup.status,
                    ]
                ).where(AdminGroup.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("角色不存在")

            return success(dict(info))

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新角色信息"""
        if id == 1:
            return error("无法操作")
        return await self.common_update(
            id=id,
            data=data,
            model_class=AdminGroup,
            pre_operation_callback=self._group_update_pre_operation,
        )

    async def _group_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """角色更新前置操作

        Args:
            id: 角色ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        name = data.get("name")

        # 检查角色名是否已被其他管理员使用
        if name:
            existing_admin = await session.execute(
                select(AdminGroup).where(AdminGroup.name == name)
            )
            group_with_name = existing_admin.scalar_one_or_none()

            if group_with_name and group_with_name.id != id:
                return error("角色已存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """角色状态"""
        if id == 1:
            return error("无法操作")
        return await self.common_update(id=id, data=data, model_class=AdminGroup)

    async def destroy(self, id: int) -> JSONResponse:
        """角色删除"""
        if id == 1:
            return error("无法操作")
        return await self.common_destroy(id=id, model_class=AdminGroup)

    async def destroy_all(self, id_array: list[int]) -> JSONResponse:
        """角色批量删除"""
        if id == 1:
            return error("无法操作")
        return await self.common_destroy_all(id_array=id_array, model_class=AdminGroup)

    async def get_access(self, id: int) -> JSONResponse:
        """获取角色信息（用于编辑）"""
        if id == 1:
            return error("无法操作")
        async with get_async_session() as session:
            # 查询管理员信息，包括关联的角色信息
            result = await session.execute(
                select(
                    *[
                        AdminGroup.id,
                        AdminGroup.rules,
                    ]
                ).where(AdminGroup.id == id)
            )
            info = result.mappings().one_or_none()

            if not info:
                return error("角色不存在")
            list = await self.get_rule_list(session)
            rules = []
            if info.rules:
                rules = info.rules.split("|")
                rules = [int(x) for x in rules]
                rule_result = await session.execute(
                    select(AdminRule.id).where(
                        AdminRule.id.in_(rules),  # type: ignore
                        AdminRule.type == 3,
                    )
                )
                rules = rule_result.scalars().all()

            return success({"id": info.id, "rules": rules, "list": list})

    async def get_rule_list(self, session) -> list[AdminRule]:
        """获取菜单树形结构"""
        async with get_async_session() as session:
            # 查询所有启用的菜单，按级别和排序排序
            query = (
                select(AdminRule)
                .where(AdminRule.status == 1)
                .order_by(
                    AdminRule.sort.asc(),  # type: ignore
                )
            )
            result = await session.execute(query)
            rules = list(result.scalars().all())

            # 将所有规则转换为字典格式，便于处理
            rule_dict = {}
            for rule in rules:
                rule_dict[rule.id] = {
                    "id": rule.id,
                    "name": rule.name,
                    "pid": rule.pid,
                    "value": rule.id,
                    "key": rule.id,
                    "title": rule.name,
                    "children": [],
                }

            # 构建树形结构：遍历所有规则，将子节点添加到父节点的children中
            tree_data = []
            for rule in rule_dict.values():
                parent_id = rule["pid"]
                if parent_id is None or parent_id == 0:
                    # 顶级节点，直接添加到树中
                    tree_data.append(rule)
                else:
                    # 子节点，添加到父节点的children中
                    if parent_id in rule_dict:
                        rule_dict[parent_id]["children"].append(rule)

            # 移除空的children数组
            def remove_empty_children(node):
                if not node["children"]:
                    del node["children"]
                else:
                    for child in node["children"]:
                        remove_empty_children(child)

            for node in tree_data:
                remove_empty_children(node)

            return tree_data

    async def access_update(self, id: int, rules: list[int]) -> JSONResponse:
        """更新角色信息"""
        if id == 1:
            return error("无法操作")
        return await self.common_update(
            id=id,
            data={"rules": "|".join(map(str, rules))},
            model_class=AdminGroup,
        )
