"""
图片处理器 - 负责图片的压缩、缩略图生成和水印添加
"""

import os
from pathlib import Path
from typing import Any

from PIL import Image

from Modules.common.libs.upload.compressor import ImageCompressor
from Modules.common.libs.upload.thumbnail import ThumbnailGenerator
from Modules.common.libs.upload.watermark import WatermarkHandler


class ImageProcessor:
    """图片处理器 - 整合压缩、缩略图和水印功能"""

    def __init__(self):
        """初始化图片处理器"""
        self.compressor = ImageCompressor()
        self.thumbnail_generator = ThumbnailGenerator()
        self.watermark_handler = WatermarkHandler()

    def process_image(
        self,
        img: Image.Image,
        output_path: str,
        compress_config: dict[str, Any] | None = None,
        watermark_config: dict[str, Any] | None = None,
    ) -> tuple[int, int, int]:
        """
        处理图片（压缩 + 水印）

        Args:
            img: PIL Image 对象
            output_path: 输出文件路径
            compress_config: 压缩配置
                {
                    "enabled": bool,
                    "max_width": int,
                    "max_height": int,
                    "quality": int,
                }
            watermark_config: 水印配置

        Returns:
            tuple: (宽度, 高度, 文件大小)
        """
        # 应用压缩
        if compress_config and compress_config.get("enabled", False):
            width, height, file_size = self.compressor.compress_image(
                img,
                output_path,
                max_width=compress_config.get("max_width", 1920),
                max_height=compress_config.get("max_height", 1080),
                quality=compress_config.get("quality", 85),
            )
        else:
            # 保存原始图片
            img.save(output_path)
            width, height = img.size
            file_size = os.path.getsize(output_path)

        # 应用水印
        if watermark_config and watermark_config.get("enabled", False):
            try:
                # 重新打开图片
                img = Image.open(output_path)
                img = self.watermark_handler.add_watermark(img, watermark_config)

                # 重新保存带水印的图片
                file_ext_lower = Path(output_path).suffix.lower()
                if file_ext_lower in [".jpg", ".jpeg"]:
                    # JPEG 不支持透明度，需要转换为 RGB
                    if img.mode == "RGBA":
                        # 创建白色背景
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(
                            img, mask=img.split()[3]
                        )  # 使用 alpha 通道作为 mask
                        img = background
                    img.save(output_path, "JPEG", quality=85, optimize=True)
                elif file_ext_lower == ".png":
                    img.save(output_path, "PNG", optimize=True)
                elif file_ext_lower == ".webp":
                    img.save(output_path, "WEBP", quality=85, method=6)
                else:
                    img.save(output_path)

                # 更新文件大小
                file_size = os.path.getsize(output_path)
                print("水印添加成功")
            except Exception as e:
                print(f"添加水印失败: {str(e)}")
                # 水印添加失败，不影响主文件上传

        return width, height, file_size

    def generate_thumbnail(
        self,
        img: Image.Image,
        output_path: str,
        thumbnail_config: dict[str, Any],
    ) -> int:
        """
        生成缩略图

        Args:
            img: PIL Image 对象
            output_path: 输出文件路径
            thumbnail_config: 缩略图配置
                {
                    "width": int,
                    "height": int,
                    "quality": int,
                }

        Returns:
            int: 缩略图文件大小
        """
        return self.thumbnail_generator.generate_thumbnail(
            img,
            output_path,
            max_width=thumbnail_config.get("width", 300),
            max_height=thumbnail_config.get("height", 300),
            quality=thumbnail_config.get("quality", 80),
        )

    def get_thumbnail_filename(self, filename: str, suffix: str = "_thumb") -> str:
        """
        生成缩略图文件名

        Args:
            filename: 原始文件名
            suffix: 缩略图后缀

        Returns:
            str: 缩略图文件名
        """
        return self.thumbnail_generator.generate_thumbnail_filename(filename, suffix)

    def get_image_size(self, image_path: str) -> tuple[int, int]:
        """
        获取图片尺寸

        Args:
            image_path: 图片路径

        Returns:
            tuple: (宽度, 高度)
        """
        try:
            img = Image.open(image_path)
            return img.size
        except Exception:
            return (0, 0)

    def process_from_bytes(
        self,
        image_bytes: bytes,
        output_path: str,
        compress_config: dict[str, Any] | None = None,
        watermark_config: dict[str, Any] | None = None,
    ) -> tuple[int, int, int]:
        """
        从字节数据处理图片

        Args:
            image_bytes: 图片字节数据
            output_path: 输出文件路径
            compress_config: 压缩配置
            watermark_config: 水印配置

        Returns:
            tuple: (宽度, 高度, 文件大小)
        """
        import io

        # 从字节数据打开图片
        img = Image.open(io.BytesIO(image_bytes))

        # 处理图片
        return self.process_image(img, output_path, compress_config, watermark_config)
