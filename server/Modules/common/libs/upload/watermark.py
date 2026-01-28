"""
水印处理器 - 负责添加文字和图片水印
"""

import os
from typing import Any

from PIL import Image, ImageDraw, ImageFont


class WatermarkHandler:
    """水印处理器"""

    def __init__(self):
        """初始化水印处理器"""
        pass

    def add_watermark(
        self, img: Image.Image, watermark_config: dict[str, Any]
    ) -> Image.Image:
        """
        添加水印

        Args:
            img: PIL Image 对象
            watermark_config: 水印配置字典

        Returns:
            Image.Image: 添加水印后的图片
        """
        watermark_type = watermark_config.get("type", "text")

        if watermark_type == "text":
            return self.add_text_watermark(img, watermark_config)
        elif watermark_type == "image":
            return self.add_image_watermark(img, watermark_config)
        else:
            # 未知类型，返回原图
            return img

    def add_text_watermark(
        self, img: Image.Image, watermark_config: dict[str, Any]
    ) -> Image.Image:
        """
        添加文字水印

        Args:
            img: PIL Image 对象
            watermark_config: 水印配置字典

        Returns:
            Image.Image: 添加水印后的图片
        """
        text = watermark_config.get("text", "")
        if not text:
            return img

        # 获取配置参数
        font_size = watermark_config.get("font_size", 20)
        font_color = watermark_config.get("font_color", "#FFFFFF")
        opacity = watermark_config.get("opacity", 0.5)
        position = watermark_config.get("position", "bottom-right")
        margin = watermark_config.get("margin", 10)
        font_path = watermark_config.get("font_path", "")

        # 创建图片副本
        img = img.copy()

        # 如果图片不是 RGBA 模式，转换为 RGBA
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # 创建透明图层
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # 加载字体
        font = self._load_font(font_path, font_size)

        # 解析颜色
        color = self._parse_color(font_color, opacity)

        # 计算文字位置
        text_width, text_height = self._get_text_size(draw, text, font, font_size)

        x, y = self._calculate_watermark_position(
            img.size, (text_width, text_height), position, margin, font_size
        )

        # 绘制文字
        draw.text((x, y), text, font=font, fill=color)

        # 合成图层
        watermarked = Image.alpha_composite(img, txt_layer)

        # 转换回原始模式
        if watermarked.mode != img.mode:
            watermarked = watermarked.convert(img.mode)

        return watermarked

    def add_image_watermark(
        self, img: Image.Image, watermark_config: dict[str, Any]
    ) -> Image.Image:
        """
        添加图片水印

        Args:
            img: PIL Image 对象
            watermark_config: 水印配置字典

        Returns:
            Image.Image: 添加水印后的图片
        """
        image_path = watermark_config.get("image_path", "")
        if not image_path or not os.path.exists(image_path):
            print(f"水印图片不存在: {image_path}")
            return img

        try:
            # 打开水印图片
            watermark_img = Image.open(image_path)

            # 获取配置参数
            opacity = watermark_config.get("opacity", 0.5)
            position = watermark_config.get("position", "bottom-right")
            margin = watermark_config.get("margin", 10)
            scale = watermark_config.get("image_scale", 0.2)

            # 创建图片副本
            img = img.copy()

            # 如果图片不是 RGBA 模式，转换为 RGBA
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # 如果水印图片不是 RGBA 模式，转换为 RGBA
            if watermark_img.mode != "RGBA":
                watermark_img = watermark_img.convert("RGBA")

            # 缩放水印图片
            img_width, img_height = img.size
            watermark_width = int(img_width * scale)
            watermark_height = int(
                watermark_img.height * (watermark_width / watermark_img.width)
            )
            watermark_img = watermark_img.resize(
                (watermark_width, watermark_height), Image.Resampling.LANCZOS
            )

            # 调整水印透明度
            watermark_data = watermark_img.getdata()
            new_data = []
            for item in watermark_data:
                # 修改 alpha 通道
                if isinstance(item, (tuple, list)) and len(item) == 4:
                    new_data.append((item[0], item[1], item[2], int(item[3] * opacity)))
                else:
                    new_data.append(item)
            watermark_img.putdata(new_data)

            # 计算水印位置
            x, y = self._calculate_watermark_position(
                img.size, watermark_img.size, position, margin
            )

            # 创建透明图层
            watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            watermark_layer.paste(watermark_img, (x, y), watermark_img)

            # 合成图层
            watermarked = Image.alpha_composite(img, watermark_layer)

            # 转换回原始模式
            if watermarked.mode != img.mode:
                watermarked = watermarked.convert(img.mode)

            return watermarked
        except Exception as e:
            print(f"添加图片水印失败: {str(e)}")
            return img

    def _load_font(self, font_path: str, font_size: int):
        """
        加载字体

        Args:
            font_path: 字体文件路径
            font_size: 字体大小

        Returns:
            字体对象
        """
        try:
            if font_path and os.path.exists(font_path):
                return ImageFont.truetype(font_path, font_size)
            else:
                # 使用默认字体
                return ImageFont.load_default()
        except Exception:
            # 如果字体加载失败，使用默认字体
            return ImageFont.load_default()

    def _parse_color(
        self, font_color: str, opacity: float
    ) -> tuple[int, int, int, int]:
        """
        解析颜色字符串

        Args:
            font_color: 颜色字符串（如 #FFFFFF）
            opacity: 透明度（0-1）

        Returns:
            tuple: RGBA 颜色值
        """
        try:
            # 移除 # 号并转换为 RGB
            color_hex = font_color.lstrip("#")
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            return (r, g, b, int(255 * opacity))
        except Exception:
            # 颜色解析失败，使用白色
            return (255, 255, 255, int(255 * opacity))

    def _get_text_size(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font,
        font_size: int,
    ) -> tuple[int, int]:
        """
        获取文字尺寸

        Args:
            draw: ImageDraw 对象
            text: 文字内容
            font: 字体对象
            font_size: 字体大小

        Returns:
            tuple: (文字宽度, 文字高度)
        """
        try:
            # 获取文字边界框
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = int(bbox[2] - bbox[0])
            # 使用边界框高度并增加 20% 的补偿，确保包含字体的下行部分
            text_height = int((bbox[3] - bbox[1]) * 1.2)
        except Exception:
            # 如果无法获取边界框，使用估算值
            text_width = int(len(text) * font_size)
            text_height = int(font_size * 1.2)

        return text_width, text_height

    def _calculate_watermark_position(
        self,
        img_size: tuple[int, int],
        watermark_size: tuple[int, int],
        position: str,
        margin: int,
        font_size: int = 0,
    ) -> tuple[int, int]:
        """
        计算水印位置

        Args:
            img_size: 原始图片尺寸 (width, height)
            watermark_size: 水印尺寸 (width, height)
            position: 水印位置 (top-left, top-right, bottom-left, bottom-right, center)
            margin: 边距
            font_size: 字体大小（用于计算额外的下边距补偿）

        Returns:
            tuple[int, int]: 水印坐标 (x, y)
        """
        img_width, img_height = img_size
        watermark_width, watermark_height = watermark_size

        # 计算额外的下边距补偿（用于文字水印）
        # 某些字体的实际渲染高度可能比计算的高度要大
        extra_bottom_margin = int(font_size * 0.2) if font_size > 0 else 0

        # 支持的位置映射
        position_map = {
            "top-left": (margin, margin),
            "top-right": (img_width - watermark_width - margin, margin),
            "bottom-left": (
                margin,
                img_height - watermark_height - margin - extra_bottom_margin,
            ),
            "bottom-right": (
                img_width - watermark_width - margin,
                img_height - watermark_height - margin - extra_bottom_margin,
            ),
            "center": (
                (img_width - watermark_width) // 2,
                (img_height - watermark_height) // 2,
            ),
        }

        # 获取位置坐标，如果位置不支持，默认使用右下角
        x, y = position_map.get(position, position_map["bottom-right"])

        # 确保坐标不为负数
        x = max(0, x)
        y = max(0, y)

        return (x, y)

    def get_default_watermark_config(self) -> dict[str, Any]:
        """
        获取默认水印配置

        Returns:
            dict: 默认水印配置
        """
        return {
            "enabled": False,
            "type": "text",
            "text": "Py Small Admin",
            "position": "bottom-right",
            "opacity": 0.5,
            "font_size": 20,
            "font_color": "#FFFFFF",
            "font_path": "",
            "image_path": "",
            "image_scale": 0.2,
            "margin": 10,
        }
