"""
JWT 工具函数模块

提供 JWT 相关的便捷函数和工具方法。
"""

from datetime import timedelta
from typing import Any

from .jwt_service import get_jwt_service


def jwt_create_access_token(
    payload: dict, expires_delta: timedelta | None = None
) -> str:
    """
    便捷函数：创建访问令牌

    Args:
        payload: 令牌载荷数据
        expires_delta: 自定义过期时间，默认使用配置中的过期时间

    Returns:
        JWT 访问令牌字符串
    """
    jwt_service = get_jwt_service()
    return jwt_service.create_access_token(payload, expires_delta)


def jwt_create_refresh_token(
    payload: dict, expires_delta: timedelta | None = None
) -> str:
    """
    便捷函数：创建刷新令牌

    Args:
        payload: 令牌载荷数据
        expires_delta: 自定义过期时间，默认使用配置中的过期时间

    Returns:
        JWT 刷新令牌字符串
    """
    jwt_service = get_jwt_service()
    return jwt_service.create_refresh_token(payload, expires_delta)


async def jwt_verify_token(
    token: str, token_type: str | None = None, audience: str | None = None
) -> dict:
    """
    便捷函数：验证令牌

    Args:
        token: JWT 令牌字符串
        token_type: 令牌类型，用于验证令牌类型是否匹配
        audience: 期望的受众，如果未提供则使用配置中的默认值

    Returns:
        令牌载荷字典

    Raises:
        jwt.InvalidTokenError: 令牌无效或过期
        ValueError: 令牌类型不匹配
    """
    jwt_service = get_jwt_service()
    return await jwt_service.verify_token(token, token_type, audience)


def jwt_decode_token(
    token: str, verify: bool = False, audience: str | None = None
) -> dict:
    """
    便捷函数：解码令牌

    Args:
        token: JWT 令牌字符串
        verify: 是否验证签名和过期时间，默认为False（仅解码不验证）
        audience: 期望的受众，如果未提供则使用配置中的默认值

    Returns:
        令牌载荷字典

    Raises:
        jwt.DecodeError: 令牌格式错误
        jwt.InvalidTokenError: 令牌无效或过期（当verify=True时）
    """
    jwt_service = get_jwt_service()
    return jwt_service.decode_token(token, verify, audience)


async def jwt_is_token_blacklisted(token_jti: str) -> bool:
    """
    便捷函数：检查令牌是否在黑名单中

    Args:
        token_jti: 令牌的 JTI (JWT ID)

    Returns:
        如果令牌在黑名单中返回 True，否则返回 False
    """
    jwt_service = get_jwt_service()
    return await jwt_service.is_token_blacklisted(token_jti)


async def jwt_blacklist_token(token_jti: str, expires_at) -> bool:
    """
    便捷函数：将令牌加入黑名单

    Args:
        token_jti: 令牌的 JTI (JWT ID)
        expires_at: 令牌过期时间

    Returns:
        是否成功加入黑名单
    """
    jwt_service = get_jwt_service()
    return await jwt_service.blacklist_token(token_jti, expires_at)


def jwt_get_token_payload_without_verification(token: str) -> dict:
    """
    便捷函数：获取令牌载荷（不进行任何验证）

    用于调试和日志记录，不应用于业务逻辑

    Args:
        token: JWT 令牌字符串

    Returns:
        令牌载荷字典
    """
    jwt_service = get_jwt_service()
    return jwt_service.get_token_payload_without_verification(token)


def create_user_token_payload(user_id: str, username: str, **extra_claims) -> dict:
    """
    创建用户令牌载荷的标准格式

    Args:
        user_id: 用户ID
        username: 用户名
        **extra_claims: 额外的 Claims

    Returns:
        标准格式的令牌载荷
    """
    payload = {
        "sub": user_id,
        "username": username,
    }

    # 添加额外的 Claims
    if extra_claims:
        payload.update(extra_claims)

    return payload


def extract_user_info_from_token_payload(payload: dict) -> dict[str, Any]:
    """
    从令牌载荷中提取用户信息

    Args:
        payload: 令牌载荷

    Returns:
        用户信息字典
    """
    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "token_type": payload.get("type"),
        "issued_at": payload.get("iat"),
        "expires_at": payload.get("exp"),
        "jwt_id": payload.get("jti"),
    }


def is_access_token(payload: dict) -> bool:
    """
    检查令牌是否为访问令牌

    Args:
        payload: 令牌载荷

    Returns:
        如果是访问令牌返回 True，否则返回 False
    """
    return payload.get("type") == "access"


def is_refresh_token(payload: dict) -> bool:
    """
    检查令牌是否为刷新令牌

    Args:
        payload: 令牌载荷

    Returns:
        如果是刷新令牌返回 True，否则返回 False
    """
    return payload.get("type") == "refresh"


def get_token_remaining_time(payload: dict) -> int:
    """
    获取令牌剩余有效时间（秒）

    Args:
        payload: 令牌载荷

    Returns:
        剩余有效时间（秒），如果令牌已过期返回 0
    """
    from ..time import timestamp

    exp = payload.get("exp")
    if not exp:
        return 0

    current_timestamp = timestamp()
    remaining = exp - current_timestamp

    return max(0, int(remaining))


def format_token_info(payload: dict) -> dict[str, Any]:
    """
    格式化令牌信息为可读格式

    Args:
        payload: 令牌载荷

    Returns:
        格式化后的令牌信息
    """
    from ..time import from_timestamp, isoformat

    user_info = extract_user_info_from_token_payload(payload)
    remaining_time = get_token_remaining_time(payload)

    return {
        **user_info,
        "is_expired": remaining_time == 0,
        "remaining_seconds": remaining_time,
        "formatted_expires_at": isoformat(from_timestamp(payload.get("exp", 0)))
        if payload.get("exp")
        else None,
        "formatted_issued_at": isoformat(from_timestamp(payload.get("iat", 0)))
        if payload.get("iat")
        else None,
    }
