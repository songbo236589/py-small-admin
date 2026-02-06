"""
平台账号验证器

提供平台账号相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class PlatformAccountAddUpdateRequest(BaseModel):
    """平台账号添加和更新请求模型"""

    platform: str = Field(..., description="平台标识：zhihu")
    account_name: str = Field(..., description="账号名称")
    cookies: str = Field(..., description="Cookie信息（JSON格式）")
    user_agent: str | None = Field(None, description="浏览器UA")
    status: int = Field(1, description="状态")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v):
        """验证平台标识"""
        if not v or len(v.strip()) == 0:
            raise ValueError("平台标识不能为空")
        v = v.strip().lower()
        # 支持的平台列表
        supported_platforms = ["zhihu"]
        if v not in supported_platforms:
            raise ValueError(f"不支持的平台，支持的平台有: {', '.join(supported_platforms)}")
        return v

    @field_validator("account_name")
    @classmethod
    def validate_account_name(cls, v):
        """验证账号名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError("账号名称不能为空")
        v = v.strip()
        if len(v) > 50:
            raise ValueError("账号名称长度不能超过50个字符")
        return v

    @field_validator("cookies")
    @classmethod
    def validate_cookies(cls, v):
        """验证Cookie信息"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Cookie信息不能为空")
        v = v.strip()
        # 尝试解析JSON
        try:
            import json
            cookies_dict = json.loads(v)
            if not isinstance(cookies_dict, dict):
                raise ValueError("Cookie信息格式不正确，应为JSON对象")
            # 检查是否包含cookies字段
            if "cookies" not in cookies_dict:
                raise ValueError("Cookie信息必须包含cookies字段")
            if not isinstance(cookies_dict["cookies"], list):
                raise ValueError("cookies字段应为数组")
        except json.JSONDecodeError:
            raise ValueError("Cookie信息不是有效的JSON格式")
        return v

    @field_validator("user_agent")
    @classmethod
    def validate_user_agent(cls, v):
        """验证浏览器UA"""
        if v is None:
            return None
        v = v.strip()
        if len(v) == 0:
            return None
        if len(v) > 500:
            raise ValueError("浏览器UA长度不能超过500个字符")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1, 2]:
            raise ValueError("状态值只能为0、1或2（0=失效, 1=有效, 2=过期）")
        return v
