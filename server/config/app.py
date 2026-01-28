from enum import Enum

from pydantic import Field

from config.base import BaseConfig


class AppEnv(str, Enum):
    """
    应用运行环境枚举

    使用 Enum 的好处：
    - 防止 APP_ENV 拼写错误
    - IDE 可自动补全
    - 代码中可安全判断环境类型
    """

    local = "local"
    development = "development"
    testing = "testing"
    production = "production"


class AppConfig(BaseConfig):
    """应用基础配置"""

    # 给应用配置单独加前缀
    model_config = BaseConfig.model_config | {"env_prefix": "APP_"}

    # ========== 应用基础配置 ==========
    # 应用名称
    name: str = Field(default="Fast API", description="应用名称")

    # 当前运行环境
    # 不同环境可用于切换：
    # - 日志级别
    # - 数据库
    # - 第三方服务配置
    env: AppEnv = Field(default=AppEnv.production, description="当前运行环境")

    # 调试模式
    # 开发环境建议开启，生产环境务必关闭
    debug: bool = Field(default=False, description="调试模式")

    # API 版本
    version: str = Field(default="1.0.0", description="API 版本")

    # API 描述
    description: str = Field(default="FastAPI 应用程序", description="API 描述")

    # 服务主机地址
    host: str = Field(default="0.0.0.0", description="服务主机地址")

    # 服务端口
    port: int = Field(default=8000, description="服务端口")

    # 是否自动重载
    # 开发环境建议开启，代码变更自动重启服务
    reload: bool = Field(default=False, description="是否自动重载")

    # API 前缀
    # 例如：/api/v1
    api_prefix: str = Field(default="/api", description="API 前缀")

    # 是否启用 OpenAPI 文档
    # 生产环境可考虑关闭
    docs_enabled: bool = Field(default=True, description="是否启用 OpenAPI 文档")

    # 文档路径
    # 默认为 /docs，可自定义
    docs_url: str = Field(default="/docs", description="文档路径")

    # OpenAPI JSON规范路径
    # 提供API的机器可读规范，Swagger UI等工具会读取此文件生成文档
    # 设置为 None 可禁用 OpenAPI JSON 规范生成
    # 默认为 /openapi.json，生产环境可修改为复杂路径或禁用
    openapi_url: str = Field(
        default="/openapi.json", description="OpenAPI JSON规范路径"
    )

    # 跨域配置
    # 是否允许所有来源
    cors_allow_all: bool = Field(default=True, description="是否允许所有来源")

    # 允许的来源列表
    cors_origins: list[str] = Field(default=["*"], description="允许的来源列表")

    # 允许的方法
    cors_methods: list[str] = Field(default=["*"], description="允许的方法")

    # 允许的头部
    cors_headers: list[str] = Field(default=["*"], description="允许的头部")

    # 时区设置
    # 用于应用中的时间处理，确保时间显示与本地时区一致
    timezone: str = Field(default="Asia/Shanghai", description="时区设置")

    # Admin X API Key
    # 用于管理员接口验证的API密钥
    admin_x_api_key: str = Field(default="", description="管理员接口验证API密钥")

    # ========== 默认管理员账号配置 ==========
    # 默认管理员账号1
    default_admin_username: str = Field(
        default="admin", description="默认管理员账号用户名"
    )
    default_admin_password: str = Field(
        default="123456", description="默认管理员账号密码"
    )
