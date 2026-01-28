"""
统一响应模块

提供标准化的 API 响应格式和状态码常量。
支持成功响应、错误响应、分页响应等常见场景。
"""

from .response import (
    ResponseService,
    error,
    success,
)
from .status_codes import StatusCodes, StatusMessage

# 导出主要接口
__all__ = [
    # 核心服务类
    "ResponseService",
    # 状态码常量
    "StatusCodes",
    # 状态消息常量
    "StatusMessage",
    # 便捷函数
    "success",
    "error",
]
