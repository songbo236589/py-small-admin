"""
内容模块配置

用于管理内容发布相关的配置，包括：
- Playwright 浏览器自动化配置
- 平台 Cookie 验证配置
- 文章发布配置
"""

from pydantic import Field

from config.base import BaseConfig


class ContentConfig(BaseConfig):
    """内容模块配置"""

    # 使用前缀 CONTENT_
    model_config = BaseConfig.model_config | {"env_prefix": "CONTENT_"}

    # ============================================================
    # Playwright 浏览器自动化配置
    # ============================================================

    # 是否无头模式
    # True: 不显示浏览器窗口（生产环境推荐）
    # False: 显示浏览器窗口（开发调试时推荐）
    playwright_headless: bool = Field(
        default=True,
        description="是否无头模式，开发时设为 False 可看到浏览器操作过程",
    )

    # 浏览器操作超时时间（毫秒）
    # 用于设置页面加载、元素等待等的超时时间
    playwright_timeout: int = Field(
        default=30000,
        description="浏览器操作超时时间（毫秒），默认 30 秒",
    )

    # 浏览器窗口大小
    playwright_width: int = Field(
        default=1920,
        description="浏览器窗口宽度（像素）",
    )

    playwright_height: int = Field(
        default=1080,
        description="浏览器窗口高度（像素）",
    )

    # ============================================================
    # 平台验证配置
    # ============================================================

    # 知乎验证 URL
    zhihu_verify_url: str = Field(
        default="https://www.zhihu.com",
        description="知乎验证 URL",
    )

    # 知乎登录检测选择器
    # 存在此元素说明未登录，不存在说明已登录
    zhihu_login_selector: str = Field(
        default=".AppHeader-login",
        description="知乎登录按钮选择器（存在则未登录）",
    )

    # 知乎登录后的元素选择器
    # 存在此元素说明已登录
    zhihu_logged_in_selector: str = Field(
        default=".AppHeader-notifications",
        description="知乎登录后的元素选择器（存在则已登录）",
    )

    # ============================================================
    # Cookie 验证配置
    # ============================================================

    # Cookie 自动验证间隔（秒）
    # 用于定时任务自动验证 Cookie 有效性
    cookie_verify_interval: int = Field(
        default=3600,
        description="Cookie 自动验证间隔（秒），默认 1 小时",
    )

    # Cookie 过期预警时间（天）
    # 在 Cookie 过期前多少天发送预警
    cookie_expire_warning_days: int = Field(
        default=7,
        description="Cookie 过期预警时间（天）",
    )

    # ============================================================
    # 反检测配置（降低平台封号风险）
    # ============================================================

    # 是否启用反检测功能
    human_behavior_enabled: bool = Field(
        default=True,
        description="是否启用人类行为模拟（随机延迟、滚动、鼠标移动等）",
    )

    # 随机延迟配置（秒）
    random_delay_min: float = Field(
        default=1.0,
        description="操作间最小随机延迟时间（秒）",
    )

    random_delay_max: float = Field(
        default=3.0,
        description="操作间最大随机延迟时间（秒）",
    )

    # 验证间隔限制（秒）
    verify_interval_min: int = Field(
        default=300,
        description="最小验证间隔（秒），默认 5 分钟，防止频繁验证",
    )

    # 页面停留时间配置（秒）
    stay_time_success_min: float = Field(
        default=5.0,
        description="验证成功后最小停留时间（秒）",
    )

    stay_time_success_max: float = Field(
        default=8.0,
        description="验证成功后最大停留时间（秒）",
    )

    stay_time_failed_min: float = Field(
        default=2.0,
        description="验证失败后最小停留时间（秒）",
    )

    stay_time_failed_max: float = Field(
        default=4.0,
        description="验证失败后最大停留时间（秒）",
    )

    # 人类行为模拟配置
    scroll_count_min: int = Field(
        default=1,
        description="最小滚动次数",
    )

    scroll_count_max: int = Field(
        default=3,
        description="最大滚动次数",
    )

    mouse_move_count_min: int = Field(
        default=2,
        description="最小鼠标移动次数",
    )

    mouse_move_count_max: int = Field(
        default=4,
        description="最大鼠标移动次数",
    )

    # ============================================================
    # Ollama AI 配置
    # ============================================================

    # Ollama 服务地址
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama 服务地址",
    )

    # Ollama 模型名称
    ollama_model: str = Field(
        default="qwen2.5:7b",
        description="Ollama 使用的模型名称",
    )

    # AI 生成超时时间（秒）
    ollama_timeout: int = Field(
        default=120,
        description="AI 生成超时时间（秒），默认 2 分钟",
    )

    # 是否启用 AI 功能
    ollama_enabled: bool = Field(
        default=True,
        description="是否启用 Ollama AI 功能",
    )
