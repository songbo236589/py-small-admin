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

    # 页面刷新配置（用于Cookie验证）
    enable_page_refresh: bool = Field(
        default=True,
        description="是否在验证时刷新页面（刷新可以让Cookie完全生效）",
    )

    page_refresh_delay_min: float = Field(
        default=2.0,
        description="刷新前最小延迟时间（秒）",
    )

    page_refresh_delay_max: float = Field(
        default=4.0,
        description="刷新前最大延迟时间（秒）",
    )

    page_refresh_after_delay_min: float = Field(
        default=1.0,
        description="刷新后最小延迟时间（秒）",
    )

    page_refresh_after_delay_max: float = Field(
        default=2.0,
        description="刷新后最大延迟时间（秒）",
    )

    # ============================================================
    # Ollama AI 配置
    # ============================================================

    # 是否启用 Ollama AI 功能
    ollama_enabled: bool = Field(
        default=True,
        description="是否启用 Ollama AI 功能",
    )

    # Ollama 服务地址
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama 服务地址",
    )

    # AI 生成超时时间（秒）
    ollama_timeout: int = Field(
        default=120,
        description="AI 生成超时时间（秒），默认 2 分钟",
    )

    # ============================================================
    # 智谱AI 配置
    # ============================================================

    # 是否启用智谱AI功能
    zhipu_enabled: bool = Field(
        default=False,
        description="是否启用智谱AI功能",
    )

    # 智谱AI API Key
    zhipu_api_key: str = Field(
        default="",
        description="智谱AI API Key",
    )

    # 智谱AI API 地址
    zhipu_base_url: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4",
        description="智谱AI API 地址",
    )

    # 智谱AI 生成超时时间（秒）
    zhipu_timeout: int = Field(
        default=120,
        description="智谱AI 生成超时时间（秒），默认 2 分钟",
    )

    # 智谱AI 模型列表（JSON 格式）
    zhipu_models: str = Field(
        default="",
        description="智谱AI模型列表（JSON格式）",
    )

    # ============================================================
    # 小红书配置
    # ============================================================

    # 小红书验证 URL（使用主站点进行登录验证，参考 go 实现）
    xiaohongshu_verify_url: str = Field(
        default="https://www.xiaohongshu.com/explore",
        description="小红书验证 URL（主站）",
    )

    # 小红书创作者平台验证 URL
    xiaohongshu_creator_verify_url: str = Field(
        default="https://creator.xiaohongshu.com/new/home",
        description="小红书创作者平台验证 URL",
    )

    # 是否启用创作者平台验证（二级验证）
    xiaohongshu_enable_creator_verify: bool = Field(
        default=True,
        description="是否在主站验证成功后，额外验证创作者平台访问权限",
    )

    # 小红书发布 URL
    xiaohongshu_publish_url: str = Field(
        default="https://creator.xiaohongshu.com/publish/publish?from=menu&target=article",
        description="小红书发布 URL",
    )

    # 小红书登录检测选择器
    # 存在此元素说明未登录，不存在说明已登录
    xiaohongshu_login_selector: str = Field(
        default=".login-container",
        description="小红书登录容器选择器（存在则未登录）",
    )

    # 小红书登录后的元素选择器
    # 存在此元素说明已登录
    xiaohongshu_logged_in_selector: str = Field(
        default=".main-container .user .link-wrapper .channel",
        description="小红书登录后的元素选择器（存在则已登录）",
    )

    # 小红书最大标题长度（字）
    xiaohongshu_max_title_length: int = Field(
        default=20,
        description="小红书最大标题长度（字），中文算2字节",
    )

    # 小红书建议正文长度（字）
    xiaohongshu_max_content_length: int = Field(
        default=1000,
        description="小红书建议正文长度（字）",
    )

    # 小红书最大标签数量
    xiaohongshu_max_tags: int = Field(
        default=10,
        description="小红书最大标签数量",
    )

    # ============================================================
    # 今日头条配置
    # ============================================================

    # 今日头条验证 URL
    toutiao_verify_url: str = Field(
        default="https://www.toutiao.com",
        description="今日头条验证 URL（主站）",
    )

    # 今日头条发布 URL
    toutiao_publish_url: str = Field(
        default="https://mp.toutiao.com/profile_v4/graphic/publish?from=toutiao_pc",
        description="今日头条发布 URL",
    )

    # 今日头条登录检测选择器
    # 存在此元素说明未登录
    toutiao_login_selector: str = Field(
        default=".user-card.login",
        description="今日头条登录容器选择器（存在则未登录）",
    )

    # 今日头条登录后的元素选择器
    # 存在此元素说明已登录
    toutiao_logged_in_selector: str = Field(
        default=".user-card.logged",
        description="今日头条登录后的元素选择器（存在则已登录）",
    )
