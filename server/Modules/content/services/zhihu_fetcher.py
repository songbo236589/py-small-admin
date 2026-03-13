"""
知乎问题内容抓取器

用于抓取知乎问题页面，提取问题描述和高赞回答，为 AI 文章生成提供真实的参考内容。
"""

import re
from dataclasses import dataclass
from typing import Any

from config.content import ContentConfig
from loguru import logger
from playwright.async_api import Page, async_playwright
from playwright_stealth import stealth_async


@dataclass
class ZhihuQuestionContent:
    """知乎问题内容

    Attributes:
        title: 问题标题
        description: 问题描述
        answers: 高赞回答列表
        url: 问题链接
    """

    title: str
    description: str
    answers: list[dict[str, Any]]
    url: str

    def to_prompt_context(self, max_answers: int = 3, max_answer_length: int = 500) -> str:
        """转换为 AI prompt 上下文

        Args:
            max_answers: 最大回答数量
            max_answer_length: 每个回答最大长度（字符数）

        Returns:
            格式化的上下文字符串
        """
        parts = []

        # 问题标题和描述
        parts.append(f"## 问题标题\n{self.title}\n")

        if self.description:
            parts.append(f"## 问题描述\n{self.description}\n")

        # 高赞回答
        if self.answers:
            parts.append("## 高赞回答参考\n")

            for i, answer in enumerate(self.answers[:max_answers], 1):
                author = answer.get("author", "匿名用户")
                content = answer.get("content", "")

                # 截断过长的回答
                if len(content) > max_answer_length:
                    content = content[:max_answer_length] + "..."

                parts.append(f"### 回答 {i}（作者：{author}）\n{content}\n")

        return "\n".join(parts)


