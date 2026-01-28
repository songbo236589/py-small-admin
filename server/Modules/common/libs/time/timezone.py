"""
时区管理模块

提供时区管理功能，支持从配置中读取时区设置并提供时区相关的服务。
使用单例模式确保全局时区设置的一致性。
"""

from threading import Lock
from zoneinfo import ZoneInfo

from loguru import logger

from ..config import Config


class TimezoneManager:
    """
    时区管理器（单例模式）

    负责管理应用的时区设置，提供时区对象的创建、缓存和访问功能。
    采用单例模式确保全局时区设置的一致性。

    设计目标：
    - 全局统一的时区管理
    - 时区对象的缓存和复用
    - 配置驱动的时区设置
    - 线程安全的时区操作

    实现特点：
    - 使用单例模式确保全局唯一
    - 时区对象缓存提高性能
    - 完善的错误处理和降级策略
    - 线程安全的初始化和访问
    """

    # 类变量，实现单例模式
    _instance: "TimezoneManager | None" = None
    _lock: Lock = Lock()

    def __new__(cls) -> "TimezoneManager":
        """
        单例模式实现

        使用双重检查锁定确保线程安全的单例创建。

        Returns:
            TimezoneManager: 单例实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # 不要在这里设置 _initialized，让 __init__ 方法处理
        return cls._instance

    def __init__(self):
        """初始化时区管理器"""
        if hasattr(self, "_initialized"):
            return

        self._timezone: ZoneInfo | None = None
        self._timezone_cache: dict[str, ZoneInfo] = {}
        self._initialized = True

    def init_timezone(self) -> None:
        """
        从配置初始化时区

        从应用配置中读取时区设置，创建对应的时区对象。
        如果配置无效，则使用默认时区作为降级策略。

        Raises:
            ValueError: 当时区配置完全无效时抛出
        """
        try:
            # 从配置获取时区字符串
            timezone_str = Config.get("app.timezone", "Asia/Shanghai")
            logger.info(f"正在初始化时区: {timezone_str}")

            # 创建时区对象
            self._timezone = self._create_timezone(timezone_str)
            logger.info(f"时区初始化成功: {timezone_str}")

        except Exception as e:
            logger.error(f"时区初始化失败: {e}")
            # 降级策略：使用默认时区
            try:
                self._timezone = self._create_timezone("Asia/Shanghai")
                logger.warning("使用默认时区: Asia/Shanghai")
            except Exception as fallback_error:
                logger.error(f"默认时区也失败: {fallback_error}")
                # 最后降级：使用UTC
                self._timezone = self._create_timezone("UTC")
                logger.warning("使用UTC时区作为最后降级")

    def _create_timezone(self, timezone_str: str) -> ZoneInfo:
        """
        创建时区对象

        Args:
            timezone_str: 时区字符串，如 "Asia/Shanghai"

        Returns:
            ZoneInfo: 时区对象

        Raises:
            ValueError: 当时区字符串无效时抛出
        """
        if not timezone_str or not isinstance(timezone_str, str):
            raise ValueError(f"无效的时区字符串: {timezone_str}")

        # 检查缓存
        if timezone_str in self._timezone_cache:
            return self._timezone_cache[timezone_str]

        try:
            timezone = ZoneInfo(timezone_str)
            # 缓存时区对象
            self._timezone_cache[timezone_str] = timezone
            return timezone
        except Exception as e:
            raise ValueError(f"无法创建时区对象 '{timezone_str}': {e}") from e

    def get_timezone(self) -> ZoneInfo:
        """
        获取当前时区对象

        如果时区尚未初始化，会自动触发初始化过程。

        Returns:
            ZoneInfo: 当前时区对象

        Raises:
            ValueError: 当时区初始化失败时抛出
        """
        if self._timezone is None:
            self.init_timezone()

        if self._timezone is None:
            raise ValueError("时区初始化失败")

        return self._timezone

    def set_timezone(self, timezone_str: str) -> None:
        """
        设置时区

        动态设置应用时区，仅影响当前进程。

        Args:
            timezone_str: 时区字符串，如 "Asia/Shanghai"

        Raises:
            ValueError: 当时区字符串无效时抛出
        """
        try:
            self._timezone = self._create_timezone(timezone_str)
            logger.info(f"时区已设置为: {timezone_str}")
        except Exception as e:
            logger.error(f"设置时区失败: {e}")
            raise ValueError(f"无法设置时区 '{timezone_str}': {e}") from e

    def get_timezone_string(self) -> str:
        """
        获取当前时区字符串

        Returns:
            str: 当前时区字符串，如 "Asia/Shanghai"
        """
        timezone = self.get_timezone()
        return str(timezone)

    def is_valid_timezone(self, timezone_str: str) -> bool:
        """
        验证时区字符串是否有效

        Args:
            timezone_str: 时区字符串

        Returns:
            bool: 是否有效
        """
        try:
            ZoneInfo(timezone_str)
            return True
        except Exception:
            return False

    def clear_cache(self) -> None:
        """清空时区对象缓存"""
        self._timezone_cache.clear()
        logger.debug("时区对象缓存已清空")

    def get_cached_timezones(self) -> list[str]:
        """
        获取已缓存的时区列表

        Returns:
            list[str]: 已缓存的时区字符串列表
        """
        return list(self._timezone_cache.keys())


# 全局时区管理器实例
_timezone_manager: TimezoneManager | None = None


def get_timezone_manager() -> TimezoneManager:
    """
    获取时区管理器实例（单例）

    Returns:
        TimezoneManager: 时区管理器实例
    """
    global _timezone_manager
    if _timezone_manager is None:
        _timezone_manager = TimezoneManager()
    return _timezone_manager


def init_timezone() -> None:
    """
    初始化时区（便捷函数）

    从配置中读取时区设置并初始化时区管理器。
    这个函数通常在应用启动时调用。
    """
    manager = get_timezone_manager()
    manager.init_timezone()


def set_timezone(timezone_str: str) -> None:
    """
    设置时区（便捷函数）

    Args:
        timezone_str: 时区字符串，如 "Asia/Shanghai"
    """
    manager = get_timezone_manager()
    manager.set_timezone(timezone_str)


def get_timezone() -> ZoneInfo:
    """
    获取当前时区对象（便捷函数）

    Returns:
        ZoneInfo: 当前时区对象
    """
    manager = get_timezone_manager()
    return manager.get_timezone()


def get_timezone_string() -> str:
    """
    获取当前时区字符串（便捷函数）

    Returns:
        str: 当前时区字符串，如 "Asia/Shanghai"
    """
    manager = get_timezone_manager()
    return manager.get_timezone_string()


def is_valid_timezone(timezone_str: str) -> bool:
    """
    验证时区字符串是否有效（便捷函数）

    Args:
        timezone_str: 时区字符串

    Returns:
        bool: 是否有效
    """
    manager = get_timezone_manager()
    return manager.is_valid_timezone(timezone_str)
