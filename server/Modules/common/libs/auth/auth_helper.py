"""
认证辅助工具类
提供从请求对象中获取认证信息的便捷方法
"""

from typing import Any

from fastapi import HTTPException, Request


class AuthHelper:
    """认证辅助工具类"""

    @staticmethod
    def get_current_user_id(request: Request) -> Any:
        """
        从请求中获取当前用户ID

        Args:
            request: FastAPI请求对象

        Returns:
            用户ID

        Raises:
            HTTPException: 如果用户ID不存在
        """
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        if user_id is None:
            raise HTTPException(status_code=401, detail="用户未认证")
        return user_id

    @staticmethod
    def get_current_username(request: Request) -> str:
        """
        从请求中获取当前用户名

        Args:
            request: FastAPI请求对象

        Returns:
            用户名

        Raises:
            HTTPException: 如果用户名不存在
        """
        username = (
            request.state.username if hasattr(request.state, "username") else None
        )
        if username is None:
            raise HTTPException(status_code=401, detail="用户未认证")
        return username

    @staticmethod
    def get_current_user(request: Request) -> dict[str, Any]:
        """
        从请求中获取当前用户完整信息

        Args:
            request: FastAPI请求对象

        Returns:
            用户信息字典

        Raises:
            HTTPException: 如果用户信息不存在
        """
        user = request.state.user if hasattr(request.state, "user") else None
        if user is None:
            raise HTTPException(status_code=401, detail="用户未认证")
        return user

    @staticmethod
    def get_auth_info(request: Request) -> dict[str, Any]:
        """
        从请求中获取所有认证相关信息

        Args:
            request: FastAPI请求对象

        Returns:
            包含所有认证信息的字典

        Raises:
            HTTPException: 如果用户未认证
        """
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        username = (
            request.state.username if hasattr(request.state, "username") else None
        )
        user = request.state.user if hasattr(request.state, "user") else None

        if user_id is None and username is None and user is None:
            raise HTTPException(status_code=401, detail="用户未认证")

        return {"user_id": user_id, "username": username, "user": user}
