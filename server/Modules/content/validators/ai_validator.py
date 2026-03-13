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
    model: str | None = Field(None, description="指定模型（可选）")
    variant_index: int = Field(0, ge=0, description="变体索引，用于生成不同版本的文章（可选）")

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
