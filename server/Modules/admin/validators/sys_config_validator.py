"""
系统配置验证器

提供系统配置相关的参数验证功能。
"""

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class SysConfigGroupCodeRequest(BaseModel):
    """配置分组请求模型"""

    group_code: str = Field(..., description="配置分组")

    @field_validator("group_code")
    @classmethod
    def validate_group_code(cls, v):
        """验证配置分组"""
        if not v or len(v.strip()) == 0:
            raise ValueError("配置分组不能为空")
        v = v.strip()
        valid_groups = ["system", "email", "upload"]
        if v not in valid_groups:
            raise ValueError(f"配置分组必须是: {', '.join(valid_groups)} 中的一个")
        return v
