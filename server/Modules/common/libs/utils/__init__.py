"""
通用工具函数模块

提供项目中常用的工具函数，包括数字、字符串、日期等处理工具。
"""

from .decimal import (
    compare_decimal,
    format_decimal,
    round_decimal,
    safe_decimal,
    safe_decimal_with_default,
)

__all__ = [
    "safe_decimal",
    "safe_decimal_with_default",
    "format_decimal",
    "round_decimal",
    "compare_decimal",
]
