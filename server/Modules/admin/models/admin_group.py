"""
角色模型

对应数据库表：admin_groups
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TEXT, Column, DateTime, SmallInteger, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

if TYPE_CHECKING:
    from .admin_admin import AdminAdmin


class AdminGroup(BaseTableModel, table=True):
    """
    角色模型

    对应数据库表 admin_groups，存储系统角色信息。
    """

    # 表注释
    __table_comment__ = "角色表，存储系统角色信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 角色名称
    name: str | None = Field(
        sa_column=Column(
            String(100),
            nullable=False,
            unique=True,
            index=True,
            server_default="",
            comment="角色名称",
        ),
        default="",
    )

    # 角色描述
    content: str | None = Field(
        sa_column=Column(
            String(100), nullable=True, server_default="", comment="角色描述"
        ),
        default="",
    )

    # 状态: 0=禁用, 1=启用
    status: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="状态:0=禁用,1=启用",
            index=True,
        ),
        default=1,
    )

    # 菜单规则，多个用|隔开
    rules: str | None = Field(
        sa_column=Column(TEXT, nullable=True, comment="菜单规则多个用|隔开"),
        default="",
    )

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    # 一对多：一个组 → 多个管理员
    admins: list["AdminAdmin"] = Relationship(back_populates="group")

    class Config:
        """Pydantic配置"""

        from_attributes = True
