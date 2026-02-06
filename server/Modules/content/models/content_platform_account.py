"""
第三方平台账号模型

对应数据库表：content_platform_accounts
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class ContentPlatformAccount(BaseTableModel, table=True):
    """
    第三方平台账号模型

    对应数据库表 content_platform_accounts，存储第三方平台账号信息。
    """

    # 表注释
    __table_comment__ = "第三方平台账号表，存储第三方平台账号信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 平台标识：zhihu
    platform: str = Field(
        sa_column=Column(
            String(20), nullable=False, comment="平台标识：zhihu", index=True
        ),
        default="",
    )

    # 账号名称
    account_name: str = Field(
        sa_column=Column(String(50), nullable=False, comment="账号名称"),
        default="",
    )

    # Cookie信息（JSON格式加密存储）
    cookies: str = Field(
        sa_column=Column(
            Text, nullable=False, comment="Cookie信息（JSON格式加密存储）"
        ),
        default="",
    )

    # 浏览器UA
    user_agent: str | None = Field(
        sa_column=Column(String(500), nullable=True, comment="浏览器UA"),
        default=None,
    )

    # 状态: 0=失效, 1=有效, 2=过期
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="状态: 0=失效, 1=有效, 2=过期",
            index=True,
        ),
        default=1,
    )

    # 最后验证时间
    last_verified: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="最后验证时间"),
        default=None,
    )

    # 创建人ID
    created_by: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            comment="创建人ID",
        ),
        default=0,
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
