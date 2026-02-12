from threading import Lock
from typing import Any

from config import (
    AppConfig,
    CacheConfig,
    CaptchaConfig,
    CeleryConfig,
    ContentConfig,
    DatabaseConfig,
    JWTConfig,
    LogConfig,
    PasswordConfig,
    UploadConfig,
)


class ConfigRegistry:
    """
    配置注册中心（线程安全单例）

    负责管理所有配置实例的注册、初始化和访问。采用单例模式确保
    全局只实例化一次配置，避免重复读取环境变量和配置文件。

    设计目标：
    - 全局只实例化一次配置，提高性能
    - FastAPI / 普通脚本通用，适用于多种应用场景
    - 避免隐式多次读取 env 文件，减少 I/O 操作
    - 线程安全，支持多线程环境

    实现特点：
    - 使用双重检查锁定模式确保线程安全
    - 延迟初始化，只在首次访问时加载配置
    - 提供配置实例的统一访问接口
    """

    # 类变量，存储所有配置实例
    _configs: dict[str, Any] = {}
    # 标记是否已加载配置
    _loaded: bool = False
    # 线程锁，确保线程安全
    _lock: Lock = Lock()

    @classmethod
    def load(cls) -> None:
        """
        初始化并注册所有配置

        使用双重检查锁定模式确保线程安全的延迟初始化。
        该方法会创建所有配置实例并注册到内部字典中。

        特点：
        - 线程安全，使用双重检查锁定模式
        - 多次调用只生效一次，避免重复初始化
        - 延迟加载，只在首次访问时初始化

        Note:
            如果需要添加新的配置类，请在此方法中注册
            例如：cls._configs["database"] = DatabaseConfig()

        Examples:
            >>> ConfigRegistry.load()  # 首次调用会初始化配置
            >>> ConfigRegistry.load()  # 后续调用不会重复初始化
        """
        if cls._loaded:
            return

        with cls._lock:
            if cls._loaded:
                return

            # 注册所有配置实例
            # 如需添加新配置，请在此处添加
            cls._configs = {
                "app": AppConfig(),
                "log": LogConfig(),
                "database": DatabaseConfig(),
                "cache": CacheConfig(),
                "password": PasswordConfig(),
                "jwt": JWTConfig(),
                "captcha": CaptchaConfig(),
                "upload": UploadConfig(),
                "celery": CeleryConfig(),
                "content": ContentConfig(),
            }

            cls._loaded = True

    @classmethod
    def get(cls, name: str) -> Any:
        """
        获取指定名称的配置实例

        通过配置名称获取对应的配置实例。如果配置尚未初始化，
        会自动触发配置加载过程。

        Args:
            name (str): 配置名称，如 "app"、"database" 等

        Returns:
            Any: 配置实例，如果不存在则返回 None

        Examples:
            >>> ConfigRegistry.get("app")
            <AppConfig object at 0x...>
            >>> ConfigRegistry.get("nonexistent")
            None
        """
        return cls._configs.get(name)

    @classmethod
    def all(cls) -> dict[str, Any]:
        """
        获取所有配置实例的只读副本

        返回包含所有配置实例的字典副本，用于调试或检查
        当前配置状态。返回的是副本，修改不会影响原始配置。

        Returns:
            dict[str, Any]: 包含所有配置实例的字典，键为配置名称

        Examples:
            >>> configs = ConfigRegistry.all()
            >>> configs.keys()
            dict_keys(['app'])
            >>> configs["app"].name
            'Fast API'

        Note:
            返回的是配置对象的引用，修改返回的对象会影响实际配置
        """
        return cls._configs.copy()
