"""
认证服务层 - 负责用户认证相关的业务逻辑处理
"""

from collections.abc import Sequence
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlmodel import select

from Modules.admin.models.admin_admin import AdminAdmin
from Modules.admin.models.admin_group import AdminGroup
from Modules.admin.models.admin_rule import AdminRule
from Modules.common.libs.auth.auth_helper import AuthHelper
from Modules.common.libs.captcha import captcha_service
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.jwt import get_jwt_service
from Modules.common.libs.password import PasswordService
from Modules.common.libs.responses import error, success
from Modules.common.libs.time import from_timestamp


class AuthService:
    """认证服务类"""

    def __init__(self):
        """初始化认证服务"""
        self.jwt_service = get_jwt_service()
        self.password_service = PasswordService()

    async def login(self, login_data: dict[str, Any]) -> JSONResponse:
        """
        用户登录

        Args:
            login_data: 登录数据，包含用户名、密码、验证码等
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 登录结果
        """
        username = login_data.get("username", "")
        password = login_data.get("password", "")
        captcha = login_data.get("captcha", "")
        captcha_id = login_data.get("captcha_id", "")
        # 如果提供了验证码，先验证验证码
        is_captcha_valid = await captcha_service.verify_captcha(captcha_id, captcha)
        if not is_captcha_valid:
            return error("验证码错误")

        try:
            # 查询用户
            async with get_async_session() as session:
                stmt = select(AdminAdmin).where(AdminAdmin.username == username)
                result = await session.execute(stmt)
                admin = result.scalar_one_or_none()

                # 验证用户是否存在
                if not admin:
                    return error("用户名或密码错误")

                # 验证用户状态
                if admin.status != 1:
                    return error("用户已被禁用")

                # 验证密码
                if not self.password_service.verify_password(
                    password, admin.password or ""
                ):
                    return error("用户名或密码错误")

                # 查询用户组信息
                group = None
                if admin.group_id is not None:
                    group = await session.get(AdminGroup, admin.group_id)
                    if not group:
                        return error("权限组不存在")

                    if group.status != 1:
                        return error("权限组已被禁用")

                # 生成JWT令牌
                token_payload = {
                    "sub": str(admin.id),  # 使用JWT标准的sub claim存储用户ID
                    "username": admin.username,
                    "name": admin.name,
                    "group_id": admin.group_id,
                    "group_name": group.name if group else None,
                }

                access_token = self.jwt_service.create_access_token(token_payload)
                refresh_token = self.jwt_service.create_refresh_token(
                    {"sub": str(admin.id)}  # 刷新令牌也使用sub claim
                )

                # 获取令牌过期时间信息
                access_expires_in = self.jwt_service.get_token_expires_in(
                    self.jwt_service._config.access_token_type
                )
                refresh_expires_in = self.jwt_service.get_token_expires_in(
                    self.jwt_service._config.refresh_token_type
                )
                access_expires_at = self.jwt_service.get_token_expires_at(
                    self.jwt_service._config.access_token_type
                )
                refresh_expires_at = self.jwt_service.get_token_expires_at(
                    self.jwt_service._config.refresh_token_type
                )

                return success(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "Bearer",
                        "expires_in": access_expires_in,
                        "refresh_expires_in": refresh_expires_in,
                        "access_expires_at": access_expires_at,
                        "refresh_expires_at": refresh_expires_at,
                    },
                    "登录成功",
                )

        except Exception as e:
            logger.error(f"登录失败: {e}")
            return error("登录失败，请稍后重试")

    async def logout(self, request: Request, refresh_token: str) -> JSONResponse:
        """
        用户登出

        Args:
            request: FastAPI请求对象
            refresh_token: 刷新令牌

        Returns:
            Dict[str, Any]: 登出结果
        """
        try:
            # 从请求头获取令牌
            authorization = request.headers.get("authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return error("未提供有效的令牌")

            token = authorization.split(" ")[1]

            # 验证并解码令牌
            try:
                payload = self.jwt_service.decode_token(token)
                token_jti = payload.get("jti")
                exp = payload.get("exp")

                # 如果有JTI，将令牌加入黑名单
                if token_jti and exp:
                    exp_datetime = from_timestamp(exp)
                    await self.jwt_service.blacklist_token(token_jti, exp_datetime)

            except Exception as e:
                logger.warning(f"处理登出access_token时出错: {e}")

            # 处理refresh_token
            try:
                refresh_payload = self.jwt_service.decode_token(refresh_token)
                refresh_jti = refresh_payload.get("jti")
                refresh_exp = refresh_payload.get("exp")

                # 如果有JTI，将refresh_token加入黑名单
                if refresh_jti and refresh_exp:
                    refresh_exp_datetime = from_timestamp(refresh_exp)
                    await self.jwt_service.blacklist_token(
                        refresh_jti, refresh_exp_datetime
                    )

            except Exception as e:
                logger.warning(f"处理登出refresh_token时出错: {e}")

            return success(None, "登出成功")

        except Exception as e:
            logger.error(f"登出失败: {e}")
            return error("登出失败，请稍后重试")

    async def refresh_token(
        self, refresh_data: dict[str, Any], request: Request
    ) -> JSONResponse:
        """
        刷新访问令牌

        Args:
            refresh_data: 刷新令牌数据
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 刷新结果
        """
        try:
            refresh_token = refresh_data.get("refresh_token")
            if not refresh_token:
                return error("未提供刷新令牌")

            # 验证刷新令牌
            try:
                payload = await self.jwt_service.verify_token(
                    refresh_token, self.jwt_service._config.refresh_token_type
                )
            except Exception as e:
                logger.warning(f"刷新令牌验证失败: {e}")
                return error("刷新令牌无效或已过期")

            user_id = payload.get("sub")  # 使用sub claim获取用户ID
            if not user_id:
                return error("刷新令牌无效")

            # 查询用户信息
            async with get_async_session() as session:
                admin = await session.get(AdminAdmin, user_id)
                if not admin or admin.status != 1:
                    return error("用户不存在或已被禁用")

                # 查询用户组信息
                group = None
                if admin.group_id is not None:
                    group = await session.get(AdminGroup, admin.group_id)
                    if not group:
                        return error("权限组不存在")

                    if group.status != 1:
                        return error("权限组已被禁用")

                # 生成新的访问令牌
                token_payload = {
                    "sub": str(admin.id),  # 使用JWT标准的sub claim存储用户ID
                    "username": admin.username,
                    "name": admin.name,
                    "group_id": admin.group_id,
                    "group_name": group.name if group else None,
                }

                access_token = self.jwt_service.create_access_token(token_payload)
                access_expires_in = self.jwt_service.get_token_expires_in(
                    self.jwt_service._config.access_token_type
                )
                access_expires_at = self.jwt_service.get_token_expires_at(
                    self.jwt_service._config.access_token_type
                )
                return success(
                    {
                        "access_token": access_token,
                        "access_expires_in": access_expires_in,
                        "access_expires_at": access_expires_at,
                    },
                    "令牌刷新成功",
                )

        except Exception as e:
            logger.error(f"刷新令牌失败: {e}")
            return error("刷新令牌失败，请稍后重试")

    async def get_current_user_info(self, request: Request) -> JSONResponse:
        """
        获取当前登录用户信息

        Args:
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 用户信息
        """
        try:
            user_id = AuthHelper().get_current_user_id(request)
            # 查询用户信息
            async with get_async_session() as session:
                admin = await session.get(AdminAdmin, user_id)

                if not admin or admin.status != 1:
                    return error("用户不存在或已被禁用")

                # 查询用户组信息
                group = None
                if admin.group_id is not None:
                    group = await session.get(AdminGroup, admin.group_id)
                    if not group:
                        return error("权限组不存在")

                    if group.status != 1:
                        return error("权限组已被禁用")

                # 构建用户信息
                user_info = {
                    "id": admin.id,
                    "username": admin.username,
                    "name": admin.name,
                    "phone": admin.phone,
                    "group_id": admin.group_id,
                    "group_name": group.name if group else None,
                    "status": admin.status,
                }

                return success(user_info, "获取用户信息成功")

        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return error("获取用户信息失败，请稍后重试")

    async def change_password(
        self, password_data: dict[str, Any], request: Request
    ) -> JSONResponse:
        """
        修改当前用户密码

        Args:
            password_data: 密码数据，包含旧密码、新密码等
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 修改结果
        """
        try:
            user_id = AuthHelper().get_current_user_id(request)

            old_password = password_data.get("old_password", "")
            new_password = password_data.get("new_password", "")

            # 查询用户并验证旧密码
            async with get_async_session() as session:
                admin = await session.get(AdminAdmin, user_id)

                if not admin or admin.status != 1:
                    return error("用户不存在或已被禁用")

                # 验证旧密码
                if not self.password_service.verify_password(
                    old_password, admin.password or ""
                ):
                    return error("旧密码错误")

                # 更新密码
                admin.password = self.password_service.hash_password(new_password)
                session.add(admin)
                await session.commit()

                return success(None, "密码修改成功")

        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return error("修改密码失败，请稍后重试")

    async def get_menu_tree(self, request: Request) -> JSONResponse:
        """
        获取当前用户的菜单树

        Args:
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 菜单树
        """
        try:
            user_id = AuthHelper().get_current_user_id(request)
            # 查询用户信息和权限
            async with get_async_session() as session:
                admin = await session.get(AdminAdmin, user_id)
                if not admin or admin.status != 1:
                    return error("用户不存在或已被禁用")

                # 查询用户组信息
                group = None
                if admin.group_id is not None:
                    group = await session.get(AdminGroup, admin.group_id)
                    if not group:
                        return error("权限组不存在")

                    if group.status != 1:
                        return error("权限组已被禁用")

                    if group.id != 1 and group.rules == "":
                        return error("没有可用权限")
                else:
                    return error("未分配权限组")

                # 获取用户可访问的菜单规则
                accessible_rule_ids = set()
                if group and group.rules:
                    # 解析组规则ID
                    rule_ids = [
                        int(rule_id)
                        for rule_id in group.rules.split("|")
                        if rule_id.isdigit()
                    ]
                    accessible_rule_ids.update(rule_ids)

                # 查询所有菜单规则
                rule_stmt = select(AdminRule).where(
                    AdminRule.status == 1,
                )
                if group.id != 1:
                    rule_stmt = rule_stmt.where(AdminRule.id.in_(accessible_rule_ids))  # type: ignore

                rule_stmt = rule_stmt.order_by(
                    AdminRule.sort.asc(),  # type: ignore
                )

                rule_result = await session.execute(rule_stmt)
                all_rules = rule_result.scalars().all()

                # 构建菜单树
                menu_tree = self._build_menu_tree(all_rules)

                return success(menu_tree, "获取菜单树成功")

        except Exception as e:
            logger.error(f"获取菜单树失败: {e}")
            return error("获取菜单树失败，请稍后重试")

    def _build_menu_tree(self, rules: Sequence[AdminRule]) -> list[dict[str, Any]]:
        """
        构建菜单树

        Args:
            rules: 菜单规则列表

        Returns:
            List[Dict[str, Any]]: 菜单树
        """
        # 将规则转换为字典并按ID索引
        rule_dict = {}
        for rule in rules:
            rule_dict[rule.id] = {
                "id": rule.id,
                "path": rule.path,
                "component": rule.component,
                "redirect": rule.redirect,
                "name": rule.name,
                "type": rule.type,
                "status": rule.status,
                "icon": rule.icon,
                "pid": rule.pid,
                "target": rule.target,
                "children": [],
            }

        # 构建树形结构
        tree = []
        for rule in rules:
            rule_data = rule_dict[rule.id]
            if rule.pid == 0:
                # 顶级菜单
                tree.append(rule_data)
            else:
                # 子菜单
                parent = rule_dict.get(rule.pid)
                if parent:
                    parent["children"].append(rule_data)
        return tree
