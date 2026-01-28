from pydantic import Field

from config.base import BaseConfig


class LogConfig(BaseConfig):
    """
    日志配置类，支持每天生成一个文件

    该配置类基于 Pydantic Settings，可以从环境变量中读取配置。
    所有环境变量都需要以 "LOG_" 为前缀，例如：LOG_LEVEL, LOG_CONSOLE 等。

    使用示例：
        config = LogConfig()
        logger.add(config.file_path, rotation=config.rotation, retention=config.retention)
    """

    # 继承 BaseConfig 的配置，并添加环境变量前缀
    # 这意味着所有环境变量都需要以 "LOG_" 开头
    model_config = BaseConfig.model_config | {"env_prefix": "LOG_"}

    # ==================== 基础设置 ====================

    # 日志级别，控制哪些级别的日志会被输出
    # 可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # DEBUG: 显示所有日志，包括调试信息，开发环境常用
    # INFO: 显示一般信息，生产环境推荐
    # WARNING: 显示警告和错误
    # ERROR: 仅显示错误信息
    # CRITICAL: 仅显示严重错误
    level: str = Field(
        default="INFO", description="日志级别，控制哪些级别的日志会被输出"
    )

    # 是否在控制台输出日志
    # True: 在控制台显示彩色日志，开发环境建议开启
    # False: 不在控制台显示，生产环境可考虑关闭以提升性能
    console: bool = Field(default=True, description="是否在控制台输出日志")

    # ==================== 文件输出设置 ====================

    # 日志文件路径，支持时间变量占位符
    # {time:YYYY-MM-DD} 会被替换为当前日期，实现按天分割日志
    # 示例: logs/2023-12-25.log
    # 其他可用格式:
    #   - logs/app_{time:YYYY-MM-DD}.log
    #   - logs/{time:YYYY}/{time:MM}/{time:DD}.log
    file_path: str = Field(
        default="logs/{time:YYYY-MM-DD}.log",
        description="日志文件路径，支持时间变量占位符",
    )

    # ==================== 文件轮转与保留设置 ====================

    # 日志文件轮转策略
    # "00:00": 每天午夜 00:00 创建新文件
    # "1 week": 每周创建新文件
    # "500 MB": 文件大小达到 500MB 时创建新文件
    # "10:00": 每天 10:00 创建新文件
    rotation: str = Field(default="00:00", description="日志文件轮转策略")

    # 日志文件保留时间
    # 超过此时间的日志文件会被自动删除
    # "30 days": 保留最近 30 天的日志
    # "1 week": 保留最近一周的日志
    # "10 GB": 保留总大小不超过 10GB 的日志文件
    retention: str = Field(default="30 days", description="日志文件保留时间")

    # 轮转后的日志文件压缩格式
    # "zip": 压缩为 zip 格式，节省磁盘空间
    # "gz": 压缩为 gzip 格式
    # "tar": 压缩为 tar 格式
    # None: 不压缩
    compression: str = Field(default="zip", description="轮转后的日志文件压缩格式")

    # ==================== 日志输出格式设置 ====================

    # 控制台日志输出格式，支持颜色和样式
    # <green>...</green>: 绿色文本
    # <level>...</level>: 根据日志级别显示不同颜色
    # <cyan>...</cyan>: 青色文本
    # {time:YYYY-MM-DD HH:mm:ss}: 时间戳，精确到秒
    # {level: <8}: 日志级别，左对齐，占8个字符宽度
    # {name}: 模块名称
    # {function}: 函数名称
    # {line}: 代码行号
    # {message}: 日志消息内容
    console_format: str = Field(
        default=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        description="控制台日志输出格式，支持颜色和样式",
    )

    # 文件日志输出格式，不包含颜色标记
    # 文件中的日志通常是纯文本，不需要颜色标记
    # 格式与控制台类似，但移除了 HTML 风格的颜色标签
    file_format: str = Field(
        default=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
        ),
        description="文件日志输出格式，不包含颜色标记",
    )
