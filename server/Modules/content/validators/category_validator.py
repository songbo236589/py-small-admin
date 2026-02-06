"""
文章分类验证器

提供文章分类相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class CategoryAddUpdateRequest(BaseModel):
    """分类添加和更新请求模型"""

    name: str = Field(..., description="分类名称")
    slug: str = Field(..., description="分类别名")
    parent_id: int | None = Field(None, description="父分类ID")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态")
    description: str | None = Field(None, description="分类描述")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证分类名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError("分类名称不能为空")
        if len(v) > 50:
            raise ValueError("分类名称长度不能超过50个字符")
        return v.strip()

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        """验证分类别名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("分类别名不能为空")
        v = v.strip()
        if len(v) > 50:
            raise ValueError("分类别名长度不能超过50个字符")
        # 验证别名格式（只能包含小写字母、数字、连字符）
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError("分类别名只能包含小写字母、数字和连字符")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """验证分类描述"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 200:
            raise ValueError("分类描述长度不能超过200个字符")
        return v if v else None

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
