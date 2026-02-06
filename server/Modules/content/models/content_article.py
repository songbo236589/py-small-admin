"""
文章模型

对应数据库表：content_articles
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Index, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

# 导入链接表（非 TYPE_CHECKING 块）
from .content_article_tag import ContentArticleTag

if TYPE_CHECKING:
    from .content_category import ContentCategory
    from .content_publish_log import ContentPublishLog
    from .content_tag import ContentTag


class ContentArticle(BaseTableModel, table=True):
    """
    文章模型

    对应数据库表 content_articles，存储文章信息。
    """

    # 表注释
    __table_comment__ = "文章表，存储文章信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 文章标题
    title: str = Field(
        sa_column=Column(String(200), nullable=False, comment="文章标题"),
        default="",
    )

    # 文章内容（Markdown格式）
    content: str = Field(
        sa_column=Column(Text, nullable=False, comment="文章内容（Markdown格式）"),
        default="",
    )

    # 文章摘要
    summary: str | None = Field(
        sa_column=Column(String(500), nullable=True, comment="文章摘要"),
        default=None,
    )

    # 封面图片ID
    cover_image_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            comment="封面图片ID",
        ),
        default=None,
    )

    # 状态: 0=草稿, 1=已发布, 2=审核中, 3=发布失败
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="0",
            comment="状态: 0=草稿, 1=已发布, 2=审核中, 3=发布失败",
            index=True,
        ),
        default=0,
    )

    # 作者ID
    author_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            comment="作者ID",
        ),
        default=0,
    )

    # 分类ID
    category_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_categorys.id", ondelete="SET NULL"),
            nullable=True,
            comment="分类ID",
        ),
        default=None,
    )

    # 浏览次数
    view_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="浏览次数",
        ),
        default=0,
    )

    # 发布时间
    published_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="发布时间"),
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

    # 多对一：文章 → 分类
    category: Mapped[Optional["ContentCategory"]] = Relationship(
        back_populates="articles"
    )

    # 多对多：文章 ↔ 标签
    tags: Mapped[list["ContentTag"]] = Relationship(
        back_populates="articles",
        link_model=ContentArticleTag,
    )

    # 一对多：文章 → 发布日志
    publish_logs: Mapped[list["ContentPublishLog"]] = Relationship(
        back_populates="article"
    )

    # 索引
    __table_args__ = (
        Index("idx_author_status", "author_id", "status"),
        Index("idx_category_status", "category_id", "status"),
        Index("idx_status_created", "status", "created_at"),
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
