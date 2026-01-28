"""
图片验证码生成器

基于 CaptchaConfig 配置生成图片验证码。
"""

import io
import random

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from ..config import Config
from .utils import generate_random_text, get_character_set


class ImageGenerator:
    """图片验证码生成器"""

    def __init__(self):
        """初始化图片生成器"""
        self._config = Config.get("captcha")
        self._font = None
        self._load_font()

    def _load_font(self):
        """加载字体"""
        try:
            if self._config.font_path:
                # 使用自定义字体
                self._font = ImageFont.truetype(
                    self._config.font_path, self._config.font_size
                )
            else:
                # 使用默认字体
                try:
                    # 尝试使用系统字体
                    self._font = ImageFont.truetype("arial.ttf", self._config.font_size)
                except OSError:
                    # 如果系统字体不可用，使用默认字体
                    self._font = ImageFont.load_default()
                    logger.warning("使用默认字体，建议指定自定义字体路径")
        except Exception as e:
            logger.error(f"字体加载失败: {e}")
            self._font = ImageFont.load_default()

    def generate_image(self, text: str) -> bytes:
        """
        生成验证码图片

        Args:
            text: 验证码文本

        Returns:
            bytes: 图片数据
        """
        try:
            # 创建图片
            image = Image.new(
                "RGB",
                (self._config.width, self._config.height),
                self._config.background_color,
            )

            # 创建绘图对象
            draw = ImageDraw.Draw(image)

            # 添加干扰线
            if self._config.noise_line_count > 0:
                self._add_noise_lines(draw)

            # 添加干扰点
            if self._config.noise_point_count > 0:
                self._add_noise_points(draw)

            # 添加验证码文本
            self._add_text(draw, text)

            # 应用扭曲变形
            if self._config.distortion:
                image = self._apply_distortion(image)

            # 转换为字节流
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            return img_buffer.getvalue()

        except Exception as e:
            logger.error(f"生成验证码图片失败: {e}")
            raise

    def _add_noise_lines(self, draw):
        """添加干扰线"""
        for _ in range(self._config.noise_line_count):
            # 获取随机颜色
            color = self._get_random_color(self._config.noise_line_color_range)

            # 随机起点和终点
            x1 = random.randint(0, self._config.width)
            y1 = random.randint(0, self._config.height)
            x2 = random.randint(0, self._config.width)
            y2 = random.randint(0, self._config.height)

            # 绘制线条
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    def _add_noise_points(self, draw):
        """添加干扰点"""
        for _ in range(self._config.noise_point_count):
            # 获取随机颜色
            color = self._get_random_color(self._config.noise_point_color_range)

            # 随机位置
            x = random.randint(0, self._config.width)
            y = random.randint(0, self._config.height)

            # 绘制点
            draw.point([(x, y)], fill=color)

    def _add_text(self, draw, text: str):
        """添加验证码文本"""
        # 计算文本位置 - 使用 textbbox 替代已弃用的 textsize
        try:
            # 新版 Pillow 使用 textbbox
            bbox = draw.textbbox((0, 0), text, font=self._font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # 兼容旧版 Pillow
            text_width, text_height = draw.textsize(text, font=self._font)

        # 居中显示
        x = (self._config.width - text_width) // 2
        y = (self._config.height - text_height) // 2

        # 为每个字符添加随机偏移和旋转
        char_width = text_width // len(text) if len(text) > 0 else 0

        for i, char in enumerate(text):
            # 计算字符位置（添加随机偏移）
            char_x = x + i * char_width + random.randint(-5, 5)
            char_y = y + random.randint(-5, 5)

            # 绘制字符
            draw.text(
                (char_x, char_y), char, fill=self._config.text_color, font=self._font
            )

    def _apply_distortion(self, image: Image.Image) -> Image.Image:
        """应用扭曲变形"""
        import numpy as np

        try:
            # 将 PIL 图像转换为 numpy 数组
            img_array = np.array(image)

            # 获取图像尺寸
            height, width = img_array.shape[:2]

            # 创建扭曲映射
            distortion_level = self._config.distortion_level

            # 生成扭曲网格
            x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

            # 添加正弦波扭曲
            x_distortion = distortion_level * 10 * np.sin(2 * np.pi * y_coords / height)
            y_distortion = distortion_level * 10 * np.cos(2 * np.pi * x_coords / width)

            # 应用扭曲
            x_new = x_coords + x_distortion
            y_new = y_coords + y_distortion

            # 确保坐标在有效范围内
            x_new = np.clip(x_new, 0, width - 1).astype(np.float32)
            y_new = np.clip(y_new, 0, height - 1).astype(np.float32)

            # 使用 OpenCV 进行重映射（如果可用）
            try:
                import cv2

                distorted_array = cv2.remap(img_array, x_new, y_new, cv2.INTER_LINEAR)
            except ImportError:
                # 如果没有 OpenCV，使用简单的插值
                logger.warning("OpenCV 不可用，使用简单扭曲效果")
                distorted_array = self._simple_distortion(img_array, x_new, y_new)

            # 转换回 PIL 图像
            return Image.fromarray(distorted_array)

        except Exception as e:
            logger.warning(f"扭曲变形失败，返回原图: {e}")
            return image

    def _simple_distortion(self, img_array, x_new, y_new):
        """简单的扭曲实现（不依赖 OpenCV）"""
        import numpy as np

        height, width = img_array.shape[:2]
        distorted_array = np.zeros_like(img_array)

        for y in range(height):
            for x in range(width):
                # 获取扭曲后的坐标
                src_x = int(x_new[y, x])
                src_y = int(y_new[y, x])

                # 确保坐标在有效范围内
                if 0 <= src_x < width and 0 <= src_y < height:
                    distorted_array[y, x] = img_array[src_y, src_x]
                else:
                    distorted_array[y, x] = img_array[y, x]

        return distorted_array

    def _get_random_color(
        self, color_range: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
    ) -> tuple[int, int, int]:
        """获取随机颜色"""
        r_range, g_range, b_range = color_range
        r = random.randint(r_range[0], r_range[1])
        g = random.randint(g_range[0], g_range[1])
        b = random.randint(b_range[0], b_range[1])
        return (r, g, b)

    def generate_text(self) -> str:
        """生成验证码文本"""
        char_set = get_character_set(self._config.char_type)
        return generate_random_text(self._config.length, char_set)
