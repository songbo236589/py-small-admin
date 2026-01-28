from typing import Any

from .registry import ConfigRegistry


class Config:
    """
    全局配置访问门面

    提供统一的配置访问接口，支持通过点号分隔的键名来访问和设置配置值。
    该类作为配置系统的门面模式实现，隐藏了内部配置注册中心的复杂性。

    主要功能：
    - 支持多级配置路径访问（如 "app.name"）
    - 提供默认值支持
    - 动态设置配置值（仅影响当前进程）
    - 检查配置是否存在
    - 获取所有配置的快照

    用法示例：
        Config.get("app.name")  # 获取应用名称
        Config.get("app.debug", False)  # 获取调试模式，默认为 False
        Config.set("app.debug", True)  # 设置调试模式为 True
        Config.has("app.name")  # 检查应用名称是否存在
        Config.all()  # 获取所有配置快照

    注意事项：
    - 所有配置访问都会触发配置注册中心的初始化
    - 动态设置的配置仅影响当前进程，不会持久化
    - 设置配置时会触发 Pydantic 类型校验
    """

    @staticmethod
    def _resolve(key: str) -> list[str]:
        """
        解析配置路径为组件列表

        将点号分隔的配置键名解析为组件列表，用于后续的配置访问。
        支持两种格式：
        1. "namespace" - 直接获取配置对象
        2. "namespace.attr" 或多级路径 - 获取配置对象的特定属性

        Args:
            key (str): 配置键名，格式为 "namespace" 或 "namespace.attr" 或多级路径

        Returns:
            list[str]: 解析后的路径组件列表

        Raises:
            ValueError: 当键名为空时抛出

        Examples:
            >>> Config._resolve("app")
            ["app"]
            >>> Config._resolve("app.name")
            ["app", "name"]
            >>> Config._resolve("database.connection.timeout")
            ["database", "connection", "timeout"]
        """
        if not key:
            raise ValueError("Config key 不能为空")
        return key.split(".")

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持多级路径）

        通过键名获取配置值，支持两种方式：
        1. 直接获取配置对象：Config.get("jwt")
        2. 获取配置对象的特定属性：Config.get("jwt.secret_key")

        如果配置不存在，返回提供的默认值。

        Args:
            key (str): 配置键名，格式为 "namespace" 或 "namespace.attr" 或多级路径
            default (Any, optional): 配置不存在时的默认值，默认为 None

        Returns:
            Any: 配置值或默认值

        Examples:
            >>> Config.get("jwt")  # 获取整个 JWT 配置对象
            <JWTConfig object at 0x...>
            >>> Config.get("jwt.secret_key")
            "my-super-secure-jwt-secret-key-12345"
            >>> Config.get("app.debug", False)
            False
            >>> Config.get("database.connection.timeout", 30)
            30
        """
        ConfigRegistry.load()

        parts = cls._resolve(key)
        namespace, attrs = parts[0], parts[1:]

        value = ConfigRegistry.get(namespace)
        if value is None:
            return default

        # 如果没有属性路径，直接返回整个配置对象
        if not attrs:
            return value

        # 遍历属性路径获取最终值
        for attr in attrs:
            if not hasattr(value, attr):
                return default
            value = getattr(value, attr)

        return value

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        动态设置配置值（仅影响当前进程）

        通过点号分隔的键名设置配置值，仅支持设置一层属性。
        设置操作会触发 Pydantic 类型校验，确保值的类型正确。

        注意：
        - 会触发 Pydantic 类型校验
        - 建议仅在开发 / 测试环境使用
        - 仅影响当前进程，不会持久化到配置文件
        - 只支持设置一层属性（如 "app.debug"，不支持 "app.database.host"）

        Args:
            key (str): 配置键名，格式为 "namespace.attr"
            value (Any): 要设置的配置值

        Raises:
            ValueError: 当键名包含多级路径时抛出
            KeyError: 当配置命名空间不存在时抛出
            pydantic.ValidationError: 当值类型不匹配时抛出

        Examples:
            >>> Config.set("app.debug", True)  # 正确
            >>> Config.set("app.database.host", "localhost")  # 抛出 ValueError
        """
        ConfigRegistry.load()

        parts = cls._resolve(key)
        namespace, attrs = parts[0], parts[1:]

        if len(attrs) != 1:
            raise ValueError("Config.set 只支持设置一层属性")

        config = ConfigRegistry.get(namespace)
        if config is None:
            raise KeyError(f"Config namespace '{namespace}' 不存在")

        setattr(config, attrs[0], value)

    @classmethod
    def has(cls, key: str) -> bool:
        """
        判断配置是否存在

        检查指定键名的配置是否存在，不会抛出异常。
        支持两种方式：
        1. 检查配置对象是否存在：Config.has("jwt")
        2. 检查配置对象的属性是否存在：Config.has("jwt.secret_key")

        Args:
            key (str): 配置键名，格式为 "namespace" 或 "namespace.attr" 或多级路径

        Returns:
            bool: 如果配置存在返回 True，否则返回 False

        Examples:
            >>> Config.has("jwt")  # 检查 JWT 配置对象是否存在
            True
            >>> Config.has("app.name")  # 检查 app.name 属性是否存在
            True
            >>> Config.has("app.nonexistent")  # 检查不存在的属性
            False
        """
        sentinel = object()
        return cls.get(key, sentinel) is not sentinel

    @classmethod
    def all(cls) -> dict[str, Any]:
        """
        获取当前所有配置快照（调试用）

        返回所有配置的只读副本，主要用于调试和检查当前配置状态。

        Returns:
            dict[str, Any]: 包含所有配置的字典，键为命名空间，值为配置对象

        Examples:
            >>> configs = Config.all()
            >>> configs["app"].name
            "Fast API"

        Note:
            返回的是配置对象的引用，修改返回的对象会影响实际配置
        """
        ConfigRegistry.load()
        return ConfigRegistry.all()
