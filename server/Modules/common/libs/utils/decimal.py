"""
Decimal 工具函数模块

提供安全的 Decimal 转换和处理工具函数。
"""

import math
from decimal import Decimal
from typing import Any


def safe_decimal(value: Any) -> Decimal | None:
    """
    安全地转换为 Decimal

    将任意值安全地转换为 Decimal 类型，处理各种边界情况和异常。

    Args:
        value: 要转换的值，可以是任意类型

    Returns:
        Decimal | None: 转换后的 Decimal 对象，失败返回 None

    Returns None 的情况:
        - value 为 None
        - value 为空字符串 ""
        - value 为连字符 "-"
        - value 为 NaN (float 类型)
        - 转换过程中发生 ValueError 或 TypeError

    Example:
        >>> safe_decimal("123.45")
        Decimal('123.45')
        >>> safe_decimal(100)
        Decimal('100')
        >>> safe_decimal(None)
        None
        >>> safe_decimal("")
        None
        >>> safe_decimal(float('nan'))
        None
    """
    if value is None or value == "" or value == "-":
        return None
    # 检查是否为 nan 值
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def safe_decimal_with_default(
    value: Any, default: Decimal | None = None
) -> Decimal | None:
    """
    安全地转换为 Decimal，支持自定义默认值

    与 safe_decimal 类似，但允许指定转换失败时的默认返回值。

    Args:
        value: 要转换的值
        default: 转换失败时的默认返回值，默认为 None

    Returns:
        Decimal | None: 转换后的 Decimal 对象，失败返回 default

    Example:
        >>> safe_decimal_with_default("123.45")
        Decimal('123.45')
        >>> safe_decimal_with_default(None, Decimal('0'))
        Decimal('0')
    """
    result = safe_decimal(value)
    return result if result is not None else default


def format_decimal(value: Any, precision: int = 2) -> str:
    """
    格式化 Decimal 为字符串

    将值转换为 Decimal 并格式化为指定精度的字符串。

    Args:
        value: 要格式化的值
        precision: 小数点后保留位数，默认为 2

    Returns:
        str: 格式化后的字符串，转换失败返回 "0.00"

    Example:
        >>> format_decimal("123.456", 2)
        '123.46'
        >>> format_decimal(None)
        '0.00'
    """
    decimal_value = safe_decimal(value)
    if decimal_value is None:
        return f"0.{precision * '0'}"
    return f"{decimal_value:.{precision}f}"


def round_decimal(
    value: Any, precision: int = 2, rounding: str = "ROUND_HALF_UP"
) -> Decimal | None:
    """
    对 Decimal 进行舍入

    将值转换为 Decimal 并进行舍入操作。

    Args:
        value: 要舍入的值
        precision: 小数点后保留位数，默认为 2
        rounding: 舍入方式，默认为 "ROUND_HALF_UP"，可选值：
            - ROUND_UP: 向远离零的方向舍入
            - ROUND_DOWN: 向零的方向舍入
            - ROUND_HALF_UP: 四舍五入（默认）
            - ROUND_HALF_DOWN: 五舍六入
            - ROUND_HALF_EVEN: 银行家舍入法

    Returns:
        Decimal | None: 舍入后的 Decimal，转换失败返回 None

    Example:
        >>> round_decimal("123.456", 2)
        Decimal('123.46')
        >>> round_decimal("123.454", 2)
        Decimal('123.45')
    """
    decimal_value = safe_decimal(value)
    if decimal_value is None:
        return None

    rounding_modes = {
        "ROUND_UP": "ROUND_UP",
        "ROUND_DOWN": "ROUND_DOWN",
        "ROUND_HALF_UP": "ROUND_HALF_UP",
        "ROUND_HALF_DOWN": "ROUND_HALF_DOWN",
        "ROUND_HALF_EVEN": "ROUND_HALF_EVEN",
    }

    rounding_mode = rounding_modes.get(rounding, "ROUND_HALF_UP")
    return decimal_value.quantize(Decimal(f"1e-{precision}"), rounding=rounding_mode)


def compare_decimal(a: Any, b: Any) -> int | None:
    """
    比较两个 Decimal 值

    将两个值转换为 Decimal 并进行比较。

    Args:
        a: 第一个值
        b: 第二个值

    Returns:
        int | None: 比较结果
            - -1: a < b
            - 0: a == b
            - 1: a > b
            - None: 任一值转换失败

    Example:
        >>> compare_decimal("123.45", "123.46")
        -1
        >>> compare_decimal("123.45", "123.45")
        0
        >>> compare_decimal("123.46", "123.45")
        1
    """
    decimal_a = safe_decimal(a)
    decimal_b = safe_decimal(b)

    if decimal_a is None or decimal_b is None:
        return None

    if decimal_a < decimal_b:
        return -1
    elif decimal_a > decimal_b:
        return 1
    else:
        return 0
