"""
系统配置模型

对应数据库表：admin_sys_configs
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class AdminSysConfig(BaseTableModel, table=True):
    """
    系统配置模型

    对应数据库表 admin_sys_configs，存储系统配置信息。
    """

    # 表注释
    __table_comment__ = "系统配置表，存储系统配置信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 配置键（唯一）
    config_key: str | None = Field(
        sa_column=Column(
            String(100),
            nullable=False,
            unique=True,
            index=True,
            comment="配置键（唯一）",
        ),
        default="",
    )

    # 配置值
    config_value: str | None = Field(
        sa_column=Column(Text, nullable=False, comment="配置值"),
        default="",
    )

    # 值类型
    value_type: str | None = Field(
        sa_column=Column(
            String(20),
            nullable=False,
            comment="值类型(string/int/bool/json)",
            index=True,
        ),
        default="string",
    )

    # 配置说明
    description: str | None = Field(
        sa_column=Column(String(255), nullable=True, comment="配置说明"),
        default=None,
    )

    # 配置分组
    group_code: str | None = Field(
        sa_column=Column(String(50), nullable=True, comment="配置分组", index=True),
        default=None,
    )

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
