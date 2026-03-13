"""
话题验证器

提供话题相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class UpdateDescriptionRequest(BaseModel):
    """更新话题描述请求模型"""

    description: str = Field(..., min_length=1, max_length=2000, description="描述内容")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """验证描述内容"""
        if not v or len(v.strip()) == 0:
            raise ValueError("描述内容不能为空")
        v = v.strip()
        if len(v) < 5:
            raise ValueError("描述内容至少需要5个字符")
        if len(v) > 2000:
            raise ValueError("描述内容不能超过2000个字符")
        return v


class GenerateDescriptionRequest(BaseModel):
    """生成话题描述请求模型"""

    model: str | None = Field(None, description="AI 模型名称")

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        """验证模型名称"""
        if v is None:
            return None
        v = v.strip()
        if len(v) == 0:
            return None
        if len(v) > 100:
            raise ValueError("模型名称长度不能超过100个字符")
        return v


class UpdateCategoryRequest(BaseModel):
    """更新话题分类请求模型"""

    category_id: int | None = Field(None, description="分类ID")

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, v):
        """验证分类ID"""
        if v is None:
            return None
        if v <= 0:
            raise ValueError("分类ID必须大于0")
        return v


class BatchUpdateCategoryRequest(BaseModel):
    """批量更新话题分类请求模型"""

    id_array: list[int] = Field(..., min_length=1, description="话题ID列表")
    category_id: int | None = Field(None, description="分类ID")

    @field_validator("id_array")
    @classmethod
    def validate_id_array(cls, v):
        """验证ID数组"""
        if not v or len(v) == 0:
            raise ValueError("请选择要更新的话题")
        if len(v) > 1000:
            raise ValueError("批量更新最多支持1000条记录")
        return v

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, v):
        """验证分类ID"""
        if v is None:
            return None
        if v <= 0:
            raise ValueError("分类ID必须大于0")
        return v
