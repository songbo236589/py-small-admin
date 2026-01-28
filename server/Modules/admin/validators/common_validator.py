"""
通用验证器

定义各种请求验证模型和验证规则，包括验证码、登录、令牌刷新和密码修改等。
"""

from pydantic import field_validator
from sqlmodel import Field

from Modules.common.models.base_model import BaseModel


class FileTypeRequest(BaseModel):
    """文件类型请求模型"""

    file_type: str = Field(..., description="文件类型")

    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, v):
        """验证文件类型"""
        if not v or not v.strip():
            raise ValueError("文件类型不能为空")

        file_type = v.strip().lower()
        valid_types = ["image", "document", "video", "audio"]

        if file_type not in valid_types:
            raise ValueError(f"文件类型无效，支持的类型: {', '.join(valid_types)}")

        return file_type


class CaptchaVerifyRequest(BaseModel):
    """验证码验证请求模型"""

    captcha_id: str = Field(..., description="验证码ID")
    captcha_text: str = Field(..., description="用户输入的验证码")

    @field_validator("captcha_id")
    @classmethod
    def validate_captcha_id(cls, v):
        """验证验证码ID格式"""
        if not v or not v.strip():
            raise ValueError("验证码ID不能为空")
        if len(v.strip()) < 10:
            raise ValueError("验证码ID格式不正确，长度不能少于10个字符")
        return v.strip()

    @field_validator("captcha_text")
    @classmethod
    def validate_captcha_text(cls, v):
        """验证验证码文本"""
        if not v or not v.strip():
            raise ValueError("验证码不能为空")
        if len(v.strip()) < 1:
            raise ValueError("验证码长度不能少于1个字符")
        return v.strip()


class LoginRequest(BaseModel):
    """登录请求模型"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    captcha: str | None = Field(None, description="验证码")
    captcha_id: str | None = Field(None, description="验证码ID")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """验证用户名"""
        if not v or not v.strip():
            raise ValueError("用户名不能为空")
        if len(v.strip()) < 3:
            raise ValueError("用户名长度不能少于3个字符")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """验证密码"""
        if not v:
            raise ValueError("密码不能为空")
        if len(v) < 6:
            raise ValueError("密码长度不能少于6个字符")
        return v


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""

    refresh_token: str = Field(..., description="刷新令牌")

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v):
        """验证刷新令牌"""
        if not v or not v.strip():
            raise ValueError("刷新令牌不能为空")
        if len(v.strip()) < 10:
            raise ValueError("刷新令牌格式不正确")
        return v.strip()


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @field_validator("old_password")
    @classmethod
    def validate_old_password(cls, v):
        """验证旧密码"""
        if not v:
            raise ValueError("旧密码不能为空")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """验证新密码"""
        if not v:
            raise ValueError("新密码不能为空")
        if len(v) < 6:
            raise ValueError("新密码长度不能少于6个字符")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v, info):
        """验证确认密码"""
        if not v:
            raise ValueError("确认密码不能为空")
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("确认密码与新密码不匹配")
        return v


class LogoutRequest(BaseModel):
    """登出请求模型"""

    refresh_token: str = Field(..., description="刷新令牌")

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v):
        """验证刷新令牌"""
        if not v or not v.strip():
            raise ValueError("刷新令牌不能为空")
        if len(v.strip()) < 10:
            raise ValueError("刷新令牌格式不正确")
        return v.strip()
