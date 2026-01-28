"""
股票-概念关联表模型

对应数据库表：quant_stock_concepts
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class QuantStockConcept(BaseTableModel, table=True):
    """
    股票-概念关联表模型

    对应数据库表 quant_stock_concepts，存储股票与概念的多对多关联关系。
    """

    # 表注释
    __table_comment__ = "股票-概念关联表，存储股票与概念的多对多关联关系"

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

    # 股票ID（关联 quant_stocks.id）
    stock_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey(
                "quant_stocks.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            index=True,
            comment="股票ID",
        ),
        default=None,
    )

    # 概念ID（关联 quant_concepts.id）
    concept_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("quant_concepts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="概念ID",
        ),
        default=None,
    )

    # ==================== 状态控制字段 ====================

    # 创建时间
    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
