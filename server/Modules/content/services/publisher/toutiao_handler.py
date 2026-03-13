"""
今日头条平台处理器

支持文章发布到今日头条平台。
"""

import asyncio
import random
import re
from typing import Any

from loguru import logger

from Modules.common.libs.config.config import Config
from .base_platform_handler import (
    DEFAULT_USER_AGENT,
    BasePlatformHandler,
    PublishResult,
)


class ToutiaoHandler(BasePlatformHandler):
    """今日头条平台处理器"""

    @property
    def platform_name(self) -> str:
        """平台名称"""
        return "今日头条"

    @property
    def platform_domain(self) -> str:
        """平台域名"""
        return "www.toutiao.com"

    async def get_verify_url(self) -> str:
        """获取验证 URL"""
        config = Config.get("content")
        return config.toutiao_verify_url

    async def get_publish_url(self) -> str:
        """获取发布页面 URL"""
        config = Config.get("content")
        return config.toutiao_publish_url

    async def check_login_status(self) -> bool:
        """检查是否已登录

        Returns:
            True 表示已登录，False 表示未登录
        """
        try:
            assert self.page is not None

            config = Config.get("content")

            # 方法1: 检查已登录选择器（推荐）
            logged_in_selector = config.toutiao_logged_in_selector
            logged_in_element = await self.page.query_selector(logged_in_selector)
            if logged_in_element:
                logger.debug(f"[今日头条] ✓ 检测到已登录元素: {logged_in_selector}")
                return True

            # 方法2: 检查未登录选择器
            login_selector = config.toutiao_login_selector
            login_element = await self.page.query_selector(login_selector)
            if login_element:
                logger.debug(f"[今日头条] ✗ 检测到未登录元素: {login_selector}")
                return False

            # 方法3: 备用 - 检查登录按钮
            login_button = await self.page.query_selector("a.login-button")
            if login_button:
                logger.debug("[今日头条] ✗ 检测到登录按钮")
                return False

            # 方法4: 检查用户信息区域
            user_info = await self.page.query_selector(".user-info")
            if user_info:
                logger.debug("[今日头条] ✓ 检测到用户信息区域")
                return True

            logger.warning("[今日头条] ========== 所有检测方式均未通过，判定为未登录 ==========")
            return False

        except Exception as e:
            logger.error(f"[今日头条] 检查登录状态时出错: {str(e)}", exc_info=True)
            return False

    async def fill_article_content(self) -> None:
        """填写文章内容

        今日头条发布流程：
        1. 等待发布页面加载
        2. 填写标题
        3. 填写正文（ProseMirror编辑器）
        4. 选择封面为"无封面"
        5. 选择作品声明为"个人观点，仅供参考"
        6. 选择"头条首发"
        """
        config = Config.get("content")

        assert self.page is not None
        assert self.article_data is not None, "article_data 不能为 None"

        # 等待页面稳定
        logger.info("[今日头条] 等待页面稳定...")
        await asyncio.sleep(3)

        # 当前页面 URL
        current_url = self.page.url
        logger.debug(f"[今日头条] 当前页面 URL: {current_url}")

        # 1. 填写标题
        logger.info("[今日头条] ========== 开始填写标题 ==========")
        title = self.article_data.get("title", "").strip()
        if title:
            try:
                # 等待标题输入框出现
                title_selectors = [
                    'textarea[placeholder*="请输入文章标题"]',
                    '.publish-editor-title-inner textarea',
                    'div.publish-editor-title-inner textarea',
                ]

                title_input = None
                for selector in title_selectors:
                    try:
                        title_input = await self.page.wait_for_selector(
                            selector, timeout=5000, state="visible"
                        )
                        if title_input:
                            logger.info(f"[今日头条] ✓ 找到标题输入框: {selector}")
                            break
                    except Exception:
                        logger.debug(f"[今日头条] 标题输入框选择器未找到: {selector}")
                        continue

                if title_input:
                    await title_input.click()
                    await asyncio.sleep(0.5)

                    # 清空现有内容
                    await self.page.keyboard.press("Control+A")
                    await asyncio.sleep(0.2)
                    await self.page.keyboard.press("Backspace")
                    await asyncio.sleep(0.3)

                    # 逐字输入标题（模拟人类）
                    for char in title:
                        await self.page.keyboard.type(char)
                        await asyncio.sleep(random.uniform(0.01, 0.05))

                    logger.info(f"[今日头条] ✓ 标题已填写: {title}")
                    await asyncio.sleep(1)
                else:
                    logger.error("[今日头条] ✗ 未找到标题输入框")
                    raise Exception("未找到标题输入框")

            except Exception as e:
                logger.error(f"[今日头条] ✗ 填写标题失败: {e}")
                raise
        else:
            logger.warning("[今日头条] ⚠ 未提供标题")

        # 2. 填写正文
        logger.info("[今日头条] ========== 开始填写正文 ==========")
        content = self.article_data.get("content", "").strip()
        if content:
            try:
                # 等待正文编辑器出现（ProseMirror）
                editor_selectors = [
                    'div.publish-editor div.ProseMirror',
                    'div.ProseMirror[contenteditable="true"]',
                    '.publish-editor .ProseMirror',
                ]

                editor = None
                for selector in editor_selectors:
                    try:
                        editor = await self.page.wait_for_selector(
                            selector, timeout=10000, state="visible"
                        )
                        if editor:
                            logger.info(f"[今日头条] ✓ 找到正文编辑器: {selector}")
                            break
                    except Exception:
                        logger.debug(f"[今日头条] 正文编辑器选择器未找到: {selector}")
                        continue

                if not editor:
                    logger.error("[今日头条] ✗ 未找到正文编辑器")
                    raise Exception("未找到正文编辑器")

                await editor.click()
                await asyncio.sleep(1)
                logger.info("[今日头条] ✓ 已点击编辑区域")

                # 清空现有内容
                logger.info("[今日头条] 清空现有内容...")
                await self.page.keyboard.press("Control+A")
                await asyncio.sleep(0.3)
                await self.page.keyboard.press("Delete")
                await asyncio.sleep(0.5)
                logger.info("[今日头条] ✓ 内容已清空")

                # 将 Markdown 转换为 HTML
                html_content = self._markdown_to_html(content)
                logger.info(f"[今日头条] Markdown 转 HTML 完成，长度: {len(html_content)} 字符")

                # 使用 Clipboard API 粘贴 HTML 内容
                logger.info("[今日头条] 使用剪贴板粘贴 HTML 内容...")

                # 清理 HTML，只保留安全的标签
                safe_html = self._sanitize_html(html_content)

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
                logger.info("[今日头条] ✓ HTML 内容已写入剪贴板")

                # 模拟人工操作：添加短暂延迟后粘贴
                await asyncio.sleep(random.uniform(1.0, 2.0))

                # 执行粘贴操作
                logger.info("[今日头条] 执行粘贴操作...")
                await self.page.keyboard.press("Control+V")
                await asyncio.sleep(2)
                logger.info("[今日头条] ✓ 正文粘贴完成")

            except Exception as e:
                logger.error(f"[今日头条] ✗ 正文输入失败: {type(e).__name__}: {str(e)}")
                raise
        else:
            logger.warning("[今日头条] ⚠ 未提供正文内容")

        # 4. 选择封面为"无封面"
        logger.info("[今日头条] ========== 选择封面展示 ==========")
        try:
            # 等待封面选项区域出现
            await self.page.wait_for_selector('.article-cover-radio-group', timeout=5000)
            # 点击可见的label元素（不是隐藏的input）
            no_cover_label = await self.page.query_selector('.article-cover-radio-group label:nth-child(3)')
            if no_cover_label:
                await no_cover_label.click()
                logger.info("[今日头条] ✓ 已选择封面: 无封面")
            else:
                logger.debug("[今日头条] 未找到无封面选项")
        except Exception as e:
            logger.warning(f"[今日头条] 选择封面失败: {e}，继续执行")

        # 5. 选择作品声明为"个人观点，仅供参考"
        logger.info("[今日头条] ========== 选择作品声明 ==========")
        try:
            # 等待作品声明区域出现
            await self.page.wait_for_selector('.source-info-wrap', timeout=5000)
            # 点击可见的label元素（"个人观点，仅供参考"是第3个label）
            statement_label = await self.page.query_selector('.source-info-wrap label.byte-checkbox:nth-child(3)')
            if statement_label:
                # 先检查是否已选中（通过检查内部的input）
                checkbox = await statement_label.query_selector('input[type="checkbox"]')
                if checkbox:
                    is_checked = await checkbox.is_checked()
                    if not is_checked:
                        await statement_label.click()
                        logger.info("[今日头条] ✓ 已选择作品声明: 个人观点，仅供参考")
                    else:
                        logger.debug("[今日头条] 作品声明已选中")
            else:
                logger.debug("[今日头条] 未找到作品声明选项")
        except Exception as e:
            logger.warning(f"[今日头条] 选择作品声明失败: {e}，继续执行")

        # 6. 选择"头条首发"
        logger.info("[今日头条] ========== 选择头条首发 ==========")
        try:
            # 使用更精确的选择器定位"头条首发" checkbox
            first_publish_label = await self.page.query_selector('.exclusive-checkbox-wraper .byte-checkbox, .byte-checkbox.checkbox-with-tip')
            if first_publish_label:
                # 检查是否已选中
                checkbox = await first_publish_label.query_selector('input[type="checkbox"]')
                if checkbox:
                    is_checked = await checkbox.is_checked()
                    if not is_checked:
                        await first_publish_label.click()
                        logger.info("[今日头条] ✓ 已选择头条首发")
                    else:
                        logger.debug("[今日头条] 头条首发已选中")
            else:
                logger.debug("[今日头条] 未找到头条首发选项")
        except Exception as e:
            logger.warning(f"[今日头条] 选择头条首发失败: {e}，继续执行")

        # 滚动到底部确保所有内容加载
        await asyncio.sleep(2)
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def submit_article(self) -> PublishResult:
        """提交文章

        今日头条发布流程：
        1. 点击"预览并发布"按钮
        2. 等待预览页面加载（5-10秒）
        3. 点击"确认发布"按钮
        4. 等待文章在后台完成发布（10-15秒）
        5. 主动打开文章列表页面
        6. 从文章列表页面提取刚发布的文章ID和URL

        Returns:
            发布结果，包含平台文章ID和链接
        """
        assert self.page is not None

        try:
            # 等待随机时间（模拟人工操作）
            wait_time = random.uniform(2, 5)
            logger.info(f"[今日头条] 等待 {wait_time:.1f} 秒（模拟人工操作）...")
            await asyncio.sleep(wait_time)

            # 1. 查找并点击发布按钮
            logger.info("[今日头条] ========== 查找发布按钮 ==========")

            publish_button_selectors = [
                '.publish-btn-last',
                'button.publish-btn-last',
                'button.byte-btn-primary.publish-btn',
            ]

            publish_button = None
            for selector in publish_button_selectors:
                try:
                    publish_button = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if publish_button:
                        # 验证按钮文本包含"发布"或"预览并发布"
                        text = await publish_button.text_content()
                        if text and ('发布' in text or '预览并发布' in text):
                            logger.info(f"[今日头条] ✓ 找到发布按钮: {selector} ({text.strip()})")
                            break
                        else:
                            publish_button = None
                except Exception:
                    logger.debug(f"[今日头条] 发布按钮选择器未找到: {selector}")
                    continue

            if not publish_button:
                logger.error("[今日头条] ✗ 未找到发布按钮")
                return PublishResult(
                    success=False,
                    message="未找到发布按钮，发布页面可能已改变",
                )

            # 1. 点击"预览并发布"按钮
            logger.info("[今日头条] 点击【预览并发布】按钮...")
            await publish_button.click()
            logger.info("[今日头条] ✓ 已点击【预览并发布】按钮")

            # 2. 等待预览页面加载（5-10秒）
            wait_time = random.uniform(5, 10)
            logger.info(f"[今日头条] 等待 {wait_time:.1f} 秒（加载预览页面）...")
            await asyncio.sleep(wait_time)

            # 3. 查找并点击"确认发布"按钮
            logger.info("[今日头条] ========== 查找确认发布按钮 ==========")

            confirm_button_selectors = [
                '.publish-footer .publish-btn-last',
                '.publish-footer button.byte-btn-primary',
                'button.publish-btn-last:has-text("确认发布")',
                'button.publish-btn-last',
            ]

            confirm_button = None
            for selector in confirm_button_selectors:
                try:
                    # 对于包含 :has-text 的选择器，使用不同的处理方式
                    if ':has-text' in selector:
                        # 使用通用选择器然后验证文本
                        base_selector = '.publish-footer button.publish-btn-last'
                        confirm_button = await self.page.query_selector(base_selector)
                        if confirm_button:
                            text = await confirm_button.text_content()
                            if text and '确认发布' in text:
                                logger.info(f"[今日头条] ✓ 找到确认发布按钮 ({text.strip()})")
                                break
                            else:
                                confirm_button = None
                    else:
                        confirm_button = await self.page.wait_for_selector(
                            selector, timeout=5000, state="visible"
                        )
                        if confirm_button:
                            # 验证按钮文本包含"确认发布"
                            text = await confirm_button.text_content()
                            if text and '确认发布' in text:
                                logger.info(f"[今日头条] ✓ 找到确认发布按钮: {selector} ({text.strip()})")
                                break
                            else:
                                confirm_button = None
                except Exception:
                    logger.debug(f"[今日头条] 确认发布按钮选择器未找到: {selector}")
                    continue

            if not confirm_button:
                logger.error("[今日头条] ✗ 未找到确认发布按钮")
                return PublishResult(
                    success=False,
                    message="未找到确认发布按钮，发布流程可能已改变",
                )

            # 4. 点击"确认发布"按钮
            logger.info("[今日头条] 点击【确认发布】按钮...")
            await confirm_button.click()
            logger.info("[今日头条] ✓ 已点击【确认发布】按钮")

            # 5. 等待文章在后台完成发布（10-15秒）
            logger.info("[今日头条] 等待文章发布完成...")
            wait_time = random.uniform(10, 15)
            logger.info(f"[今日头条] 等待 {wait_time:.1f} 秒...")
            await asyncio.sleep(wait_time)

            # 6. 主动在新标签页打开文章列表页面获取链接
            logger.info("[今日头条] ========== 打开文章列表页面 ==========")
            article_id = None
            article_url = None

            try:
                # 保存原始页面（写作/预览页）
                original_page = self.page

                # 创建新标签页
                logger.info("[今日头条] 正在创建新标签页...")
                context = self.page.context
                list_page = await context.new_page()
                logger.info("[今日头条] ✓ 新标签页已创建")

                # 在新标签页中打开文章列表
                article_list_url = "https://mp.toutiao.com/profile_v4/graphic/articles"
                logger.info(f"[今日头条] 正在打开文章列表: {article_list_url}")
                await list_page.goto(article_list_url, timeout=30000)
                logger.info("[今日头条] ✓ 文章列表页面已打开")

                # 等待页面加载（React应用需要时间渲染和数据加载）
                logger.info("[今日头条] 等待页面加载完成...")
                await asyncio.sleep(random.uniform(10, 15))
                logger.info("[今日头条] ✓ 页面等待完成")

                # 提取文章信息
                logger.info("[今日头条] ========== 提取文章信息 ==========")

                try:
                    # 步骤1: 等待文章卡片出现
                    logger.info("[今日头条] 步骤1: 等待文章卡片出现...")
                    await list_page.wait_for_selector('.article-card', timeout=10000)
                    logger.info("[今日头条] ✓ 文章卡片已出现")

                    # 步骤2: 获取所有文章卡片
                    logger.info("[今日头条] 步骤2: 获取所有文章卡片...")
                    article_cards = await list_page.query_selector_all('.article-card')
                    logger.info(f"[今日头条] ✓ 找到 {len(article_cards)} 篇文章")

                    if article_cards:
                        # 步骤3: 获取第一篇文章
                        logger.info("[今日头条] 步骤3: 获取第一篇文章（刚发布的文章）...")
                        first_article = article_cards[0]
                        logger.info("[今日头条] ✓ 已获取第一篇文章卡片")

                        # 步骤4: 获取标题链接元素
                        logger.info("[今日头条] 步骤4: 查找文章标题链接元素...")
                        title_link = await first_article.query_selector('.title-wrap .title')

                        if title_link:
                            logger.info("[今日头条] ✓ 找到标题链接元素")

                            # 步骤5: 提取链接和标题
                            logger.info("[今日头条] 步骤5: 提取链接和标题...")
                            href = await title_link.get_attribute('href')
                            title_text = await title_link.text_content()

                            logger.info(f"[今日头条] ✓ 提取完成:")
                            logger.info(f"[今日头条]   - 标题: {title_text}")
                            logger.info(f"[今日头条]   - 链接: {href}")

                            # 步骤6: 从 href 中提取文章ID
                            logger.info("[今日头条] 步骤6: 从链接中提取文章ID...")
                            # href 格式: https://www.toutiao.com/item/7616200863446483494/
                            match = re.search(r'/item/(\d+)/', href)

                            if match:
                                article_id = match.group(1)
                                article_url = href
                                logger.info(f"[今日头条] ✓ 文章ID提取成功: {article_id}")
                                logger.info(f"[今日头条] ✓ 完整文章URL: {article_url}")
                            else:
                                logger.warning(f"[今日头条] ✗ 未能从链接中提取文章ID, 链接格式: {href}")
                        else:
                            logger.warning("[今日头条] ✗ 未找到文章标题链接元素")
                            logger.debug("[今日头条] 尝试的选择器: .title-wrap .title")
                    else:
                        logger.warning("[今日头条] ✗ 未找到任何文章卡片")
                        logger.debug("[今日头条] 尝试的选择器: .article-card")
                except Exception as e:
                    logger.error(f"[今日头条] ✗ 提取文章信息异常: {str(e)}", exc_info=True)

                # 关闭新标签页
                await list_page.close()
                logger.info("[今日头条] ✓ 已关闭文章列表标签页")

                # 恢复原始页面
                self.page = original_page

            except Exception as e:
                logger.warning(f"[今日头条] 提取文章信息失败: {e}")

            # 7. 检查是否有错误提示
            try:
                error_message = await self.page.query_selector('.error-message, .toast-error')
                if error_message:
                    error_text = await error_message.text_content()
                    logger.error(f"[今日头条] ✗ 发布失败: {error_text}")
                    return PublishResult(
                        success=False,
                        message=f"发布失败: {error_text}",
                    )
            except Exception:
                pass

            # 8. 返回发布结果
            if article_id and article_url:
                logger.info("[今日头条] ✓ 发布成功")
                return PublishResult(
                    success=True,
                    message="发布成功",
                    platform_article_id=article_id,
                    platform_url=article_url,
                )
            else:
                logger.info("[今日头条] 发布操作已完成（未获取到文章链接）")
                return PublishResult(
                    success=True,
                    message="文章已提交发布",
                    platform_article_id=None,
                    platform_url=None,
                )

        except Exception as e:
            logger.error(f"[今日头条] ✗ 提交文章时出错: {str(e)}", exc_info=True)
            return PublishResult(
                success=False,
                message=f"提交文章时出错: {str(e)}",
            )

    def _markdown_to_html(self, markdown: str) -> str:
        """将 Markdown 转换为 HTML

        Args:
            markdown: Markdown 格式的文本

        Returns:
            HTML 格式的文本
        """
        # 简单的 Markdown 到 HTML 转换
        html = markdown

        # 转义 HTML 特殊字符（除了要处理的标签）
        html = html.replace("&", "&amp;")

        # 标题
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # 粗体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)

        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # 代码块
        html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # 链接
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

        # 无序列表
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\n\0</ul>', html)

        # 有序列表
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # 段落（非标签行）
        lines = html.split('\n')
        result_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<'):
                result_lines.append(f'<p>{line}</p>')
            elif line:
                result_lines.append(line)
        html = '\n'.join(result_lines)

        # 换行
        html = html.replace('\n\n', '<br><br>')

        # 恢复 & 符号
        html = html.replace("&amp;", "&")

        return html

    def _sanitize_html(self, html: str) -> str:
        """清理 HTML，只保留安全的标签

        Args:
            html: 原始 HTML

        Returns:
            清理后的 HTML
        """
        # 允许的标签和属性
        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'p', 'br',
            'strong', 'em', 'u', 's',
            'ul', 'ol', 'li',
            'pre', 'code',
            'a',
            'blockquote',
        ]

        # 移除不允许的标签（简单实现）
        # 注意：这是一个基础实现，生产环境建议使用专业的HTML清理库如bleach
        soup = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        soup = re.sub(r'<style[^>]*>.*?</style>', '', soup, flags=re.DOTALL | re.IGNORECASE)
        soup = re.sub(r'<iframe[^>]*>.*?</iframe>', '', soup, flags=re.DOTALL | re.IGNORECASE)

        # 移除危险属性
        soup = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', soup, flags=re.IGNORECASE)
        soup = re.sub(r'\sjavascript:', '', soup, flags=re.IGNORECASE)

        return soup

    def _extract_article_id(self, url: str) -> str | None:
        """从URL中提取文章ID

        Args:
            url: 页面URL

        Returns:
            文章ID，如果无法提取则返回None
        """
        # 今日头条文章URL通常包含文章ID
        # 例如: https://www.toutiao.com/article/7xxxxxxxxx/
        match = re.search(r'/article/(\d+)/', url)
        if match:
            return match.group(1)

        # 也可能包含 item ID
        match = re.search(r'/item/(\d+)/', url)
        if match:
            return match.group(1)

        return None
