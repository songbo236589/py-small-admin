"""
角色验证器

提供角色相关的参数验证功能。
"""

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class GroupAddUpdateRequest(BaseModel):
    """角色添加和更新请求模型"""

    name: str = Field(..., description="角色名称")
    content: str | None = Field("", description="角色描述")
    status: int = Field(..., description="状态")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证角色名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError("角色名称不能为空")
        if len(v) > 100:
            raise ValueError("角色名称长度不能超过100个字符")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """验证角色描述"""
        if v is None:
            return ""
        v = v.strip()
        if len(v) > 100:
            raise ValueError("角色描述长度不能超过100个字符")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1]:
            raise ValueError("状态值只能为0或1")
        return v


class GroupAccessUpdateRequest(BaseModel):
    """ID数组请求模型"""

    rules: list[int] = Field(..., description="权限规则")

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, v):
        """验证权限规则"""
        if not v or len(v) == 0:
            raise ValueError("请选择权限规则")

        for id_item in v:
            if id_item <= 0:
                raise ValueError("权限规则不合法")

        return v
