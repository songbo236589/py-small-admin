import re
from enum import Enum

from pydantic import Field, field_validator, model_validator

from config.base import BaseConfig


class JWTAlgorithm(str, Enum):
    """
    JWT 支持的签名算法枚举

    - 使用 Enum 防止算法拼写错误
    - 便于 IDE 自动补全
    - 与 PyJWT 2.x 完全兼容
    """

    HS256 = "HS256"  # HMAC + SHA-256（对称加密）
    HS384 = "HS384"
    HS512 = "HS512"

    RS256 = "RS256"  # RSA + SHA-256（非对称加密）
    RS384 = "RS384"
    RS512 = "RS512"

    ES256 = "ES256"  # ECDSA P-256 + SHA-256
    ES384 = "ES384"  # ECDSA P-384 + SHA-384
    ES512 = "ES512"  # ECDSA P-521 + SHA-512


class TokenType(str, Enum):
    """JWT 令牌类型"""

    ACCESS = "access"
    REFRESH = "refresh"


class JWTConfig(BaseConfig):
    """
    JWT 认证配置

    适配：
    - PyJWT >= 2.x
    - FastAPI
    - Redis 黑名单扩展
    """

    # 单独的环境变量前缀
    model_config = BaseConfig.model_config | {"env_prefix": "JWT_"}

    # ==================== 基础配置 ====================

    secret_key: str = Field(
        default="my-super-secure-jwt-secret-key-12345",
        description="JWT 密钥（HS算法为共享密钥，RS/ES 为 PEM 私钥）",
    )

    algorithm: JWTAlgorithm = Field(
        default=JWTAlgorithm.HS256,
        description="JWT 签名算法",
    )

    access_token_expire_minutes: int = Field(
        default=30,
        description="访问令牌过期时间（分钟）",
    )

    refresh_token_expire_days: int = Field(
        default=7,
        description="刷新令牌过期时间（天）",
    )

    # ==================== 校验相关 ====================

    issuer: str | None = Field(default=None, description="令牌签发者（iss）")
    audience: str | None = Field(default=None, description="令牌受众（aud）")

    verify_expiration: bool = Field(default=True, description="是否校验过期时间")
    verify_issuer: bool = Field(default=True, description="是否校验 issuer")
    verify_audience: bool = Field(default=True, description="是否校验 audience")

    # ==================== Claim 配置 ====================

    access_token_type: TokenType = Field(
        default=TokenType.ACCESS, description="访问令牌类型"
    )
    refresh_token_type: TokenType = Field(
        default=TokenType.REFRESH, description="刷新令牌类型"
    )

    # ==================== 黑名单（可选） ====================

    enable_blacklist: bool = Field(default=False, description="是否启用 JWT 黑名单")
    blacklist_prefix: str = Field(
        default="jwt:blacklist:", description="黑名单 Key 前缀"
    )

    # ==================== 验证器 ====================

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        """验证密钥强度"""
        if not v:
            raise ValueError("JWT密钥不能为空")

        # 检查是否为不安全的默认值
        if v in ["change-me-in-production", "secret", "key"]:
            raise ValueError("请使用安全的JWT密钥，不要使用默认值")

        # 获取算法类型
        algorithm = info.data.get("algorithm", JWTAlgorithm.HS256)

        # 对称算法（HS系列）需要足够长的密钥
        if algorithm.value.startswith("HS"):
            if len(v) < 32:
                raise ValueError("HS算法密钥长度至少需要32个字符")
            # 检查密钥复杂度
            if not re.search(r"[A-Za-z]", v) or not re.search(r"[0-9]", v):
                raise ValueError("HS算法密钥应包含字母和数字")

        # 非对称算法（RS/ES系列）需要PEM格式
        elif algorithm.value.startswith(("RS", "ES")):
            if not (v.startswith("-----BEGIN") and v.endswith("-----")):
                raise ValueError("RS/ES算法需要PEM格式的密钥")

        return v

    @model_validator(mode="after")
    def validate_config_consistency(self):
        """验证配置一致性"""
        # 如果设置了issuer，应该启用verify_issuer
        if self.issuer and not self.verify_issuer:
            raise ValueError("设置了issuer时，verify_issuer应该为True")

        # 如果设置了audience，应该启用verify_audience
        if self.audience and not self.verify_audience:
            raise ValueError("设置了audience时，verify_audience应该为True")

        # 如果启用了verify_issuer但没有设置issuer，给出警告
        if self.verify_issuer and not self.issuer:
            # 这里不抛出异常，但可以在日志中记录警告
            pass

        # 如果启用了verify_audience但没有设置audience，给出警告
        if self.verify_audience and not self.audience:
            # 这里不抛出异常，但可以在日志中记录警告
            pass

        return self
