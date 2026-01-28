"""
文件上传模型

对应数据库表：admin_uploads
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from Modules.common.models.base_model import BaseTableModel

if TYPE_CHECKING:
    from .admin_admin import AdminAdmin


class AdminUpload(BaseTableModel, table=True):
    """
    文件上传模型

    对应数据库表 admin_uploads，存储系统文件上传信息。
    """

    # 表注释
    __table_comment__ = "文件上传表，存储系统文件上传信息"

    id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            primary_key=True,
            autoincrement=True,
            comment="主键 ID",
        ),
        default=None,
    )

    # ==================== 核心字段 ====================

    # 原始文件名
    original_name: str | None = Field(
        sa_column=Column(
            String(255), nullable=False, server_default="", comment="原始文件名"
        ),
        default="",
    )

    # 存储文件名（根据命名规则生成）
    filename: str | None = Field(
        sa_column=Column(
            String(255), nullable=False, server_default="", comment="存储文件名"
        ),
        default="",
    )

    # 文件存储路径（相对路径）
    file_path: str | None = Field(
        sa_column=Column(
            String(500), nullable=False, server_default="", comment="文件存储路径"
        ),
        default="",
    )

    # 文件大小（字节）
    file_size: int | None = Field(
        sa_column=Column(
            BIGINT(unsigned=True),
            nullable=False,
            server_default="0",
            comment="文件大小（字节）",
        ),
        default=0,
    )

    # MIME类型
    mime_type: str | None = Field(
        sa_column=Column(
            String(100), nullable=False, server_default="", comment="MIME类型"
        ),
        default="",
    )

    # 文件扩展名
    file_ext: str | None = Field(
        sa_column=Column(
            String(20), nullable=False, server_default="", comment="文件扩展名"
        ),
        default="",
    )

    # ==================== 安全与校验字段 ====================

    # 文件哈希值（SHA256，用于去重和校验）
    file_hash: str | None = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            server_default="",
            comment="文件哈希值（SHA256）",
            index=True,
        ),
        default="",
    )

    # 存储类型(local/aliyun_oss/tencent_oss/qiniu_oss)
    storage_type: str | None = Field(
        sa_column=Column(
            String(20),
            nullable=False,
            server_default="local",
            comment="存储类型(local/aliyun_oss/tencent_oss/qiniu_oss)",
            index=True,
        ),
        default="local",
    )

    # ==================== 分类与状态字段 ====================

    # 文件分类（image/document/video/audio/other）
    file_type: str | None = Field(
        sa_column=Column(
            String(50),
            nullable=False,
            server_default="other",
            comment="文件分类:image/document/video/audio/other",
        ),
        default="other",
    )

    # ==================== 业务关联字段 ====================

    # 上传者ID
    admin_id: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            ForeignKey("admin_admins.id", ondelete="SET NULL"),
            nullable=True,
            comment="上传者ID",
        ),
        default=None,
    )

    # ==================== 扩展信息字段 ====================

    # 图片宽度（仅图片类型）
    width: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            server_default="0",
            comment="图片宽度",
        ),
        default=0,
    )

    # 图片高度（仅图片类型）
    height: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            server_default="0",
            comment="图片高度",
        ),
        default=0,
    )

    # 时长（秒，仅视频/音频类型）
    duration: int | None = Field(
        sa_column=Column(
            INTEGER(unsigned=True),
            nullable=True,
            server_default="0",
            comment="时长（秒）",
        ),
        default=0,
    )

    # 缩略图文件名
    thumbnail_filename: str | None = Field(
        sa_column=Column(
            String(255), nullable=True, server_default="", comment="缩略图文件名"
        ),
        default="",
    )

    # 缩略图存储路径（相对路径）
    thumbnail_path: str | None = Field(
        sa_column=Column(
            String(500), nullable=True, server_default="", comment="缩略图存储路径"
        ),
        default="",
    )

    # 扩展信息（JSON格式）
    extra_info: str | None = Field(
        sa_column=Column(
            String(1000), nullable=True, server_default="", comment="扩展信息（JSON）"
        ),
        default="",
    )

    # ==================== 时间字段 ====================

    created_at: datetime | None = Field(
        sa_column=Column(DateTime(), nullable=False, comment="创建时间", index=True),
        default=None,
    )

    # ==================== 关系定义 ====================

    # 多对一：上传文件 → 管理员
    admin: Mapped[Optional["AdminAdmin"]] = Relationship(back_populates="uploads")

    class Config:
        """Pydantic配置"""

        from_attributes = True
