"""
验证码服务核心模块

提供验证码的生成、验证和管理功能。
"""

from typing import Any

from loguru import logger

from config.captcha import CaptchaType

from ..cache import get_async_cache_service
from ..config import Config
from .image_generator import ImageGenerator
from .utils import (
    CaptchaResult,
    generate_captcha_id,
    generate_math_question,
)


class CaptchaService:
    """
    验证码服务类

    提供完整的验证码管理功能，包括：
    - 图片验证码生成和验证
    - 数学题验证码生成和验证
    - 验证码存储和过期管理
    - 与配置系统的集成
    """

    def __init__(self):
        """初始化验证码服务"""
        # 加载验证码配置
        self._config = Config.get("captcha")
        self._cache_service = get_async_cache_service()

        # 初始化图片生成器
        self._image_generator = ImageGenerator()

    async def generate_captcha(
        self, captcha_type: CaptchaType | None = None
    ) -> CaptchaResult:
        """
        生成验证码

        Args:
            captcha_type: 验证码类型

        Returns:
            CaptchaResult: 验证码生成结果
        """
        try:
            # 如果没有指定验证码类型，使用配置中的默认值
            if captcha_type is None:
                captcha_type = self._config.default_type

            # 生成验证码 ID
            captcha_id = generate_captcha_id()

            if captcha_type == CaptchaType.IMAGE:
                return await self._generate_image_captcha(captcha_id)
            elif captcha_type == CaptchaType.MATH:
                return await self._generate_math_captcha(captcha_id)
            else:
                raise ValueError(f"不支持的验证码类型: {captcha_type}")

        except Exception as e:
            logger.error(f"生成验证码失败: {e}")
            raise

    async def _generate_image_captcha(self, captcha_id: str) -> CaptchaResult:
        """生成图片验证码"""
        # 生成验证码文本
        text = self._image_generator.generate_text()

        # 生成验证码图片
        image_data = self._image_generator.generate_image(text)

        # 存储验证码答案
        cache_key = f"{self._config.redis_key_prefix}{captcha_id}"
        await self._cache_service.set(
            cache_key,
            text.lower(),  # 统一转换为小写，便于验证
            ttl=self._config.expire_seconds,
        )

        return CaptchaResult(
            captcha_id=captcha_id,
            captcha_type=CaptchaType.IMAGE,
            image_data=image_data,
            expire_seconds=self._config.expire_seconds,
            metadata={"length": len(text)},
            font_size=self._config.font_size,
        )

    async def _generate_math_captcha(self, captcha_id: str) -> CaptchaResult:
        """生成数学题验证码"""
        # 生成数学题
        question, answer = generate_math_question()

        # 生成数学题图片
        image_data = self._image_generator.generate_image(question)

        # 存储验证码答案
        cache_key = f"{self._config.redis_key_prefix}{captcha_id}"
        await self._cache_service.set(
            cache_key, answer, ttl=self._config.expire_seconds
        )

        return CaptchaResult(
            captcha_id=captcha_id,
            captcha_type=CaptchaType.MATH,
            image_data=image_data,  # 返回图片数据
            # question=question,  # 保留文本作为备用
            # answer=answer,  # 仅用于调试，实际使用时不应该返回答案
            expire_seconds=self._config.expire_seconds,
            metadata={"question_type": "math", "format": "image"},
            font_size=self._config.font_size,
        )

    async def verify_captcha(self, captcha_id: str, answer: str) -> bool:
        """
        验证验证码

        Args:
            captcha_id: 验证码 ID
            answer: 用户输入的答案

        Returns:
            bool: 验证结果
        """
        try:
            if not captcha_id or not answer:
                return False

            # 获取存储的验证码答案
            cache_key = f"{self._config.redis_key_prefix}{captcha_id}"
            stored_answer = await self._cache_service.get(cache_key)

            if stored_answer is None:
                logger.warning(f"验证码不存在或已过期: {captcha_id}")
                return False

            # 验证答案（忽略大小写）
            is_valid = str(answer).strip().lower() == str(stored_answer).lower()

            if is_valid:
                # 验证成功，删除验证码（一次性使用）
                await self._cache_service.delete(cache_key)
                logger.debug(f"验证码验证成功: {captcha_id}")
            else:
                logger.warning(
                    f"验证码验证失败: {captcha_id}, 输入: {answer}, 正确: {stored_answer}"
                )

            return is_valid

        except Exception as e:
            logger.error(f"验证验证码失败: {e}")
            return False

    async def get_captcha_image(self, captcha_id: str) -> bytes | None:
        """
        获取验证码图片

        Args:
            captcha_id: 验证码 ID

        Returns:
            bytes | None: 图片数据，如果不存在返回 None
        """
        try:
            # 获取存储的验证码信息
            cache_key = f"{self._config.redis_key_prefix}{captcha_id}"
            stored_answer = await self._cache_service.get(cache_key)

            if stored_answer is None:
                logger.warning(f"验证码不存在或已过期: {captcha_id}")
                return None

            # 重新生成图片（基于存储的答案）
            image_data = self._image_generator.generate_image(stored_answer)

            return image_data

        except Exception as e:
            logger.error(f"获取验证码图片失败: {e}")
            return None

    async def refresh_captcha(self, captcha_id: str) -> CaptchaResult | None:
        """
        刷新验证码（延长过期时间）

        Args:
            captcha_id: 验证码 ID

        Returns:
            CaptchaResult | None: 刷新后的验证码信息，如果不存在返回 None
        """
        try:
            # 获取存储的验证码答案
            cache_key = f"{self._config.redis_key_prefix}{captcha_id}"
            stored_answer = await self._cache_service.get(cache_key)

            if stored_answer is None:
                logger.warning(f"验证码不存在或已过期: {captcha_id}")
                return None

            # 延长过期时间
            await self._cache_service.expire(cache_key, self._config.expire_seconds)

            # 重新生成图片
            image_data = self._image_generator.generate_image(stored_answer)

            return CaptchaResult(
                captcha_id=captcha_id,
                captcha_type=CaptchaType.IMAGE,
                image_data=image_data,
                expire_seconds=self._config.expire_seconds,
                metadata={"refreshed": True},
            )

        except Exception as e:
            logger.error(f"刷新验证码失败: {e}")
            return None

    async def cleanup_expired_captcha(self) -> int:
        """
        清理过期的验证码

        Returns:
            int: 清理的数量
        """
        try:
            # 这个方法需要根据具体的缓存实现来清理过期键
            # 对于 Redis，可以配置自动过期，这个方法主要用于其他缓存后端
            logger.info("清理过期验证码")
            return 0

        except Exception as e:
            logger.error(f"清理过期验证码失败: {e}")
            return 0

    async def get_captcha_stats(self) -> dict[str, Any]:
        """
        获取验证码统计信息

        Returns:
            dict[str, Any]: 统计信息
        """
        try:
            # 获取当前活跃的验证码数量
            # 这个方法的具体实现取决于缓存后端的支持
            stats = {
                "active_captchas": 0,
                "config": {
                    "length": self._config.length,
                    "expire_seconds": self._config.expire_seconds,
                    "char_type": self._config.char_type.value,
                    "distortion": self._config.distortion,
                },
            }

            return stats

        except Exception as e:
            logger.error(f"获取验证码统计信息失败: {e}")
            return {}


# 全局验证码服务实例
_captcha_service: CaptchaService | None = None


def get_captcha_service() -> CaptchaService:
    """
    获取验证码服务实例（单例模式）

    Returns:
        CaptchaService: 验证码服务实例
    """
    global _captcha_service
    if _captcha_service is None:
        _captcha_service = CaptchaService()
    return _captcha_service


# 便捷函数
async def generate_captcha(
    captcha_type: CaptchaType | None = None,
) -> CaptchaResult:
    """便捷函数：生成验证码"""
    service = get_captcha_service()
    return await service.generate_captcha(captcha_type)


async def verify_captcha(captcha_id: str, answer: str) -> bool:
    """便捷函数：验证验证码"""
    service = get_captcha_service()
    return await service.verify_captcha(captcha_id, answer)


async def get_captcha_image(captcha_id: str) -> bytes | None:
    """便捷函数：获取验证码图片"""
    service = get_captcha_service()
    return await service.get_captcha_image(captcha_id)
