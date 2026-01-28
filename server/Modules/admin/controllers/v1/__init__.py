"""
Admin 模块 v1 控制器包
"""

from .admin_controller import AdminController
from .common_controller import CommonController
from .group_controller import GroupController

__all__ = ["CommonController", "AdminController", "GroupController"]
