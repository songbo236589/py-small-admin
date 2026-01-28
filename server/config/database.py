from typing import Any

from pydantic import Field

from config.base import BaseConfig


class DatabaseConfig(BaseConfig):
    """
    数据库配置类（SQL + Redis），参考 Laravel 风格

    该配置类基于 Pydantic Settings，可以从环境变量中读取配置。
    所有环境变量都需要以 "DB_" 为前缀，例如：DB_DEFAULT, DB_CONNECTIONS__MYSQL__HOST 等。

    嵌套结构使用双下划线 "__" 作为分隔符，例如：
        DB_CONNECTIONS__MYSQL__HOST=127.0.0.1
        DB_REDIS__DEFAULT__HOST=127.0.0.1

    使用示例：
        config = DatabaseConfig()
        mysql_config = config.connections[config.default]
        redis_config = config.redis["default"]
    """

    # 继承 BaseConfig 的配置，并添加环境变量前缀
    # 这意味着所有环境变量都需要以 "DB_" 开头
    model_config = BaseConfig.model_config | {"env_prefix": "DB_"}

    # ==================== 默认数据库连接设置 ====================

    # 指定默认使用的数据库连接名称
    # 该值必须在 connections 字典中存在对应的键
    # 常用值: "mysql", "pgsql", "sqlite", "sqlsrv"
    # 环境变量: DB_DEFAULT=mysql
    default: str = Field(default="mysql", description="默认数据库连接名称")

    # ==================== 数据库连接信息 ====================

    # 数据库连接配置字典
    # 键为连接名称（如 "mysql", "pgsql"），值为该连接的详细配置
    # 支持多种数据库类型：MySQL, PostgreSQL, SQLite, SQL Server
    #
    # 环境变量格式：DB_CONNECTIONS__{CONNECTION_NAME}__{PARAMETER}
    # 例如：DB_CONNECTIONS__MYSQL__HOST=127.0.0.1
    connections: dict[str, dict[str, Any]] = Field(
        default_factory=lambda: {
            "mysql": {
                # 数据库驱动类型，必须指定
                "driver": "mysql",
                # 完整的数据库连接 URL
                # 如果提供了 url，其他连接参数（host, port 等）将被忽略
                # 格式: mysql://user:password@host:port/database
                "url": None,
                # 数据库服务器地址
                "host": "127.0.0.1",
                # 数据库服务器端口
                "port": 3306,
                # 默认连接的数据库名称
                "database": "fastapi_db",
                # 数据库用户名
                "username": "root",
                # 数据库密码
                "password": "",
                # Unix 套接字路径（可选）
                # 用于本地连接，通常比 TCP 连接更快
                "unix_socket": "",
                # 字符集
                "charset": "utf8mb4",
                # 排序规则
                "collation": "utf8mb4_unicode_ci",
                # 表名前缀
                # 用于在多应用共享数据库时避免表名冲突
                "prefix": "",
                # 是否为索引添加表名前缀
                "prefix_indexes": True,
                # 是否启用严格模式
                # True: 禁止无效数据，提高数据完整性
                "strict": True,
                # 默认存储引擎
                "engine": "InnoDB",
                # 额外的驱动选项
                # 可以设置各种 MySQL 特定的连接参数
                "options": {},
            },
        }
    )

    # ==================== Redis 配置 ====================

    # Redis 连接配置字典
    # 支持配置多个 Redis 连接，用于不同的用途（如缓存、会话存储等）
    #
    # 环境变量格式：DB_REDIS__{CONNECTION_NAME}__{PARAMETER}
    # 例如：DB_REDIS__DEFAULT__HOST=127.0.0.1
    redis: dict[str, Any] = Field(
        default_factory=lambda: {
            # 默认 Redis 连接配置
            "default": {
                # Redis 连接 URL
                # 如果提供了 url，其他连接参数将被忽略
                # 格式: redis://username:password@host:port/database
                "url": None,
                # Redis 服务器地址
                "host": "127.0.0.1",
                # Redis 认证用户名（Redis 6.0+支持ACL功能）
                "username": "default",
                # Redis 认证密码
                "password": None,
                # Redis 服务器端口
                "port": 6379,
                # Redis 数据库编号（0-15）
                "database": 0,
                # 键名前缀
                # 用于在多应用共享 Redis 实例时避免键名冲突
                "prefix": "redis_default_",
                # 连接池最大连接数
                "max_connections": 50,
                # 连接超时是否重试
                "retry_on_timeout": True,
                # 套接字超时时间（秒）
                "socket_timeout": 5,
                # 套接字连接超时时间（秒）
                "socket_connect_timeout": 5,
                # 健康检查间隔（秒）
                "health_check_interval": 30,
            },
            # 缓存专用 Redis 连接配置
            "cache": {
                # Redis 连接 URL
                # 如果提供了 url，其他连接参数将被忽略
                # 格式: redis://username:password@host:port/database
                "url": None,
                # Redis 服务器地址
                "host": "127.0.0.1",
                # Redis 认证用户名（Redis 6.0+支持ACL功能）
                "username": "default",
                # Redis 认证密码
                "password": None,
                # Redis 服务器端口
                "port": 6379,
                # Redis 数据库编号（0-15），使用不同的 DB 避免与业务数据冲突
                "database": 1,
                # 键名前缀
                # 用于在多应用共享 Redis 实例时避免键名冲突
                "prefix": "cache_",
                # 连接池最大连接数
                "max_connections": 50,
                # 连接超时是否重试
                "retry_on_timeout": True,
                # 套接字超时时间（秒）
                "socket_timeout": 5,
                # 套接字连接超时时间（秒）
                "socket_connect_timeout": 5,
                # 健康检查间隔（秒）
                "health_check_interval": 30,
            },
        }
    )
