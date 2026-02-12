"""
发布验证器

提供发布相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class PublishArticleRequest(BaseModel):
    """发布文章请求模型"""

    platform: str = Field(..., description="发布平台：zhihu")
    platform_account_id: int = Field(..., description="平台账号ID")
    article_id: int | None = Field(None, description="文章ID（单篇发布）")
    article_ids: list[int] | None = Field(None, description="文章ID列表（批量发布）")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v):
        """验证平台标识"""
        if not v or len(v.strip()) == 0:
            raise ValueError("平台标识不能为空")
        v = v.strip().lower()
        supported_platforms = ["zhihu"]
        if v not in supported_platforms:
            raise ValueError(f"不支持的平台，支持的平台有: {', '.join(supported_platforms)}")
        return v

    @field_validator("platform_account_id")
    @classmethod
    def validate_platform_account_id(cls, v):
        """验证平台账号ID"""
        if v <= 0:
            raise ValueError("平台账号ID必须大于0")
        return v

    @field_validator("article_id")
    @classmethod
    def validate_article_id(cls, v):
        """验证文章ID"""
        if v is not None and v <= 0:
            raise ValueError("文章ID必须大于0")
        return v

    @field_validator("article_ids")
    @classmethod
    def validate_article_ids(cls, v):
        """验证文章ID列表"""
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("文章ID列表格式不正确")
        # 去重并过滤掉无效值
        article_ids = list(set([aid for aid in v if aid and isinstance(aid, int) and aid > 0]))
        if len(article_ids) == 0:
            raise ValueError("文章ID列表不能为空")
        if len(article_ids) > 50:
            raise ValueError("批量发布一次最多支持50篇文章")
        return article_ids

    @field_validator("article_ids")
    @classmethod
    def validate_exclusive(cls, v, values):
        """验证单篇发布和批量发布不能同时使用"""
        # 获取 article_id 的值
        article_id = values.data.get("article_id") if hasattr(values, "data") else None
        if v is not None and article_id is not None:
            raise ValueError("单篇发布(article_id)和批量发布(article_ids)不能同时使用")
        if v is None and article_id is None:
            raise ValueError("必须指定文章ID(article_id)或文章ID列表(article_ids)")
        return v


class PublishBatchRequest(BaseModel):
    """批量发布请求模型"""

    platform: str = Field(..., description="发布平台")
    platform_account_id: int = Field(..., description="平台账号ID")
    article_ids: list[int] = Field(..., description="文章ID列表")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v):
        """验证平台标识"""
        if not v or len(v.strip()) == 0:
            raise ValueError("平台标识不能为空")
        v = v.strip().lower()
        supported_platforms = ["zhihu"]
        if v not in supported_platforms:
            raise ValueError(f"不支持的平台，支持的平台有: {', '.join(supported_platforms)}")
        return v

    @field_validator("platform_account_id")
    @classmethod
    def validate_platform_account_id(cls, v):
        """验证平台账号ID"""
        if v <= 0:
            raise ValueError("平台账号ID必须大于0")
        return v

    @field_validator("article_ids")
    @classmethod
    def validate_article_ids(cls, v):
        """验证文章ID列表"""
        if not v or len(v) == 0:
            raise ValueError("文章ID列表不能为空")
        # 去重并过滤掉无效值
        article_ids = list(set([aid for aid in v if aid and isinstance(aid, int) and aid > 0]))
        if len(article_ids) == 0:
            raise ValueError("文章ID列表不能为空")
        if len(article_ids) > 50:
            raise ValueError("批量发布一次最多支持50篇文章")
        return article_ids


class RetryPublishRequest(BaseModel):
    """重试发布请求模型"""

    article_id: int | None = Field(None, description="文章ID")
    log_id: int | None = Field(None, description="发布日志ID")

    @field_validator("article_id")
    @classmethod
    def validate_article_id(cls, v):
        """验证文章ID"""
        if v is not None and v <= 0:
            raise ValueError("文章ID必须大于0")
        return v

    @field_validator("log_id")
    @classmethod
    def validate_log_id(cls, v):
        """验证发布日志ID"""
        if v is not None and v <= 0:
            raise ValueError("发布日志ID必须大于0")
        return v
