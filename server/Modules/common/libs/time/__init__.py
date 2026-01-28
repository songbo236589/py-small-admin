"""
时间处理模块

提供时区管理和时间工具函数，支持应用配置的时区设置。

主要功能：
- 时区管理和初始化
- 时区感知的时间获取和格式化
- 时间解析和转换
- 与项目配置系统的集成

使用示例：
    from Modules.common.libs.time import now, format_datetime

    # 获取当前时间（应用配置时区）
    current_time = now()

    # 格式化时间
    formatted = format_datetime(current_time, "%Y-%m-%d %H:%M:%S")
"""

from .timezone import (
    TimezoneManager,
    get_timezone,
    get_timezone_manager,
    get_timezone_string,
    init_timezone,
    is_valid_timezone,
    set_timezone,
)
from .utils import (
    add_time,
    end_of_day,
    format_datetime,
    from_timestamp,
    from_utc,
    is_same_day,
    isoformat,
    now,
    parse_datetime,
    start_of_day,
    time_diff,
    timestamp,
    to_timezone,
    to_utc,
    utc_now,
)

# 导出主要接口
__all__ = [
    # 时区管理
    "TimezoneManager",
    "get_timezone_manager",
    "init_timezone",
    "set_timezone",
    "get_timezone",
    "get_timezone_string",
    "is_valid_timezone",
    # 时间工具
    "now",
    "utc_now",
    "format_datetime",
    "parse_datetime",
    "to_timezone",
    "to_utc",
    "from_utc",
    "isoformat",
    "timestamp",
    "from_timestamp",
    "add_time",
    "time_diff",
    "is_same_day",
    "start_of_day",
    "end_of_day",
]
