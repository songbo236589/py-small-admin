"""
JWT 模块

提供完整的 JWT 令牌管理功能，包括：
- JWT 服务核心类
- 便捷工具函数
"""

# 导入 JWT 服务核心类
from .jwt_service import JWTService, get_jwt_service

# 导入便捷工具函数
from .utils import (
    create_user_token_payload,
    extract_user_info_from_token_payload,
    format_token_info,
    get_token_remaining_time,
    is_access_token,
    is_refresh_token,
    jwt_blacklist_token,
    jwt_create_access_token,
    jwt_create_refresh_token,
    jwt_decode_token,
    jwt_get_token_payload_without_verification,
    jwt_is_token_blacklisted,
    jwt_verify_token,
)

# 导出所有公共接口
__all__ = [
    # JWT 服务
    "JWTService",
    "get_jwt_service",
    # 便捷函数
    "jwt_create_access_token",
    "jwt_create_refresh_token",
    "jwt_verify_token",
    "jwt_decode_token",
    "jwt_is_token_blacklisted",
    "jwt_blacklist_token",
    "jwt_get_token_payload_without_verification",
    # 工具函数
    "create_user_token_payload",
    "extract_user_info_from_token_payload",
    "is_access_token",
    "is_refresh_token",
    "get_token_remaining_time",
    "format_token_info",
]

# 版本信息
__version__ = "1.0.0"