class ZhihuFetcher:
    """知乎问题内容抓取器"""

    def __init__(self):
        """初始化抓取器"""
        self.config = ContentConfig()
        self.playwright = None
        self.browser = None
        self.page: Page | None = None

    async def fetch_question(self, url: str) -> ZhihuQuestionContent | None:
        """抓取知乎问题内容

        Args:
            url: 知乎问题链接，格式如：https://www.zhihu.com/question/639511247

        Returns:
            ZhihuQuestionContent 对象，失败时返回 None
        """
        logger.info(f"[ZhihuFetcher] 开始抓取知乎问题: {url}")

        try:
            # 启动 Playwright
            self.playwright = await async_playwright().start()

            # 启动浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.playwright_headless,
            )

            # 创建页面
            self.page = await self.browser.new_page(
                viewport={"width": self.config.playwright_width, "height": self.config.playwright_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )

            # 应用 playwright-stealth 反检测
            logger.debug(f"[ZhihuFetcher] 应用 playwright-stealth 反检测...")
            await stealth_async(self.page)

            # 访问问题页面
            logger.info(f"[ZhihuFetcher] 访问问题页面...")
            await self.page.goto(
                url,
                wait_until="networkidle",
                timeout=self.config.playwright_timeout,
            )

            # 等待页面加载
            await self.page.wait_for_timeout(2000)

            # 提取问题标题
            title = await self._extract_title()
            if not title:
                logger.error(f"[ZhihuFetcher] 未能提取问题标题")
                return None

            logger.info(f"[ZhihuFetcher] 问题标题: {title}")

            # 提取问题描述
            description = await self._extract_description()
            if description:
                logger.info(f"[ZhihuFetcher] 问题描述长度: {len(description)} 字符")
            else:
                logger.warning(f"[ZhihuFetcher] 未能提取问题描述")

            # 提取高赞回答
            answers = await self._extract_answers()
            logger.info(f"[ZhihuFetcher] 提取到 {len(answers)} 个回答")

            # 构建结果
            result = ZhihuQuestionContent(
                title=title,
                description=description,
                answers=answers,
                url=url,
            )

            logger.info(f"[ZhihuFetcher] ✓ 抓取完成")
            return result

        except Exception as e:
            logger.error(f"[ZhihuFetcher] 抓取失败: {str(e)}")
            return None

        finally:
            await self._cleanup()

    async def _extract_title(self) -> str | None:
        """提取问题标题

        Returns:
            问题标题，失败时返回 None
        """
        if not self.page:
            return None

        try:
            # 尝试多个选择器
            selectors = [
                "h1.QuestionHeader-title",
                "h1",
                ".QuestionHeader-main .QuestionHeader-title",
            ]

            for selector in selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        title = await element.inner_text()
                        if title and title.strip():
                            return title.strip()
                except Exception:
                    continue

            return None

        except Exception as e:
            logger.error(f"[ZhihuFetcher] 提取标题失败: {str(e)}")
            return None

    async def _extract_description(self) -> str | None:
        """提取问题描述

        Returns:
            问题描述，失败时返回空字符串
        """
        if not self.page:
            return None

        try:
            # 尝试多个选择器
            selectors = [
                ".QuestionHeader-detail .RichContent-inner",
                ".QuestionHeader-detail",
                ".RichContent-inner",
                "[itemprop='text']",
            ]

            for selector in selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        desc = await element.inner_text()
                        if desc and desc.strip():
                            return desc.strip()
                except Exception:
                    continue

            return None

        except Exception as e:
            logger.error(f"[ZhihuFetcher] 提取描述失败: {str(e)}")
            return None

    async def _extract_answers(self, max_answers: int = 5) -> list[dict[str, Any]]:
        """提取高赞回答

        Args:
            max_answers: 最大提取回答数量

        Returns:
            回答列表，每个回答包含 author 和 content
        """
        if not self.page:
            return []

        answers = []

        try:
            # 尝试多个选择器
            selectors = [
                ".List-item",
                "[itemprop='answer']",
                ".AnswerItem",
            ]

            answer_elements = []

            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        answer_elements = elements
                        logger.info(f"[ZhihuFetcher] 使用选择器 '{selector}' 找到 {len(elements)} 个回答元素")
                        break
                except Exception:
                    continue

            if not answer_elements:
                logger.warning(f"[ZhihuFetcher] 未能找到回答元素")
                return []

            # 提取回答内容
            for i, element in enumerate(answer_elements[:max_answers]):
                try:
                    # 提取作者
                    author_element = await element.query_selector(".AuthorInfo-name, [itemprop='name']")
                    author = "匿名用户"
                    if author_element:
                        author_text = await author_element.inner_text()
                        if author_text and author_text.strip():
                            author = author_text.strip()

                    # 提取内容
                    content_element = await element.query_selector(".RichContent-inner, [itemprop='text']")
                    content = ""
                    if content_element:
                        content_text = await content_element.inner_text()
                        if content_text:
                            content = content_text.strip()

                    if content:
                        answers.append({
                            "author": author,
                            "content": content,
                        })
                        logger.debug(f"[ZhihuFetcher] 提取回答 {i+1}: 作者={author}, 内容长度={len(content)}")

                except Exception as e:
                    logger.warning(f"[ZhihuFetcher] 提取单个回答失败: {str(e)}")
                    continue

            return answers

        except Exception as e:
            logger.error(f"[ZhihuFetcher] 提取回答失败: {str(e)}")
            return []

    async def _cleanup(self) -> None:
        """清理资源"""
        try:
            if self.page:
                await self.page.close()
                logger.debug(f"[ZhihuFetcher] 页面已关闭")

            if self.browser:
                await self.browser.close()
                logger.debug(f"[ZhihuFetcher] 浏览器已关闭")

            if self.playwright:
                await self.playwright.stop()
                logger.debug(f"[ZhihuFetcher] Playwright 已停止")

        except Exception as e:
            logger.warning(f"[ZhihuFetcher] 清理资源时出错: {str(e)}")


# 便捷函数
async def fetch_zhihu_question(url: str) -> ZhihuQuestionContent | None:
    """便捷函数：抓取知乎问题内容

    Args:
        url: 知乎问题链接

    Returns:
        ZhihuQuestionContent 对象，失败时返回 None
    """
    fetcher = ZhihuFetcher()
    return await fetcher.fetch_question(url)
