"""
股票验证器

提供股票相关的参数验证功能。
"""

from pydantic import Field, field_validator

from ...common.models.base_model import BaseModel


class QuantStockAddUpdateRequest(BaseModel):
    """股票添加和更新请求模型"""

    stock_code: str | None = Field(None, description="股票代码")
    stock_name: str | None = Field(None, description="股票名称")
    market: int | None = Field(None, description="市场类型")
    exchange: int | None = Field(None, description="交易所")
    industry_id: int | None = Field(None, description="行业ID")
    list_status: int | None = Field(None, description="上市状态")
    trade_status: int | None = Field(None, description="交易状态")
    is_st: int | None = Field(None, description="是否ST股")
    stock_type: int | None = Field(None, description="股票类型")
    total_market_cap: float | None = Field(None, description="总市值")
    circulating_market_cap: float | None = Field(None, description="流通市值")
    pe_ratio: float | None = Field(None, description="市盈率")
    pb_ratio: float | None = Field(None, description="市净率")
    total_shares: float | None = Field(None, description="总股本")
    circulating_shares: float | None = Field(None, description="流通股本")
    list_date: str | None = Field(None, description="上市日期")
    delist_date: str | None = Field(None, description="退市日期")
    ipo_price: float | None = Field(None, description="发行价格")
    ipo_shares: float | None = Field(None, description="发行数量")
    description: str | None = Field(None, description="股票描述")
    website: str | None = Field(None, description="官方网站")
    logo_url: str | None = Field(None, description="Logo URL")
    status: int | None = Field(None, description="状态")

    @field_validator("stock_code")
    @classmethod
    def validate_stock_code(cls, v):
        """验证股票代码"""
        if v is None:
            return None
        v = v.strip()
        if len(v) == 0:
            raise ValueError("股票代码不能为空")
        if len(v) > 20:
            raise ValueError("股票代码长度不能超过20个字符")
        return v

    @field_validator("stock_name")
    @classmethod
    def validate_stock_name(cls, v):
        """验证股票名称"""
        if v is None:
            return None
        v = v.strip()
        if len(v) == 0:
            raise ValueError("股票名称不能为空")
        if len(v) > 100:
            raise ValueError("股票名称长度不能超过100个字符")
        return v

    @field_validator("market")
    @classmethod
    def validate_market(cls, v):
        """验证市场类型"""
        if v is None:
            return None
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError("市场类型必须为1-5之间的整数")
        return v

    @field_validator("exchange")
    @classmethod
    def validate_exchange(cls, v):
        """验证交易所"""
        if v is None:
            return None
        if v not in [1, 2, 3, 4, 5, 6]:
            raise ValueError("交易所代码必须为1-6之间的整数")
        return v

    @field_validator("industry_id")
    @classmethod
    def validate_industry_id(cls, v):
        """验证行业ID"""
        if v is None:
            return None
        if v <= 0:
            raise ValueError("行业ID必须大于0")
        return v

    @field_validator("list_status")
    @classmethod
    def validate_list_status(cls, v):
        """验证上市状态"""
        if v is None:
            return None
        if v not in [0, 1, 2, 3]:
            raise ValueError("上市状态必须为0-3之间的整数")
        return v

    @field_validator("trade_status")
    @classmethod
    def validate_trade_status(cls, v):
        """验证交易状态"""
        if v is None:
            return None
        if v not in [0, 1, 2]:
            raise ValueError("交易状态必须为0-2之间的整数")
        return v

    @field_validator("is_st")
    @classmethod
    def validate_is_st(cls, v):
        """验证是否ST股"""
        if v is None:
            return None
        if v not in [0, 1]:
            raise ValueError("是否ST股必须为0或1")
        return v

    @field_validator("stock_type")
    @classmethod
    def validate_stock_type(cls, v):
        """验证股票类型"""
        if v is None:
            return None
        if v not in [1, 2, 3, 4]:
            raise ValueError("股票类型必须为1-4之间的整数")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """验证股票描述"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 1000:
            raise ValueError("股票描述长度不能超过1000个字符")
        return v if v else None

    @field_validator("website")
    @classmethod
    def validate_website(cls, v):
        """验证官方网站"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 200:
            raise ValueError("官方网站长度不能超过200个字符")
        return v if v else None

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v):
        """验证Logo URL"""
        if v is None:
            return None
        v = v.strip()
        if len(v) > 500:
            raise ValueError("Logo URL长度不能超过500个字符")
        return v if v else None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v is None:
            return None
        if v not in [0, 1]:
            raise ValueError("状态值只能为0或1")
        return v


class QuantStockSyncRequest(BaseModel):
    """股票行情数据同步请求模型"""

    market: int = Field(
        1, description="市场类型（1=上海、2=深圳、3=北交所、4=港股、5=美股）"
    )

    @field_validator("market")
    @classmethod
    def validate_market(cls, v):
        """验证市场类型"""
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError("市场类型必须为1-5之间的整数")
        return v
