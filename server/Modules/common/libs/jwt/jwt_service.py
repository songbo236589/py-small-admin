"""
JWT 服务核心模块

提供 JWT 令牌的生成、验证、解码和管理功能。
"""

import uuid
from datetime import datetime, timedelta

from loguru import logger

import jwt

from ..cache import get_async_cache_service
from ..config import Config
from ..time import now


class JWTService:
    """
    JWT 服务类

    提供完整的 JWT 令牌管理功能，包括：
    - 访问令牌和刷新令牌的生成
    - 令牌验证和解码
    - 令牌黑名单管理
    - 与配置系统的集成
    """

    def __init__(self):
        """初始化 JWT 服务"""
        # 加载 JWT 配置
        self._config = Config.get("jwt")
        self._cache_service = get_async_cache_service()

    def create_access_token(
        self, payload: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        创建访问令牌

        Args:
            payload: 令牌载荷数据
            expires_delta: 自定义过期时间，默认使用配置中的过期时间

        Returns:
            JWT 访问令牌字符串
        """
        return self._create_token(
            payload=payload,
            token_type=self._config.access_token_type,
            expires_delta=expires_delta
            or timedelta(minutes=self._config.access_token_expire_minutes),
        )

    def create_refresh_token(
        self, payload: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        创建刷新令牌

        Args:
            payload: 令牌载荷数据
            expires_delta: 自定义过期时间，默认使用配置中的过期时间

        Returns:
            JWT 刷新令牌字符串
        """
        return self._create_token(
            payload=payload,
            token_type=self._config.refresh_token_type,
            expires_delta=expires_delta
            or timedelta(days=self._config.refresh_token_expire_days),
        )

    async def verify_token(
        self, token: str, token_type: str | None = None, audience: str | None = None
    ) -> dict:
        """
        验证令牌并返回载荷

        Args:
            token: JWT 令牌字符串
            token_type: 令牌类型，用于验证令牌类型是否匹配
            audience: 期望的受众，如果未提供则使用配置中的默认值

        Returns:
            令牌载荷字典

        Raises:
            jwt.InvalidTokenError: 令牌无效或过期
            ValueError: 令牌类型不匹配
        """
        try:
            # 如果未提供 audience，使用配置中的默认值
            if audience is None:
                audience = self._config.audience

            # 构建验证选项
            options = {}
            if not self._config.verify_expiration:
                options["verify_exp"] = False
            if not self._config.verify_issuer:
                options["verify_iss"] = False
            if not self._config.verify_audience:
                options["verify_aud"] = False

            # 验证令牌（包括签名和过期时间）
            payload = jwt.decode(
                token,
                self._config.secret_key,
                algorithms=[self._config.algorithm],
                options=options,
                audience=audience,
            )

            # 检查令牌是否在黑名单中
            if self._config.enable_blacklist and payload.get("jti"):
                if await self.is_token_blacklisted(payload["jti"]):
                    raise jwt.InvalidTokenError("令牌已被撤销")

            # 验证令牌类型
            if token_type and payload.get("type") != token_type:
                raise ValueError(
                    f"令牌类型不匹配，期望: {token_type}, 实际: {payload.get('type')}"
                )

            return payload

        except jwt.ExpiredSignatureError as e:
            logger.warning("JWT 令牌已过期")
            raise jwt.InvalidTokenError("令牌已过期") from e
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT 令牌验证失败: {e}")
            raise jwt.InvalidTokenError(f"令牌无效: {e}") from e

    def decode_token(
        self, token: str, verify: bool = False, audience: str | None = None
    ) -> dict:
        """
        解码令牌

        Args:
            token: JWT 令牌字符串
            verify: 是否验证签名和过期时间，默认为False（仅解码不验证）
            audience: 期望的受众，如果未提供则使用配置中的默认值

        Returns:
            令牌载荷字典

        Raises:
            jwt.DecodeError: 令牌格式错误
            jwt.InvalidTokenError: 令牌无效或过期（当verify=True时）
        """
        try:
            if verify:
                # 如果未提供 audience，使用配置中的默认值
                if audience is None:
                    audience = self._config.audience

                # 验证模式：验证签名和过期时间
                options = {}
                if not self._config.verify_expiration:
                    options["verify_exp"] = False
                if not self._config.verify_issuer:
                    options["verify_iss"] = False
                if not self._config.verify_audience:
                    options["verify_aud"] = False

                return jwt.decode(
                    token,
                    self._config.secret_key,
                    algorithms=[self._config.algorithm],
                    options=options,
                    audience=audience,
                )
            else:
                # 仅解码模式：不验证任何内容
                return jwt.decode(
                    token,
                    options={
                        "verify_signature": False,
                        "verify_exp": False,
                        "verify_iat": False,
                        "verify_nbf": False,
                        "verify_iss": False,
                        "verify_aud": False,
                    },
                )
        except jwt.ExpiredSignatureError as e:
            logger.warning(f"JWT 令牌已过期: {e}")
            raise jwt.InvalidTokenError("令牌已过期") from e
        except jwt.DecodeError as e:
            logger.error(f"JWT 令牌解码失败: {e}")
            raise jwt.DecodeError(f"令牌格式错误: {e}") from e
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT 令牌验证失败: {e}")
            raise jwt.InvalidTokenError(f"令牌无效: {e}") from e

    async def is_token_blacklisted(self, token_jti: str) -> bool:
        """
        检查令牌是否在黑名单中

        Args:
            token_jti: 令牌的 JTI (JWT ID)

        Returns:
            如果令牌在黑名单中返回 True，否则返回 False
        """
        if not self._config.enable_blacklist:
            return False

        blacklist_key = f"{self._config.blacklist_prefix}{token_jti}"
        return await self._cache_service.exists(blacklist_key)

    async def blacklist_token(self, token_jti: str, expires_at: datetime) -> bool:
        """
        将令牌加入黑名单

        Args:
            token_jti: 令牌的 JTI (JWT ID)
            expires_at: 令牌过期时间

        Returns:
            是否成功加入黑名单
        """
        if not self._config.enable_blacklist:
            return True

        try:
            blacklist_key = f"{self._config.blacklist_prefix}{token_jti}"

            # 计算剩余过期时间（秒）
            current_time = now()
            ttl = int((expires_at - current_time).total_seconds())

            # 如果令牌已过期，无需加入黑名单
            if ttl <= 0:
                return True

            success = await self._cache_service.set(blacklist_key, "1", ttl=ttl)

            if success:
                logger.info(f"令牌已加入黑名单: {token_jti}")

            return success
        except Exception as e:
            logger.error(f"加入令牌黑名单失败: {e}")
            return False

    def _create_token(
        self, payload: dict, token_type: str, expires_delta: timedelta
    ) -> str:
        """
        创建 JWT 令牌的内部方法

        Args:
            payload: 令牌载荷数据
            token_type: 令牌类型
            expires_delta: 过期时间增量

        Returns:
            JWT 令牌字符串
        """
        # 复制载荷以避免修改原始数据
        token_payload = payload.copy()

        # 添加标准 Claims
        current_time = now()
        token_payload.update(
            {
                "iat": current_time,
                "exp": current_time + expires_delta,
                "type": token_type,
                "jti": str(uuid.uuid4()),  # 生成唯一的 JWT ID
            }
        )

        # 添加配置中的 Claims
        if self._config.issuer:
            token_payload["iss"] = self._config.issuer
        if self._config.audience:
            token_payload["aud"] = self._config.audience

        # 构建验证选项
        verification_options = {}
        if not self._config.verify_expiration:
            verification_options["verify_exp"] = False
        if not self._config.verify_issuer:
            verification_options["verify_iss"] = False
        if not self._config.verify_audience:
            verification_options["verify_aud"] = False

        try:
            # 生成令牌
            token = jwt.encode(
                token_payload,
                self._config.secret_key,
                algorithm=self._config.algorithm,
                headers=None,
                json_encoder=None,
            )

            logger.debug(f"创建 {token_type} 令牌成功，JTI: {token_payload['jti']}")
            return token

        except Exception as e:
            logger.error(f"创建 JWT 令牌失败: {e}")
            raise ValueError(f"令牌创建失败: {e}") from e

    def get_token_expires_in(self, token_type: str) -> int:
        """
        获取令牌过期时间（秒）

        Args:
            token_type: 令牌类型（access 或 refresh）

        Returns:
            int: 过期时间（秒）

        Example:
            >>> jwt_service.get_token_expires_in("access")
            1800
        """
        if token_type == self._config.access_token_type:
            return self._config.access_token_expire_minutes * 60
        elif token_type == self._config.refresh_token_type:
            return self._config.refresh_token_expire_days * 24 * 60 * 60
        else:
            raise ValueError(f"未知的令牌类型: {token_type}")

    def get_token_expires_at(self, token_type: str) -> str:
        """
        获取令牌过期时间的格式化字符串

        Args:
            token_type: 令牌类型（access 或 refresh）

        Returns:
            str: 格式化的过期时间字符串 (YYYY-MM-DD HH:MM:SS)

        Example:
            >>> jwt_service.get_token_expires_at("access")
            '2023-12-25 10:30:00'
        """
        from ..time import add_time, format_datetime, now

        current_time = now()

        if token_type == self._config.access_token_type:
            expires_time = add_time(
                current_time, minutes=self._config.access_token_expire_minutes
            )
        elif token_type == self._config.refresh_token_type:
            expires_time = add_time(
                current_time, days=self._config.refresh_token_expire_days
            )
        else:
            raise ValueError(f"未知的令牌类型: {token_type}")

        return format_datetime(expires_time, "%Y-%m-%d %H:%M:%S")

    def get_token_payload_without_verification(self, token: str) -> dict:
        """
        获取令牌载荷（不进行任何验证）

        用于调试和日志记录，不应用于业务逻辑

        Args:
            token: JWT 令牌字符串

        Returns:
            令牌载荷字典
        """
        try:
            return jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                    "verify_iss": False,
                    "verify_aud": False,
                },
            )
        except Exception as e:
            logger.error(f"获取令牌载荷失败: {e}")
            return {}


# 全局 JWT 服务实例
_jwt_service: JWTService | None = None


def get_jwt_service() -> JWTService:
    """
    获取 JWT 服务实例（单例模式）

    Returns:
        JWT 服务实例
    """
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = JWTService()
    return _jwt_service
