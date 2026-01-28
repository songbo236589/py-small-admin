"""
公共接口控制器 - 负责公共接口处理
"""

from fastapi import Form, Request
from fastapi.responses import JSONResponse

from Modules.admin.services import (
    AuthService,
    CaptchaService,
    SysConfigService,
)
from Modules.admin.validators.common_validator import (
    CaptchaVerifyRequest,
    ChangePasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
)
from Modules.common.libs.validation.decorators import validate_request_data


class CommonController:
    """公共接口控制器"""

    def __init__(self):
        """初始化验证码控制器"""
        self.captcha_service = CaptchaService()
        self.auth_service = AuthService()
        self.sys_config_service = SysConfigService()

    async def generate_captcha(self) -> JSONResponse:
        """
        生成验证码

        Args:
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 验证码生成结果
        """
        return await self.captcha_service.generate_captcha()

    @validate_request_data(CaptchaVerifyRequest)
    async def verify_captcha(
        self,
        captcha_id: str = Form(..., description="验证码ID"),
        captcha_text: str = Form(..., description="用户输入的验证码"),
    ) -> JSONResponse:
        """
        验证验证码

        Args:
            captcha_id: 验证码ID
            captcha_text: 用户输入的验证码

        Returns:
            Dict[str, Any]: 验证结果
        """
        return await self.captcha_service.verify_captcha(captcha_id, captcha_text)

    async def get_system_config(self, request: Request) -> JSONResponse:
        """
        获取项目配置信息

        Args:
            request: FastAPI请求对象

        Returns:
            Dict[str, Any]: 验证码生成结果
        """
        return await self.sys_config_service.get_system_config(request)

    @validate_request_data(LoginRequest)
    async def login(
        self,
        username: str = Form(..., description="用户名"),
        password: str = Form(..., description="密码"),
        captcha_id: str = Form(..., description="验证码ID"),
        captcha: str = Form(..., description="验证码"),
    ) -> JSONResponse:
        """用户登录接口"""
        return await self.auth_service.login(
            {
                "username": username.strip(),
                "password": password,
                "captcha_id": captcha_id,
                "captcha": captcha,
            }
        )

    @validate_request_data(LogoutRequest)
    async def logout(
        self, request: Request, refresh_token: str = Form(..., description="刷新令牌")
    ) -> JSONResponse:
        """用户登出接口"""
        return await self.auth_service.logout(request, refresh_token)

    @validate_request_data(RefreshTokenRequest)
    async def refresh_token(
        self, request: Request, refresh_token: str = Form(..., description="刷新令牌")
    ) -> JSONResponse:
        """刷新访问令牌接口"""
        return await self.auth_service.refresh_token(
            {"refresh_token": refresh_token}, request
        )

    async def get_current_user_info(self, request: Request) -> JSONResponse:
        """获取当前登录用户信息"""
        return await self.auth_service.get_current_user_info(request)

    @validate_request_data(ChangePasswordRequest)
    async def change_password(
        self,
        request: Request,
        old_password: str = Form(..., description="旧密码"),
        new_password: str = Form(..., description="新密码"),
        confirm_password: str = Form(..., description="确认新密码"),
    ) -> JSONResponse:
        """修改当前用户密码"""
        return await self.auth_service.change_password(
            {
                "old_password": old_password,
                "new_password": new_password,
                "confirm_password": confirm_password,
            },
            request,
        )

    async def get_menu_tree(self, request: Request) -> JSONResponse:
        """获取当前用户的菜单树"""
        return await self.auth_service.get_menu_tree(request)
