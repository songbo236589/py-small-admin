"""
AI 验证器

提供 AI 生成文章相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class AIGenerateArticleRequest(BaseModel):
    """AI 生成文章请求模型"""

    id: int = Field(..., gt=0, description="话题ID")
    mode: str = Field(..., description="生成模式: title/description/full")
    title: str = Field(..., description="问题标题")
    description: str | None = Field(None, description="问题描述")
    model: str | None = Field(None, description="指定模型（可选）")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        """验证话题ID"""
        if v <= 0:
            raise ValueError("话题ID必须大于0")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        """验证生成模式"""
        valid_modes = ["title", "description", "full"]
        if v not in valid_modes:
            raise ValueError(f"生成模式只能是: {', '.join(valid_modes)}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """验证问题标题"""
        if not v or len(v.strip()) == 0:
            raise ValueError("问题标题不能为空")
        v = v.strip()
        if len(v) > 500:
            raise ValueError("问题标题长度不能超过500个字符")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """验证问题描述"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 5000:
            raise ValueError("问题描述长度不能超过5000个字符")
        return v if v else None

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        """验证模型名称"""
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > 100:
            raise ValueError("模型名称长度不能超过100个字符")
        return v
