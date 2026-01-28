"""
分页验证器

提供通用的分页参数验证功能，可在整个项目中复用。
"""

from fastapi_pagination import Params as BaseParams
from pydantic import Field, field_validator

from ...models.base_model import BaseModel


# 自定义分页参数类，支持更大的分页值
class CustomParams(BaseParams):
    """
    自定义分页参数类，继承自 fastapi_pagination.Params

    默认值：
    - page: 页码，默认为 1
    - size: 每页记录数，默认为 20，最大值为 10000
    """

    size: int = Field(default=20, ge=1, le=10000, description="每页记录数")


class PaginationRequest(BaseModel):
    """通用分页请求模型"""

    page: int = Field(default=1, description="页码")
    limit: int = Field(
        default=20, description="每页返回多少条记录，用于控制每页显示数量"
    )

    @field_validator("page")
    @classmethod
    def validate_page(cls, v):
        """验证页码"""
        if v < 1:
            raise ValueError("页码必须大于0")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        """验证每页记录数"""
        if v < 1:
            raise ValueError("每页记录数必须大于0")
        if v > 10000:
            raise ValueError("每页记录数不能超过10000")
        return v


class ListStatusRequest(BaseModel):
    """通用列表状态验证"""

    status: int | None = Field(default=None, description="状态")

    @field_validator("status")
    @classmethod
    def validate_page(cls, v):
        """验证状态"""
        if v is not None and v < 0:
            raise ValueError("status必须大于等于0")
        return v


class ListSortRequest(BaseModel):
    """通用列表排序验证"""

    sort: int | None = Field(default=None, description="排序")

    @field_validator("sort")
    @classmethod
    def validate_page(cls, v):
        """验证状态"""
        if v is not None and v < 0:
            raise ValueError("sort必须大于等于0")
        return v


class IdRequest(BaseModel):
    """通用分页请求模型"""

    id: int = Field(..., description="页码")

    @field_validator("id")
    @classmethod
    def validate_page(cls, v):
        """验证页码"""
        if v < 1:
            raise ValueError("id必须大于0")
        return v


class IdArrayRequest(BaseModel):
    """ID数组请求模型"""

    id_array: list[int] = Field(..., description="ID列表")

    @field_validator("id_array")
    @classmethod
    def validate_id_array(cls, v):
        """验证ID数组"""
        if not v or len(v) == 0:
            raise ValueError("ID列表不能为空")

        for id_item in v:
            if id_item <= 0:
                raise ValueError("ID必须大于0")

        return v
