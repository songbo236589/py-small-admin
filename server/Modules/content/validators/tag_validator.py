"""
文章标签验证器

提供文章标签相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class TagAddUpdateRequest(BaseModel):
    """标签添加和更新请求模型"""

    name: str = Field(..., description="标签名称")
    slug: str = Field(..., description="标签别名")
    color: str | None = Field(None, description="标签颜色")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证标签名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError("标签名称不能为空")
        if len(v) > 30:
            raise ValueError("标签名称长度不能超过30个字符")
        return v.strip()

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        """验证标签别名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("标签别名不能为空")
        v = v.strip()
        if len(v) > 30:
            raise ValueError("标签别名长度不能超过30个字符")
        # 验证别名格式（只能包含小写字母、数字、连字符）
        import re

        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("标签别名只能包含小写字母、数字和连字符")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        """验证标签颜色"""
        if v is None:
            return None
        v = v.strip()
        if len(v) == 0:
            return None
        # 验证颜色格式（如 #ffffff 或 #fff）
        import re

        if not re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', v):
            raise ValueError("标签颜色格式不正确，应为 #fff 或 #ffffff 格式")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1]:
            raise ValueError("状态值只能为0或1")
        return v

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, v):
        """验证排序"""
        if v < 0:
            raise ValueError("排序值不能小于0")
        return v
