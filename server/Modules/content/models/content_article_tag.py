"""
文章标签关联模型

对应数据库表：content_article_tags
"""

from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import Field

from Modules.common.models.base_model import BaseTableModel


class ContentArticleTag(BaseTableModel, table=True):
    """
    文章标签关联模型

    对应数据库表 content_article_tags，存储文章与标签的多对多关系。
    """

    # 表注释
    __table_comment__ = "文章标签关联表，存储文章与标签的多对多关系"

    # 文章ID
    article_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_articles.id", ondelete="CASCADE"),
            primary_key=True,
            comment="文章ID",
        ),
        default=0,
    )

    # 标签ID
    tag_id: int = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("content_tags.id", ondelete="CASCADE"),
            primary_key=True,
            comment="标签ID",
        ),
        default=0,
    )

    # 索引
    __table_args__ = (Index("idx_article_tag", "article_id", "tag_id"),)

    class Config:
        """Pydantic配置"""

        from_attributes = True
