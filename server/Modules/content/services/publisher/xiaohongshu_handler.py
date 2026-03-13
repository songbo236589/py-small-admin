"""
小红书平台处理器

支持图文笔记的发布到小红书平台。
"""

import asyncio
import random
import re
from typing import TYPE_CHECKING

from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

from Modules.common.libs.config.config import Config
from .base_platform_handler import (
    DEFAULT_USER_AGENT,
    BasePlatformHandler,
    PublishResult,
)

if TYPE_CHECKING:
    pass


class XiaohongshuHandler(BasePlatformHandler):
    """小红书平台处理器"""

    @property
    def platform_name(self) -> str:
        """平台名称"""
        return "小红书"

    @property
    def platform_domain(self) -> str:
        """平台域名"""
        return "www.xiaohongshu.com"

    async def get_verify_url(self) -> str:
        """获取验证 URL"""
        config = Config.get("content")
        return config.xiaohongshu_verify_url

    async def get_publish_url(self) -> str:
        """获取发布页面 URL"""
        config = Config.get("content")
        return config.xiaohongshu_publish_url

    async def verify(self) -> dict:
        """验证 Cookie 有效性（双阶段验证）

        阶段1: 验证主站登录状态
        阶段2: 验证创作者平台访问权限

        Returns:
            验证结果字典，包含:
            - success: 是否验证成功
            - message: 结果消息
        """
        logger.info(f"[小红书] ========== 开始双阶段 Cookie 验证 ==========")
        logger.debug(
            f"[小红书] Cookie 数量: {len(self.cookies)}, User-Agent: {(self.user_agent or DEFAULT_USER_AGENT)[:50]}..."
        )

        try:
            from playwright.async_api import async_playwright

            # 获取配置
            config = Config.get("content")
            if config is None:
                logger.error(f"[小红书] Config.get('content') 返回 None")
                return {
                    "success": False,
                    "message": "配置未加载，请重启后端服务",
                }

            logger.debug(
                f"[小红书] 配置 - headless: {config.playwright_headless}, timeout: {config.playwright_timeout}ms"
            )

            # 启动浏览器
            logger.info(f"[小红书] 正在启动 Playwright...")
            self.playwright = await async_playwright().start()

            logger.info(
                f"[小红书] 正在启动 Chromium 浏览器 (headless={config.playwright_headless})..."
            )
            self.browser = await self.playwright.chromium.launch(
                headless=config.playwright_headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            logger.info(f"[小红书] ✓ 浏览器启动成功")

            # 创建上下文和页面
            logger.debug(f"[小红书] 创建浏览器上下文...")
            context = await self.browser.new_context(
                user_agent=self.user_agent or DEFAULT_USER_AGENT,
                viewport={
                    "width": config.playwright_width,
                    "height": config.playwright_height,
                },
            )
            self.page = await context.new_page()
            logger.debug(
                f"[小红书] ✓ 页面创建成功, viewport: {config.playwright_width}x{config.playwright_height}"
            )

            # 应用 playwright-stealth 反检测
            logger.debug(f"[小红书] 应用 playwright-stealth 反检测...")
            await stealth_async(self.page)

            # 设置默认超时时间
            self.page.set_default_timeout(config.playwright_timeout)

            # 先添加 Cookies
            converted_cookies = self._convert_cookies()
            cookie_names = [c.get('name', '') for c in converted_cookies]
            logger.debug(f"[小红书] 添加 {len(converted_cookies)} 个 Cookie...")
            logger.debug(f"[小红书] Cookie 名称列表: {cookie_names}")
            await context.add_cookies(converted_cookies)  # type: ignore
            logger.debug(f"[小红书] ✓ Cookie 添加完成")

            # 反检测：添加 Cookies 后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[小红书] ✓ 延迟 {delay:.2f} 秒")

            # ==================== 阶段1: 主站验证 ====================
            logger.info(f"[小红书] ========== 阶段1: 主站登录验证 ==========")
            verify_url = await self.get_verify_url()
            logger.debug(f"[小红书] 访问主站验证页面: {verify_url}")
            await self.page.goto(verify_url)

            logger.debug(f"[小红书] 等待主站页面加载完成...")
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.debug(f"[小红书] ✓ 主站页面加载完成")

            # 反检测：页面加载后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(2.0, 3.0)
                logger.debug(f"[小红书] ✓ 延迟 {delay:.2f} 秒")

            # 刷新页面让 Cookie 完全生效
            if config.enable_page_refresh:
                logger.info(f"[小红书] 刷新主站页面...")
                delay = await self._random_delay(
                    config.page_refresh_delay_min, config.page_refresh_delay_max
                )
                logger.debug(f"[小红书] 刷新前延迟 {delay:.2f} 秒")

                await self.page.reload(wait_until="networkidle", timeout=10000)
                logger.debug(f"[小红书] ✓ 主站页面刷新完成")

                delay = await self._random_delay(
                    config.page_refresh_after_delay_min, config.page_refresh_after_delay_max
                )
                logger.debug(f"[小红书] 刷新后延迟 {delay:.2f} 秒")

            # 模拟人类行为
            await self._simulate_human_behavior()

            # 检查主站登录状态
            logger.debug(f"[小红书] 检查主站登录状态...")
            is_logged_in = await self.check_login_status()

            if not is_logged_in:
                logger.warning(f"[小红书] ✗ 阶段1验证失败：主站登录状态无效")

                # 反检测：失败后停留
                if config.human_behavior_enabled:
                    delay = await self._random_delay(
                        config.stay_time_failed_min, config.stay_time_failed_max
                    )
                    logger.debug(f"[小红书] 停留 {delay:.2f} 秒")

                return {
                    "success": False,
                    "message": "Cookie 已失效（主站验证失败）",
                }

            logger.info(f"[小红书] ✓ 阶段1验证成功：主站登录状态有效")

            # 反检测：成功后停留
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.stay_time_success_min, config.stay_time_success_max
                )
                logger.debug(f"[小红书] ✓ 停留 {delay:.2f} 秒")

            # ==================== 阶段2: 创作者平台验证 ====================
            if config.xiaohongshu_enable_creator_verify:
                logger.info(f"[小红书] ========== 阶段2: 创作者平台访问验证 ==========")

                # 在新标签页中打开创作者平台
                logger.debug(f"[小红书] 创建新标签页访问创作者平台...")
                self.page = await context.new_page()

                creator_verify_url = config.xiaohongshu_creator_verify_url
                logger.debug(f"[小红书] 访问创作者平台: {creator_verify_url}")

                # 反检测：打开新标签前的延迟
                if config.human_behavior_enabled:
                    delay = await self._random_delay(1.0, 2.0)
                    logger.debug(f"[小红书] 打开新标签前延迟 {delay:.2f} 秒...")
                    await asyncio.sleep(delay)

                try:
                    await self.page.goto(creator_verify_url, timeout=30000)
                    logger.debug(f"[小红书] ✓ 创作者平台页面已加载")

                    # 等待页面稳定
                    await asyncio.sleep(2)

                    # 检查创作者平台访问权限
                    logger.debug(f"[小红书] 检查创作者平台访问权限...")
                    has_creator_access = await self._check_creator_platform_access()

                    if has_creator_access:
                        logger.info(f"[小红书] ✓ 阶段2验证成功：具有创作者平台访问权限")

                        # 反检测：成功后停留
                        if config.human_behavior_enabled:
                            delay = await self._random_delay(2.0, 3.0)
                            logger.debug(f"[小红书] ✓ 停留 {delay:.2f} 秒")

                        return {
                            "success": True,
                            "message": "验证成功，Cookie 有效（主站 + 创作者平台）",
                        }
                    else:
                        logger.warning(f"[小红书] ⚠ 阶段2验证失败：无创作者平台访问权限")
                        # 即使创作者平台验证失败，如果主站验证成功，仍然返回部分成功
                        return {
                            "success": True,
                            "message": "验证成功（仅主站），建议重新获取创作者平台权限",
                            "warning": "无创作者平台访问权限，可能无法发布内容",
                        }

                except Exception as e:
                    logger.warning(f"[小红书] 创作者平台访问出错: {str(e)}")
                    # 如果创作者平台无法访问，但主站验证成功，仍然返回成功
                    return {
                        "success": True,
                        "message": "验证成功（仅主站），创作者平台暂时无法访问",
                        "warning": f"创作者平台访问异常: {str(e)}",
                    }
            else:
                # 不启用创作者平台验证
                return {
                    "success": True,
                    "message": "验证成功，Cookie 有效（仅主站验证）",
                }

        except Exception as e:
            error_msg = f"验证过程出错: {str(e)}"
            logger.error(f"[小红书] {error_msg}", exc_info=True)
            return {
                "success": False,
                "message": error_msg,
            }
        finally:
            # 清理资源
            logger.debug(f"[小红书] 清理资源...")
            if self.browser:
                await self.browser.close()
                logger.debug(f"[小红书] ✓ 浏览器已关闭")
            if self.playwright:
                await self.playwright.stop()
                logger.debug(f"[小红书] ✓ Playwright 已停止")
            logger.info(f"[小红书] ===== Cookie 验证结束 =====\n")

    async def _check_creator_platform_access(self) -> bool:
        """检查创作者平台访问权限

        Returns:
            True 表示可以访问创作者平台，False 表示无权限
        """
        try:
            assert self.page is not None

            current_url = self.page.url
            page_title = await self.page.title()

            logger.debug(f"[小红书] 当前创作者平台 URL: {current_url}")
            logger.debug(f"[小红书] 当前创作者平台标题: {page_title}")

            # 等待页面稳定
            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                logger.debug(f"[小红书] 页面 networkidle 超时，继续执行")

            # 方式1: 检查 URL 是否跳转到登录页
            if "login" in current_url.lower():
                logger.warning(f"[小红书] URL 包含 'login'，跳转到登录页")
                return False

            # 方式2: 检查创作者平台特有的登录状态选择器
            # 创作者平台登录后会显示用户头像、昵称等
            creator_logged_in_selectors = [
                # 创作者平台顶部的用户信息区域
                '.creator-header .user-info',
                '.creator-nav .user-avatar',
                # 通用用户元素
                '.user-avatar',
                '.avatar',
                '[class*="user"]',
                '[class*="avatar"]',
                # 创作者平台主页特有元素（登录后可见）
                '.creator-home',
                '.publish-entry',
                '[class*="creator-home"]',
            ]

            for selector in creator_logged_in_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        logger.debug(f"[小红书] 检测到元素 '{selector}': 可见={is_visible}")
                        if is_visible:
                            # 获取元素文本内容
                            try:
                                text = await element.text_content()
                                logger.debug(f"[小红书] 元素文本: {text[:50] if text else 'empty'}")
                            except Exception:
                                pass

                            logger.info(f"[小红书] ✓ 检测到创作者平台登录元素 ({selector})")
                            return True
                except Exception as e:
                    logger.debug(f"[小红书] 查询选择器 '{selector}' 时出错: {e}")
                    continue

            # 方式3: 检查页面是否显示"登录"或"请登录"等提示
            login_indicators = [
                'text="登录"',
                'text="请登录"',
                'text="立即登录"',
                '.login-btn',
                '[class*="login"]',
            ]

            for selector in login_indicators:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            logger.warning(f"[小红书] 检测到登录提示元素: {selector}")
                            return False
                except Exception:
                    continue

            # 方式4: 检查页面标题或内容
            page_content = await self.page.content()
            # 如果页面包含创作者平台特有的内容，认为访问成功
            creator_indicators = ['创作中心', '数据管理', '内容管理', '发布']
            found_indicators = [ind for ind in creator_indicators if ind in page_content]

            if found_indicators:
                logger.info(f"[小红书] ✓ 检测到创作者平台内容标识: {found_indicators}")
                return True

            # 如果以上方式都没有明确结果，保守返回 False
            logger.warning(f"[小红书] 无法确定创作者平台访问状态，保守返回 False")
            return False

        except Exception as e:
            logger.error(f"[小红书] 检查创作者平台访问权限时出错: {str(e)}", exc_info=True)
            return False

    async def check_login_status(self) -> bool:
        """检查小红书登录状态

        检测方式：
        1. 检查是否存在登录容器（存在则未登录）
        2. 检查是否存在用户信息元素（存在则已登录）

        Returns:
            True 表示已登录，False 表示未登录
        """
        config = Config.get("content")

        try:
            # 确保页面已初始化
            assert self.page is not None

            current_url = self.page.url
            page_title = await self.page.title()

            logger.debug(f"[小红书] check_login_status 开始")
            logger.debug(f"[小红书] 当前页面 URL: {current_url}")
            logger.debug(f"[小红书] 当前页面标题: {page_title}")

            # 获取 Cookie 信息
            cookies = await self.page.context.cookies()
            cookie_names = [c.get('name') for c in cookies]
            logger.debug(f"[小红书] 当前页面 Cookie 数量: {len(cookies)}")
            logger.debug(f"[小红书] Cookie 名称列表: {cookie_names}")

            # 检查关键 Cookie 是否存在
            critical_cookies = ['a1', 'web_session', 'webId']
            missing_cookies = [name for name in critical_cookies if name not in cookie_names]
            if missing_cookies:
                logger.warning(f"[小红书] ⚠ 缺少关键 Cookie: {missing_cookies}")
            else:
                logger.debug(f"[小红书] ✓ 所有关键 Cookie 都存在")

            # 等待页面稳定
            logger.debug(f"[小红书] 等待页面加载完成...")
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.debug(f"[小红书] ✓ 页面加载完成")

            # 获取页面 HTML 内容的前 500 个字符用于调试
            try:
                page_html = await self.page.evaluate("() => document.documentElement.outerHTML.substring(0, 500)")
                logger.debug(f"[小红书] 页面 HTML 前 500 字符:\n{page_html}")
            except Exception as e:
                logger.debug(f"[小红书] 无法获取页面 HTML: {e}")

            # 尝试多种选择器来检测登录状态
            login_selectors = [
                config.xiaohongshu_login_selector,
                '.login-container',
                '.login-wrapper',
                '[class*="login"]',
            ]

            logged_in_selectors = [
                config.xiaohongshu_logged_in_selector,
                '.user-avatar',
                '.avatar',
                '.user-info',
                '[class*="user"]',
                '[class*="avatar"]',
                '.main-container .user',
                '.header-user',
            ]

            # 方式 1: 检查是否存在登录容器（存在则未登录）
            logger.debug(f"[小红书] ========== 方式1: 检查登录容器（存在则未登录） ==========")
            logger.debug(f"[小红书] 尝试的选择器: {login_selectors}")

            for selector in login_selectors:
                try:
                    logger.debug(f"[小红书] 尝试选择器: {selector}")
                    login_container = await self.page.query_selector(selector)
                    if login_container:
                        is_visible = await login_container.is_visible()
                        logger.debug(f"[小红书] ✓ 元素存在，可见性: {is_visible}")
                        if is_visible:
                            logger.debug(f"[小红书] ✗ 检测到登录容器可见 ({selector})，判定为未登录")
                            # 获取元素的文本内容
                            try:
                                text_content = await login_container.text_content()
                                logger.debug(f"[小红书] 登录容器文本内容: {text_content[:100] if text_content else 'empty'}")
                            except:
                                pass
                            return False
                    else:
                        logger.debug(f"[小红书] ✗ 元素不存在")
                except Exception as e:
                    logger.debug(f"[小红书] 查询选择器 {selector} 时出错: {e}")

            # 方式 2: 检查是否存在用户信息元素（存在则已登录）
            logger.debug(f"[小红书] ========== 方式2: 检查用户信息元素（存在则已登录） ==========")
            logger.debug(f"[小红书] 尝试的选择器: {logged_in_selectors}")

            for selector in logged_in_selectors:
                try:
                    logger.debug(f"[小红书] 尝试选择器: {selector}")
                    user_element = await self.page.query_selector(selector)
                    if user_element:
                        is_visible = await user_element.is_visible()
                        logger.debug(f"[小红书] ✓ 元素存在，可见性: {is_visible}")
                        if is_visible:
                            logger.debug(f"[小红书] ✓✓ 检测到用户元素可见 ({selector})，判定为已登录")
                            # 获取元素的文本内容
                            try:
                                text_content = await user_element.text_content()
                                logger.debug(f"[小红书] 用户元素文本内容: {text_content[:100] if text_content else 'empty'}")
                            except:
                                pass
                            return True
                    else:
                        logger.debug(f"[小红书] ✗ 元素不存在")
                except Exception as e:
                    logger.debug(f"[小红书] 查询选择器 {selector} 时出错: {e}")

            # 检查 URL 是否包含登录相关的关键词
            login_keywords = ['login', 'signin', 'auth']
            for keyword in login_keywords:
                if keyword in current_url.lower():
                    logger.warning(f"[小红书] URL 包含登录关键词 '{keyword}'，判定为未登录")
                    return False

            logger.warning(f"[小红书] ========== 所有检测方式均未通过，判定为未登录 ==========")
            logger.warning(f"[小红书] 页面 URL: {current_url}")
            logger.warning(f"[小红书] 页面标题: {page_title}")
            logger.warning(f"[小红书] Cookie 数量: {len(cookies)}")
            logger.warning(f"[小红书] Cookie 名称: {cookie_names}")
            return False

        except Exception as e:
            # 发生异常时，保守处理，认为未登录
            logger.error(f"[小红书] 检查登录状态时出错: {str(e)}", exc_info=True)
            return False

    async def fill_article_content(self) -> None:
        """填写文章内容

        小红书长文发布流程：
        1. 点击"写长文" TAB
        2. 点击"新的创作"按钮
        3. 等待富文本编辑器加载
        4. 填写标题
        5. 填写正文
        """
        config = Config.get("content")

        assert self.page is not None
        assert self.article_data is not None, "article_data 不能为 None"

        # 等待页面稳定
        logger.info("[小红书] 等待页面稳定...")
        await asyncio.sleep(2)

        # 当前页面 URL
        current_url = self.page.url
        page_title = await self.page.title()
        logger.debug(f"[小红书] 当前页面 URL: {current_url}")
        logger.debug(f"[小红书] 当前页面标题: {page_title}")

        # 1. 点击"写长文" TAB
        logger.info("[小红书] ========== 点击写长文 TAB ==========")
        try:
            long_article_tab = await self.page.wait_for_selector(
                'text="写长文"',
                timeout=10000,
            )
            await long_article_tab.click()
            await asyncio.sleep(1)
            logger.info("[小红书] ✓ 已点击写长文 TAB")
        except Exception as e:
            logger.warning(f"[小红书] 点击写长文 TAB 失败: {e}，可能已在正确页面")

        # 2. 点击"新的创作"按钮
        logger.info("[小红书] ========== 点击新的创作按钮 ==========")
        try:
            new_article_btn = await self.page.wait_for_selector(
                'button:has-text("新的创作"), .rich-editor-container .left:has-text("新的创作")',
                timeout=10000,
            )
            await new_article_btn.click()
            await asyncio.sleep(2)
            logger.info("[小红书] ✓ 已点击新的创作按钮")
        except Exception as e:
            logger.warning(f"[小红书] 点击新的创作按钮失败: {e}，可能已在编辑页面")

        # 3. 等待富文本编辑器加载
        logger.info("[小红书] ========== 等待富文本编辑器加载 ==========")
        try:
            # 等待富文本编辑器标题输入框出现
            title_textarea = await self.page.wait_for_selector(
                'textarea.d-text[placeholder*="输入标题"]',
                timeout=15000,
            )
            logger.info("[小红书] ✓ 富文本编辑器已加载")
            await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"[小红书] 等待富文本编辑器超时: {e}")

        # 4. 填写标题
        logger.info("[小红书] ========== 开始填写标题 ==========")
        title = self.article_data.get("title", "")
        if title:
            # 富文本编辑器的标题输入框是 textarea
            try:
                title_input = await self.page.wait_for_selector(
                    'textarea.d-text[placeholder*="输入标题"]',
                    timeout=10000,
                )
                await title_input.click()
                await asyncio.sleep(0.5)
                await title_input.fill(title)
                logger.info(f"[小红书] ✓ 标题已填写: {title}")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[小红书] ✗ 填写标题失败: {e}")
                raise
        else:
            logger.warning("[小红书] ⚠ 未提供标题")

        # 5. 填写正文
        logger.info("[小红书] ========== 开始填写正文 ==========")
        content = self.article_data.get("content", "")
        if content:
            # 富文本编辑器使用 ProseMirror
            logger.info("[小红书] 查找正文编辑区域...")
            try:
                editor = await self.page.wait_for_selector(
                    'div.ProseMirror[contenteditable="true"]',
                    timeout=10000,
                )
                await editor.click()
                await asyncio.sleep(1)
                logger.info("[小红书] ✓ 已点击编辑区域")

                # 清空现有内容
                logger.info("[小红书] 清空现有内容...")
                await self.page.keyboard.press("Control+A")
                await asyncio.sleep(0.3)
                await self.page.keyboard.press("Delete")
                await asyncio.sleep(0.5)
                logger.info("[小红书] ✓ 内容已清空")

                # 使用 Clipboard API 粘贴 HTML 内容
                logger.info(f"[小红书] 使用剪贴板粘贴正文，长度: {len(content)} 字符")

                # 检查内容是否包含 HTML 标签
                has_html = bool(re.search(r'<[^>]+>', content))
                if has_html:
                    logger.info("[小红书] 检测到 HTML 标签，使用 HTML 格式粘贴")

                    # 转义 HTML 中的特殊字符，防止 JavaScript 注入
                    # 只保留基本的 HTML 标签（h2, h3, h4, p, strong, em, ul, ol, li, br）
                    # 其他标签和属性将被移除
                    safe_html = self._sanitize_html(content)

                    # 使用 Clipboard API 设置 HTML 内容并粘贴
                    await self.page.evaluate(
                        """(htmlContent) => {
                        const clipboardItem = new ClipboardItem({
                            'text/html': new Blob([htmlContent], { type: 'text/html' }),
                            'text/plain': new Blob([htmlContent], { type: 'text/plain' })
                        });
                        navigator.clipboard.write([clipboardItem]);
                    }""",
                        safe_html,
                    )
                    logger.info("[小红书] ✓ HTML 内容已写入剪贴板")
                else:
                    logger.info("[小红书] 纯文本内容，使用纯文本格式粘贴")
                    # 纯文本内容直接写入剪贴板
                    await self.page.evaluate(
                        """(textContent) => {
                        navigator.clipboard.writeText(textContent);
                    }""",
                        content,
                    )
                    logger.info("[小红书] ✓ 纯文本内容已写入剪贴板")

                # 模拟人工操作：添加短暂延迟后粘贴
                await asyncio.sleep(random.uniform(1.0, 2.0))

                # 执行粘贴操作
                logger.info("[小红书] 执行粘贴操作...")
                await self.page.keyboard.press("Control+V")
                await asyncio.sleep(2)
                logger.info("[小红书] ✓ 正文粘贴完成")

            except Exception as e:
                logger.error(f"[小红书] ✗ 正文输入失败: {type(e).__name__}: {str(e)}")
                raise
        else:
            logger.warning("[小红书] ⚠ 未提供正文内容")

        # 5. 添加标签（可选）
        logger.info("[小红书] ========== 开始添加标签 ==========")
        tags = self.article_data.get("tags", [])
        if tags:
            await self._add_tags(tags[: config.xiaohongshu_max_tags])
            logger.info(f"[小红书] ✓ 已添加 {len(tags)} 个标签")
        else:
            logger.debug("[小红书] 未提供标签")

        # 滚动到底部确保所有内容加载
        await asyncio.sleep(2)
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def submit_article(self) -> PublishResult:
        """提交文章

        小红书长文发布流程：
        1. 点击"一键排版"按钮（格式化内容并进入下一步）
        2. 等待页面跳转/加载
        3. 查找并点击发布按钮
        4. 等待发布完成并获取结果

        Returns:
            发布结果，包含平台文章ID和链接
        """
        assert self.page is not None, "页面未初始化"

        try:
            # 1. 先点击"一键排版"按钮（这是进入下一步的按钮）
            logger.info("[小红书] ========== 查找'一键排版'按钮 ==========")
            try:
                format_button_selectors = [
                    'button.next-btn:has-text("一键排版")',
                    'button.next-btn',
                    'button:has-text("一键排版")',
                    'button:has-text("下一步")',
                ]

                format_button = None
                for selector in format_button_selectors:
                    try:
                        format_button = await self.page.wait_for_selector(
                            selector, timeout=5000, state="visible"
                        )
                        if format_button:
                            logger.info(f"[小红书] ✓ 找到按钮: {selector}")
                            break
                    except Exception:
                        logger.debug(f"[小红书] 按钮选择器未找到: {selector}")
                        continue

                if format_button:
                    logger.info("[小红书] 点击'一键排版'按钮...")
                    await format_button.click()
                    logger.info("[小红书] ✓ 已点击'一键排版'按钮")

                    # 等待 5-10 秒随机时间（模拟人工操作）
                    wait_time = random.uniform(5, 10)
                    logger.info(f"[小红书] 等待 {wait_time:.1f} 秒（模拟人工操作）...")
                    await asyncio.sleep(wait_time)

                    # 检查页面是否发生变化（跳转到模板选择页面）
                    current_url = self.page.url
                    logger.debug(f"[小红书] 当前URL: {current_url}")

                    # 等待模板选择页面加载
                    logger.info("[小红书] 等待模板选择页面加载...")
                    try:
                        template_page = await self.page.wait_for_selector(
                            '.setting-container.show, .template-list',
                            timeout=10000,
                        )
                        if template_page:
                            logger.info("[小红书] ✓ 模板选择页面已加载")

                            # 默认已选中"灵感备忘"模板，直接点击"下一步"按钮
                            logger.info("[小红书] ========== 点击'下一步'按钮 ==========")
                            next_button_selectors = [
                                'button.submit:has-text("下一步")',
                                'button:has-text("下一步")',
                                'button.submit',
                                '.footer button.submit',
                            ]

                            next_button = None
                            for selector in next_button_selectors:
                                try:
                                    next_button = await self.page.wait_for_selector(
                                        selector, timeout=5000, state="visible"
                                    )
                                    if next_button:
                                        logger.info(f"[小红书] ✓ 找到下一步按钮: {selector}")
                                        break
                                except Exception:
                                    logger.debug(f"[小红书] 下一步按钮选择器未找到: {selector}")
                                    continue

                            if next_button:
                                logger.info("[小红书] ========== 点击下一步按钮 ==========")
                                await next_button.click()
                                logger.info("[小红书] ✓ 已点击下一步按钮")

                                # 等待 5-10 秒随机时间（模拟人工操作）
                                wait_time = random.uniform(5, 10)
                                logger.info(f"[小红书] 等待 {wait_time:.1f} 秒（模拟人工操作）...")
                                await asyncio.sleep(wait_time)

                                # 等待最终编辑页面加载
                                logger.info("[小红书] ========== 等待最终编辑页面加载 ==========")
                                page_loaded = await self._wait_for_final_page()

                                if not page_loaded:
                                    logger.error("[小红书] 最终编辑页面加载超时")
                                    return PublishResult(
                                        success=False,
                                        message="最终编辑页面加载超时",
                                    )

                                # 填写文章描述
                                logger.info("[小红书] ========== 填写文章描述 ==========")
                                await self._fill_summary()

                                # 等待 5-10 秒随机时间（模拟人工操作）
                                wait_time = random.uniform(5, 10)
                                logger.info(f"[小红书] 等待 {wait_time:.1f} 秒（模拟人工操作）...")
                                await asyncio.sleep(wait_time)

                                # 点击原创声明开关
                                logger.info("[小红书] ========== 点击原创声明开关 ==========")
                                await self._click_original_switch()

                                # 等待 5-10 秒随机时间（模拟人工操作）
                                wait_time = random.uniform(5, 10)
                                logger.info(f"[小红书] 等待 {wait_time:.1f} 秒（模拟人工操作）...")
                                await asyncio.sleep(wait_time)

                                # 点击发布按钮并获取结果
                                logger.info("[小红书] ========== 点击发布按钮 ==========")
                                result = await self._click_final_publish()

                                return result
                            else:
                                logger.warning("[小红书] 未找到'下一步'按钮，可能已在后续页面")
                                # 尝试直接在当前页面操作
                                logger.info("[小红书] ========== 尝试在当前页面继续操作 ==========")

                                # 等待最终编辑页面加载
                                page_loaded = await self._wait_for_final_page()
                                if page_loaded:
                                    # 填写文章描述
                                    await self._fill_summary()
                                    await asyncio.sleep(random.uniform(5, 10))
                                    # 点击原创声明开关
                                    await self._click_original_switch()
                                    await asyncio.sleep(random.uniform(5, 10))
                                    # 点击发布按钮
                                    result = await self._click_final_publish()
                                    return result

                            # 检查是否切换到"封面设置"标签页
                            logger.info("[小红书] 检查页面状态...")
                            await asyncio.sleep(1)
                    except Exception:
                        logger.warning("[小红书] 未检测到模板选择页面，可能已进入发布流程")
                        # 尝试等待最终编辑页面
                        logger.info("[小红书] ========== 尝试等待最终编辑页面 ==========")
                        page_loaded = await self._wait_for_final_page()
                        if page_loaded:
                            # 填写文章描述
                            await self._fill_summary()
                            await asyncio.sleep(random.uniform(5, 10))
                            # 点击原创声明开关
                            await self._click_original_switch()
                            await asyncio.sleep(random.uniform(5, 10))
                            # 点击发布按钮
                            result = await self._click_final_publish()
                            return result

                else:
                    logger.warning("[小红书] ⚠ 未找到'一键排版'按钮，尝试直接查找发布页面")
                    # 尝试等待最终编辑页面
                    page_loaded = await self._wait_for_final_page()
                    if page_loaded:
                        # 填写文章描述
                        await self._fill_summary()
                        await asyncio.sleep(random.uniform(5, 10))
                        # 点击原创声明开关
                        await self._click_original_switch()
                        await asyncio.sleep(random.uniform(5, 10))
                        # 点击发布按钮
                        result = await self._click_final_publish()
                        return result

            except Exception as e:
                logger.warning(f"[小红书] 点击'一键排版'按钮失败: {e}，尝试等待最终编辑页面")
                # 最后尝试：直接等待最终编辑页面
                page_loaded = await self._wait_for_final_page()
                if page_loaded:
                    # 填写文章描述
                    await self._fill_summary()
                    await asyncio.sleep(random.uniform(5, 10))
                    # 点击原创声明开关
                    await self._click_original_switch()
                    await asyncio.sleep(random.uniform(5, 10))
                    # 点击发布按钮
                    result = await self._click_final_publish()
                    return result

            # 如果所有尝试都失败，返回错误
            logger.error("[小红书] ✗ 无法进入最终编辑页面，发布失败")
            return PublishResult(
                success=False,
                message="无法进入最终编辑页面，发布流程可能已改变",
            )

        except Exception as e:
            logger.error(f"[小红书] ✗ 提交文章时出错: {str(e)}", exc_info=True)
            return PublishResult(
                success=False,
                message=f"提交文章时出错: {str(e)}",
            )

    async def _wait_for_final_page(self) -> bool:
        """等待最终编辑页面加载

        Returns:
            True 表示页面加载成功，False 表示超时
        """
        assert self.page is not None

        try:
            logger.debug("[小红书] 等待最终编辑页面加载...")
            logger.debug(f"[小红书] 当前 URL: {self.page.url}")

            # 等待页面元素出现
            final_page_selectors = [
                '.edit-container',
                '.publish-page-content-base',
                '.editor-content',
            ]

            for selector in final_page_selectors:
                try:
                    element = await self.page.wait_for_selector(
                        selector, timeout=10000, state="visible"
                    )
                    if element:
                        logger.info(f"[小红书] ✓ 最终编辑页面已加载 ({selector})")
                        await asyncio.sleep(2)  # 额外等待页面稳定
                        return True
                except Exception:
                    logger.debug(f"[小红书] 选择器未找到: {selector}")
                    continue

            logger.warning("[小红书] 最终编辑页面加载超时")
            return False

        except Exception as e:
            logger.error(f"[小红书] 等待最终编辑页面时出错: {str(e)}", exc_info=True)
            return False

    async def _fill_summary(self) -> None:
        """填写文章描述"""
        assert self.page is not None
        assert self.article_data is not None, "article_data 不能为 None"

        summary = self.article_data.get("summary", "").strip()

        if not summary:
            logger.info("[小红书] 文章描述为空，跳过填写")
            return

        logger.info(f"[小红书] 准备填写文章描述，长度: {len(summary)} 字符")

        try:
            # 查找描述输入框
            editor_selectors = [
                '.ProseMirror[contenteditable="true"]',
                '.editor-content .ProseMirror',
                '.tiptap-container .ProseMirror',
            ]

            editor = None
            for selector in editor_selectors:
                try:
                    editor = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if editor:
                        logger.info(f"[小红书] ✓ 找到描述输入框: {selector}")
                        break
                except Exception:
                    logger.debug(f"[小红书] 描述输入框选择器未找到: {selector}")
                    continue

            if not editor:
                logger.warning("[小红书] ⚠ 未找到描述输入框，跳过填写")
                return

            # 点击获取焦点
            await editor.click()
            await asyncio.sleep(0.5)
            logger.debug("[小红书] ✓ 已点击输入框")

            # 清空现有内容
            logger.debug("[小红书] 清空现有内容...")
            await self.page.keyboard.press("Control+A")
            await asyncio.sleep(0.3)
            await self.page.keyboard.press("Delete")
            await asyncio.sleep(0.5)
            logger.debug("[小红书] ✓ 内容已清空")

            # 使用剪贴板粘贴内容
            logger.info(f"[小红书] 使用剪贴板粘贴描述，长度: {len(summary)} 字符")

            # 检查内容是否包含 HTML 标签
            has_html = bool(re.search(r'<[^>]+>', summary))
            if has_html:
                logger.info("[小红书] 检测到 HTML 标签，清理后使用纯文本粘贴")
                # 清理 HTML，保留纯文本
                clean_text = re.sub(r'<[^>]+>', '', summary)
                clean_text = clean_text.strip()
                await self.page.evaluate(
                    """(textContent) => {
                    navigator.clipboard.writeText(textContent);
                }""",
                    clean_text,
                )
            else:
                logger.info("[小红书] 纯文本内容，直接粘贴")
                await self.page.evaluate(
                    """(textContent) => {
                    navigator.clipboard.writeText(textContent);
                }""",
                    summary,
                )

            logger.info("[小红书] ✓ 描述内容已写入剪贴板")

            # 模拟人工操作：添加短暂延迟后粘贴
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # 执行粘贴操作
            logger.info("[小红书] 执行粘贴操作...")
            await self.page.keyboard.press("Control+V")
            await asyncio.sleep(2)
            logger.info("[小红书] ✓ 文章描述填写完成")

        except Exception as e:
            logger.error(f"[小红书] ✗ 填写文章描述失败: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    async def _click_original_switch(self) -> None:
        """点击原创声明开关并处理弹窗"""
        assert self.page is not None

        try:
            logger.info("[小红书] ========== 点击原创声明开关 ==========")

            # 查找原创声明开关 - 优先点击开关本身（.d-switch）
            switch_selectors = [
                '.custom-switch-wrapper .d-switch',  # 开关本身
                'd-switch',  # 直接查找开关组件
                '.custom-switch-wrapper .custom-switch-card',  # 最后尝试整个卡片
            ]

            switch_element = None
            for selector in switch_selectors:
                try:
                    switch_element = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if switch_element:
                        logger.info(f"[小红书] ✓ 找到原创声明开关: {selector}")
                        break
                except Exception:
                    logger.debug(f"[小红书] 原创声明开关选择器未找到: {selector}")
                    continue

            if not switch_element:
                logger.warning("[小红书] ⚠ 未找到原创声明开关，跳过")
                return

            # 直接点击开关（不管当前状态）
            logger.info("[小红书] 点击原创声明开关...")
            await switch_element.click()
            await asyncio.sleep(1)

            # ========== 处理原创声明弹窗 ==========
            logger.info("[小红书] 等待原创声明弹窗出现...")

            modal_selectors = [
                '.d-modal.creator-modal-style',
                '.d-modal.d-modal-centered.creator-modal-style',
                '.creator-modal-style',
            ]

            modal = None
            for selector in modal_selectors:
                try:
                    modal = await self.page.wait_for_selector(
                        selector, timeout=8000, state="visible"
                    )
                    if modal:
                        logger.info(f"[小红书] ✓ 原创声明弹窗已出现: {selector}")
                        break
                except Exception:
                    logger.debug(f"[小红书] 弹窗选择器未找到: {selector}")
                    continue

            if not modal:
                logger.warning("[小红书] ⚠ 未检测到原创声明弹窗，继续执行")
                return

            # 等待一下让弹窗完全加载
            await asyncio.sleep(1)

            # 点击同意复选框
            logger.info("[小红书] 点击《原创声明须知》同意复选框...")
            checkbox_selectors = [
                '.footer .d-checkbox.d-clickable',
                '.footer .d-grid.d-checkbox.d-clickable',
                '.d-checkbox.d-clickable',
            ]

            checkbox_clicked = False
            for selector in checkbox_selectors:
                try:
                    checkbox = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if checkbox:
                        await checkbox.click()
                        logger.info(f"[小红书] ✓ 已点击同意复选框: {selector}")
                        checkbox_clicked = True
                        break
                except Exception:
                    logger.debug(f"[小红书] 复选框选择器未找到: {selector}")
                    continue

            if not checkbox_clicked:
                logger.warning("[小红书] ⚠ 未找到同意复选框")

            # 等待"声明原创"按钮启用
            logger.info("[小红书] 等待'声明原创'按钮启用...")
            await asyncio.sleep(1)

            # 点击"声明原创"按钮
            logger.info("[小红书] 点击'声明原创'按钮...")
            confirm_button_selectors = [
                '.footer button.bg-red:not(.disabled)',
                '.footer button.bg-red',
                'button.bg-red:has-text("声明原创")',
            ]

            button_clicked = False
            for selector in confirm_button_selectors:
                try:
                    confirm_button = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if confirm_button:
                        # 检查按钮是否可用
                        is_disabled = await confirm_button.get_attribute("disabled")
                        if is_disabled != "true":
                            await confirm_button.click()
                            logger.info(f"[小红书] ✓ 已点击'声明原创'按钮: {selector}")
                            button_clicked = True
                            break
                        else:
                            logger.debug(f"[小红书] 按钮仍被禁用: {selector}")
                except Exception:
                    logger.debug(f"[小红书] 确认按钮选择器未找到: {selector}")
                    continue

            if not button_clicked:
                logger.warning("[小红书] ⚠ 未找到可用的'声明原创'按钮")

            # 等待弹窗关闭
            logger.info("[小红书] 等待弹窗关闭...")
            await asyncio.sleep(2)

            # 验证弹窗是否关闭
            try:
                modal_check = await self.page.query_selector('.d-modal.creator-modal-style')
                if not modal_check:
                    logger.info("[小红书] ✓ 弹窗已关闭")
                else:
                    logger.warning("[小红书] ⚠ 弹窗可能未关闭，继续执行")
            except Exception:
                logger.debug("[小红书] 无法验证弹窗状态")

            # 验证原创声明是否开启
            try:
                switch_span = await self.page.query_selector('.custom-switch-wrapper .d-switch-simulator')
                if switch_span:
                    class_list = await switch_span.get_attribute('class') or ''
                    if 'checked' in class_list:
                        logger.info("[小红书] ✓ 原创声明已开启")
                    else:
                        logger.warning("[小红书] ⚠ 原创声明开关状态未改变，可能需要手动操作")
            except Exception:
                logger.debug("[小红书] 无法验证开关状态")

        except Exception as e:
            logger.warning(f"[小红书] 点击原创声明开关时出错: {str(e)}，继续执行")

    async def _click_final_publish(self) -> PublishResult:
        """点击最终发布按钮

        Returns:
            发布结果
        """
        assert self.page is not None

        try:
            logger.info("[小红书] 查找发布按钮...")

            # 查找发布按钮
            publish_button_selectors = [
                '.publish-page-publish-btn button.bg-red:has-text("发布")',
                '.publish-page-publish-btn button.bg-red',
                'button.bg-red:has-text("发布")',
                'button:has-text("发布")',
            ]

            publish_button = None
            for selector in publish_button_selectors:
                try:
                    publish_button = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if publish_button:
                        # 检查按钮是否可用
                        is_disabled = await publish_button.get_attribute("disabled")
                        if is_disabled != "true":
                            logger.info(f"[小红书] ✓ 找到发布按钮: {selector}")
                            break
                        else:
                            logger.debug(f"[小红书] 发布按钮不可用: {selector}")
                            publish_button = None
                except Exception:
                    logger.debug(f"[小红书] 发布按钮选择器未找到: {selector}")
                    continue

            if not publish_button:
                logger.error("[小红书] 未找到可用的发布按钮")
                return PublishResult(
                    success=False,
                    message="未找到可用的发布按钮",
                )

            # 点击发布按钮
            logger.info("[小红书] 点击发布按钮...")
            await publish_button.click()
            logger.info("[小红书] ✓ 已点击发布按钮")

            # 等待发布完成（10-15秒随机延迟）
            wait_time = random.uniform(10, 15)
            logger.info(f"[小红书] 等待 {wait_time:.1f} 秒（模拟人工操作）...")
            await asyncio.sleep(wait_time)

            logger.info("[小红书] ✓ 发布完成")
            return PublishResult(
                success=True,
                message="已发布",
            )

        except Exception as e:
            logger.error(f"[小红书] ✗ 点击发布按钮时出错: {str(e)}", exc_info=True)
            return PublishResult(
                success=False,
                message=f"点击发布按钮时出错: {str(e)}",
            )

    async def _upload_images(self, images: list[str]) -> None:
        """上传图片

        Args:
            images: 图片路径列表
        """
        assert self.page is not None

        logger.info(f"[小红书] 准备上传 {len(images)} 张图片")

        # 查找文件输入框
        try:
            # 小红书的文件输入框
            file_input = await self.page.wait_for_selector(
                'input[type="file"]',
                timeout=10000,
            )

            # 上传第一张图片（作为封面）
            if images and len(images) > 0:
                first_image = images[0]
                logger.info(f"[小红书] 上传封面图片: {first_image}")

                # 使用 set_input_files 上传文件
                await file_input.set_input_files(first_image)
                await asyncio.sleep(2)  # 等待上传处理

                logger.info("[小红书] ✓ 封面图片上传完成")

                # 如果有更多图片，继续上传
                if len(images) > 1:
                    logger.info(f"[小红书] 继续上传剩余 {len(images) - 1} 张图片...")
                    for i, image_path in enumerate(images[1:], 1):
                        logger.info(f"[小红书] 上传第 {i + 1} 张图片: {image_path}")

                        # 重新查找文件输入框（可能需要重新点击上传按钮）
                        try:
                            file_input = await self.page.wait_for_selector(
                                'input[type="file"]',
                                timeout=5000,
                            )
                            await file_input.set_input_files(image_path)
                            await asyncio.sleep(1)  # 等待上传处理

                            logger.info(f"[小红书] ✓ 第 {i + 1} 张图片上传完成")
                        except Exception as e:
                            logger.warning(f"[小红书] 第 {i + 1} 张图片上传失败: {e}")

        except Exception as e:
            logger.error(f"[小红书] ✗ 图片上传失败: {str(e)}", exc_info=True)
            raise

    async def _fill_title(self, title: str) -> None:
        """填写标题

        Args:
            title: 标题文本
        """
        assert self.page is not None

        try:
            # 查找标题输入框（富文本编辑器优先）
            title_selectors = [
                # 富文本编辑器使用 textarea
                'textarea.d-text[placeholder*="输入标题"]',
                'textarea[placeholder*="标题"]',
                # 图文上传使用 input
                'input[placeholder*="填写标题"]',
                'input[placeholder*="标题"]',
                'input.title-input',
                'input[type="text"]',
            ]

            title_input = None
            for selector in title_selectors:
                try:
                    title_input = await self.page.wait_for_selector(
                        selector, timeout=3000, state="visible"
                    )
                    if title_input:
                        logger.info(f"[小红书] ✓ 找到标题输入框: {selector}")
                        break
                except Exception:
                    logger.debug(f"[小红书] 标题输入框选择器未找到: {selector}")
                    continue

            if title_input:
                await title_input.click()
                await asyncio.sleep(0.5)
                # 清空并输入标题
                await title_input.fill("")
                await title_input.type(title, delay=100)
                logger.info(f"[小红书] ✓ 标题已填写: {title}")
            else:
                logger.warning("[小红书] ⚠ 未找到标题输入框，跳过标题填写")

        except Exception as e:
            logger.error(f"[小红书] ✗ 填写标题失败: {str(e)}", exc_info=True)
            raise

    def _sanitize_html(self, html_content: str) -> str:
        """清理 HTML 内容，仅保留安全的标签

        保留的标签：h2, h3, h4, h5, h6, p, strong, b, em, i, u, ul, ol, li, br, span
        移除所有属性（包括 style, class 等），仅保留标签结构

        Args:
            html_content: 原始 HTML 内容

        Returns:
            清理后的 HTML 内容
        """
        # 允许的标签白名单
        allowed_tags = {
            "h2", "h3", "h4", "h5", "h6",
            "p", "div",
            "strong", "b",
            "em", "i",
            "u",
            "ul", "ol", "li",
            "br",
            "span",
            "pre", "code",
        }

        # 移除 script 标签及其内容
        html_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

        # 移除 style 标签及其内容
        html_content = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

        # 移除所有 HTML 标签的属性
        # 对于允许的标签，保留标签但移除属性
        # 对于不允许的标签，移除标签但保留内容
        def clean_tag(match):
            tag_name = match.group(1).lower()
            is_closing = match.group(0).startswith('</')
            is_self_closing = match.group(0).endswith('/>')

            if tag_name in allowed_tags:
                if is_closing:
                    return f'</{tag_name}>'
                elif is_self_closing:
                    return f'<{tag_name} />'
                else:
                    return f'<{tag_name}>'
            else:
                # 不允许的标签，移除标签符号
                return ''

        # 处理开始标签和自闭合标签
        html_content = re.sub(r'<\/?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*\/?>', clean_tag, html_content)

        # 清理多余的空白行
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)

        return html_content.strip()

    async def _add_tags(self, tags: list[str]) -> None:
        """添加标签

        Args:
            tags: 标签列表
        """
        assert self.page is not None

        try:
            # 查找标签输入框
            tag_selectors = [
                'input[placeholder*="#话题"]',
                'input[placeholder*="标签"]',
                'input.tag-input',
            ]

            tag_input = None
            for selector in tag_selectors:
                try:
                    tag_input = await self.page.wait_for_selector(
                        selector, timeout=3000, state="visible"
                    )
                    if tag_input:
                        logger.info(f"[小红书] ✓ 找到标签输入框: {selector}")
                        break
                except Exception:
                    logger.debug(f"[小红书] 标签输入框选择器未找到: {selector}")
                    continue

            if tag_input:
                for tag in tags:
                    # 清空并输入标签（小红书会自动添加 # 符号）
                    await tag_input.click()
                    await asyncio.sleep(0.3)
                    await tag_input.fill("")
                    await tag_input.type(tag, delay=50)
                    await asyncio.sleep(0.5)

                    # 按回车确认标签
                    await self.page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)

                logger.info(f"[小红书] ✓ 已添加 {len(tags)} 个标签")
            else:
                logger.warning("[小红书] ⚠ 未找到标签输入框，跳过标签添加")

        except Exception as e:
            logger.warning(f"[小红书] 添加标签失败: {str(e)}")
            # 标签是可选的，失败不抛出异常

    def _process_title(self, title: str, config) -> str:
        """处理标题长度

        小红书标题限制：最多 20 字（中文算 2 字节）

        Args:
            title: 原始标题
            config: 配置对象

        Returns:
            处理后的标题
        """
        max_length = config.xiaohongshu_max_title_length

        # 计算标题长度
        title_length = self._calc_xiaohongshu_title_length(title)

        if title_length <= max_length:
            return title

        # 标题过长，需要截断
        logger.warning(
            f"[小红书] 标题过长 ({title_length}/{max_length})，将进行截断"
        )

        # 逐字截断，直到满足长度要求
        result = ""
        for char in title:
            test_result = result + char
            if self._calc_xiaohongshu_title_length(test_result) <= max_length:
                result = test_result
            else:
                break

        logger.info(f"[小红书] 标题已截断: {title} -> {result}")
        return result

    def _calc_xiaohongshu_title_length(self, title: str) -> int:
        """计算小红书标题长度

        规则：
        - 非ASCII字符（中文）算 2 字节
        - ASCII字符算 1 字节
        - 最终结果向上取整除以 2

        Args:
            title: 标题文本

        Returns:
            标题长度（字）

        Examples:
            "你好" → 2 (4字节/2)
            "Hello" → 3 (5字节/2 向上取整)
        """
        byte_len = 0
        for char in title:
            if ord(char) > 127:
                byte_len += 2
            else:
                byte_len += 1
        return (byte_len + 1) // 2

    async def publish(self) -> PublishResult:
        """执行发布（带验证流程）

        发布流程：
        1. 启动浏览器，添加 Cookies
        2. 访问主站验证登录状态
        3. 访问创作者平台验证访问权限
        4. 打开发布页面进行发布

        Returns:
            发布结果对象
        """
        logger.info(f"[小红书] ========== 开始发布（带验证流程） ==========")

        try:
            from playwright.async_api import async_playwright

            # 获取配置
            config = Config.get("content")
            if config is None:
                logger.error(f"[小红书] Config.get('content') 返回 None")
                return PublishResult(
                    success=False,
                    message="配置未加载，请重启后端服务",
                )

            # 启动浏览器
            logger.info(f"[小红书] 正在启动 Playwright...")
            self.playwright = await async_playwright().start()

            logger.info(
                f"[小红书] 正在启动 Chromium 浏览器 (headless={config.playwright_headless})..."
            )
            self.browser = await self.playwright.chromium.launch(
                headless=config.playwright_headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            logger.info(f"[小红书] ✓ 浏览器启动成功")

            # 创建浏览器上下文
            logger.debug(f"[小红书] 创建浏览器上下文...")
            context = await self.browser.new_context(
                user_agent=self.user_agent or DEFAULT_USER_AGENT,
                viewport={
                    "width": config.playwright_width,
                    "height": config.playwright_height,
                },
            )
            self.page = await context.new_page()
            logger.debug(
                f"[小红书] ✓ 页面创建成功, viewport: {config.playwright_width}x{config.playwright_height}"
            )

            # 应用 playwright-stealth 反检测
            logger.debug(f"[小红书] 应用 playwright-stealth 反检测...")
            await stealth_async(self.page)

            # 设置默认超时时间
            self.page.set_default_timeout(config.playwright_timeout)

            # 添加 Cookies
            converted_cookies = self._convert_cookies()
            cookie_names = [c.get('name', '') for c in converted_cookies]
            logger.debug(f"[小红书] 添加 {len(converted_cookies)} 个 Cookie...")
            logger.debug(f"[小红书] Cookie 名称列表: {cookie_names}")
            await context.add_cookies(converted_cookies)
            logger.debug(f"[小红书] ✓ Cookie 添加完成")

            # 反检测：添加 Cookies 后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(
                    config.random_delay_min, config.random_delay_max
                )
                logger.debug(f"[小红书] ✓ 延迟 {delay:.2f} 秒")

            # ==================== 步骤1: 验证主站登录状态 ====================
            logger.info(f"[小红书] ========== 步骤1: 验证主站登录状态 ==========")
            main_site_url = config.xiaohongshu_verify_url
            logger.debug(f"[小红书] 访问主站: {main_site_url}")
            await self.page.goto(main_site_url)
            await self.page.wait_for_load_state("networkidle", timeout=10000)

            # 刷新页面
            if config.enable_page_refresh:
                logger.info(f"[小红书] 刷新主站页面...")
                delay = await self._random_delay(
                    config.page_refresh_delay_min, config.page_refresh_delay_max
                )
                await self.page.reload(wait_until="networkidle", timeout=10000)
                logger.debug(f"[小红书] ✓ 主站页面刷新完成")

            # 检查登录状态
            is_logged_in = await self.check_login_status()
            if not is_logged_in:
                logger.error(f"[小红书] ✗ 主站登录验证失败")
                return PublishResult(
                    success=False,
                    message="Cookie 已失效（主站验证失败），请重新验证",
                )
            logger.info(f"[小红书] ✓ 主站登录验证成功")

            # ==================== 步骤2: 验证创作者平台访问权限 ====================
            if config.xiaohongshu_enable_creator_verify:
                logger.info(f"[小红书] ========== 步骤2: 验证创作者平台访问权限 ==========")

                # 创建新标签页
                self.page = await context.new_page()
                creator_home_url = config.xiaohongshu_creator_verify_url
                logger.debug(f"[小红书] 访问创作者平台: {creator_home_url}")

                if config.human_behavior_enabled:
                    delay = await self._random_delay(1.0, 2.0)
                    await asyncio.sleep(delay)

                await self.page.goto(creator_home_url, timeout=30000)
                await asyncio.sleep(2)

                has_creator_access = await self._check_creator_platform_access()
                if not has_creator_access:
                    logger.warning(f"[小红书] ⚠ 创作者平台验证失败，继续尝试发布")
                else:
                    logger.info(f"[小红书] ✓ 创作者平台验证成功")

            # ==================== 步骤3: 打开发布页面 ====================
            logger.info(f"[小红书] ========== 步骤3: 打开发布页面 ==========")
            publish_url = await self.get_publish_url()
            logger.debug(f"[小红书] 发布页面 URL: {publish_url}")

            # 创建新标签页访问发布页面
            if config.human_behavior_enabled:
                delay = await self._random_delay(0.5, 1.5)
                await asyncio.sleep(delay)

            self.page = await context.new_page()
            logger.debug(f"[小红书] 正在访问发布页面...")
            await self.page.goto(publish_url, timeout=30000)
            await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            await asyncio.sleep(3)
            logger.debug(f"[小红书] ✓ 发布页面已就绪")

            # 检查是否跳转到登录页
            is_at_login_page = await self._check_if_at_login_page()
            if is_at_login_page:
                logger.warning(f"[小红书] Cookie 已失效，跳转到登录页")
                return PublishResult(
                    success=False,
                    message="Cookie 已失效，请重新验证",
                )

            # 反检测：随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(2.0, 3.0)
                logger.debug(f"[小红书] ✓ 延迟 {delay:.2f} 秒")

            # ==================== 步骤4: 填写内容并提交 ====================
            logger.info(f"[小红书] ========== 步骤4: 填写文章内容 ==========")
            try:
                await self.fill_article_content()
                logger.info(f"[小红书] ✓ 文章内容填写完成")
            except Exception as fill_error:
                logger.error(f"[小红书] ✗ 填写文章内容时出错: {type(fill_error).__name__}: {str(fill_error)}")
                return PublishResult(
                    success=False,
                    message=f"填写文章内容失败: {str(fill_error)}",
                )

            # 反检测：填写后随机延迟
            if config.human_behavior_enabled:
                delay = await self._random_delay(2.0, 4.0)
                logger.debug(f"[小红书] ✓ 延迟 {delay:.2f} 秒")

            # 提交文章
            logger.info(f"[小红书] 提交文章...")
            result = await self.submit_article()

            if result.success:
                logger.info(f"[小红书] ✓ 发布成功: {result.message}")
                if result.platform_url:
                    logger.info(f"[小红书] ✓ 文章链接: {result.platform_url}")
            else:
                logger.error(f"[小红书] ✗ 发布失败: {result.message}")

            return result

        except Exception as e:
            logger.error(f"[小红书] ========== 发布过程出错 ==========")
            logger.error(f"[小红书] 错误类型: {type(e).__name__}")
            logger.error(f"[小红书] 错误信息: {str(e)}")
            logger.error(f"[小红书] 当前页面 URL: {self.page.url if self.page else 'N/A'}")
            logger.error(f"[小红书] 详细堆栈:", exc_info=True)
            return PublishResult(
                success=False,
                message=f"发布过程出错: {type(e).__name__}: {str(e)}",
            )

        finally:
            # 清理资源
            logger.info(f"[小红书] ========== 清理资源 ==========")
            if self.browser:
                await self.browser.close()
                logger.info(f"[小红书] ✓ 浏览器已关闭")
            if self.playwright:
                await self.playwright.stop()
                logger.info(f"[小红书] ✓ Playwright 已停止")
            logger.info(f"[小红书] ===== 发布结束 =====\n")
