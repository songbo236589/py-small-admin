"""
时间工具函数模块

提供时区感知的时间处理工具函数，包括时间获取、格式化、解析和转换等功能。
所有时间函数都会自动应用配置的时区设置。
"""

from datetime import UTC, date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from loguru import logger

from .timezone import get_timezone


def now() -> datetime:
    """
    获取当前时间（应用配置时区）

    返回带有应用配置时区信息的当前时间对象。

    Returns:
        datetime: 带时区信息的当前时间

    Example:
        >>> now()
        datetime.datetime(2023, 12, 25, 10, 30, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    try:
        tz = get_timezone()
        return datetime.now(tz)
    except Exception as e:
        logger.error(f"获取当前时间失败: {e}")
        # 降级到系统本地时间
        return datetime.now()


def utc_now() -> datetime:
    """
    获取当前UTC时间

    返回UTC时区的当前时间对象。

    Returns:
        datetime: UTC时区的当前时间

    Example:
        >>> utc_now()
        datetime.datetime(2023, 12, 25, 2, 30, tzinfo=datetime.UTC)
    """
    return datetime.now(UTC)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化时间

    将datetime对象格式化为指定格式的字符串。
    如果时间对象没有时区信息，会使用应用配置时区。

    Args:
        dt: 时间对象
        fmt: 格式字符串，默认为 "%Y-%m-%d %H:%M:%S"

    Returns:
        str: 格式化后的时间字符串

    Example:
        >>> dt = now()
        >>> format_datetime(dt, "%Y年%m月%d日 %H:%M:%S")
        '2023年12月25日 10:30:00'
    """
    try:
        # 如果时间对象没有时区信息，添加应用配置时区
        if dt.tzinfo is None:
            tz = get_timezone()
            dt = dt.replace(tzinfo=tz)

        return dt.strftime(fmt)
    except Exception as e:
        logger.error(f"格式化时间失败: {e}")
        # 降级到简单格式化
        return str(dt)


