"""
文章发布日志模型

对应数据库表：content_publish_logs
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Index, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

if TYPE_CHECKING:
    from .content_article import ContentArticle


class ContentPublishLog(BaseTableModel, table=True):
    """
    文章发布日志模型

    对应数据库表 content_publish_logs，存储文章发布日志信息。
    """

    # 表注释
    __table_comment__ = "文章发布日志表，存储文章发布日志信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 文章ID
    article_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_articles.id", ondelete="CASCADE"),
            nullable=False,
            comment="文章ID",
        ),
        default=0,
    )

    # 发布平台
    platform: str = Field(
        sa_column=Column(
            String(20), nullable=False, comment="发布平台"
        ),
        default="",
    )

    # 平台文章ID
    platform_article_id: str | None = Field(
        sa_column=Column(
            String(50), nullable=True, comment="平台文章ID"
        ),
        default=None,
    )

    # 平台文章链接
    platform_url: str | None = Field(
        sa_column=Column(
            String(200), nullable=True, comment="平台文章链接"
        ),
        default=None,
    )

    # 状态: 0=待发布, 1=发布中, 2=成功, 3=失败
    status: int = Field(
        sa_column=Column(
            SmallInteger,
            nullable=False,
            server_default="0",
            comment="状态: 0=待发布, 1=发布中, 2=成功, 3=失败",
            index=True,
        ),
        default=0,
    )

    # 错误信息
    error_message: str | None = Field(
        sa_column=Column(
            Text, nullable=True, comment="错误信息"
        ),
        default=None,
    )

    # 重试次数
    retry_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="重试次数",
        ),
        default=0,
    )

    # Celery任务ID
    task_id: str | None = Field(
        sa_column=Column(
            String(50), nullable=True, comment="Celery任务ID"
        ),
        default=None,
    )

    # 完成时间
    completed_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="完成时间"),
        default=None,
    )

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    # 多对一：发布日志 → 文章
    article: Mapped[Optional["ContentArticle"]] = Relationship(
        back_populates="publish_logs"
    )

    # 索引
    __table_args__ = (
        Index("idx_article_platform", "article_id", "platform"),
        Index("idx_platform_status", "platform", "status"),
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
