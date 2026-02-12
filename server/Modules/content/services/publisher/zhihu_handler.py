"""
知乎平台处理器

融合了知乎验证器和知乎发布器的功能。
"""

import asyncio
import random
import re

from loguru import logger
from markdownify import markdownify as md

from .base_platform_handler import (
    DEFAULT_USER_AGENT,
    BasePlatformHandler,
    PublishResult,
)


class ZhihuHandler(BasePlatformHandler):
    """知乎平台处理器（融合验证器和发布器）"""

    @property
    def platform_name(self) -> str:
        """平台名称"""
        return "知乎"

    @property
    def platform_domain(self) -> str:
        """平台域名"""
        return "www.zhihu.com"

    async def get_verify_url(self) -> str:
        """获取验证 URL"""
        from Modules.common.libs.config.registry import ConfigRegistry

        config = ConfigRegistry.get("content")
        return config.zhihu_verify_url

    async def get_publish_url(self) -> str:
        """获取发布页面 URL

        使用专栏编辑页面（而不是提问页），因为专栏更适合文章发布
        """
        # 知乎专栏写作页面
        return "https://zhuanlan.zhihu.com/write"

    async def check_login_status(self) -> bool:
        """检查知乎登录状态

        检测方式（融合了 Verifier 和 Publisher 的所有方法）：
        1. 检查是否存在登录按钮（存在则未登录）
        2. 检查是否存在消息图标（存在则已登录）
        3. 检查是否存在用户头像（存在则已登录）
        4. 检查是否能访问个人主页（通过访问设置页验证）

        Returns:
            True 表示已登录，False 表示未登录
        """
        from Modules.common.libs.config.registry import ConfigRegistry

        config = ConfigRegistry.get("content")

        try:
            # 确保页面已初始化
            assert self.page is not None

            # 记录当前页面 URL（用于检测是否跳转）
            original_url = self.page.url
            logger.debug(f"[知乎] check_login_status 开始 - 当前页面: {original_url}")

            # 等待页面稳定
            await self.page.wait_for_load_state("networkidle", timeout=5000)

            # 方式 1: 检查是否存在登录按钮（存在则未登录）
            logger.debug("[知乎] 方式1: 检查登录按钮...")
            logger.debug(f"[知乎]   当前页面URL: {self.page.url}")
            logger.debug(f"[知乎]   使用选择器: {config.zhihu_login_selector}")
            login_button = await self.page.query_selector(config.zhihu_login_selector)
            if login_button:
                # 如果能找到登录按钮且可见，说明未登录
                is_visible = await login_button.is_visible()
                logger.debug(f"[知乎]   登录按钮存在，可见性: {is_visible}")
                if is_visible:
                    logger.debug("[知乎] 检测到登录按钮可见，判定为未登录")
                    return False
            else:
                logger.debug("[知乎]   登录按钮元素不存在")
            logger.debug("[知乎] 未检测到登录按钮")

            # 方式 2: 检查是否存在消息图标（存在则已登录）
            logger.debug("[知乎] 方式2: 检查消息图标...")
            logger.debug(f"[知乎]   当前页面URL: {self.page.url}")
            logger.debug(f"[知乎]   使用选择器: {config.zhihu_logged_in_selector}")
            message_icon = await self.page.query_selector(
                config.zhihu_logged_in_selector
            )
            if message_icon:
                is_visible = await message_icon.is_visible()
                logger.debug(f"[知乎]   消息图标存在，可见性: {is_visible}")
                if is_visible:
                    logger.debug("[知乎] 检测到消息图标可见，判定为已登录")
                    return True
            else:
                logger.debug("[知乎]   消息图标元素不存在")
            logger.debug("[知乎] 未检测到消息图标")

            # 方式 3: 检查是否存在用户头像
            logger.debug("[知乎] 方式3: 检查用户头像...")
            logger.debug(f"[知乎]   当前页面URL: {self.page.url}")

            # 尝试多个头像选择器
            avatar_selectors = [
                ".AppHeader-profileAvatar",  # 新版知乎
                ".AppHeader-profile .Avatar",  # 旧版知乎
                ".Avatar",  # 通用头像
            ]

            for avatar_selector in avatar_selectors:
                logger.debug(f"[知乎]   使用选择器: {avatar_selector}")
                avatar = await self.page.query_selector(avatar_selector)
                if avatar:
                    is_visible = await avatar.is_visible()
                    logger.debug(f"[知乎]   头像存在，可见性: {is_visible}")
                    if is_visible:
                        logger.debug(
                            f"[知乎] ✓ 检测到头像可见（{avatar_selector}），判定为已登录"
                        )
                        return True
                    logger.debug("[知乎]   头像存在但不可见")
                else:
                    logger.debug("[知乎]   头像元素不存在")

            logger.debug("[知乎] 未检测到用户头像")

            # 方式 3.5: 检查是否存在个人资料菜单（新版知乎）
            logger.debug("[知乎] 方式3.5: 检查个人资料菜单...")
            profile_menu_selectors = [
                ".AppHeader-profileMenu",
                ".AppHeader-profileEntry",
            ]
            for profile_selector in profile_menu_selectors:
                logger.debug(f"[知乎]   使用选择器: {profile_selector}")
                profile_menu = await self.page.query_selector(profile_selector)
                if profile_menu:
                    is_visible = await profile_menu.is_visible()
                    logger.debug(f"[知乎]   个人资料菜单存在，可见性: {is_visible}")
                    if is_visible:
                        logger.debug(
                            f"[知乎] ✓ 检测到个人资料菜单可见（{profile_selector}），判定为已登录"
                        )
                        return True
                else:
                    logger.debug("[知乎]   个人资料菜单元素不存在")
            logger.debug("[知乎] 未检测到个人资料菜单")

            # 方式 4: 检查是否能访问个人主页
            logger.debug("[知乎] 方式4: 检查是否能访问设置页...")
            logger.debug(f"[知乎]   跳转前URL: {self.page.url}")
            logger.warning("[知乎] ⚠️ 方式4 将跳转到设置页，这会导致离开当前页面！")
            try:
                await self.page.goto("https://www.zhihu.com/settings", timeout=5000)
                # 如果能成功跳转到设置页面，说明已登录
                # 未登录会重定向到登录页
                current_url = self.page.url
                logger.debug(f"[知乎]   跳转后URL: {current_url}")
                logger.debug(
                    f"[知乎]   URL是否包含'settings': {'settings' in current_url}"
                )
                if "settings" in current_url:
                    logger.debug(
                        f"[知乎] ⚠️ 成功访问设置页，但当前仍在设置页: {current_url}"
                    )
                    logger.warning(
                        "[知乎] ⚠️ 登录检查完成后未返回原页面，可能导致后续操作失败！"
                    )
                    return True
            except Exception as e:
                logger.debug(f"[知乎] 无法访问设置页: {str(e)}")

            logger.warning("[知乎] 所有检测方式均未通过，判定为未登录")
            return False

        except Exception as e:
            # 发生异常时，保守处理，认为未登录
            logger.error(f"[知乎] 检查登录状态时出错: {str(e)}", exc_info=True)
            return False

    async def _check_login_by_cookie(self) -> bool:
        """通过Cookie检查登录状态（轻量级版本，不跳转页面）

        专门为API获取方案设计，只检查关键Cookie是否存在，不进行页面跳转。

        Returns:
            True 表示已登录，False 表示未登录
        """
        try:
            assert self.page is not None, "页面未初始化"

            # 获取当前context的所有Cookie
            cookies = await self.page.context.cookies()

            # 检查关键Cookie是否存在
            # d_c0 是知乎的主要登录Cookie
            login_cookies = ["d_c0", "tgw_login", "z_c0"]

            has_login_cookie = any(
                cookie.get("name") in login_cookies for cookie in cookies
            )

            if has_login_cookie:
                # 进一步检查Cookie是否有效（是否有值）
                for cookie in cookies:
                    if cookie.get("name") in login_cookies and cookie.get("value"):
                        logger.debug(
                            f"[知乎] ✓ 检测到有效登录Cookie: {cookie.get('name')}"
                        )
                        return True

            logger.debug("[知乎] 未检测到有效登录Cookie")
            return False

        except Exception as e:
            logger.warning(f"[知乎] Cookie检查失败: {str(e)}")
            return False

    async def fill_article_content(self) -> None:
        """填写文章内容

        知乎文章发布流程：
        1. 等待编辑器加载
        2. 填写标题
        3. 填写正文内容
        """
        assert self.page is not None
        assert self.article_data is not None, "article_data 不能为 None"

        # 1. 等待编辑器加载
        logger.info("[知乎] 等待编辑器加载...")
        editor_selectors = [
            '[contenteditable="true"]',
            ".DraftEditor-editorContainer",
            ".public-DraftEditor-content",
        ]

        editor = None
        for selector in editor_selectors:
            try:
                editor = await self.page.wait_for_selector(
                    selector, timeout=5000, state="visible"
                )
                if editor:
                    logger.info(f"[知乎] ✓ 编辑器已加载: {selector}")
                    break
            except Exception:
                logger.debug(f"[知乎] 选择器未找到: {selector}")
                continue

        if not editor:
            logger.error("[知乎] 编辑器加载超时，所有选择器均未找到")
            raise Exception("编辑器加载超时，请检查网络或页面状态")

        # 2. 填写标题
        logger.info("[知乎] 填写文章标题...")
        title = self.article_data.get("title", "")
        if title:
            # 知乎的标题输入框选择器
            title_selectors = [
                'input[placeholder*="请输入标题"]',
                'input[placeholder*="标题"]',
                ".QuestionAsk-titleInput",
                ".WriteIndex-titleInput",
                'input[type="text"]',
            ]

            title_input = None
            for selector in title_selectors:
                try:
                    title_input = await self.page.wait_for_selector(
                        selector, timeout=3000, state="visible"
                    )
                    if title_input:
                        logger.info(f"[知乎] ✓ 找到标题输入框: {selector}")
                        break
                except Exception:
                    logger.debug(f"[知乎] 标题输入框选择器未找到: {selector}")
                    continue

            if title_input:
                await title_input.click()
                await asyncio.sleep(0.5)
                # 清空并输入标题
                await title_input.fill("")
                await title_input.type(title, delay=100)
                logger.info(f"[知乎] ✓ 标题已填写: {title}")
            else:
                logger.warning("[知乎] ⚠ 未找到标题输入框，跳过标题填写")

        # 3. 填写正文内容
        logger.info("[知乎] 填写正文内容...")
        content = self.article_data.get("content", "")
        if content:
            # 检查内容是否为 HTML 格式（包含 HTML 标签）
            if "<" in content and ">" in content:
                logger.info("[知乎] 检测到 HTML 格式内容，正在转换为 Markdown...")
                # 使用 markdownify 将 HTML 转换为 Markdown
                markdown_content = md(content)
                logger.debug(
                    f"[知乎] HTML 转换前长度: {len(content)}, Markdown 转换后长度: {len(markdown_content)}"
                )
                logger.debug(f"[知乎] HTML 原文: {content[:100]}...")
                logger.debug(f"[知乎] Markdown 结果: {markdown_content[:100]}...")
                content = markdown_content
            else:
                logger.debug("[知乎] 内容非 HTML 格式，直接使用原文")

            # 等待并点击正文编辑区域
            await editor.click()
            await asyncio.sleep(1)

            # 清空现有内容
            await self.page.keyboard.press("Control+A")
            await asyncio.sleep(0.3)
            await self.page.keyboard.press("Delete")
            await asyncio.sleep(0.5)

            # 输入正文（使用 type 方法模拟打字，更自然）
            logger.info(f"[知乎] 正在输入正文（长度: {len(content)} 字符）...")
            await editor.type(content, delay=50)  # 每个字符延迟 50ms
            logger.info("[知乎] ✓ 正文已填写")

        # 4. 滚动到编辑器底部，确保所有内容加载
        await asyncio.sleep(2)
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def submit_article(self) -> PublishResult:
        """提交文章

        Returns:
            发布结果，包含平台文章ID和链接
        """
        assert self.page is not None, "页面未初始化"

        try:
            # 1. 查找并点击发布按钮
            logger.info("[知乎] 查找发布按钮...")
            publish_button_selectors = [
                'button:has-text("发布")',
                'button:has-text("提交")',
                ".PublishButton",
                'button[class*="publish"]',
                'button[class*="submit"]',
                ".PublishPanel-stepTwoButton",  # 知乎专栏发布按钮
            ]

            publish_button = None
            for selector in publish_button_selectors:
                try:
                    # 等待按钮可见且可点击
                    publish_button = await self.page.wait_for_selector(
                        selector, timeout=3000, state="visible"
                    )
                    if publish_button:
                        # 检查按钮是否可用
                        is_disabled = await publish_button.get_attribute("disabled")
                        if is_disabled != "true":
                            logger.info(f"[知乎] ✓ 找到发布按钮: {selector}")
                            break
                except Exception:
                    logger.debug(f"[知乎] 发布按钮选择器未找到: {selector}")
                    continue

            if not publish_button:
                logger.error("[知乎] 未找到可用的发布按钮")
                return PublishResult(
                    success=False,
                    message="未找到可用的发布按钮，请检查文章内容是否完整",
                )

            # 2. 点击发布按钮
            logger.info("[知乎] 点击发布按钮...")
            await publish_button.click()

            # 3. 等待发布完成
            logger.info("[知乎] 等待发布完成...")
            await asyncio.sleep(3)

            # 4. 检查是否成功发布
            # 成功标志：页面跳转到文章详情页或显示成功提示
            current_url = self.page.url
            publish_url = await self.get_publish_url()
            logger.debug(f"[知乎] 当前URL: {current_url}")

            success_indicators = [
                lambda: "zhuanlan.zhihu.com/p/" in current_url,  # 专栏文章
                lambda: "zhihu.com/question/" in current_url
                or "zhihu.com/p/" in current_url,
                lambda: current_url != publish_url,
            ]

            is_published = False
            for i, indicator in enumerate(success_indicators, 1):
                try:
                    if indicator():
                        logger.debug(f"[知乎] 成功标志 {i} 检测通过")
                        is_published = True
                        break
                except Exception:
                    logger.debug(f"[知乎] 成功标志 {i} 检测失败")
                    continue

            if is_published:
                # 从 URL 中提取文章 ID
                article_id = self._extract_article_id_from_url(current_url)
                logger.info(f"[知乎] ✓ 发布成功，文章ID: {article_id}")

                return PublishResult(
                    success=True,
                    message="文章发布成功",
                    platform_article_id=article_id,
                    platform_url=current_url,
                )
            else:
                # 检查是否有错误提示
                error_selectors = [
                    ".error-message",
                    ".error-tip",
                    '[class*="error"]',
                    '[role="alert"]',
                ]

                error_message = "发布失败，未知错误"
                for selector in error_selectors:
                    try:
                        error_elem = await self.page.query_selector(selector)
                        if error_elem:
                            error_text = await error_elem.text_content()
                            if error_text and error_text.strip():
                                error_message = error_text.strip()
                                logger.warning(
                                    f"[知乎] 检测到错误提示: {error_message}"
                                )
                                break
                    except Exception:
                        continue

                logger.error(f"[知乎] ✗ 发布失败: {error_message}")
                return PublishResult(
                    success=False,
                    message=error_message,
                )

        except Exception as e:
            logger.error(f"[知乎] ✗ 提交文章时出错: {str(e)}", exc_info=True)
            return PublishResult(
                success=False,
                message=f"提交文章时出错: {str(e)}",
            )

    def _extract_article_id_from_url(self, url: str) -> str | None:
        """从知乎文章 URL 中提取文章 ID

        Args:
            url: 知乎文章 URL

        Returns:
            文章 ID，如果无法提取则返回 None
        """
        # 知乎文章 URL 格式：
        # https://zhuanlan.zhihu.com/p/xxxxxxxx
        # https://www.zhihu.com/question/xxxxx/answer/xxxxx
        # https://www.zhihu.com/p/xxxxx

        logger.debug(f"[知乎] 从URL提取文章ID: {url}")

        # 尝试从 URL 中提取 ID
        patterns = [
            r"/zhuanlan\.zhihu\.com/p/(\d+)",  # 专栏文章
            r"/p/(\d+)",  # /p/数字 格式
            r"/answer/(\d+)",  # /answer/数字 格式
            r"/question/(\d+)",  # /question/数字 格式
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                article_id = match.group(1)
                logger.debug(f"[知乎] 使用模式 '{pattern}' 提取到文章ID: {article_id}")
                return article_id

        logger.warning(f"[知乎] 无法从URL提取文章ID，返回原始URL: {url}")
        return url

    async def fetch_recommended_questions(
        self,
        limit: int = 20,
        category: str | None = None,
    ) -> list[dict]:
        """获取知乎推荐问题列表（API方式）

        通过知乎API直接获取推荐问题，不依赖HTML解析。

        Args:
            limit: 获取数量，默认20条
            category: 分类筛选（暂不支持）

        Returns:
            问题列表，每项包含:
            - question_id: 问题ID
            - title: 问题标题
            - description: 问题描述
            - url: 问题链接
            - view_count: 浏览量
            - answer_count: 回答数
            - follower_count: 关注者数
            - category: 分类
            - hot_score: 热度分数
            - author_name: 提问者昵称
        """
        from playwright.async_api import async_playwright

        from Modules.common.libs.config.registry import ConfigRegistry

        config = ConfigRegistry.get("content")
        questions = []

        try:
            # 启动浏览器
            logger.info("[知乎] 正在启动 Playwright...")
            self.playwright = await async_playwright().start()

            logger.info(
                f"[知乎] 正在启动 Chromium 浏览器 (headless={config.playwright_headless})..."
            )
            self.browser = await self.playwright.chromium.launch(
                headless=config.playwright_headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            logger.info("[知乎] ✓ 浏览器启动成功")

            # 创建浏览器上下文
            logger.debug("[知乎] 创建浏览器上下文...")
            context = await self.browser.new_context(
                user_agent=self.user_agent or DEFAULT_USER_AGENT,
                viewport={
                    "width": config.playwright_width,
                    "height": config.playwright_height,
                },
            )
            self.page = await context.new_page()
            logger.debug(
                f"[知乎] ✓ 页面创建成功, viewport: {config.playwright_width}x{config.playwright_height}"
            )

            # 设置默认超时时间
            self.page.set_default_timeout(config.playwright_timeout)

            # 反检测：页面创建后随机延迟
            if config.human_behavior_enabled:
                delay = random.uniform(config.random_delay_min, config.random_delay_max)
                await asyncio.sleep(delay)
                logger.debug(f"[知乎] ✓ 延迟 {delay:.2f} 秒")

            # 先访问平台域名（避免跨域问题）
            logger.debug(f"[知乎] 访问平台域名: https://{self.platform_domain}")
            await self.page.goto(f"https://{self.platform_domain}")

            # 反检测：访问域名后随机延迟
            if config.human_behavior_enabled:
                delay = random.uniform(config.random_delay_min, config.random_delay_max)
                await asyncio.sleep(delay)
                logger.debug(f"[知乎] ✓ 延迟 {delay:.2f} 秒")

            # 添加 Cookies
            converted_cookies = self._convert_cookies()
            logger.debug(f"[知乎] 添加 {len(converted_cookies)} 个 Cookie...")
            await context.add_cookies(converted_cookies)  # type: ignore
            logger.debug("[知乎] ✓ Cookie 添加完成")

            # 反检测：添加 Cookies 后随机延迟
            if config.human_behavior_enabled:
                delay = random.uniform(config.random_delay_min, config.random_delay_max)
                await asyncio.sleep(delay)
                logger.debug(f"[知乎] ✓ 延迟 {delay:.2f} 秒")

            # 检查登录状态（使用简化版Cookie检查，不跳转页面）
            logger.info("[知乎] 检查登录状态（Cookie方式）...")
            is_logged_in = await self._check_login_by_cookie()
            logger.info(f"[知乎] 登录状态: {'已登录' if is_logged_in else '未登录'}")

            if not is_logged_in:
                logger.error("[知乎] 未登录，无法获取推荐问题")
                raise Exception("知乎账号未登录，请先验证账号状态")

            logger.info("[知乎] ✓ 已登录，开始通过API获取推荐问题...")

            # 使用 API 方式获取推荐问题
            questions = await self._fetch_questions_via_api(limit, category)

        except Exception as e:
            logger.error(f"[知乎] ✗ 抓取推荐问题时出错: {str(e)}", exc_info=True)
            raise

        finally:
            # 清理资源
            logger.debug("[知乎] 清理资源...")
            if self.browser:
                await self.browser.close()
                logger.debug("[知乎] ✓ 浏览器已关闭")
            if self.playwright:
                await self.playwright.stop()
                logger.debug("[知乎] ✓ Playwright 已停止")
            logger.info("[知乎] ===== 抓取推荐问题结束 =====\n")

        return questions

    async def _fetch_questions_via_api(
        self, limit: int = 20, category: str | None = None
    ) -> list[dict]:
        """通过 API 获取推荐问题（主动调用方式）

        使用 page.evaluate() 在页面上下文中主动调用 fetch() 获取 API 数据。
        API 端点: https://www.zhihu.com/api/v4/creators/question_route/author_related/recommend

        Args:
            limit: 获取数量，默认20条
            category: 分类筛选（暂不支持）

        Returns:
            问题列表，每项包含:
            - question_id: 问题ID
            - title: 问题标题
            - description: 问题描述
            - url: 问题链接
            - view_count: 浏览量
            - answer_count: 回答数
            - follower_count: 关注者数
            - category: 分类
            - hot_score: 热度分数
            - author_name: 提问者昵称
        """
        assert self.page is not None, "页面未初始化"
        questions = []

        try:
            logger.info("[知乎] 正在通过 API 主动调用获取推荐问题...")

            # 确保在推荐问题页面（用于设置正确的 referer）
            recommend_url = "https://www.zhihu.com/creator/featured-question/recommend"
            if "recommend" not in self.page.url:
                logger.info(f"[知乎] 导航到推荐问题页面: {recommend_url}")
                await self.page.goto(recommend_url, timeout=10000)
                await self.page.wait_for_load_state("networkidle", timeout=10000)

            # 构造 API URL
            # API 参数说明:
            # - limit: 返回数量
            # - offset: 偏移量（用于分页）
            # - page_source: 页面来源标识
            # - recom_domain_score_ab: AB测试参数
            api_url = (
                "https://www.zhihu.com/api/v4/creators/question_route/author_related/recommend"
                f"?limit={limit}&offset=0&page_source=web_author_recommend&recom_domain_score_ab=1"
            )
            logger.debug(f"[知乎] API URL: {api_url}")

            # 在页面上下文中执行 fetch 请求
            # 使用 credentials: 'include' 自动携带 Cookie
            logger.debug("[知乎] 执行 fetch 请求...")
            response_data = await self.page.evaluate(
                """
                async (url) => {
                    try {
                        const response = await fetch(url, {
                            method: 'GET',
                            credentials: 'include',  // 自动携带 Cookie
                            headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json',
                            }
                        });
                        if (!response.ok) {
                            return {
                                error: true,
                                status: response.status,
                                statusText: response.statusText
                            };
                        }
                        const data = await response.json();
                        return {
                            error: false,
                            data: data
                        };
                    } catch (error) {
                        return {
                            error: true,
                            message: error.toString()
                        };
                    }
                }
            """,
                api_url,
            )

            if response_data.get("error"):
                error_msg = (
                    response_data.get("message")
                    or f"HTTP {response_data.get('status')}"
                )
                logger.error(f"[知乎] API 请求失败: {error_msg}")
                return questions

            data = response_data.get("data", {})
            logger.debug("[知乎] ✓ API 请求成功")

            # 解析 API 响应数据结构
            # 知乎 API 返回格式: { "data": [ ... ], "paging": { ... } }
            questions_data = data.get("data", [])

            if not questions_data:
                logger.warning("[知乎] API 返回数据为空")
                # 尝试直接解析数据
                if isinstance(data, list):
                    questions_data = data

            logger.info(f"[知乎] 解析到 {len(questions_data)} 条问题数据")

            for i, item in enumerate(questions_data[:limit]):
                try:
                    logger.debug(
                        f"[知乎] 解析第 {i + 1}/{min(limit, len(questions_data))} 个问题..."
                    )

                    # API 返回的字段结构解析
                    # 实际数据结构: item["question"] 包含问题数据
                    question = {}

                    # 提取问题数据（注意：API返回的是 "question" 字段，不是 "target"）
                    q = item.get("question", {})

                    # 提取问题 ID
                    question_id = q.get("id", "")

                    # 提取标题
                    title = q.get("title", "")

                    # 清理标题前缀
                    title = self._clean_title(title)

                    # 提取问题描述（excerpt）
                    description = q.get("excerpt", "")

                    # 提取 URL
                    url = q.get("url", "")
                    if not url and question_id:
                        url = f"https://www.zhihu.com/question/{question_id}"

                    # 提取统计数据（浏览量、回答数、关注数）
                    # 注意：API返回的字段名是 visit_count（访问量=浏览量）
                    view_count = q.get("visit_count", 0)
                    answer_count = q.get("answer_count", 0)
                    follower_count = q.get("follower_count", 0)

                    # 提取作者信息
                    author_name = None
                    if "author" in q:
                        author = q["author"]
                        author_name = author.get("name", "") if isinstance(author, dict) else str(author)

                    # 提取分类/话题（如果有的话）
                    category_name = None
                    # 注意：当前API返回的数据中没有 topic 信息
                    # 如果有需要，可以从 item["reason"] 中提取推荐原因作为分类

                    # 计算热度分数
                    hot_score = view_count + answer_count * 10 + follower_count * 5

                    question = {
                        "question_id": question_id,
                        "title": title,
                        "description": description if description else None,
                        "url": url,
                        "view_count": view_count,
                        "answer_count": answer_count,
                        "follower_count": follower_count,
                        "category": category_name,
                        "hot_score": hot_score,
                        "author_name": author_name,
                    }

                    questions.append(question)
                    logger.debug(
                        f"[知乎] ✓ API 解析问题 {i + 1}: {title[:30]}... (ID: {question_id})"
                    )

                except Exception as e:
                    logger.warning(f"[知乎] API 解析问题 {i + 1} 时出错: {str(e)}")
                    continue

            if questions:
                logger.info(f"[知乎] ✓ API 成功获取 {len(questions)} 个推荐问题")
            else:
                logger.warning("[知乎] API 未能解析出任何问题数据")
                logger.debug(f"[知乎] 原始响应数据: {data}")

        except Exception as e:
            logger.error(f"[知乎] API 获取失败: {str(e)}", exc_info=True)

        return questions

    def _parse_zhihu_number(self, text: str, keyword: str = "") -> int:
        """解析知乎的数字格式

        Args:
            text: 包含数字的文本，如 "10.2 万 浏览 · 320 回答 · 342 关注"
            keyword: 关键词筛选（如"浏览"、"回答"、"关注"）

        Returns:
            解析后的整数值

        Examples:
            "10.2 万 浏览 · 320 回答 · 342 关注", "浏览" -> 102000
            "10.2 万 浏览 · 320 回答 · 342 关注", "回答" -> 320
            "10.2 万 浏览 · 320 回答 · 342 关注", "关注" -> 342
        """
        if keyword and keyword not in text:
            return 0

        # 数字格式模式（带单位），数字和单位之间可能有空格
        num_patterns_with_unit = [
            (r"(\d+\.\d+)\s*亿", 100000000),  # 1.2亿 -> 120000000
            (r"(\d+)\s*亿", 100000000),  # 12亿 -> 1200000000
            (r"(\d+\.\d+)\s*万", 10000),  # 1.2万 -> 12000
            (r"(\d+)\s*万", 10000),  # 12万 -> 120000
            (r"(\d+\.\d+)k", 1000),  # 1.2k -> 1200
            (r"(\d+)k", 1000),  # 12k -> 12000
            (r"(\d+)", 1),  # 356 -> 356
        ]

        # 如果有关键词，构造 "数字 + 任意空白 + 关键词" 的模式
        for pattern, multiplier in num_patterns_with_unit:
            if keyword:
                # 匹配 "数字 [空白] 关键词"
                search_pattern = pattern + r"\s*" + keyword
            else:
                # 没有关键词时，直接匹配数字
                search_pattern = pattern

            match = re.search(search_pattern, text)
            if match:
                num_str = match.group(1)
                num = float(num_str) if "." in num_str else int(num_str)
                return int(num * multiplier)

        return 0

    def _extract_question_id_from_url(self, url: str) -> str | None:
        """从知乎问题 URL 中提取问题 ID

        Args:
            url: 知乎问题 URL

        Returns:
            问题 ID

        Examples:
            https://www.zhihu.com/question/123456 -> 123456
        """
        patterns = [
            r"/question/(\d+)",
            r"/p/(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _clean_title(self, title: str) -> str:
        """清理标题，移除前缀标记和多余空白

        Args:
            title: 原始标题

        Returns:
            清理后的标题

        Examples:
            "飙升颜值真的有那么重要吗？" -> "颜值真的有那么重要吗？"
            "新问可以帮我看看这段css出啥问题了吗？" -> "可以帮我看看这段css出啥问题了吗？"
            "标题勤劳未必能致富..." -> "勤劳未必能致富..."
        """
        if not title:
            return title

        # 需要移除的前缀标记列表
        prefixes = ["飙升", "新问", "标题"]

        # 移除前缀标记（移除标记本身和后面的空格）
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix) :].lstrip()
                break

        # 清理多余的空白字符
        title = title.strip().replace("\n", " ").replace("\r", "")
        # 将多个连续空格替换为单个空格
        title = " ".join(title.split())

        return title
