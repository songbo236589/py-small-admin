"""
菜单模型

对应数据库表：admin_rules
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, SmallInteger, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class AdminRule(BaseTableModel, table=True):
    """
    菜单模型

    对应数据库表 admin_rules，存储系统菜单信息。
    """

    # 表注释
    __table_comment__ = "菜单表，存储系统菜单信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 路由路径
    path: str | None = Field(
        sa_column=Column(
            String(100), nullable=True, server_default="", comment="路由路径"
        ),
        default="",
    )

    # 组件路径
    component: str | None = Field(
        sa_column=Column(
            String(100), nullable=True, server_default="", comment="组件路径"
        ),
        default="",
    )

    # 重定向路径
    redirect: str | None = Field(
        sa_column=Column(
            String(100), nullable=True, server_default="", comment="重定向路径"
        ),
        default="",
    )

    # 菜单名称
    name: str | None = Field(
        sa_column=Column(
            String(100), nullable=False, server_default="", comment="菜单名称"
        ),
        default="",
    )

    # 菜单类型: 1=模块, 2=目录, 3=菜单
    type: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="菜单类型:1=模块,2=目录,3=菜单",
        ),
        default=1,
    )

    # 侧边栏显示状态: 0=隐藏, 1=显示
    status: int | None = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="侧边栏显示状态:0=隐藏,1=显示",
            index=True,
        ),
        default=1,
    )

    # 级别
    level: int | None = Field(
        sa_column=Column(
            SmallInteger, nullable=False, server_default="1", comment="级别"
        ),
        default=1,
    )

    # 图标
    icon: str | None = Field(
        sa_column=Column(String(50), nullable=True, server_default="", comment="图标"),
        default="",
    )

    # 父级ID
    pid: int | None = Field(
        sa_column=Column(
            Integer, nullable=False, server_default="0", comment="父级ID", index=True
        ),
        default=0,
    )

    # 排序
    sort: int | None = Field(
        sa_column=Column(Integer, nullable=False, server_default="1", comment="排序"),
        default=1,
    )
    target: str | None = Field(
        sa_column=Column(
            String(10),
            nullable=False,
            server_default="",
            comment="链接打开方式：_self/_blank",
        ),
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

    class Config:
        """Pydantic配置"""

        from_attributes = True
