from enum import Enum

from pydantic import Field, field_validator

from config.base import BaseConfig


class CaptchaType(str, Enum):
    """验证码类型枚举"""

    IMAGE = "image"  # 图片验证码
    MATH = "math"  # 数学题验证码


class CaptchaCharType(str, Enum):
    """验证码字符类型枚举"""

    NUMERIC = "numeric"  # 纯数字
    ALPHA = "alpha"  # 纯字母
    ALPHANUMERIC = "alphanumeric"  # 字母数字混合
    MIXED = "mixed"  # 包含特殊字符


class CaptchaConfig(BaseConfig):
    """
    图片验证码配置类

    该配置类基于 Pydantic Settings，专门为图片验证码生成提供配置支持。
    所有环境变量都需要以 "CAPTCHA_" 为前缀。

    环境变量格式：
    - 简单配置：CAPTCHA_LENGTH=6
    - 嵌套配置：CAPTCHA_WIDTH=120

    使用示例：
        config = CaptchaConfig()
        captcha_length = config.length
        captcha_width = config.width

    环境变量完整示例：
        # 验证码基本配置
        CAPTCHA_LENGTH=6
        CAPTCHA_WIDTH=120
        CAPTCHA_HEIGHT=50
        CAPTCHA_FONT_SIZE=36
        CAPTCHA_CHAR_TYPE=alphanumeric

        # 验证码样式配置
        CAPTCHA_BACKGROUND_COLOR=255,255,255
        CAPTCHA_TEXT_COLOR=0,0,0
        CAPTCHA_NOISE_LINE_COUNT=4
        CAPTCHA_NOISE_POINT_COUNT=100

        # 验证码安全配置
        CAPTCHA_DISTORTION=true
        CAPTCHA_DISTORTION_LEVEL=0.5
        CAPTCHA_EXPIRE_SECONDS=300
        CAPTCHA_REDIS_KEY_PREFIX=captcha:
    """

    model_config = BaseConfig.model_config | {"env_prefix": "CAPTCHA_"}

    # ==================== 基本配置 ====================

    # 验证码长度
    length: int = Field(
        default=4,
        ge=4,
        le=8,
        description="验证码字符长度（4-8）",
    )

    # 验证码宽度（像素）
    width: int = Field(
        default=120,
        ge=80,
        le=300,
        description="验证码图片宽度（像素）",
    )

    # 验证码高度（像素）
    height: int = Field(
        default=50,
        ge=30,
        le=150,
        description="验证码图片高度（像素）",
    )

    # 字体大小（像素）
    font_size: int = Field(
        default=36,
        ge=20,
        le=60,
        description="验证码字体大小（像素）",
    )

    # 字符类型：numeric, alpha, alphanumeric, mixed
    char_type: CaptchaCharType = Field(
        default=CaptchaCharType.ALPHANUMERIC,
        description="验证码字符类型",
    )

    # 字体文件路径（留空使用默认字体）
    font_path: str = Field(
        default="",
        description="自定义字体文件路径（留空使用默认字体）",
    )

    # ==================== 样式配置 ====================

    # 背景颜色（RGB元组）
    background_color: tuple[int, int, int] = Field(
        default=(255, 255, 255),
        description="验证码背景颜色（RGB）",
    )

    # 文字颜色（RGB元组）
    text_color: tuple[int, int, int] = Field(
        default=(0, 0, 0),
        description="验证码文字颜色（RGB）",
    )

    # 干扰线数量
    noise_line_count: int = Field(
        default=4,
        ge=0,
        le=10,
        description="干扰线数量（0-10）",
    )

    # 干扰点数量
    noise_point_count: int = Field(
        default=100,
        ge=0,
        le=500,
        description="干扰点数量（0-500）",
    )

    # 干扰线颜色范围（RGB元组范围）
    noise_line_color_range: tuple[tuple[int, int], tuple[int, int], tuple[int, int]] = (
        Field(
            default=((100, 200), (100, 200), (100, 200)),
            description="干扰线颜色范围（RGB范围）",
        )
    )

    # 干扰点颜色范围（RGB元组范围）
    noise_point_color_range: tuple[
        tuple[int, int], tuple[int, int], tuple[int, int]
    ] = Field(
        default=((150, 255), (150, 255), (150, 255)),
        description="干扰点颜色范围（RGB范围）",
    )

    # ==================== 安全配置 ====================

    # 是否扭曲变形
    distortion: bool = Field(
        default=True,
        description="是否对验证码进行扭曲变形",
    )

    # 扭曲程度（0-1）
    distortion_level: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="验证码扭曲程度（0-1）",
    )

    # 验证码过期时间（秒）
    expire_seconds: int = Field(
        default=300,
        ge=60,
        le=1800,
        description="验证码过期时间（秒）",
    )

    # 验证码存储键前缀
    redis_key_prefix: str = Field(
        default="captcha:",
        description="Redis中验证码存储键前缀",
    )

    # 默认验证码类型
    default_type: CaptchaType = Field(
        default=CaptchaType.MATH,
        description="默认验证码类型",
    )

    # ==================== 验证器 ====================

    @field_validator("background_color", "text_color", mode="before")
    @classmethod
    def parse_color(cls, v):
        """解析颜色配置"""
        if isinstance(v, str):
            # 从字符串 "255,255,255" 解析为元组
            try:
                r, g, b = map(int, v.split(","))
                return (r, g, b)
            except (ValueError, AttributeError) as err:
                raise ValueError("颜色必须是 'r,g,b' 格式的字符串") from err
        return v

    @field_validator("noise_line_color_range", "noise_point_color_range", mode="before")
    @classmethod
    def parse_color_range(cls, v):
        """解析颜色范围配置"""
        if isinstance(v, str):
            # 从字符串 "100-200,100-200,100-200" 解析为元组
            try:
                ranges = v.split(",")
                result = []
                for color_range in ranges:
                    min_val, max_val = map(int, color_range.split("-"))
                    result.append((min_val, max_val))
                return tuple(result)
            except (ValueError, AttributeError) as err:
                raise ValueError(
                    "颜色范围必须是 'min-max,min-max,min-max' 格式的字符串"
                ) from err
        return v