def parse_datetime(
    dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S", apply_timezone: bool = True
) -> datetime:
    """
    解析时间字符串

    将时间字符串解析为datetime对象。
    可以选择是否应用配置的时区。

    Args:
        dt_str: 时间字符串
        fmt: 时间格式，默认为 "%Y-%m-%d %H:%M:%S"
        apply_timezone: 是否应用配置时区，默认为True

    Returns:
        datetime: 解析后的时间对象

    Example:
        >>> parse_datetime("2023-12-25 10:30:00")
        datetime.datetime(2023, 12, 25, 10, 30, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    try:
        dt = datetime.strptime(dt_str, fmt)

        # 如果需要应用时区且时间对象没有时区信息
        if apply_timezone and dt.tzinfo is None:
            tz = get_timezone()
            dt = dt.replace(tzinfo=tz)

        return dt
    except Exception as e:
        logger.error(f"解析时间字符串失败: {e}")
        # 降级：尝试其他常见格式
        try:
            dt = datetime.fromisoformat(dt_str)
            if apply_timezone and dt.tzinfo is None:
                tz = get_timezone()
                dt = dt.replace(tzinfo=tz)
            return dt
        except Exception:
            # 最后降级：返回当前时间
            return now()


def to_timezone(dt: datetime, timezone_str: str) -> datetime:
    """
    时区转换

    将时间对象转换到指定时区。

    Args:
        dt: 时间对象
        timezone_str: 目标时区字符串，如 "UTC" 或 "Asia/Shanghai"

    Returns:
        datetime: 转换时区后的时间对象

    Example:
        >>> dt = now()
        >>> to_timezone(dt, "UTC")
        datetime.datetime(2023, 12, 25, 2, 30, tzinfo=zoneinfo.ZoneInfo('UTC'))
    """
    try:
        target_tz = ZoneInfo(timezone_str)

        # 如果时间对象没有时区信息，先添加应用配置时区
        if dt.tzinfo is None:
            source_tz = get_timezone()
            dt = dt.replace(tzinfo=source_tz)

        return dt.astimezone(target_tz)
    except Exception as e:
        logger.error(f"时区转换失败: {e}")
        # 降级：返回原时间对象
        return dt


def to_utc(dt: datetime) -> datetime:
    """
    转换为UTC时间

    将时间对象转换为UTC时区。

    Args:
        dt: 时间对象

    Returns:
        datetime: UTC时区的时间对象

    Example:
        >>> dt = now()
        >>> to_utc(dt)
        datetime.datetime(2023, 12, 25, 2, 30, tzinfo=datetime.UTC)
    """
    return to_timezone(dt, "UTC")


def from_utc(dt: datetime) -> datetime:
    """
    从UTC时间转换为应用配置时区

    将UTC时间对象转换为应用配置的时区。

    Args:
        dt: UTC时间对象

    Returns:
        datetime: 应用配置时区的时间对象

    Example:
        >>> dt = utc_now()
        >>> from_utc(dt)
        datetime.datetime(2023, 12, 25, 10, 30, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    try:
        app_timezone_str = get_timezone()
        return to_timezone(dt, str(app_timezone_str))
    except Exception as e:
        logger.error(f"UTC时间转换失败: {e}")
        # 降级：返回原时间对象
        return dt


def isoformat(dt: datetime | None = None) -> str:
    """
    获取ISO格式时间字符串

    返回ISO 8601格式的时间字符串。
    如果不提供时间对象，则使用当前时间。

    Args:
        dt: 时间对象，如果为None则使用当前时间

    Returns:
        str: ISO格式的时间字符串

    Example:
        >>> isoformat()
        '2023-12-25T10:30:00+08:00'
    """
    if dt is None:
        dt = now()
    elif dt.tzinfo is None:
        # 如果时间对象没有时区信息，添加应用配置时区
        tz = get_timezone()
        dt = dt.replace(tzinfo=tz)

    return dt.isoformat()


def timestamp(dt: datetime | None = None) -> float:
    """
    获取时间戳

    返回时间对象的Unix时间戳（秒）。
    如果不提供时间对象，则使用当前时间。

    Args:
        dt: 时间对象，如果为None则使用当前时间

    Returns:
        float: Unix时间戳

    Example:
        >>> timestamp()
        1703490600.0
    """
    if dt is None:
        dt = now()
    elif dt.tzinfo is None:
        # 如果时间对象没有时区信息，添加应用配置时区
        tz = get_timezone()
        dt = dt.replace(tzinfo=tz)

    return dt.timestamp()


def from_timestamp(ts: float, apply_timezone: bool = True) -> datetime:
    """
    从时间戳创建时间对象

    从Unix时间戳创建datetime对象。

    Args:
        ts: Unix时间戳
        apply_timezone: 是否应用配置时区，默认为True

    Returns:
        datetime: 时间对象

    Example:
        >>> from_timestamp(1703490600.0)
        datetime.datetime(2023, 12, 25, 10, 30, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    try:
        dt = datetime.fromtimestamp(ts)

        if apply_timezone:
            tz = get_timezone()
            dt = dt.replace(tzinfo=tz)

        return dt
    except Exception as e:
        logger.error(f"从时间戳创建时间对象失败: {e}")
        # 降级：返回当前时间
        return now()


def add_time(dt: datetime, **kwargs: Any) -> datetime:
    """
    时间加减

    对时间对象进行加减操作。

    Args:
        dt: 时间对象
        **kwargs: 时间参数，如 days=1, hours=2, minutes=30

    Returns:
        datetime: 加减后的时间对象

    Example:
        >>> dt = now()
        >>> add_time(dt, days=1, hours=2)
        datetime.datetime(2023, 12, 26, 12, 30, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    try:
        from datetime import timedelta

        return dt + timedelta(**kwargs)
    except Exception as e:
        logger.error(f"时间加减失败: {e}")
        # 降级：返回原时间对象
        return dt


def time_diff(dt1: datetime, dt2: datetime | None = None) -> float:
    """
    计算时间差

    计算两个时间对象之间的差值（秒）。
    如果不提供第二个时间对象，则与当前时间比较。

    Args:
        dt1: 第一个时间对象
        dt2: 第二个时间对象，如果为None则使用当前时间

    Returns:
        float: 时间差（秒）

    Example:
        >>> dt1 = now()
        >>> dt2 = add_time(dt1, hours=1)
        >>> time_diff(dt2, dt1)
        3600.0
    """
    if dt2 is None:
        dt2 = now()

    # 确保两个时间对象都有时区信息
    if dt1.tzinfo is None:
        tz = get_timezone()
        dt1 = dt1.replace(tzinfo=tz)

    if dt2.tzinfo is None:
        tz = get_timezone()
        dt2 = dt2.replace(tzinfo=tz)

    return abs((dt2 - dt1).total_seconds())


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """
    判断是否为同一天

    判断两个时间对象是否为同一天（基于应用配置时区）。

    Args:
        dt1: 第一个时间对象
        dt2: 第二个时间对象

    Returns:
        bool: 是否为同一天

    Example:
        >>> dt1 = now()
        >>> dt2 = add_time(dt1, hours=5)
        >>> is_same_day(dt1, dt2)
        True
    """
    # 确保两个时间对象都有时区信息
    if dt1.tzinfo is None:
        tz = get_timezone()
        dt1 = dt1.replace(tzinfo=tz)

    if dt2.tzinfo is None:
        tz = get_timezone()
        dt2 = dt2.replace(tzinfo=tz)

    return dt1.date() == dt2.date()


def start_of_day(dt: datetime | None = None) -> datetime:
    """
    获取一天的开始时间

    返回指定日期的00:00:00时间。
    如果不提供时间对象，则使用当前日期。

    Args:
        dt: 时间对象，如果为None则使用当前时间

    Returns:
        datetime: 一天开始的时间

    Example:
        >>> start_of_day()
        datetime.datetime(2023, 12, 25, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    if dt is None:
        dt = now()
    elif dt.tzinfo is None:
        tz = get_timezone()
        dt = dt.replace(tzinfo=tz)

    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime | None = None) -> datetime:
    """
    获取一天的结束时间

    返回指定日期的23:59:59时间。
    如果不提供时间对象，则使用当前日期。

    Args:
        dt: 时间对象，如果为None则使用当前时间

    Returns:
        datetime: 一天结束的时间

    Example:
        >>> end_of_day()
        datetime.datetime(2023, 12, 25, 23, 59, 59, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai'))
    """
    if dt is None:
        dt = now()
    elif dt.tzinfo is None:
        tz = get_timezone()
        dt = dt.replace(tzinfo=tz)

    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def parse_date(value: Any) -> date | None:
    """
    解析日期字符串为 date 对象

    支持多种日期格式：YYYY-MM-DD、YYYY/MM/DD、YYYYMMDD

    Args:
        value: 日期字符串或 None

    Returns:
        date | None: 解析后的 date 对象，失败返回 None

    Example:
        >>> parse_date("2023-12-25")
        datetime.date(2023, 12, 25)
        >>> parse_date("2023/12/25")
        datetime.date(2023, 12, 25)
        >>> parse_date("20231225")
        datetime.date(2023, 12, 25)
        >>> parse_date(None)
        None
    """
    if value is None or value == "" or value == "-":
        return None
    try:
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
            try:
                return datetime.strptime(str(value), fmt).date()
            except ValueError:
                continue
        return None
    except (ValueError, TypeError):
        return None
