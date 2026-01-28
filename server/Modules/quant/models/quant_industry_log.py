"""
行业历史记录表模型

对应数据库表：quant_industry_logs
"""

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class QuantIndustryLog(BaseTableModel, table=True):
    """
    行业历史记录表模型

    对应数据库表 quant_industry_logs，存储行业数据的变更历史记录。
    用于数据追踪、趋势分析和审计日志。
    """

    # 表注释
    __table_comment__ = "行业历史记录表，存储行业数据的变更历史记录"

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

    # 关联的行业ID（外键）
    industry_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("quant_industrys.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            comment="关联的行业ID",
        ),
        default=None,
    )

    # 记录日期（年月日，用于按日期查询历史记录）
    record_date: date | None = Field(
        sa_column=Column(
            Date(),
            nullable=False,
            index=True,
            comment="记录日期（年月日）",
        ),
        default=None,
    )

    # ==================== 行业基础信息快照 ====================

    # 行业名称
    name: str | None = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            index=True,
            comment="行业名称（如：电子化学品、银行、房地产）",
        ),
        default="",
    )

    # 行业代码
    code: str | None = Field(
        sa_column=Column(
            String(20),
            nullable=False,
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

    # ==================== 行情数据快照 ====================

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

    # ==================== 审计字段 ====================

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
