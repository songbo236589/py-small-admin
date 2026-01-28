"""
Admin 模块中间件包 - 简化版本
"""

from .permission_middleware import require_authentication

__all__ = [
    "require_authentication"
]
