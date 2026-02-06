"""
文章分类模型

对应数据库表：content_categories
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, SmallInteger, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

if TYPE_CHECKING:
    from .content_article import ContentArticle


class ContentCategory(BaseTableModel, table=True):
    """
    文章分类模型

    对应数据库表 content_categories，存储文章分类信息。
    """

    # 表注释
    __table_comment__ = "文章分类表，存储文章分类信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 分类名称
    name: str = Field(
        sa_column=Column(String(50), nullable=False, comment="分类名称"),
        default="",
    )

    # 分类别名
    slug: str = Field(
        sa_column=Column(
            String(50), nullable=False, unique=True, index=True, comment="分类别名"
        ),
        default="",
    )

    # 父分类ID
    parent_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="父分类ID",
            index=True,
        ),
        default=0,
    )

    # 排序
    sort: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="排序",
        ),
        default=0,
    )

    # 状态: 0=禁用, 1=启用
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="1",
            comment="状态: 0=禁用, 1=启用",
            index=True,
        ),
        default=1,
    )

    # 分类描述
    description: str | None = Field(
        sa_column=Column(String(200), nullable=True, comment="分类描述"),
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

    # 一对多：一个分类 → 多个文章
    articles: list["ContentArticle"] = Relationship(back_populates="category")

    class Config:
        """Pydantic配置"""

        from_attributes = True
