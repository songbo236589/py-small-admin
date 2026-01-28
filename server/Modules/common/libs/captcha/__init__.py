"""
验证码服务模块

提供验证码生成、验证等功能，支持多种验证码类型。
"""

from .captcha_service import CaptchaService, generate_captcha, get_captcha_service
from .utils import CaptchaResult

__all__ = [
    "CaptchaService",
    "get_captcha_service",
    "generate_captcha",
    "CaptchaResult",
]
