"""
平台处理器模块

融合了验证器和发布器的功能，提供统一的平台操作接口。
"""

from .base_platform_handler import BasePlatformHandler, PublishResult
from .toutiao_handler import ToutiaoHandler
from .xiaohongshu_handler import XiaohongshuHandler
from .zhihu_handler import ZhihuHandler

__all__ = [
    "BasePlatformHandler",
    "PublishResult",
    "ToutiaoHandler",
    "XiaohongshuHandler",
    "ZhihuHandler",
]
