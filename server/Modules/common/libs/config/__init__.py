"""
配置管理模块

该模块提供了一个统一的配置管理系统，支持通过点号分隔的键名来访问和设置配置值。
基于 Pydantic 实现类型安全的配置管理，支持从环境变量和配置文件中读取配置。

主要组件：
- Config: 提供静态方法 get/set/has/all 来访问和操作配置
- ConfigRegistry: 配置注册中心，管理所有配置实例的生命周期

特性：
- 类型安全：基于 Pydantic 的类型校验和转换
- 环境变量支持：自动从环境变量读取配置
- 多级路径：支持通过点号分隔访问嵌套配置
- 线程安全：配置注册中心采用线程安全设计
- 延迟加载：只在首次访问时初始化配置

使用示例：
    from Modules.common.libs.config import Config

    # 获取配置
    app_name = Config.get("app.name")  # 获取应用名称
    debug_mode = Config.get("app.debug", False)  # 获取调试模式，默认为 False

    # 检查配置是否存在
    if Config.has("app.api_prefix"):
        prefix = Config.get("app.api_prefix")

    # 设置配置（仅影响当前进程）
    Config.set("app.debug", True)

    # 获取所有配置快照（调试用）
    all_configs = Config.all()
"""

from .config import Config
from .registry import ConfigRegistry

# 导出主要接口
__all__ = [
    "Config",
    "ConfigRegistry",
]
