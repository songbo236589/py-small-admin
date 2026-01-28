"""
缩略图生成器 - 负责生成图片缩略图
"""

import os
from pathlib import Path
from typing import Any

from PIL import Image


class ThumbnailGenerator:
    """缩略图生成器"""

    def __init__(self):
        """初始化缩略图生成器"""
        pass

    def generate_thumbnail(
        self,
        img: Image.Image,
        output_path: str,
        max_width: int = 300,
        max_height: int = 300,
        quality: int = 80,
    ) -> int:
        """
        生成缩略图

        Args:
            img: PIL Image 对象
            output_path: 输出文件路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: 压缩质量（1-100）

        Returns:
            int: 缩略图文件大小
        """
        # 创建缩略图副本
        thumb_img = img.copy()

        # 使用 thumbnail 方法生成缩略图（保持宽高比）
        thumb_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # 根据格式选择保存参数
        save_kwargs = self._get_save_kwargs(thumb_img, quality)

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存缩略图
        thumb_img.save(output_path, **save_kwargs)

        # 获取缩略图文件大小
        thumbnail_size = os.path.getsize(output_path)

        return thumbnail_size

    def _get_save_kwargs(self, img: Image.Image, quality: int) -> dict[str, Any]:
        """
        根据图片格式获取保存参数

        Args:
            img: PIL Image 对象
            quality: 压缩质量

        Returns:
            dict: 保存参数字典
        """
        save_kwargs = {}

        # JPEG 格式优化
        if img.format == "JPEG":
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
            save_kwargs["progressive"] = True
        # PNG 格式优化
        elif img.format == "PNG":
            save_kwargs["optimize"] = True
        # WebP 格式优化
        elif img.format == "WEBP":
            save_kwargs["quality"] = quality
            save_kwargs["method"] = 6

        return save_kwargs

    def generate_thumbnail_filename(self, filename: str, suffix: str = "_thumb") -> str:
        """
        生成缩略图文件名

        Args:
            filename: 原始文件名
            suffix: 缩略图后缀

        Returns:
            str: 缩略图文件名
        """
        # 分离文件名和扩展名
        name_without_ext = os.path.splitext(filename)[0]
        file_ext = os.path.splitext(filename)[1]
        # 添加后缀
        return f"{name_without_ext}{suffix}{file_ext}"

    def generate_from_file(
        self,
        input_path: str,
        output_path: str,
        max_width: int = 300,
        max_height: int = 300,
        quality: int = 80,
    ) -> int:
        """
        从文件生成缩略图

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: 压缩质量

        Returns:
            int: 缩略图文件大小
        """
        # 打开图片
        img = Image.open(input_path)

        # 生成缩略图
        return self.generate_thumbnail(img, output_path, max_width, max_height, quality)

    def generate_from_bytes(
        self,
        image_bytes: bytes,
        output_path: str,
        max_width: int = 300,
        max_height: int = 300,
        quality: int = 80,
    ) -> int:
        """
        从字节数据生成缩略图

        Args:
            image_bytes: 图片字节数据
            output_path: 输出文件路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: 压缩质量

        Returns:
            int: 缩略图文件大小
        """
        import io

        # 从字节数据打开图片
        img = Image.open(io.BytesIO(image_bytes))

        # 生成缩略图
        return self.generate_thumbnail(img, output_path, max_width, max_height, quality)
