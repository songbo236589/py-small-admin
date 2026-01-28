from pydantic import Field

from config.base import BaseConfig


class CacheConfig(BaseConfig):
    """
    缓存配置

    该配置类基于 Pydantic Settings，提供简洁的 Redis 缓存配置。
    所有环境变量都需要以 "CACHE_" 为前缀。

    设计特点：
    - 简洁的配置结构
    - 与 database.py 的 Redis 配置解耦
    - 支持通过环境变量覆盖配置

    环境变量格式：
    - CACHE_CONNECTION=cache
    - CACHE_DEFAULT_TTL=3600
    - CACHE_KEY_PREFIX=

    使用示例：
        config = CacheConfig()
        connection_name = config.connection
        ttl = config.default_ttl

    环境变量完整示例：
        # Redis 连接名称（对应 config/database.py 中的 redis 配置）
        CACHE_CONNECTION=cache

        # 默认 TTL（秒）
        CACHE_DEFAULT_TTL=3600

        # 键名前缀
        CACHE_KEY_PREFIX=
    """

    model_config = BaseConfig.model_config | {"env_prefix": "CACHE_"}

    # ==================== Redis 连接配置 ====================

    connection: str = Field(
        default="cache",
        description="Redis 连接名称（对应 config/database.py 中的 redis 配置）",
    )

    # ==================== 缓存行为配置 ====================

    default_ttl: int = Field(
        default=3600,
        description="默认缓存过期时间（秒）",
    )

    key_prefix: str = Field(
        default="",
        description="缓存键名前缀",
    )
