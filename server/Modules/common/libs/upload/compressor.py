"""
图片压缩处理器 - 负责图片压缩功能
"""

import os
from pathlib import Path
from typing import Any

from PIL import Image


class ImageCompressor:
    """图片压缩处理器"""

    def __init__(self):
        """初始化图片压缩处理器"""
        pass

    def compress_image(
        self,
        img: Image.Image,
        output_path: str,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
    ) -> tuple[int, int, int]:
        """
        压缩图片

        Args:
            img: PIL Image 对象
            output_path: 输出文件路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: 压缩质量（1-100）

        Returns:
            tuple: (压缩后的宽度, 压缩后的高度, 压缩后的文件大小)
        """
        # 获取原始尺寸
        original_width, original_height = img.size

        # 调整尺寸（如果超过最大宽高）
        if original_width > max_width or original_height > max_height:
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            # 使用高质量缩放算法 (LANCZOS = 6)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            new_width, new_height = original_width, original_height

        # 根据格式选择保存参数
        save_kwargs = self._get_save_kwargs(img, quality)

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存图片
        img.save(output_path, **save_kwargs)

        # 获取压缩后的文件大小
        compressed_size = os.path.getsize(output_path)

        return new_width, new_height, compressed_size

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

    def compress_from_bytes(
        self,
        image_bytes: bytes,
        output_path: str,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
    ) -> tuple[int, int, int]:
        """
        从字节数据压缩图片

        Args:
            image_bytes: 图片字节数据
            output_path: 输出文件路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: 压缩质量

        Returns:
            tuple: (压缩后的宽度, 压缩后的高度, 压缩后的文件大小)
        """
        import io

        # 从字节数据打开图片
        img = Image.open(io.BytesIO(image_bytes))

        # 压缩图片
        return self.compress_image(img, output_path, max_width, max_height, quality)
