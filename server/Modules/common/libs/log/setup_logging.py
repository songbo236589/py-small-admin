from zoneinfo import ZoneInfo

from loguru import logger

from ..config import Config


def setup_logging() -> None:
    """初始化 Loguru 日志，按天生成日志文件，支持时区配置"""

    # 移除默认 handler
    logger.remove()

    log_config = Config.get("log")
    level = log_config.level
    console = log_config.console
    file_path = log_config.file_path
    rotation = log_config.rotation
    retention = log_config.retention
    compression = log_config.compression
    console_format = log_config.console_format
    file_format = log_config.file_format

    # 获取时区配置
    timezone_str = Config.get("app.timezone", "Asia/Shanghai")
    timezone = ZoneInfo(timezone_str)

    # 创建时区感知的格式化器
    def timezone_formatter(record):
        """为日志记录添加时区感知的时间戳"""
        # 获取记录的原始时间并转换为配置的时区
        record_time = record["time"]
        if record_time.tzinfo is None:
            # 如果时间没有时区信息，假设为UTC并转换
            record_time = record_time.replace(tzinfo=ZoneInfo("UTC"))

        # 转换为配置的时区
        localized_time = record_time.astimezone(timezone)
        # 更新时间格式
        record["extra"]["timezone_time"] = localized_time.strftime("%Y-%m-%d %H:%M:%S")
        return record

    # 控制台输出
    if console:
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level=level,
            format=console_format.replace(
                "{time:YYYY-MM-DD HH:mm:ss}", "{extra[timezone_time]}"
            ),
            enqueue=True,
            filter=timezone_formatter,
        )

    # 文件输出，每天生成一个日志文件
    if file_path:
        logger.add(
            file_path,
            level=level,
            format=file_format.replace(
                "{time:YYYY-MM-DD HH:mm:ss}", "{extra[timezone_time]}"
            ),
            rotation=rotation,  # 每天 00:00 轮转
            retention=retention,
            compression=compression,
            enqueue=True,
            filter=timezone_formatter,
        )
