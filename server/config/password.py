from pydantic import Field

from config.base import BaseConfig


class PasswordConfig(BaseConfig):
    """
    密码配置类

    管理密码哈希、验证、强度检查等相关配置。
    支持多种哈希算法和密码策略配置。
    """

    # 给密码配置单独加前缀
    model_config = BaseConfig.model_config | {"env_prefix": "PWD_"}

    # ========== Passlib / CryptContext 配置 ==========

    # 启用的密码哈希算法
    # passlib[bcrypt] 下只支持 bcrypt
    password_schemes: list[str] = Field(
        default=["bcrypt"],
        description="启用的密码哈希算法列表",
    )

    # 默认密码哈希算法
    password_default_scheme: str = Field(
        default="bcrypt",
        description="默认密码哈希算法",
    )

    # 是否自动弃用旧算法
    # 推荐使用 auto，便于未来升级算法
    password_deprecated: str | None = Field(
        default="auto",
        description="是否自动弃用旧密码算法",
    )

    # ========== bcrypt 专属参数（passlib 1.7.4 支持） ==========

    # bcrypt 计算成本
    # 开发环境可用 10，生产环境建议 12~14
    bcrypt_rounds: int = Field(
        default=12,
        ge=4,
        le=20,
        description="bcrypt 计算轮数（安全成本）",
    )

    # bcrypt 版本标识
    bcrypt_ident: str = Field(
        default="2b",
        description="bcrypt 版本标识（推荐 2b）",
    )

    # salt 长度
    bcrypt_salt_size: int = Field(
        default=22,
        description="bcrypt salt 长度",
    )

    # 是否对超长密码抛出异常（bcrypt 72 bytes 限制）
    bcrypt_truncate_error: bool = Field(
        default=True,
        description="密码超过 bcrypt 长度限制时是否报错",
    )

    # ========== 安全增强（可选） ==========

    # 最小密码校验耗时（秒）
    # 用于缓解定时攻击，一般不需要开启  0.1
    min_verify_time: float | None = Field(
        default=None,
        description="最小密码校验耗时（防定时攻击）",
    )
