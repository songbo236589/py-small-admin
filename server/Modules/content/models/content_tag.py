"""
文章标签模型

对应数据库表：content_tags
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, SmallInteger, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

# 导入链接表（非 TYPE_CHECKING 块）
from .content_article_tag import ContentArticleTag

if TYPE_CHECKING:
    from .content_article import ContentArticle


class ContentTag(BaseTableModel, table=True):
    """
    文章标签模型

    对应数据库表 content_tags，存储文章标签信息。
    """

    # 表注释
    __table_comment__ = "文章标签表，存储文章标签信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 标签名称
    name: str = Field(
        sa_column=Column(
            String(30), nullable=False, unique=True, index=True, comment="标签名称"
        ),
        default="",
    )

    # 标签别名
    slug: str = Field(
        sa_column=Column(
            String(30), nullable=False, unique=True, index=True, comment="标签别名"
        ),
        default="",
    )

    # 标签颜色
    color: str | None = Field(
        sa_column=Column(String(7), nullable=True, comment="标签颜色"),
        default=None,
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

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间", index=True),
        default=None,
    )

    # 多对多：标签 ↔ 文章
    articles: Mapped[list["ContentArticle"]] = Relationship(
        back_populates="tags",
        link_model=ContentArticleTag,
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
