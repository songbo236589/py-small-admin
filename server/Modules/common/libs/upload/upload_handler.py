"""
文件上传处理器 - 负责文件上传的核心逻辑
"""

import hashlib
import os
from pathlib import Path
from typing import Any

from PIL import Image

from config.upload import UploadConfig
from Modules.common.libs.upload.filename_generator import FilenameGenerator
from Modules.common.libs.upload.image_processor import ImageProcessor
from Modules.common.libs.upload.validator import UploadValidator


class UploadHandler:
    """文件上传处理器 - 负责文件上传的核心逻辑"""

    def __init__(
        self,
        upload_dir: str,
        upload_config: dict[str, Any] | UploadConfig | None = None,
    ):
        """
        初始化上传处理器

        Args:
            upload_dir: 上传根目录
            upload_config: 上传配置字典或UploadConfig对象
        """
        self.upload_dir = upload_dir
        self.upload_config = upload_config or {}

        # 初始化子处理器
        self.filename_generator = FilenameGenerator(upload_dir)
        # 如果是 UploadConfig 对象，传递 None（因为 UploadConfig 不包含验证相关字段）
        # 验证相关的配置从 sys_config 获取
        validator_config = (
            None if isinstance(self.upload_config, UploadConfig) else self.upload_config
        )
        self.validator = UploadValidator(validator_config)
        self.image_processor = ImageProcessor()

    def get_file_extension(self, filename: str) -> str:
        """
        获取文件扩展名

        Args:
            filename: 文件名

        Returns:
            str: 文件扩展名（包含点号）
        """
        return os.path.splitext(filename)[1].lower()

    def calculate_file_hash(self, file_content: bytes) -> str:
        """
        计算文件哈希值

        Args:
            file_content: 文件内容

        Returns:
            str: SHA256 哈希值
        """
        return hashlib.sha256(file_content).hexdigest()

    def save_file(self, file_content: bytes, file_path: str) -> int:
        """
        保存文件到指定路径

        Args:
            file_content: 文件内容
            file_path: 文件相对路径

        Returns:
            int: 文件大小
        """
        full_path = Path(self.upload_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file_content)

        return len(file_content)

    def save_image(
        self,
        file_content: bytes,
        file_path: str,
        compress_config: dict[str, Any] | None = None,
        watermark_config: dict[str, Any] | None = None,
    ) -> tuple[int, int, int]:
        """
        保存图片（可选压缩和水印）

        Args:
            file_content: 图片内容
            file_path: 文件相对路径
            compress_config: 压缩配置
            watermark_config: 水印配置

        Returns:
            tuple: (宽度, 高度, 文件大小)
        """
        import io

        # 从字节数据打开图片
        img = Image.open(io.BytesIO(file_content))

        # 确保输出目录存在
        full_path = Path(self.upload_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 处理图片（压缩 + 水印）
        return self.image_processor.process_image(
            img,
            str(full_path),
            compress_config,
            watermark_config,
        )

    def generate_filename(
        self,
        file_type: str,
        file_ext: str,
        original_filename: str = "",
    ) -> str:
        """
        生成唯一的文件名

        Args:
            file_type: 文件类型
            file_ext: 文件扩展名
            original_filename: 原始文件名

        Returns:
            str: 唯一的文件名
        """
        if isinstance(self.upload_config, dict):
            filename_rule = self.upload_config.get("filename_rule", "uuid")
            path_rule = self.upload_config.get("path_rule", "Y-m-d")
        else:
            filename_rule = self.upload_config.filename_rule.value
            path_rule = self.upload_config.path_rule.value

        return self.filename_generator.generate_unique_filename(
            file_type,
            file_ext,
            original_filename,
            filename_rule,
            path_rule,
        )

    def generate_file_path(self, file_type: str, filename: str) -> str:
        """
        生成文件存储路径

        Args:
            file_type: 文件类型
            filename: 文件名

        Returns:
            str: 文件存储路径（相对路径）
        """
        if isinstance(self.upload_config, dict):
            path_rule = self.upload_config.get("path_rule", "Y-m-d")
        else:
            path_rule = self.upload_config.path_rule.value
        return self.filename_generator.generate_file_path(
            file_type, filename, path_rule
        )

    def validate_file_size(self, file_type: str, file_size: int) -> dict[str, Any]:
        """
        验证文件大小

        Args:
            file_type: 文件类型
            file_size: 文件大小

        Returns:
            dict: 验证结果
        """
        return self.validator.validate_file_size(file_type, file_size)

    def validate_file_extension(self, file_type: str, file_ext: str) -> dict[str, Any]:
        """
        验证文件扩展名

        Args:
            file_type: 文件类型
            file_ext: 文件扩展名

        Returns:
            dict: 验证结果
        """
        return self.validator.validate_file_extension(file_type, file_ext)

    def generate_thumbnail(
        self,
        image_path: str,
        thumbnail_config: dict[str, Any],
    ) -> tuple[str, int]:
        """
        生成缩略图

        Args:
            image_path: 图片路径
            thumbnail_config: 缩略图配置

        Returns:
            tuple: (缩略图路径, 缩略图大小)
        """
        # 生成缩略图文件名
        filename = Path(image_path).name
        thumbnail_filename = self.image_processor.get_thumbnail_filename(
            filename, thumbnail_config.get("suffix", "_thumb")
        )

        # 生成缩略图路径
        file_type = image_path.split("/")[0]
        thumbnail_path = self.filename_generator.generate_file_path(
            file_type, thumbnail_filename
        )

        # 缩略图完整路径
        thumbnail_full_path = Path(self.upload_dir) / thumbnail_path
        thumbnail_full_path.parent.mkdir(parents=True, exist_ok=True)

        # 打开图片并生成缩略图
        img = Image.open(Path(self.upload_dir) / image_path)
        thumbnail_size = self.image_processor.generate_thumbnail(
            img,
            str(thumbnail_full_path),
            thumbnail_config,
        )

        return thumbnail_path, thumbnail_size

    def get_image_size(self, image_path: str) -> tuple[int, int]:
        """
        获取图片尺寸

        Args:
            image_path: 图片路径

        Returns:
            tuple: (宽度, 高度)
        """
        return self.image_processor.get_image_size(
            str(Path(self.upload_dir) / image_path)
        )

    def get_full_path(self, file_path: str) -> Path:
        """
        获取文件的完整路径

        Args:
            file_path: 相对路径

        Returns:
            Path: 完整路径
        """
        return self.filename_generator.get_full_path(file_path)
