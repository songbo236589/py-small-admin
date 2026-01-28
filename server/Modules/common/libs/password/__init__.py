"""
密码服务模块

提供密码哈希、验证等功能的安全密码管理服务。

主要功能：
- 密码哈希生成和验证

使用示例：
    from Modules.common.libs.password import PasswordService

    # 初始化服务
    pwd_service = PasswordService()

    # 哈希密码
    hashed = pwd_service.hash_password("user_password")

    # 验证密码
    is_valid = pwd_service.verify_password("user_password", hashed)
"""

from .password import PasswordService

__all__ = [
    "PasswordService",
]
