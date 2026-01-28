"""
概念表模型

对应数据库表：quant_concepts
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

from .quant_stock_concept import QuantStockConcept

if TYPE_CHECKING:
    from .quant_stock import QuantStock


class QuantConcept(BaseTableModel, table=True):
    """
    概念表模型

    对应数据库表 quant_concepts，存储股票概念标签信息。
    """

    # 表注释
    __table_comment__ = "概念表，存储股票概念标签信息"

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

    # 概念名称（如：人工智能、芯片、5G）
    name: str | None = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            unique=True,
            index=True,
            comment="概念名称（如：人工智能、芯片、5G）",
        ),
        default="",
    )

    # 概念代码（如：AI、CHIP、5G）
    code: str | None = Field(
        sa_column=Column(
            String(20),
            nullable=False,
            unique=True,
            index=True,
            comment="概念代码（如：AI、CHIP、5G）",
        ),
        default="",
    )

    # 排名
    sort: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="排名",
        ),
        default=0,
    )

    # 最新价
    latest_price: float | None = Field(
        sa_column=Column(
            Numeric(10, 2),
            nullable=True,
            server_default="0",
            comment="最新价",
        ),
        default=0,
    )

    # 涨跌额
    change_amount: float | None = Field(
        sa_column=Column(
            Numeric(10, 2),
            nullable=True,
            server_default="0",
            comment="涨跌额",
        ),
        default=0,
    )

    # 涨跌幅
    change_percent: float | None = Field(
        sa_column=Column(
            Numeric(5, 2),
            nullable=True,
            server_default="0",
            comment="涨跌幅",
        ),
        default=0,
    )

    # 总市值
    total_market_cap: float | None = Field(
        sa_column=Column(
            Numeric(20, 2),
            nullable=True,
            server_default="0",
            comment="总市值",
        ),
        default=0,
    )

    # 换手率
    turnover_rate: float | None = Field(
        sa_column=Column(
            Numeric(5, 2),
            nullable=True,
            server_default="0",
            comment="换手率",
        ),
        default=0,
    )

    # 上涨家数
    up_count: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            server_default="0",
            comment="上涨家数",
        ),
        default=0,
    )

    # 下跌家数
    down_count: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            server_default="0",
            comment="下跌家数",
        ),
        default=0,
    )

    # 领涨股票
    leading_stock: str | None = Field(
        sa_column=Column(
            String(50),
            nullable=True,
            server_default="",
            comment="领涨股票",
        ),
        default="",
    )

    # 领涨股票涨跌幅
    leading_stock_change: float | None = Field(
        sa_column=Column(
            Numeric(5, 2),
            nullable=True,
            server_default="0",
            comment="领涨股票涨跌幅",
        ),
        default=0,
    )

    # 概念描述
    description: str | None = Field(
        sa_column=Column(String(500), nullable=True, comment="概念描述"),
        default=None,
    )

    # ==================== 状态控制字段 ====================

    # 记录状态（0=禁用、1=启用）
    status: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
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

    # 多对多：概念 → 股票
    stocks: list["QuantStock"] = Relationship(
        back_populates="concepts", link_model=QuantStockConcept
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
