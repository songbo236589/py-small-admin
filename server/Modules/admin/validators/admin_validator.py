"""
管理员验证器

提供管理员相关的参数验证功能。
"""

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class AdminAddRequest(BaseModel):
    """管理员添加请求模型"""

    username: str = Field(..., description="用户名")
    name: str = Field(..., description="真实姓名")
    password: str = Field(..., description="密码")
    phone: str | None = Field(None, description="手机号")
    status: int = Field(..., description="状态")
    group_id: int = Field(..., description="所属角色")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """验证用户名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("用户名不能为空")
        if len(v) < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if len(v) > 50:
            raise ValueError("用户名长度不能超过50个字符")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证真实姓名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("真实姓名不能为空")
        if len(v) > 50:
            raise ValueError("真实姓名长度不能超过50个字符")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """验证手机号"""
        if v is None:
            return v
        v = v.strip()
        if len(v) == 0:
            return None
        # 简单的手机号验证
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号格式不正确")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1]:
            raise ValueError("状态值只能为0或1")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """验证密码"""
        if not v or len(v.strip()) == 0:
            raise ValueError("密码不能为空")
        if len(v) < 6:
            raise ValueError("密码长度不能少于6个字符")
        if len(v) > 50:
            raise ValueError("密码长度不能超过50个字符")
        return v.strip()

    @field_validator("group_id")
    @classmethod
    def validate_group_id(cls, v):
        """验证所属角色"""
        if v <= 0:
            raise ValueError("所属角色ID必须大于0")
        return v


class AdminUpdateRequest(BaseModel):
    """管理员添加请求模型"""

    username: str = Field(..., description="用户名")
    name: str = Field(..., description="真实姓名")
    phone: str | None = Field(None, description="手机号")
    status: int = Field(..., description="状态")
    group_id: int = Field(..., description="所属角色")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """验证用户名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("用户名不能为空")
        if len(v) < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if len(v) > 50:
            raise ValueError("用户名长度不能超过50个字符")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证真实姓名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("真实姓名不能为空")
        if len(v) > 50:
            raise ValueError("真实姓名长度不能超过50个字符")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """验证手机号"""
        if v is None:
            return v
        v = v.strip()
        if len(v) == 0:
            return None
        # 简单的手机号验证
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号格式不正确")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1]:
            raise ValueError("状态值只能为0或1")
        return v

    @field_validator("group_id")
    @classmethod
    def validate_group_id(cls, v):
        """验证所属角色"""
        if v <= 0:
            raise ValueError("所属角色ID必须大于0")
        return v
