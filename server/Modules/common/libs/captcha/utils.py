"""
验证码工具函数和类型定义

提供验证码相关的数据结构和通用工具函数。
"""

import uuid
from typing import Any

from pydantic import BaseModel

from config.captcha import CaptchaType


class CaptchaResult(BaseModel):
    """验证码生成结果"""

    captcha_id: str
    captcha_type: CaptchaType
    image_data: bytes | None = None
    question: str | None = None
    answer: str | None = None
    expire_seconds: int
    metadata: dict[str, Any] = {}

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """重写 model_dump 方法，自动处理 bytes 类型的 image_data"""
        data = super().model_dump(**kwargs)
        if data.get("image_data") and isinstance(data["image_data"], bytes):
            # 将 bytes 转换为 base64 Data URL 格式，可以直接在 img 标签的 src 中使用
            import base64

            base64_str = base64.b64encode(data["image_data"]).decode("utf-8")
            data["image_data"] = f"data:image/png;base64,{base64_str}"
        return data

    @classmethod
    def model_validate(cls, obj, **kwargs) -> "CaptchaResult":
        """重写 model_validate 方法，支持从 base64 字符串还原 bytes"""
        if (
            isinstance(obj, dict)
            and obj.get("image_data")
            and isinstance(obj["image_data"], str)
        ):
            # 如果 image_data 是字符串，尝试从 base64 还原为 bytes
            import base64

            try:
                obj["image_data"] = base64.b64decode(obj["image_data"])
            except Exception:
                # 如果解码失败，保持原样
                pass
        return super().model_validate(obj, **kwargs)


def generate_captcha_id() -> str:
    """生成验证码 ID"""
    return str(uuid.uuid4())


def get_character_set(char_type: str) -> str:
    """
    根据字符类型获取字符集

    Args:
        char_type: 字符类型 (numeric, alpha, alphanumeric, mixed)

    Returns:
        str: 字符集字符串
    """
    if char_type == "numeric":
        return "0123456789"
    elif char_type == "alpha":
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    elif char_type == "alphanumeric":
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    elif char_type == "mixed":
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    else:
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_random_text(length: int, char_set: str) -> str:
    """
    生成随机文本

    Args:
        length: 文本长度
        char_set: 字符集

    Returns:
        str: 随机文本
    """
    import random

    return "".join(random.choice(char_set) for _ in range(length))


def generate_math_question() -> tuple[str, str]:
    """
    生成数学题

    Returns:
        tuple[str, str]: (问题, 答案)
    """
    import random

    # 生成两个随机数
    a = random.randint(1, 20)
    b = random.randint(1, 20)

    # 随机选择运算符
    operators = ["+", "-", "*"]
    op = random.choice(operators)

    if op == "+":
        question = f"{a} + {b}"
        answer = str(a + b)
    elif op == "-":
        # 确保结果为正数
        if a < b:
            a, b = b, a
        question = f"{a} - {b}"
        answer = str(a - b)
    else:  # "*"
        # 限制乘法结果不超过 100
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        question = f"{a} × {b}"
        answer = str(a * b)

    return question, answer
