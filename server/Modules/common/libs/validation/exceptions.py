"""
验证异常定义

定义验证过程中使用的异常类和错误码。
"""

from enum import Enum


class ValidationErrorCode(str, Enum):
    """验证错误码枚举"""

    # 通用错误码
    MISSING_REQUIRED_FIELD = "missing_required_field"
    VALIDATION_FAILED = "validation_failed"
    INVALID_TYPE = "invalid_type"

    # 验证码相关错误码
    CAPTCHA_ID_INVALID = "captcha_id_invalid"
    CAPTCHA_TEXT_INVALID = "captcha_text_invalid"
    CAPTCHA_TOO_SHORT = "captcha_too_short"
    CAPTCHA_ID_TOO_SHORT = "captcha_id_too_short"

    # 认证相关错误码
    USERNAME_EMPTY = "username_empty"
    USERNAME_TOO_SHORT = "username_too_short"
    USERNAME_TOO_LONG = "username_too_long"
    PASSWORD_EMPTY = "password_empty"
    PASSWORD_TOO_SHORT = "password_too_short"


class ValidationError(Exception):
    """验证错误异常类"""

    def __init__(
        self, message: str, code: ValidationErrorCode, details: dict | None = None
    ):
        """
        初始化验证错误异常

        Args:
            message: 错误消息
            code: 错误码
            details: 错误详情，可选
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 包含错误信息的字典
        """
        return {"error": self.message, "code": self.code, "details": self.details}
