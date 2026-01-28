"""
统一股票表模型

对应数据库表：quant_stocks
"""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.mysql import DECIMAL, INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

from .quant_stock_concept import QuantStockConcept

if TYPE_CHECKING:
    from .quant_concept import QuantConcept
    from .quant_industry import QuantIndustry


class QuantStock(BaseTableModel, table=True):
    """
    统一股票表模型

    对应数据库表 quant_stocks，存储所有市场股票基础信息。
    支持A股、港股、美股等多市场股票统一管理。
    """

    # 表注释
    __table_comment__ = "统一股票表，存储所有市场股票基础信息"

    # ==================== 基础标识字段 ====================

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 股票代码（如：600000.SH、000001.SZ、00700.HK、AAPL.US）
    stock_code: str | None = Field(
        sa_column=Column(
            String(20),
            nullable=False,
            unique=True,
            index=True,
            comment="股票代码（如：600000.SH、000001.SZ、00700.HK、AAPL.US）",
        ),
        default="",
    )

    # 股票名称
    stock_name: str | None = Field(
        sa_column=Column(
            String(100), nullable=False, server_default="", comment="股票名称"
        ),
        default="",
    )

    # ==================== 市场与分类字段 ====================

    # 市场类型（1=上海(SH)、2=深圳(SZ)、3=北京(BJ)、4=港股(HK)、5=美股(US)）
    market: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="0",
            index=True,
            comment="市场类型（1=上海(SH)、2=深圳(SZ)、3=北京(BJ)、4=港股(HK)、5=美股(US)）",
        ),
        default=0,
    )

    # 交易所代码（1=上海证券交易所(SSE)、2=深圳证券交易所(SZSE)、3=北京证券交易所(BSE)、4=香港交易所(HKEX)、5=纳斯达克(NASDAQ)、6=纽约证券交易所(NYSE)、7=美国证券交易所(AMEX)）
    exchange: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=True,
            server_default="0",
            comment="交易所代码（1=上海证券交易所(SSE)、2=深圳证券交易所(SZSE)、3=北京证券交易所(BSE)、4=香港交易所(HKEX)、5=纳斯达克(NASDAQ)、6=纽约证券交易所(NYSE)、7=美国证券交易所(AMEX)）",
        ),
        default=0,
    )

    # 行业ID（外键关联到 quant_industries 表）
    industry_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("quant_industrys.id"),
            nullable=True,
            index=True,
            comment="所属行业ID",
        ),
        default=None,
    )

    # ==================== 状态字段 ====================

    # 上市状态（0=未上市、1=已上市、2=退市、3=暂停上市）
    list_status: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            index=True,
            comment="上市状态（0=未上市、1=已上市、2=退市、3=暂停上市）",
        ),
        default=1,
    )

    # 交易状态（0=停牌、1=正常交易、2=特别处理）
    trade_status: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            index=True,
            comment="交易状态（0=停牌、1=正常交易、2=特别处理）",
        ),
        default=1,
    )

    # 是否ST股（0=否、1=是）
    is_st: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="0",
            comment="是否ST股（0=否、1=是）",
        ),
        default=0,
    )

    # 股票类型（1=主板、2=创业板、3=科创板、4=北交所）
    stock_type: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=True,
            index=True,
            comment="股票类型（1=主板、2=创业板、3=科创板、4=北交所）",
        ),
        default=None,
    )

    # ==================== 财务与估值字段 ====================

    # 总市值（单位：亿元）
    total_market_cap: Decimal | None = Field(
        sa_column=Column(DECIMAL(15, 2), nullable=True, comment="总市值（单位：亿元）"),
        default=None,
    )

    # 流通市值（单位：亿元）
    circulating_market_cap: Decimal | None = Field(
        sa_column=Column(
            DECIMAL(15, 2), nullable=True, comment="流通市值（单位：亿元）"
        ),
        default=None,
    )

    # 市盈率（动态）
    pe_ratio: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="市盈率（动态）"),
        default=None,
    )

    # 市净率
    pb_ratio: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="市净率"),
        default=None,
    )

    # 总股本（万股）
    total_shares: Decimal | None = Field(
        sa_column=Column(DECIMAL(15, 2), nullable=True, comment="总股本（万股）"),
        default=None,
    )

    # 流通股本（万股）
    circulating_shares: Decimal | None = Field(
        sa_column=Column(DECIMAL(15, 2), nullable=True, comment="流通股本（万股）"),
        default=None,
    )

    # ==================== 价格行情字段 ====================

    # 最新价
    latest_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="最新价"),
        default=None,
    )

    # 今开
    open_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="今开"),
        default=None,
    )

    # 昨收
    close_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="昨收"),
        default=None,
    )

    # 最高
    high_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="最高"),
        default=None,
    )

    # 最低
    low_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="最低"),
        default=None,
    )

    # 涨跌幅（%）
    change_percent: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="涨跌幅（%）"),
        default=None,
    )

    # 涨跌额
    change_amount: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="涨跌额"),
        default=None,
    )

    # 涨速
    change_speed: Decimal | None = Field(
        sa_column=Column(DECIMAL(8, 4), nullable=True, comment="涨速"),
        default=None,
    )

    # ==================== 交易指标字段 ====================

    # 成交量
    volume: Decimal | None = Field(
        sa_column=Column(DECIMAL(20, 0), nullable=True, comment="成交量"),
        default=None,
    )

    # 成交额
    amount: Decimal | None = Field(
        sa_column=Column(DECIMAL(20, 2), nullable=True, comment="成交额"),
        default=None,
    )

    # 量比
    volume_ratio: Decimal | None = Field(
        sa_column=Column(DECIMAL(8, 2), nullable=True, comment="量比"),
        default=None,
    )

    # 换手率（%）
    turnover_rate: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="换手率（%）"),
        default=None,
    )

    # 振幅（%）
    amplitude: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="振幅（%）"),
        default=None,
    )

    # 5分钟涨跌（%）
    change_5min: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="5分钟涨跌（%）"),
        default=None,
    )

    # 60日涨跌幅（%）
    change_60day: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="60日涨跌幅（%）"),
        default=None,
    )

    # 年初至今涨跌幅（%）
    change_ytd: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="年初至今涨跌幅（%）"),
        default=None,
    )

    # ==================== 上市信息字段 ====================

    # 上市日期
    list_date: date | None = Field(
        sa_column=Column(Date, nullable=True, index=True, comment="上市日期"),
        default=None,
    )

    # 退市日期
    delist_date: date | None = Field(
        sa_column=Column(Date, nullable=True, comment="退市日期"),
        default=None,
    )

    # 发行价格
    ipo_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="发行价格"),
        default=None,
    )

    # 发行数量（万股）
    ipo_shares: Decimal | None = Field(
        sa_column=Column(DECIMAL(15, 2), nullable=True, comment="发行数量（万股）"),
        default=None,
    )

    # ==================== 扩展字段 ====================

    # 股票描述/简介
    description: str | None = Field(
        sa_column=Column(String(1000), nullable=True, comment="股票描述/简介"),
        default=None,
    )

    # 官方网站
    website: str | None = Field(
        sa_column=Column(String(200), nullable=True, comment="官方网站"),
        default=None,
    )

    # 公司Logo URL
    logo_url: str | None = Field(
        sa_column=Column(String(500), nullable=True, comment="公司Logo URL"),
        default=None,
    )

    # ==================== 状态控制字段 ====================

    # 记录状态（0=禁用、1=启用）
    status: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="记录状态（0=禁用、1=启用）",
        ),
        default=1,
    )

    # 创建时间
    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    # 更新时间
    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    # 多对多：股票 → 概念
    concepts: Mapped[list["QuantConcept"]] = Relationship(
        back_populates="stocks", link_model=QuantStockConcept
    )

    # 多对一：股票 → 行业
    industry: Mapped["QuantIndustry"] = Relationship(back_populates="stocks")

    class Config:
        """Pydantic配置"""

        from_attributes = True
