"""
密码服务核心模块

提供密码哈希、验证等核心功能的安全密码管理服务。
"""

from passlib.context import CryptContext

from ..config import Config


class PasswordService:
    """
    密码服务类

    提供核心的密码管理功能，包括：
    - 密码哈希生成和验证
    """

    def __init__(self):
        """初始化密码服务"""

        # 获取密码配置对象
        self.password = Config.get("password")

        # 构建 CryptContext 参数
        kwargs = {
            "schemes": self.password.password_schemes,
            "default": self.password.password_default_scheme,
            "deprecated": self.password.password_deprecated,
        }

        # 添加 bcrypt 特定参数
        if "bcrypt" in self.password.password_schemes:
            kwargs.update(
                {
                    "bcrypt__rounds": self.password.bcrypt_rounds,
                    "bcrypt__ident": self.password.bcrypt_ident,
                    "bcrypt__salt_size": self.password.bcrypt_salt_size,
                    "bcrypt__truncate_error": self.password.bcrypt_truncate_error,
                }
            )

        # 添加安全增强参数
        if self.password.min_verify_time is not None:
            kwargs["min_verify_time"] = self.password.min_verify_time

        self._crypt_context = CryptContext(**kwargs)

    def hash_password(self, password: str) -> str:
        """
        生成密码哈希

        Args:
            password (str): 明文密码

        Returns:
            str: 密码哈希值
        """
        if not isinstance(password, str):
            raise ValueError("密码必须是字符串类型")

        if not password:
            raise ValueError("密码不能为空")

        try:
            # 处理 bcrypt 的 72 字节限制
            if (
                "bcrypt" in self.password.password_schemes
                and not self.password.bcrypt_truncate_error
            ):
                # 手动截断密码到 72 字节以内
                password = password[:72]

            return self._crypt_context.hash(password)
        except Exception as e:
            raise ValueError(f"密码哈希生成失败: {e}") from e

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            password (str): 明文密码
            hashed_password (str): 密码哈希值

        Returns:
            bool: 验证结果
        """
        if not isinstance(password, str) or not isinstance(hashed_password, str):
            raise ValueError("密码和哈希值必须是字符串类型")

        if not password or not hashed_password:
            raise ValueError("密码和哈希值不能为空")

        try:
            return self._crypt_context.verify(password, hashed_password)
        except Exception as e:
            raise ValueError(f"密码验证失败: {e}") from e
