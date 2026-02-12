"""
文章验证器

提供文章相关的参数验证功能。
"""

from pydantic import Field, field_validator

from Modules.common.models.base_model import BaseModel


class ArticleAddUpdateRequest(BaseModel):
    """文章添加和更新请求模型"""

    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容（HTML格式）")
    summary: str | None = Field(None, description="文章摘要")
    cover_image_id: int | None = Field(None, description="封面图片ID")
    category_id: int | None = Field(None, description="分类ID")
    tag_ids: str | int | list[int] | None = Field(None, description="标签ID列表")
    status: int = Field(0, description="状态")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """验证文章标题"""
        if not v or len(v.strip()) == 0:
            raise ValueError("文章标题不能为空")
        v = v.strip()
        if len(v) > 200:
            raise ValueError("文章标题长度不能超过200个字符")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """验证文章内容"""
        if not v or len(v.strip()) == 0:
            raise ValueError("文章内容不能为空")
        return v

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v):
        """验证文章摘要"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 500:
            raise ValueError("文章摘要长度不能超过500个字符")
        return v if v else None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1, 2, 3]:
            raise ValueError("状态值只能为0、1、2或3（0=草稿, 1=已发布, 2=审核中, 3=发布失败）")
        return v

    @field_validator("tag_ids", mode="before")
    @classmethod
    def validate_tag_ids(cls, v):
        """验证标签ID列表"""
        if v is None:
            return None
        # 如果是字符串，先转换为数组（支持逗号分隔的字符串格式）
        if isinstance(v, str):
            if not v.strip():
                return []  # 空字符串返回空列表，表示清空标签
            try:
                # 转换、去重、过滤（>0）一步完成
                tag_ids = {int(tid.strip()) for tid in v.split(',') if tid.strip()}
                return [tid for tid in tag_ids if tid > 0]
            except ValueError as err:
                raise ValueError("标签ID列表格式不正确") from err
        if not isinstance(v, list):
            raise ValueError("标签ID列表格式不正确")
        # 去重并过滤掉无效值
        tag_ids = {tid for tid in v if isinstance(tid, int) and tid > 0}
        return list(tag_ids) if tag_ids else []
