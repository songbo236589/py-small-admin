"""
行业验证器

提供行业相关的参数验证功能。
"""

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class QuantIndustryAddUpdateRequest(BaseModel):
    """行业添加和更新请求模型"""

    name: str = Field(..., description="行业名称")
    code: str | None = Field(None, description="行业代码")
    description: str | None = Field(None, description="行业描述")
    sort: int | None = Field(0, description="排名")
    latest_price: float | None = Field(None, description="最新价")
    change_amount: float | None = Field(None, description="涨跌额")
    change_percent: float | None = Field(None, description="涨跌幅")
    total_market_cap: float | None = Field(None, description="总市值")
    turnover_rate: float | None = Field(None, description="换手率")
    up_count: int | None = Field(None, description="上涨家数")
    down_count: int | None = Field(None, description="下跌家数")
    leading_stock: str | None = Field(None, description="领涨股票")
    leading_stock_change: float | None = Field(None, description="领涨股票涨跌幅")
    status: int = Field(..., description="状态")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证行业名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError("行业名称不能为空")
        if len(v) > 100:
            raise ValueError("行业名称长度不能超过100个字符")
        return v.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        """验证行业代码"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 50:
            raise ValueError("行业代码长度不能超过50个字符")
        return v if v else None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """验证行业描述"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 500:
            raise ValueError("行业描述长度不能超过500个字符")
        return v if v else None

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, v):
        """验证排名"""
        if v is None:
            return 0
        if v < 0:
            raise ValueError("排名值不能小于0")
        return v

    @field_validator("latest_price")
    @classmethod
    def validate_latest_price(cls, v):
        """验证最新价"""
        if v is None:
            return None
        if v < 0:
            raise ValueError("最新价不能小于0")
        return v

    @field_validator("change_amount")
    @classmethod
    def validate_change_amount(cls, v):
        """验证涨跌额"""
        if v is None:
            return None
        return v

    @field_validator("change_percent")
    @classmethod
    def validate_change_percent(cls, v):
        """验证涨跌幅"""
        if v is None:
            return None
        return v

    @field_validator("total_market_cap")
    @classmethod
    def validate_total_market_cap(cls, v):
        """验证总市值"""
        if v is None:
            return None
        if v < 0:
            raise ValueError("总市值不能小于0")
        return v

    @field_validator("turnover_rate")
    @classmethod
    def validate_turnover_rate(cls, v):
        """验证换手率"""
        if v is None:
            return None
        if v < 0:
            raise ValueError("换手率不能小于0")
        return v

    @field_validator("up_count")
    @classmethod
    def validate_up_count(cls, v):
        """验证上涨家数"""
        if v is None:
            return None
        if v < 0:
            raise ValueError("上涨家数不能小于0")
        return v

    @field_validator("down_count")
    @classmethod
    def validate_down_count(cls, v):
        """验证下跌家数"""
        if v is None:
            return None
        if v < 0:
            raise ValueError("下跌家数不能小于0")
        return v

    @field_validator("leading_stock")
    @classmethod
    def validate_leading_stock(cls, v):
        """验证领涨股票"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 50:
            raise ValueError("领涨股票名称长度不能超过50个字符")
        return v if v else None

    @field_validator("leading_stock_change")
    @classmethod
    def validate_leading_stock_change(cls, v):
        """验证领涨股票涨跌幅"""
        if v is None:
            return None
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v not in [0, 1]:
            raise ValueError("状态值只能为0或1")
        return v
