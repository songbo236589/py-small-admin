"""
话题/问题模型

对应数据库表：content_topics
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class ContentTopic(BaseTableModel, table=True):
    """
    话题/问题模型

    对应数据库表 content_topics，存储从第三方平台抓取的话题/问题信息。
    """

    # 表注释
    __table_comment__ = "话题/问题表，存储从第三方平台抓取的话题/问题信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # 平台标识
    platform: str = Field(
        sa_column=Column(
            String(20), nullable=False, index=True, comment="平台标识：zhihu"
        ),
        default="",
    )

    # 平台问题ID
    platform_question_id: str = Field(
        sa_column=Column(String(50), nullable=False, comment="平台问题ID"),
        default="",
    )

    # 问题标题
    title: str = Field(
        sa_column=Column(String(500), nullable=False, comment="问题标题"),
        default="",
    )

    # 问题描述
    description: str | None = Field(
        sa_column=Column(Text, nullable=True, comment="问题描述"),
        default=None,
    )

    # 问题链接
    url: str | None = Field(
        sa_column=Column(String(500), nullable=True, comment="问题链接"),
        default=None,
    )

    # 浏览量
    view_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="浏览量",
            index=True,
        ),
        default=0,
    )

    # 回答数
    answer_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="回答数",
            index=True,
        ),
        default=0,
    )

    # 关注者数
    follower_count: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=False,
            server_default="0",
            comment="关注者数",
        ),
        default=0,
    )

    # 分类/话题标签
    category: str | None = Field(
        sa_column=Column(String(100), nullable=True, comment="分类/话题标签", index=True),
        default=None,
    )

    # 热度分数
    hot_score: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            comment="热度分数",
            index=True,
        ),
        default=None,
    )

    # 提问者昵称
    author_name: str | None = Field(
        sa_column=Column(String(100), nullable=True, comment="提问者昵称"),
        default=None,
    )

    # 提问者主页
    author_url: str | None = Field(
        sa_column=Column(String(200), nullable=True, comment="提问者主页"),
        default=None,
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

    # 抓取时间
    fetched_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="抓取时间", index=True),
        default=None,
    )

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间"),
        default=None,
    )

    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=True, comment="更新时间"),
        default=None,
    )

    class Config:
        """Pydantic配置"""

        from_attributes = True
