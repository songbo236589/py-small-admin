"""
平台处理器基类

融合了验证器和发布器的功能，提供统一的平台操作接口。
"""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from playwright.async_api import Browser, Page

# 默认 User-Agent（当数据库中没有存储时使用）
# 这是常见的 Chrome 浏览器 User-Agent
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class PublishResult:
    """发布结果类"""

    def __init__(
        self,
        success: bool,
        message: str,
        platform_article_id: str | None = None,
        platform_url: str | None = None,
    ):
        """初始化发布结果

        Args:
            success: 是否发布成功
            message: 结果消息
            platform_article_id: 平台文章ID
            platform_url: 平台文章链接
        """
        self.success = success
        self.message = message
        self.platform_article_id = platform_article_id
        self.platform_url = platform_url


class BasePlatformHandler(ABC):
    """平台处理器基类（融合验证器和发布器）"""

    def __init__(
        self,
        cookies: list[dict],
        user_agent: str | None = None,
        article_data: dict[str, Any] | None = None,
    ):
        """初始化处理器

        Args:
            cookies: Cookie 列表
            user_agent: 浏览器 User-Agent
            article_data: 文章数据（发布时使用，验证时为 None）
        """
        self.cookies = cookies
        self.user_agent = user_agent
        self.article_data = article_data
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.playwright = None

        # 记录初始化信息
        logger.debug(
            f"[{self.platform_name}] 处理器初始化 - "
            f"Cookie数量: {len(cookies)}, "
            f"UA: {(user_agent or DEFAULT_USER_AGENT)[:50]}..."
        )

    # ==================== 通用属性 ====================

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称"""
        pass

    @property
    @abstractmethod
    def platform_domain(self) -> str:
        """平台域名"""
        pass

    # ==================== 验证相关 ====================

    @abstractmethod
    async def get_verify_url(self) -> str:
        """获取验证 URL"""
        pass

    # ==================== 发布相关 ====================

    @abstractmethod
    async def get_publish_url(self) -> str:
        """获取发布页面 URL"""
        pass

    @abstractmethod
    async def fill_article_content(self) -> None:
        """填写文章内容

        子类需要实现具体的填写逻辑
        """
        pass

    @abstractmethod
    async def submit_article(self) -> PublishResult:
        """提交文章

        Returns:
            发布结果，包含平台文章ID和链接
        """
        pass

    # ==================== 通用方法 ====================

    @abstractmethod
    async def check_login_status(self) -> bool:
        """检查是否已登录

        Returns:
            True 表示已登录，False 表示未登录
        """
        pass

    # ==================== 核心执行方法 ====================

    async def verify(self) -> dict:
        """验证 Cookie 有效性

        Returns:
            验证结果字典，包含:
            - success: 是否验证成功
            - message: 结果消息
        """
        logger.info(f"[{self.platform_name}] ===== 开始 Cookie 验证 =====")
        logger.debug(
            f"[{self.platform_name}] Cookie 数量: {len(self.cookies)}, User-Agent: {(self.user_agent or DEFAULT_USER_AGENT)[:50]}..."
        )

        try:
            from playwright.async_api import async_playwright

            from Modules.common.libs.config.registry import ConfigRegistry

            # 获取配置
            config = ConfigRegistry.get("content")
            if config is None:
                logger.error(
                    f"[{self.platform_name}] ConfigRegistry.get('content') 返回 None"
                )
                return {
                    "success": False,
                    "message": "配置未加载，请重启后端服务",
                }

            logger.debug(
                f"[{self.platform_name}] 配置 - headless: {config.playwright_headless}, timeout: {config.playwright_timeout}ms"
            )

            # 启动浏览器
            logger.info(f"[{self.platform_name}] 正在启动 Playwright...")
            self.playwright = await async_playwright().start()

            logger.info(
                f"[{self.platform_name}] 正在启动 Chromium 浏览器 (headless={config.playwright_headless})..."
            )
            self.browser = await self.playwright.chromium.launch(
                headless=config.playwright_headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            logger.info(f"[{self.platform_name}] ✓ 浏览器启动成功")

            # 创建上下文和页面
            logger.debug(f"[{self.platform_name}] 创建浏览器上下文...")
            context = await self.browser.new_context(
                user_agent=self.user_agent or DEFAULT_USER_AGENT,
                viewport={
                    "width": config.playwright_width,
                    "height": config.playwright_height,
                },
            )
            self.page = await context.new_page()
            logger.debug(
                f"[{self.platform_name}] ✓ 页面创建成功, viewport: {config.playwright_width}x{config.playwright_height}"
            )

            # 设置默认超时时间
            self.page.set_default_timeout(config.playwright_timeout)

            # 反检测：页面创建后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 先访问平台域名（避免跨域问题）
            logger.debug(
                f"[{self.platform_name}] 访问平台域名: https://{self.platform_domain}"
            )
            await self.page.goto(f"https://{self.platform_domain}")

            # 反检测：访问域名后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 添加 Cookies
            converted_cookies = self._convert_cookies()
            logger.debug(
                f"[{self.platform_name}] 添加 {len(converted_cookies)} 个 Cookie..."
            )
            await context.add_cookies(converted_cookies)  # type: ignore
            logger.debug(f"[{self.platform_name}] ✓ Cookie 添加完成")

            # 反检测：添加 Cookies 后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 访问验证页面
            verify_url = await self.get_verify_url()
            logger.debug(f"[{self.platform_name}] 访问验证页面: {verify_url}")
            await self.page.goto(verify_url)

            # 等待页面加载完成
            logger.debug(f"[{self.platform_name}] 等待页面加载完成...")
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.debug(f"[{self.platform_name}] ✓ 页面加载完成")

            # 反检测：页面加载后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(2.0, 3.0)
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 反检测：模拟人类行为（滚动、鼠标移动）
            await self._simulate_human_behavior()

            # 检查登录状态
            logger.debug(f"[{self.platform_name}] 检查登录状态...")
            is_logged_in = await self.check_login_status()

            # 反检测：根据验证结果随机停留
            if config.human_behavior_enabled:
                if is_logged_in:
                    # 成功：停留更长时间
                    delay = await self._random_delay(
                        config.stay_time_success_min, config.stay_time_success_max
                    )
                    logger.debug(
                        f"[{self.platform_name}] ✓ 验证成功，停留 {delay:.2f} 秒"
                    )
                else:
                    # 失败：停留较短时间
                    delay = await self._random_delay(
                        config.stay_time_failed_min, config.stay_time_failed_max
                    )
                    logger.debug(
                        f"[{self.platform_name}] ✓ 验证失败，停留 {delay:.2f} 秒"
                    )

            result = {
                "success": is_logged_in,
                "message": "验证成功，Cookie 有效" if is_logged_in else "Cookie 已失效",
            }
            logger.info(
                f"[{self.platform_name}] 验证完成: {result['success']} - {result['message']}"
            )

            return result

        except Exception as e:
            error_msg = f"验证过程出错: {str(e)}"
            logger.error(f"[{self.platform_name}] {error_msg}", exc_info=True)
            return {
                "success": False,
                "message": error_msg,
            }
        finally:
            # 清理资源
            logger.debug(f"[{self.platform_name}] 清理资源...")
            if self.browser:
                await self.browser.close()
                logger.debug(f"[{self.platform_name}] ✓ 浏览器已关闭")
            if self.playwright:
                await self.playwright.stop()
                logger.debug(f"[{self.platform_name}] ✓ Playwright 已停止")
            logger.info(f"[{self.platform_name}] ===== Cookie 验证结束 =====\n")

    async def publish(self) -> PublishResult:
        """执行发布

        Returns:
            发布结果对象
        """
        logger.info(f"[{self.platform_name}] ===== 开始发布文章 =====")
        if self.article_data:
            logger.debug(
                f"[{self.platform_name}] 文章标题: {self.article_data.get('title', '')}"
            )
        logger.debug(
            f"[{self.platform_name}] Cookie 数量: {len(self.cookies)}, User-Agent: {(self.user_agent or DEFAULT_USER_AGENT)[:50]}..."
        )

        try:
            from playwright.async_api import async_playwright

            from Modules.common.libs.config.registry import ConfigRegistry

            # 获取配置
            config = ConfigRegistry.get("content")
            if config is None:
                logger.error(
                    f"[{self.platform_name}] ConfigRegistry.get('content') 返回 None"
                )
                return PublishResult(
                    success=False,
                    message="配置未加载，请重启后端服务",
                )

            logger.debug(
                f"[{self.platform_name}] 配置 - headless: {config.playwright_headless}, timeout: {config.playwright_timeout}ms"
            )

            # 启动浏览器
            logger.info(f"[{self.platform_name}] 正在启动 Playwright...")
            self.playwright = await async_playwright().start()

            logger.info(
                f"[{self.platform_name}] 正在启动 Chromium 浏览器 (headless={config.playwright_headless})..."
            )
            self.browser = await self.playwright.chromium.launch(
                headless=config.playwright_headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            logger.info(f"[{self.platform_name}] ✓ 浏览器启动成功")

            # 创建浏览器上下文
            logger.debug(f"[{self.platform_name}] 创建浏览器上下文...")
            context = await self.browser.new_context(
                user_agent=self.user_agent or DEFAULT_USER_AGENT,
                viewport={
                    "width": config.playwright_width,
                    "height": config.playwright_height,
                },
            )
            self.page = await context.new_page()
            logger.debug(
                f"[{self.platform_name}] ✓ 页面创建成功, viewport: {config.playwright_width}x{config.playwright_height}"
            )

            # 设置默认超时时间
            self.page.set_default_timeout(config.playwright_timeout)

            # 反检测：页面创建后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 先访问平台域名（避免跨域问题）
            logger.debug(
                f"[{self.platform_name}] 访问平台域名: https://{self.platform_domain}"
            )
            await self.page.goto(f"https://{self.platform_domain}")

            # 反检测：访问域名后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 添加 Cookies
            converted_cookies = self._convert_cookies()
            logger.debug(
                f"[{self.platform_name}] 添加 {len(converted_cookies)} 个 Cookie..."
            )
            await context.add_cookies(converted_cookies)  # type: ignore
            logger.debug(f"[{self.platform_name}] ✓ Cookie 添加完成")

            # 反检测：添加 Cookies 后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 【修改】直接导航到发布页面验证登录状态
            # 获取发布页面 URL
            publish_url = await self.get_publish_url()
            logger.debug(f"[{self.platform_name}] 导航到发布页面: {publish_url}")

            # 导航到发布页面
            await self.page.goto(publish_url)

            # 等待页面加载完成
            logger.debug(f"[{self.platform_name}] 等待发布页面加载...")
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.debug(f"[{self.platform_name}] ✓ 发布页面加载完成")

            # 检查是否出现登录页面（Cookie 失效）
            logger.debug(f"[{self.platform_name}] 检查是否跳转到登录页...")
            is_at_login_page = await self._check_if_at_login_page()
            if is_at_login_page:
                logger.warning(
                    f"[{self.platform_name}] Cookie 已失效，页面已跳转到登录页"
                )
                return PublishResult(
                    success=False,
                    message="Cookie 已失效，页面已跳转到登录页，请重新验证",
                )
            logger.debug(f"[{self.platform_name}] ✓ 未检测到登录页，Cookie 有效")

            # 反检测：页面加载后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(2.0, 3.0)
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 反检测：模拟人类行为
            await self._simulate_human_behavior()

            # 填写文章内容
            logger.info(f"[{self.platform_name}] 开始填写文章内容...")
            await self.fill_article_content()
            logger.info(f"[{self.platform_name}] ✓ 文章内容填写完成")

            # 反检测：填写后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(2.0, 4.0)
                logger.debug(f"[{self.platform_name}] ✓ 延迟 {delay:.2f} 秒")

            # 提交文章
            logger.info(f"[{self.platform_name}] 提交文章...")
            result = await self.submit_article()

            if result.success:
                logger.info(f"[{self.platform_name}] ✓ 发布成功: {result.message}")
                if result.platform_url:
                    logger.info(
                        f"[{self.platform_name}] ✓ 文章链接: {result.platform_url}"
                    )
            else:
                logger.error(f"[{self.platform_name}] ✗ 发布失败: {result.message}")

            return result

        except Exception as e:
            logger.error(
                f"[{self.platform_name}] 发布过程出错: {str(e)}", exc_info=True
            )
            return PublishResult(
                success=False,
                message=f"发布过程出错: {str(e)}",
            )

        finally:
            # 清理资源
            logger.debug(f"[{self.platform_name}] 清理资源...")
            if self.browser:
                await self.browser.close()
                logger.debug(f"[{self.platform_name}] ✓ 浏览器已关闭")
            if self.playwright:
                await self.playwright.stop()
                logger.debug(f"[{self.platform_name}] ✓ Playwright 已停止")
            logger.info(f"[{self.platform_name}] ===== 发布结束 =====\n")

    # ==================== 辅助方法 ====================

    async def _check_if_at_login_page(self) -> bool:
        """检查当前页面是否是登录页面

        Returns:
            True 表示在登录页，False 表示不在登录页
        """
        try:
            assert self.page is not None

            # 方式 1: 检查 URL 是否包含登录关键词
            current_url = self.page.url
            logger.debug(f"[{self.platform_name}] 检查登录页 - 当前URL: {current_url}")
            if "login" in current_url.lower() or "signin" in current_url.lower():
                logger.debug(
                    f"[{self.platform_name}] 检测到登录页 (URL包含login/signin)"
                )
                return True

            # 方式 2: 检查是否存在登录相关的元素
            from Modules.common.libs.config.registry import ConfigRegistry

            config = ConfigRegistry.get("content")
            if config:
                login_button = await self.page.query_selector(
                    config.zhihu_login_selector
                )
                if login_button:
                    is_visible = await login_button.is_visible()
                    if is_visible:
                        logger.debug(
                            f"[{self.platform_name}] 检测到登录页 (登录按钮可见)"
                        )
                        return True

            logger.debug(f"[{self.platform_name}] 未检测到登录页")
            return False

        except Exception as e:
            logger.warning(f"[{self.platform_name}] 检查登录页时出错: {str(e)}")
            return False

    async def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0) -> float:
        """随机延迟，模拟人类行为的不确定性

        Args:
            min_sec: 最小延迟时间（秒）
            max_sec: 最大延迟时间（秒）

        Returns:
            实际延迟时间（秒）
        """
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
        return delay

    async def _random_scroll(self, scroll_count: int | None = None) -> None:
        """随机滚动页面，模拟人类浏览行为

        Args:
            scroll_count: 滚动次数，None 则使用配置的随机值
        """
        from Modules.common.libs.config.registry import ConfigRegistry

        config = ConfigRegistry.get("content")
        if config is None or not config.human_behavior_enabled:
            return

        if scroll_count is None:
            scroll_count = random.randint(
                config.scroll_count_min, config.scroll_count_max
            )

        logger.debug(f"[{self.platform_name}] 开始随机滚动，次数: {scroll_count}")

        for i in range(scroll_count):
            # 随机滚动距离
            scroll_amount = random.randint(100, 500)
            assert self.page is not None
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")

            # 滚动后停顿
            await asyncio.sleep(random.uniform(0.5, 1.5))

            logger.debug(
                f"[{self.platform_name}] 滚动 {i + 1}/{scroll_count}: {scroll_amount}px"
            )

    async def _random_mouse_move(self, move_count: int | None = None) -> None:
        """随机移动鼠标，模拟人类行为

        Args:
            move_count: 移动次数，None 则使用配置的随机值
        """
        assert self.page is not None, "页面未初始化"

        from Modules.common.libs.config.registry import ConfigRegistry

        config = ConfigRegistry.get("content")
        if config is None or not config.human_behavior_enabled:
            return

        if move_count is None:
            move_count = random.randint(
                config.mouse_move_count_min, config.mouse_move_count_max
            )

        # 获取视口大小
        viewport = self.page.viewport_size
        if not viewport:
            return

        width, height = viewport["width"], viewport["height"]
        logger.debug(
            f"[{self.platform_name}] 开始随机鼠标移动，次数: {move_count}, 视口: {width}x{height}"
        )

        for i in range(move_count):
            # 随机目标位置
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)

            # 鼠标移动
            assert self.page is not None
            await self.page.mouse.move(x, y)

            # 移动后停顿
            await asyncio.sleep(random.uniform(0.3, 0.8))

            logger.debug(
                f"[{self.platform_name}] 鼠标移动 {i + 1}/{move_count}: ({x}, {y})"
            )

    async def _simulate_human_behavior(self) -> None:
        """模拟人类浏览行为（滚动 + 鼠标移动）"""
        from Modules.common.libs.config.registry import ConfigRegistry

        config = ConfigRegistry.get("content")
        if config is None or not config.human_behavior_enabled:
            return

        logger.debug(f"[{self.platform_name}] 开始模拟人类行为...")

        # 1. 先随机滚动
        await self._random_scroll()

        # 2. 随机移动鼠标
        await self._random_mouse_move()

        # 3. 50% 概率再滚动一次
        if random.random() > 0.5:
            await self._random_scroll(1)

        logger.debug(f"[{self.platform_name}] ✓ 人类行为模拟完成")

    def _convert_cookies(self) -> list[dict]:
        """转换 Cookie 格式

        将浏览器扩展的 Cookie 格式转换为 Playwright 需要的格式。

        Returns:
            Playwright 格式的 Cookie 列表
        """

        converted = []
        for cookie in self.cookies:
            new_cookie: dict = {
                "name": cookie.get("name", ""),
                "value": cookie.get("value", ""),
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", "/"),
                "httpOnly": cookie.get("httpOnly", False),
                "secure": cookie.get("secure", True),
            }

            # 处理 sameSite
            same_site = cookie.get("sameSite")
            if same_site in ["strict", "lax", "none"]:
                new_cookie["sameSite"] = same_site.capitalize()

            # 处理过期时间
            expiration_date = cookie.get("expirationDate")
            if expiration_date:
                new_cookie["expires"] = expiration_date

            converted.append(new_cookie)  # type: ignore

        logger.debug(
            f"[{self.platform_name}] Cookie 格式转换完成: {len(self.cookies)} -> {len(converted)}"
        )
        return converted
