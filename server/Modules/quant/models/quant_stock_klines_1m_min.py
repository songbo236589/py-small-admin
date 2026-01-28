"""
1分钟K线数据表模型

对应数据库表：quant_stock_klines_1m_min
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger
from sqlalchemy.dialects.mysql import DECIMAL, INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class QuantStockKline1mMin(BaseTableModel, table=True):
    """
    1分钟K线数据表模型

    对应数据库表 quant_stock_klines_1m_min，存储股票1分钟K线数据。
    """

    # 表注释
    __table_comment__ = "1分钟K线数据表，存储股票1分钟K线数据"

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

    # 股票ID（外键关联 quant_stocks.id）
    stock_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("quant_stocks.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="股票ID",
        ),
        default=None,
    )

    # ==================== 时间字段 ====================

    # 交易时间
    trade_time: datetime | None = Field(
        sa_column=Column(
            DateTime(),
            nullable=False,
            index=True,
            comment="交易时间",
        ),
        default=None,
    )

    # ==================== OHLC价格字段 ====================

    # 开盘价
    open_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="开盘价"),
        default=None,
    )

    # 最高价
    high_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="最高价"),
        default=None,
    )

    # 最低价
    low_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="最低价"),
        default=None,
    )

    # 收盘价
    close_price: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="收盘价"),
        default=None,
    )

    # ==================== 成交量数据字段 ====================

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

    # ==================== 扩展字段 ====================

    # 换手率（%）
    turnover_rate: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="换手率（%）"),
        default=None,
    )

    # 涨跌幅（%）
    change_percent: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="涨跌幅（%）"),
        default=None,
    )

    # 振幅（%）
    amplitude: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 4), nullable=True, comment="振幅（%）"),
        default=None,
    )

    # 涨跌额
    change_amount: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, comment="涨跌额"),
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

    class Config:
        """Pydantic配置"""

        from_attributes = True
