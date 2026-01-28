"""
管理员模型

对应数据库表：admin_admins
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

if TYPE_CHECKING:
    from .admin_group import AdminGroup
    from .admin_upload import AdminUpload


class AdminAdmin(BaseTableModel, table=True):
    """
    管理员模型

    对应数据库表 admin_admins，存储系统管理员信息。
    """

    # 表注释
    __table_comment__ = "管理员表，存储系统管理员信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 管理员姓名
    name: str | None = Field(
        sa_column=Column(
            String(100), nullable=False, server_default="", comment="管理员姓名"
        ),
        default="",
    )

    # 手机号
    phone: str | None = Field(
        sa_column=Column(
            String(100), nullable=True, server_default="", comment="手机号"
        ),
        default="",
    )

    # 账号
    username: str | None = Field(
        sa_column=Column(
            String(50), nullable=False, unique=True, index=True, comment="账号"
        ),
        default="",
    )

    # 密码
    password: str | None = Field(
        sa_column=Column(
            String(191), nullable=False, server_default="", comment="密码"
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

    # 所属组ID
    group_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("admin_groups.id", ondelete="SET NULL"),
            nullable=True,
            comment="所属组ID",
        ),
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
    # 多对一：管理员 → 组
    group: Mapped[Optional["AdminGroup"]] = Relationship(back_populates="admins")

    # 一对多：管理员 → 上传文件
    uploads: list["AdminUpload"] = Relationship(back_populates="admin")

    class Config:
        """Pydantic配置"""

        from_attributes = True
