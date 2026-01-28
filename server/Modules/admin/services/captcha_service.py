"""
验证码服务层 - 负责验证码业务逻辑处理
"""

from fastapi.responses import JSONResponse

from Modules.common.libs.captcha import captcha_service
from Modules.common.libs.responses import error, success


class CaptchaService:
    """验证码服务类"""

    async def generate_captcha(self) -> JSONResponse:
        """
        生成验证码

        Returns:
            Dict[str, Any]: 验证码生成结果
        """

        result = await captcha_service.generate_captcha()
        return success(result.model_dump(), "获取验证码成功")

    async def verify_captcha(
        self,
        captcha_id: str,
        captcha_text: str,
    ) -> JSONResponse:
        """
        验证验证码

        Args:
            captcha_id: 验证码ID
            captcha_text: 用户输入的验证码

        Returns:
            Dict[str, Any]: 验证结果
        """
        is_valid = await captcha_service.verify_captcha(captcha_id, captcha_text)

        # 使用ResponseFactory处理返回结果
        if is_valid:
            return success(None, "验证码验证成功")
        else:
            return error("验证码验证失败")
