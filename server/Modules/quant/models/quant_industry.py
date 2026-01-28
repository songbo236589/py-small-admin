"""
行业表模型

对应数据库表：quant_industries
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

if TYPE_CHECKING:
    from .quant_stock import QuantStock


class QuantIndustry(BaseTableModel, table=True):
    """
    行业表模型

    对应数据库表 quant_industrys，存储股票行业分类信息。
    """

    # 表注释
    __table_comment__ = "行业表，存储股票行业分类信息"

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

    # 行业名称（如：电子化学品、银行、房地产）
    name: str | None = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            unique=True,
            index=True,
            comment="行业名称（如：电子化学品、银行、房地产）",
        ),
        default="",
    )

    # 行业代码（如：BK0433、BK0001）
    code: str | None = Field(
        sa_column=Column(
            String(20),
            nullable=False,
            unique=True,
            index=True,
            comment="行业代码（如：BK0433、BK0001）",
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

    # ==================== 行情数据字段 ====================

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

    # ==================== 扩展字段 ====================

    # 行业描述
    description: str | None = Field(
        sa_column=Column(String(500), nullable=True, comment="行业描述"),
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

    # 一对多：行业 → 股票
    stocks: list["QuantStock"] = Relationship(back_populates="industry")

    class Config:
        """Pydantic配置"""

        from_attributes = True
