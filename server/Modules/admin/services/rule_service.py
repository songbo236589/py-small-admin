"""
Admin 菜单服务 - 负责菜单相关的业务逻辑
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import select

from Modules.admin.models.admin_rule import AdminRule
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.time.utils import format_datetime
from Modules.common.services.base_service import BaseService


class RuleService(BaseService):
    """Admin菜单服务 - 负责菜单相关的业务逻辑"""

    def __init__(self):
        super().__init__()

    async def index(self) -> JSONResponse:
        """获取菜单树形结构"""
        async with get_async_session() as session:
            # 查询所有启用的菜单，按级别和排序排序
            query = select(AdminRule).order_by(
                AdminRule.sort.asc(),  # type: ignore
            )
            result = await session.execute(query)
            rules = list(result.scalars().all())

            # 将所有规则转换为字典格式，便于处理
            rule_dict = {}
            for rule in rules:
                rule_dict[rule.id] = {
                    "id": rule.id,
                    "name": rule.name,
                    "path": rule.path,
                    "component": rule.component,
                    "redirect": rule.redirect,
                    "type": rule.type,
                    "level": rule.level,
                    "icon": rule.icon,
                    "pid": rule.pid,
                    "sort": rule.sort,
                    "status": rule.status,
                    "target": rule.target,
                    "created_at": format_datetime(rule.created_at)
                    if rule.created_at
                    else None,
                    "updated_at": format_datetime(rule.updated_at)
                    if rule.updated_at
                    else None,
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

            return success(jsonable_encoder(tree_data))

    async def add(self, data: dict[str, Any]) -> JSONResponse:
        """添加菜单"""
        return await self.common_add(
            data=data,
            model_class=AdminRule,
            pre_operation_callback=self._rule_add_pre_operation,
        )

    async def _rule_add_pre_operation(
        self, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """菜单添加前置操作

        Args:
            data: 菜单数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """

        pid = data.get("pid")
        if pid == 0:
            data["level"] = 1
        else:
            # 设置菜单级别
            result = await session.execute(
                select(AdminRule.level).where(AdminRule.id == pid)
            )
            level = result.scalar_one_or_none()
            if level:
                data["level"] = level + 1
            else:
                return error("父级菜单不存在")

        return data, session

    async def edit(self, id: int) -> JSONResponse:
        """获取菜单信息（用于编辑）"""
        async with get_async_session() as session:
            # 查询菜单是否存在
            result = await session.execute(
                select(
                    *[
                        AdminRule.id,
                        AdminRule.name,
                        AdminRule.path,
                        AdminRule.component,
                        AdminRule.redirect,
                        AdminRule.type,
                        AdminRule.icon,
                        AdminRule.pid,
                        AdminRule.sort,
                        AdminRule.status,
                        AdminRule.target,
                    ]
                ).where(AdminRule.id == id)
            )
            info = result.mappings().one_or_none()
            if not info:
                return error("菜单不存在")

            return success(dict(info))

    async def update(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """更新菜单信息"""
        return await self.common_update(
            id=id,
            data=data,
            model_class=AdminRule,
            pre_operation_callback=self._rule_update_pre_operation,
        )

    async def _rule_update_pre_operation(
        self, id: int, data: dict[str, Any], session: Any
    ) -> tuple[dict[str, Any], Any] | JSONResponse:
        """菜单更新前置操作

        Args:
            id: 菜单ID
            data: 更新数据
            session: 数据库会话

        Returns:
            验证失败时返回错误响应，成功时返回(data, session)
        """
        pid = data.get("pid")
        if pid == 0:
            data["level"] = 1
        else:
            # 设置菜单级别
            result = await session.execute(
                select(AdminRule.level).where(AdminRule.id == pid)
            )
            level = result.scalar_one_or_none()
            if level:
                data["level"] = level + 1
            else:
                return error("父级菜单不存在")

        return data, session

    async def set_status(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """菜单状态"""
        return await self.common_update(id=id, data=data, model_class=AdminRule)

    async def set_sort(self, id: int, data: dict[str, Any]) -> JSONResponse:
        """菜单排序"""
        return await self.common_update(id=id, data=data, model_class=AdminRule)

    async def destroy(self, id: int) -> JSONResponse:
        """菜单删除"""
        # 获取当前菜单及其所有子菜单的ID
        id_array = await self._get_all_children_ids(id)
        return await self.common_destroy_all(id_array=id_array, model_class=AdminRule)

    async def _get_all_children_ids(self, parent_id: int) -> list[int]:
        """递归获取父菜单及其所有子菜单的ID

        Args:
            parent_id: 父菜单ID

        Returns:
            包含父菜单ID及其所有子菜单ID的列表
        """
        async with get_async_session() as session:
            # 初始化结果数组，包含父菜单ID
            result_ids = [parent_id]

            # 查询所有直接子菜单
            query = select(AdminRule.id).where(AdminRule.pid == parent_id)
            children_result = await session.execute(query)
            children_ids = children_result.scalars().all()

            # 递归获取每个子菜单的所有子菜单ID
            for child_id in children_ids:
                grandchildren_ids = await self._get_all_children_ids(child_id)
                result_ids.extend(grandchildren_ids)

            return result_ids
