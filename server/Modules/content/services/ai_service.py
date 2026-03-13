"""
Content AI 服务 - 负责 AI 生成文章的业务逻辑
"""

import asyncio
import json

import httpx
from fastapi.responses import JSONResponse
from loguru import logger
from sqlmodel import select

from config.content import ContentConfig
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.content.services.tag_service import TagService


class AIService:
    """Content AI 服务 - 负责 AI 生成文章的业务逻辑"""

    def __init__(self):
        """初始化 AI 服务"""
        self.config = ContentConfig()
        self.tag_service = TagService()

    def _get_provider(self, model: str | None) -> str:
        """根据模型名称判断使用哪个提供商

        Args:
            model: 模型名称（None 时使用默认模型）

        Returns:
            str: 提供商标识 ("zhipu" 或 "ollama")
        """
        # 处理 None 值，使用默认模型
        actual_model: str
        if model is None:
            # 优先使用智谱 AI 的第一个模型
            if self.config.zhipu_enabled:
                try:
                    models = json.loads(self.config.zhipu_models)
                    if models:
                        actual_model = models[0].get("name", "glm-4-flash")
                    else:
                        actual_model = "glm-4-flash"
                except json.JSONDecodeError:
                    actual_model = "glm-4-flash"
            # 其次使用 Ollama
            elif self.config.ollama_enabled:
                actual_model = "ollama"  # Ollama 会有默认模型
            else:
                actual_model = "glm-4-flash"  # 最后的默认值
        else:
            actual_model = model

        model_lower = actual_model.lower()
        if model_lower.startswith("glm-"):
            return "zhipu"
        return "ollama"

    def _is_reasoning_model(self, model: str) -> bool:
        """判断是否为推理模型（需要更多 token）

        Args:
            model: 模型名称

        Returns:
            bool: 是否为推理模型
        """
        # GLM-4.7 是推理模型，需要更多 token 用于推理过程
        reasoning_models = ["glm-4.7", "glm-4.7-flash"]
        return any(model.startswith(m) for m in reasoning_models)

    async def _get_ollama_models(self) -> list[dict]:
        """获取 Ollama 模型列表

        Returns:
            list[dict]: Ollama 模型列表
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.config.ollama_base_url}/api/tags")

                if response.status_code != 200:
                    return []

                result = response.json()
                models = result.get("models", [])

                # 简化模型信息，只返回需要的字段
                model_list = []
                for model in models:
                    model_list.append(
                        {
                            "name": model.get("name", ""),
                            "size": model.get("size", 0),
                            "modified_at": model.get("modified_at", ""),
                        }
                    )

                return model_list

        except httpx.ConnectError:
            return []
        except Exception:
            return []

    def _get_zhipu_models(self) -> list[dict]:
        """获取智谱AI模型列表（从配置读取）

        Returns:
            list[dict]: 智谱AI模型列表，包含 name、label、description
        """
        try:
            models = json.loads(self.config.zhipu_models)
        except json.JSONDecodeError:
            models = []

        model_list = []
        for model in models:
            model_list.append(
                {
                    "name": model.get("name", ""),
                    "label": model.get("label", model.get("name", "")),
                    "description": model.get("description", ""),
                    "size": 0,
                    "modified_at": "",
                }
            )
        return model_list

    def _get_zhipu_model_config(self, model_name: str) -> dict:
        """获取指定智谱模型的配置信息

        Args:
            model_name: 模型名称

        Returns:
            dict: 模型配置信息，可能包含 base_url 等自定义配置
        """
        try:
            models = json.loads(self.config.zhipu_models)
            for model in models:
                if model.get("name") == model_name:
                    return model
        except json.JSONDecodeError:
            pass
        return {}

    def _is_retryable_error(self, error_detail: dict) -> bool:
        """判断错误是否可重试

        Args:
            error_detail: API 返回的错误详情

        Returns:
            bool: 是否可重试
        """
        if not isinstance(error_detail, dict):
            return False

        # 智谱AI的错误结构是嵌套的: {'error': {'code': '1305', 'message': '...'}}
        if "error" in error_detail:
            error_detail = error_detail.get("error", {})

        error_code = error_detail.get("code", "")
        error_msg = error_detail.get("message", "")

        # 可重试的错误码
        retryable_codes = [
            "1305",
            "1302",
            "1303",
        ]  # 1305: 访问量过大, 1302: 服务器错误, 1303: 速率限制

        # 检查错误码
        if error_code in retryable_codes:
            return True

        # 检查错误消息中的关键词
        retryable_keywords = ["访问量过大", "请稍后再试", "服务器忙", "速率限制"]
        for keyword in retryable_keywords:
            if keyword in error_msg:
                return True

        return False

    def _get_retry_delay(self, attempt: int, base_delay: float = 2.0) -> float:
        """获取重试延迟时间（指数退避）

        Args:
            attempt: 当前重试次数（从 0 开始）
            base_delay: 基础延迟时间（秒）

        Returns:
            float: 延迟时间（秒）
        """
        # 指数退避：base_delay * 2^attempt
        # 第 0 次: 2秒, 第 1 次: 4秒, 第 2 次: 8秒
        return base_delay * (2**attempt)

    async def get_models(self) -> JSONResponse:
        """获取可用 AI 模型列表（支持多个提供商）

        Returns:
            JSONResponse: 模型列表，包含 models 和 default_model
        """
        models = []
        default_model = None

        # 1. 如果 Ollama 开启，获取 Ollama 模型
        if self.config.ollama_enabled:
            ollama_models = await self._get_ollama_models()
            models.extend(ollama_models)
            if not default_model and ollama_models:
                default_model = ollama_models[0].get("name")

        # 2. 如果智谱AI开启，添加智谱模型
        if self.config.zhipu_enabled:
            if not self.config.zhipu_api_key:
                return error("智谱AI已启用但未配置 API Key，请先配置")
            zhipu_models = self._get_zhipu_models()
            models.extend(zhipu_models)
            if not default_model and zhipu_models:
                default_model = zhipu_models[0].get("name")

        # 3. 检查是否有可用模型
        if not models:
            return error("AI 功能未启用，请在配置中启用至少一个 AI 提供商")

        return success(
            {
                "models": models,
                "default_model": default_model,
            }
        )

    async def _generate_with_zhipu(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> JSONResponse:
        """使用智谱AI生成内容（带重试机制）

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数（None 表示不限制，由模型自行决定）

        Returns:
            JSONResponse: 生成结果
        """
        logger.debug(
            f"[_generate_with_zhipu] 开始调用智谱AI，model={model}, temperature={temperature}, max_tokens={max_tokens or '不限制'}"
        )
        logger.debug(f"[_generate_with_zhipu] prompt 长度: {len(prompt)} 字符")

        if not self.config.zhipu_enabled:
            return error("智谱AI未启用")

        if not self.config.zhipu_api_key:
            return error("智谱AI API Key 未配置")

        # 重试配置
        max_retries = 3
        base_delay = 2.0  # 基础延迟 2 秒

        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.config.zhipu_api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "temperature": temperature,
                }
                # 只有在明确指定 max_tokens 时才添加此参数
                if max_tokens is not None:
                    payload["max_tokens"] = max_tokens

                # 获取模型配置，检查是否有自定义 base_url（如 glm-4.7 使用 /api/coding/paas/v4）
                model_config = self._get_zhipu_model_config(model)
                base_url = model_config.get("base_url", self.config.zhipu_base_url)
                url = f"{base_url}/chat/completions"

                # 如果使用了自定义 base_url，记录日志
                if "base_url" in model_config:
                    logger.info(
                        f"[_generate_with_zhipu] 模型 {model} 使用自定义 base_url: {base_url}"
                    )

                # 记录重试信息
                if attempt > 0:
                    logger.info(
                        f"[_generate_with_zhipu] 第 {attempt + 1} 次尝试调用智谱AI"
                    )

                logger.debug(f"[_generate_with_zhipu] 请求 URL: {url}")
                logger.debug(
                    f"[_generate_with_zhipu] 请求 payload: {json.dumps(payload, ensure_ascii=False)[:500]}..."
                )

                async with httpx.AsyncClient(
                    timeout=self.config.zhipu_timeout
                ) as client:
                    response = await client.post(url, headers=headers, json=payload)

                    logger.debug(
                        f"[_generate_with_zhipu] 响应状态码: {response.status_code}"
                    )

                    if response.status_code != 200:
                        error_msg = f"智谱AI API 调用失败: {response.status_code}"
                        try:
                            error_detail = response.json()
                            logger.error(
                                f"[_generate_with_zhipu] 错误详情: {error_detail}"
                            )

                            # 检查是否是可重试的错误
                            if self._is_retryable_error(error_detail):
                                if attempt < max_retries - 1:
                                    # 还有重试机会
                                    delay = self._get_retry_delay(attempt, base_delay)
                                    logger.warning(
                                        f"[_generate_with_zhipu] 遇到可重试错误，{delay}秒后重试 (剩余 {max_retries - attempt - 1} 次)"
                                    )
                                    await asyncio.sleep(delay)
                                    continue
                                else:
                                    error_msg = f"智谱AI服务繁忙，已重试 {max_retries} 次，请稍后再试"

                            if "error" in error_detail:
                                error_msg = f"智谱AI错误: {error_detail['error']}"
                        except Exception:
                            logger.error(
                                f"[_generate_with_zhipu] 响应内容: {response.text}"
                            )
                        return error(error_msg)

                    result = response.json()
                    logger.debug(
                        f"[_generate_with_zhipu] 原始响应结构: {json.dumps(result, ensure_ascii=False)[:500]}..."
                    )

                    # 提取 content
                    content = (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                    )

                    # 如果 content 为空，尝试使用 reasoning_content（推理模式模型）
                    if not content:
                        reasoning_content = (
                            result.get("choices", [{}])[0]
                            .get("message", {})
                            .get("reasoning_content", "")
                            .strip()
                        )
                        if reasoning_content:
                            logger.warning(
                                "[_generate_with_zhipu] content 为空，尝试从 reasoning_content 提取最终答案"
                            )
                            # 尝试从推理内容中提取最终答案
                            extracted_answer = (
                                self._extract_final_answer_from_reasoning(
                                    reasoning_content
                                )
                            )
                            if extracted_answer:
                                logger.info(
                                    f"[_generate_with_zhipu] 成功从 reasoning_content 提取答案: {extracted_answer[:100]}..."
                                )
                                content = extracted_answer
                            else:
                                logger.error(
                                    "[_generate_with_zhipu] 无法从 reasoning_content 提取有效答案，可能是 max_tokens 设置过小"
                                )
                                logger.debug(
                                    f"[_generate_with_zhipu] reasoning_content 长度: {len(reasoning_content)} 字符"
                                )
                                return error(
                                    "智谱AI推理模型未返回最终答案，请尝试增加 max_tokens 或使用非推理模型"
                                )

                    logger.debug(
                        f"[_generate_with_zhipu] 提取的 content 长度: {len(content)} 字符"
                    )
                    logger.debug(
                        f"[_generate_with_zhipu] 提取的 content 内容: {content[:200] if content else '(空)'}..."
                    )

                    if not content:
                        logger.error(
                            "[_generate_with_zhipu] content 为空！原始响应如下:"
                        )
                        logger.error(
                            f"[_generate_with_zhipu] {json.dumps(result, ensure_ascii=False, indent=2)}"
                        )
                        return error("智谱AI 生成内容为空")

                    logger.debug("[_generate_with_zhipu] 智谱AI 调用成功")
                    return success({"content": content, "model": model})

            except httpx.ConnectError as e:
                if attempt < max_retries - 1:
                    delay = self._get_retry_delay(attempt, base_delay)
                    logger.warning(
                        f"[_generate_with_zhipu] 连接错误，{delay}秒后重试: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                    continue
                return error("无法连接到智谱AI服务")
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    delay = self._get_retry_delay(attempt, base_delay)
                    logger.warning(f"[_generate_with_zhipu] 请求超时，{delay}秒后重试")
                    await asyncio.sleep(delay)
                    continue
                return error("智谱AI 生成超时，请稍后重试")
            except Exception as e:
                logger.error(f"[_generate_with_zhipu] 异常: {str(e)}")
                return error(f"智谱AI 生成失败: {str(e)}")

        return error("智谱AI 生成失败：已达到最大重试次数")

    def _clean_tags(self, text: str) -> str:
        """清理文本中的标签和元数据信息

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本
        """
        import re

        # 移除各种格式的标签信息
        text = re.sub(r"标签[：:]\s*[^\n]*", "", text)
        text = re.sub(r"#[\w\u4e00-\u9fa5]+", "", text)
        text = re.sub(r"【[^】]*标签[^】]*】", "", text)
        text = re.sub(r"相关标签[：:]\s*[^\n]*", "", text)
        text = re.sub(r"分类[：:]\s*[^\n]*", "", text)
        text = re.sub(r"话题[：:]\s*[^\n]*", "", text)
        text = re.sub(r"来源[：:]\s*[^\n]*", "", text)
        # 清理多余的空行和空格
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_final_answer_from_reasoning(
        self, reasoning_content: str
    ) -> str | None:
        """尝试从推理内容中提取最终答案

        当推理模型的 content 为空时，尝试从 reasoning_content 中提取最终答案。
        查找常见的答案模式。

        Args:
            reasoning_content: 推理内容

        Returns:
            str | None: 提取的答案，如果无法提取则返回 None
        """
        if not reasoning_content:
            return None

        import re

        # 常见的答案模式
        patterns = [
            r"最终[答案标题结果为为：:]\s*([^\n]+)",
            r"答案[标题结果为为：:]\s*([^\n]+)",
            r"结论[为为：:]\s*([^\n]+)",
            r"因此[，,][答案标题结果是为为：:]\s*([^\n]+)",
            r"综上[所述，,][答案标题结果是为为：:]\s*([^\n]+)",
            # 查找最后一行作为答案
            r"[^\n]+$",
        ]

        for pattern in patterns:
            match = re.search(pattern, reasoning_content)
            if match:
                answer = match.group(1) if match.lastindex else match.group(0)
                answer = answer.strip()
                # 如果提取的答案合理（不太长，不像推理内容），返回它
                if (
                    1 < len(answer) < 200
                    and "推理" not in answer
                    and "思考" not in answer
                ):
                    return answer

        # 如果无法提取，返回 None
        return None

    def _get_variant_guidance(self, variant_index: int) -> str:
        """根据变体索引生成不同的写作角度引导

        Args:
            variant_index: 变体索引

        Returns:
            str: 写作角度引导文本
        """
        if variant_index == 0:
            # 第一篇，标准角度
            return ""
        elif variant_index == 1:
            # 第二篇，侧重实践和案例
            return """11. **特别要求**：请从实践应用角度切入，重点结合实际案例和代码示例来讲解"""
        elif variant_index == 2:
            # 第三篇，侧重原理和深度
            return """11. **特别要求**：请从技术原理深度剖析的角度切入，重点讲解底层机制和设计思想"""
        elif variant_index == 3:
            # 第四篇，侧重最佳实践和避坑
            return """11. **特别要求**：请从最佳实践和常见陷阱的角度切入，重点分享经验和避坑指南"""
        elif variant_index == 4:
            # 第五篇，侧重对比和选型
            return """11. **特别要求**：请从技术对比和选型决策的角度切入，重点分析不同方案的优劣"""
        else:
            # 其他序号，使用通用多样化引导
            angle_options = [
                "从性能优化角度分析问题",
                "从架构设计角度探讨解决方案",
                "从工程实践角度分享经验",
                "从源码分析角度深入讲解",
                "从问题排查角度展开论述",
            ]
            selected_angle = angle_options[variant_index % len(angle_options)]
            return f"""11. **特别要求**：请{selected_angle}，与之前的文章在风格和侧重点上有所区别"""

    async def _generate_article_title(
        self,
        topic_title: str,
        description: str | None,
        model: str,
        variant_index: int = 0,
    ) -> JSONResponse:
        """生成文章标题

        Args:
            topic_title: 问题标题
            description: 问题描述（可选）
            model: 指定模型
            variant_index: 变体索引

        Returns:
            JSONResponse: 生成的文章标题
        """
        # 检查是否有可用的AI提供商
        if not self.config.ollama_enabled and not self.config.zhipu_enabled:
            return error("AI 功能未启用")

        # 确定使用的提供商
        provider = self._get_provider(model)

        # 验证提供商是否启用
        if provider == "zhipu" and not self.config.zhipu_enabled:
            return error("智谱AI未启用")
        if provider == "ollama" and not self.config.ollama_enabled:
            return error("Ollama未启用")

        # 根据变体索引添加不同的风格引导
        style_guidance = self._get_title_style_guidance(variant_index)

        desc_part = f"\n问题描述：{description}" if description else ""

        prompt = f"""请根据以下问题，生成一个吸引人的技术博客文章标题：

问题标题：{topic_title}{desc_part}

要求：
1. 标题应该简洁明了，吸引读者点击
2. 体现文章的核心价值或亮点
3. 使用技术博客常见的标题风格
4. 避免过于简单或过于复杂
5. 不要使用问号、感叹号等标点符号结尾
6. 不要包含"如何"、"怎么"等口语化表达
7. 标题长度控制在 15-30 字
8. 只输出标题，不要有其他内容
{style_guidance}

请直接输出文章标题，不要有任何标记或前缀。"""

        try:
            if provider == "zhipu":
                # 调用智谱AI
                # 推理模型需要更多 token 用于推理（虽然标题短，但推理过程可能很长）
                max_tokens = 2000 if self._is_reasoning_model(model) else None
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.8,  # 标题需要更有创意
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                article_title = data.get("data", {}).get("content", "").strip()
            else:
                # 调用 Ollama API
                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "num_predict": 100,
                    },
                }

                logger.debug(f"[_generate_article_title] Ollama API 请求 URL: {url}")
                logger.debug(
                    f"[_generate_article_title] Ollama API 请求参数: model={model}"
                )

                async with httpx.AsyncClient(
                    timeout=self.config.ollama_timeout
                ) as client:
                    response = await client.post(url, json=payload)

                    logger.debug(
                        f"[_generate_article_title] Ollama API 响应状态码: {response.status_code}"
                    )

                    if response.status_code != 200:
                        logger.error("[_generate_article_title] Ollama API 调用失败")
                        logger.error(
                            f"[_generate_article_title] 响应内容: {response.text}"
                        )
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    logger.debug("[_generate_article_title] Ollama API 调用成功")
                    article_title = self._clean_tags(result.get("response", "").strip())

            # 验证生成的标题
            if article_title:
                # 如果标题过长（可能是推理内容），尝试提取或使用降级方案
                if len(article_title) > 100:
                    logger.warning(
                        f"[_generate_article_title] 生成的标题过长 ({len(article_title)} 字符)，可能是推理内容"
                    )
                    # 尝试从推理内容中提取真正的标题
                    extracted_title = self._extract_final_answer_from_reasoning(
                        article_title
                    )
                    if extracted_title and len(extracted_title) <= 100:
                        logger.info(
                            f"[_generate_article_title] 成功提取标题: {extracted_title}"
                        )
                        article_title = extracted_title
                    else:
                        # 使用原始问题标题作为降级方案
                        logger.warning(
                            "[_generate_article_title] 无法提取有效标题，使用原始问题标题作为降级方案"
                        )
                        article_title = topic_title
                # 清理标题中的多余内容
                article_title = self._clean_tags(article_title)
                article_title = article_title.strip()

            if not article_title:
                return error("AI 生成标题为空")

            return success({"title": article_title, "model": model})

        except httpx.ConnectError:
            return error(f"无法连接到 {provider} 服务，请确认服务已启动")
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            logger.error(f"[_generate_article_title] 异常: {str(e)}")
            return error(f"AI 生成标题失败: {str(e)}")

    def _get_title_style_guidance(self, variant_index: int) -> str:
        """根据变体索引生成不同的标题风格引导

        Args:
            variant_index: 变体索引

        Returns:
            str: 标题风格引导文本
        """
        if variant_index == 0:
            # 第一篇，标准风格
            return ""
        elif variant_index == 1:
            # 第二篇，实践风格
            return """9. **特别建议**：可以加入"实战"、"实践"、"案例"等关键词，强调动手经验"""
        elif variant_index == 2:
            # 第三篇，深度风格
            return """9. **特别建议**：可以加入"深度剖析"、"原理"、"源码分析"等关键词，强调技术深度"""
        elif variant_index == 3:
            # 第四篇，经验风格
            return """9. **特别建议**：可以加入"避坑指南"、"最佳实践"、"经验总结"等关键词，强调实战经验"""
        elif variant_index == 4:
            # 第五篇，对比风格
            return """9. **特别建议**：可以加入"对比"、"选型"、"方案分析"等关键词，强调方案对比"""
        else:
            # 其他序号，使用通用风格
            style_options = [
                "使用问句形式，引发读者思考",
                "使用数字列表形式，突出文章结构",
                "使用动宾结构，强调行动和实践",
                '使用"深入"、"全面"等词强调完整性',
                '使用"快速"、"简洁"等词强调效率',
            ]
            selected_style = style_options[variant_index % len(style_options)]
            return f"""9. **特别建议**：{selected_style}"""

    async def generate_description(
        self,
        title: str,
        model: str,
    ) -> JSONResponse:
        """使用 AI 根据标题生成问题描述

        Args:
            title: 问题标题
            model: 指定模型（必填）

        Returns:
            JSONResponse: 生成的描述内容
        """
        # 检查是否有可用的AI提供商
        if not self.config.ollama_enabled and not self.config.zhipu_enabled:
            return error("AI 功能未启用")

        # 确定使用的提供商
        provider = self._get_provider(model)

        # 验证提供商是否启用
        if provider == "zhipu" and not self.config.zhipu_enabled:
            return error("智谱AI未启用")
        if provider == "ollama" and not self.config.ollama_enabled:
            return error("Ollama未启用")

        # 构建生成描述的提示词
        prompt = f"""任务：为问题标题生成一段问题描述。

标题：{title}

输出示例：
输入：如何提高编程能力？
输出：这个问题探讨了学习编程的方法和技巧，包括实践练习、系统学习路径以及常见的编程能力提升策略。

现在请输出（50-150字）：

严格要求：
- 只输出描述内容，不要任何其他文字
- 不要解释、不要分析、不要输出思考过程
- 不要添加前缀、后缀、markdown标记
- 不要包含"标签"、"分类"、"话题"等元数据信息"""

        try:
            if provider == "zhipu":
                # 调用智谱AI
                # 推理模型需要更多 token 用于推理和描述生成
                max_tokens = 5000 if self._is_reasoning_model(model) else None
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.7,
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                description = self._clean_tags(data.get("data", {}).get("content", ""))
            else:
                # 调用 Ollama API
                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 500,
                    },
                }

                logger.debug(f"[generate_description] Ollama API 请求 URL: {url}")
                logger.debug(
                    f"[generate_description] Ollama API 请求参数: model={model}"
                )

                async with httpx.AsyncClient(
                    timeout=self.config.ollama_timeout
                ) as client:
                    response = await client.post(url, json=payload)

                    logger.debug(
                        f"[generate_description] Ollama API 响应状态码: {response.status_code}"
                    )

                    if response.status_code != 200:
                        logger.error("[generate_description] Ollama API 调用失败")
                        logger.error(
                            f"[generate_description] 响应内容: {response.text}"
                        )
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    logger.debug("[generate_description] Ollama API 调用成功")
                    description = self._clean_tags(result.get("response", "").strip())

            if not description:
                return error("AI 生成内容为空")

            return success(
                {
                    "description": description,
                    "model": model,
                }
            )

        except httpx.ConnectError:
            return error(f"无法连接到 {provider} 服务，请确认服务已启动")
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            return error(f"AI 生成失败: {str(e)}")

    async def generate_article_only(
        self,
        title: str,
        model: str,
        description: str | None = None,
        word_count: str = "800-1500",
        variant_index: int = 0,
        article_title: str | None = None,
        question_url: str | None = None,
        topic_id: int | None = None,
    ) -> JSONResponse:
        """使用 AI 生成文章内容（不含摘要）

        Args:
            title: 问题标题
            description: 问题描述（可选）
            word_count: 字数要求
            model: 指定模型（必填）
            variant_index: 变体索引（用于生成不同版本的文章）
            article_title: 文章标题（如果提供，使用此标题而非问题标题）
            question_url: 问答链接（可选，用于支持联网的AI模型获取更多参考内容）
            topic_id: 话题ID（可选，用于从数据库读取已抓取的知乎内容）

        Returns:
            JSONResponse: 生成的文章内容
        """
        # 检查是否有可用的AI提供商
        if not self.config.ollama_enabled and not self.config.zhipu_enabled:
            return error("AI 功能未启用")

        # 确定使用的提供商
        provider = self._get_provider(model)

        # 验证提供商是否启用
        if provider == "zhipu" and not self.config.zhipu_enabled:
            return error("智谱AI未启用")
        if provider == "ollama" and not self.config.ollama_enabled:
            return error("Ollama未启用")

        desc_part = f"\n问题描述：{description}" if description else ""
        word_count_req = word_count

        # 根据变体索引添加不同的角度引导
        variant_guidance = self._get_variant_guidance(variant_index)

        # 如果提供了 article_title，使用它作为参考
        title_part = f"\n文章标题参考：{article_title}" if article_title else ""

        # 如果提供了 question_url，统一使用 zhihu_content 字段（所有模型一视同仁）
        reference_content = ""
        if question_url and "zhihu.com" in question_url:
            # 优先从数据库读取已抓取的知乎内容
            zhihu_content_from_db = None
            if topic_id:
                try:
                    from sqlmodel import select

                    from Modules.common.libs.database.sql.session import (
                        get_async_session,
                    )
                    from Modules.content.models.content_topic import (
                        ContentTopic,
                    )

                    async with get_async_session() as session:
                        result = await session.execute(
                            select(ContentTopic.zhihu_content).where(
                                ContentTopic.id == topic_id
                            )
                        )
                        zhihu_content_json = result.scalar_one_or_none()

                        if zhihu_content_json:
                            zhihu_data = json.loads(zhihu_content_json)
                            # 构建 ZhihuQuestionContent 对象
                            from Modules.content.services.zhihu_fetcher import (
                                ZhihuQuestionContent,
                            )

                            zhihu_content_from_db = ZhihuQuestionContent(
                                title=zhihu_data.get("title", ""),
                                description=zhihu_data.get("description", ""),
                                url=zhihu_data.get("url", ""),
                                answers=zhihu_data.get("answers", []),
                            )
                            logger.info(
                                f"[generate_article_only] ✓ 从数据库读取知乎内容: 标题={zhihu_content_from_db.title}, 回答数={len(zhihu_content_from_db.answers)}"
                            )
                except Exception as e:
                    logger.warning(
                        f"[generate_article_only] 从数据库读取知乎内容失败: {str(e)}"
                    )

            # 如果数据库中有内容，直接使用
            if zhihu_content_from_db:
                reference_content = f"\n## 网友真实经历分享\n{zhihu_content_from_db.to_prompt_context()}\n"
                logger.info(
                    f"[generate_article_only] ✓ 使用数据库中的知乎内容: 标题={zhihu_content_from_db.title}, 回答数={len(zhihu_content_from_db.answers)}"
                )
            else:
                # 数据库中没有，尝试实时抓取
                logger.info(
                    f"[generate_article_only] 数据库无知乎内容，尝试抓取: {question_url}"
                )
                try:
                    from Modules.content.services.zhihu_fetcher import (
                        ZhihuFetcher,
                    )

                    fetcher = ZhihuFetcher()
                    zhihu_content = await fetcher.fetch_question(question_url)

                    if zhihu_content:
                        # 使用抓取到的真实内容
                        reference_content = f"\n## 网友真实经历分享\n{zhihu_content.to_prompt_context()}\n"
                        logger.info(
                            f"[generate_article_only] ✓ 成功抓取知乎内容: 标题={zhihu_content.title}, 回答数={len(zhihu_content.answers)}"
                        )
                    else:
                        # 抓取失败，不添加参考内容
                        logger.warning(
                            "[generate_article_only] 抓取知乎内容失败，不使用参考内容"
                        )

                except Exception as e:
                    # 异常降级处理
                    logger.warning(
                        f"[generate_article_only] 抓取知乎内容异常: {str(e)}，不使用参考内容"
                    )

        prompt = f"""你是一位善于通过他人故事来分享见解的博主，擅长从朋友的经历中提炼观点。请根据以下话题，写一篇有温度、有观点的文章：

话题：{title}{desc_part}{title_part}{reference_content}

写作要求：
1. **朋友视角**：以"我有个朋友"或"前两天和朋友聊天"的方式引入故事
2. **故事化展开**：讲述朋友的故事、经历或遇到的问题，让读者有代入感
3. **延伸分析**：从朋友的情况延伸到普遍现象，让读者产生共鸣
4. **总结提炼**：最后给出建议或观点，重点是"从他身上我们学到什么"
5. **结构自然流畅**：
   - 开头：引入朋友和场景（不要说"本文将..."）
   - 中间：讲述朋友的故事 + 分析现象
   - 结尾：总结从朋友身上学到的教训或建议
6. **如果有参考回答**：
   - 提到"网上有位网友分享了他的经历..."
   - 或"我朋友也遇到了类似的问题..."
   - 引用具体细节和故事，不要泛泛而谈
7. **严禁编造**：不要编造名人名言、数据或案例，要真实可信
8. **使用 HTML 格式**：
   - 章节用 <h2>、<h3>（严禁 <h1>）
   - 段落用 <p>
   - 列表用 <ul>、<ol>、<li>
   - 强调用 <strong>、<em>
9. **字数**：{word_count_req} 字
10. **不要加标题**：直接从正文开始
11. **严禁提及平台名称**：
    - 不要出现"知乎"、"小红书"、"今日头条"等平台名称
    - 统一使用"网上"、"有网友"、"某平台"等通用表述
    - 引用观点时说"有网友认为"，不要说"知乎网友说"
{variant_guidance}

请直接输出文章正文，从朋友的故事开始写作。"""

        try:
            if provider == "zhipu":
                # 调用智谱AI
                # 推理模型需要大量 token：推理过程 + 文章正文
                max_tokens = 16000 if self._is_reasoning_model(model) else None
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.7,
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                content = data.get("data", {}).get("content", "").strip()
            else:
                # 调用 Ollama API
                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 3000,
                    },
                }

                logger.debug(f"[generate_article_only] Ollama API 请求 URL: {url}")
                logger.debug(
                    f"[generate_article_only] Ollama API 请求参数: model={model}"
                )

                async with httpx.AsyncClient(
                    timeout=self.config.ollama_timeout
                ) as client:
                    response = await client.post(url, json=payload)

                    logger.debug(
                        f"[generate_article_only] Ollama API 响应状态码: {response.status_code}"
                    )

                    if response.status_code != 200:
                        logger.error("[generate_article_only] Ollama API 调用失败")
                        logger.error(
                            f"[generate_article_only] 响应内容: {response.text}"
                        )
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    logger.debug("[generate_article_only] Ollama API 调用成功")
                    content = result.get("response", "").strip()

            if not content:
                return error("AI 生成内容为空")

            return success({"content": content, "model": model})

        except httpx.ConnectError:
            return error(f"无法连接到 {provider} 服务，请确认服务已启动")
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            return error(f"AI 生成失败: {str(e)}")

    async def generate_summary_from_article(
        self, article: str, model: str
    ) -> JSONResponse:
        """基于文章内容生成摘要

        Args:
            article: 文章内容
            model: 指定模型（必填）

        Returns:
            JSONResponse: 生成的摘要
        """
        # 检查是否有可用的AI提供商
        if not self.config.ollama_enabled and not self.config.zhipu_enabled:
            return error("AI 功能未启用")

        # 确定使用的提供商
        provider = self._get_provider(model)

        # 验证提供商是否启用
        if provider == "zhipu" and not self.config.zhipu_enabled:
            return error("智谱AI未启用")
        if provider == "ollama" and not self.config.ollama_enabled:
            return error("Ollama未启用")

        # 限制文章长度，避免 token 超限
        # 如果文章太长，只取前 2000 字符用于生成摘要
        if len(article) > 2000:
            article_for_summary = article[:2000] + "..."
        else:
            article_for_summary = article

        prompt = f"""请根据以下文章内容，生成一段 100-150 字的摘要：

{article_for_summary}

要求：
1. 概括文章核心内容和要点
2. 不要包含任何标签、分类、话题等元数据信息
3. 直接输出摘要内容，不要有任何标记或前缀
4. 不要包含 "摘要：" 这样的前缀

请直接输出摘要内容。"""

        try:
            if provider == "zhipu":
                # 调用智谱AI
                # 推理模型需要更多 token 用于理解文章和推理
                max_tokens = 4000 if self._is_reasoning_model(model) else None
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.5,
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                summary = self._clean_tags(data.get("data", {}).get("content", ""))
            else:
                # 调用 Ollama API
                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,  # 摘要需要更准确，降低温度
                        "top_p": 0.9,
                        "num_predict": 300,
                    },
                }

                logger.debug(
                    f"[generate_summary_from_article] Ollama API 请求 URL: {url}"
                )
                logger.debug(
                    f"[generate_summary_from_article] Ollama API 请求参数: model={model}"
                )

                async with httpx.AsyncClient(
                    timeout=self.config.ollama_timeout
                ) as client:
                    response = await client.post(url, json=payload)

                    logger.debug(
                        f"[generate_summary_from_article] Ollama API 响应状态码: {response.status_code}"
                    )

                    if response.status_code != 200:
                        logger.error(
                            "[generate_summary_from_article] Ollama API 调用失败"
                        )
                        logger.error(
                            f"[generate_summary_from_article] 响应内容: {response.text}"
                        )
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    logger.debug("[generate_summary_from_article] Ollama API 调用成功")
                    summary = self._clean_tags(result.get("response", "").strip())

            if not summary:
                return error("AI 生成摘要为空")

            return success({"summary": summary, "model": model})

        except httpx.ConnectError:
            return error(f"无法连接到 {provider} 服务，请确认服务已启动")
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            return error(f"AI 生成失败: {str(e)}")

    async def generate_category(
        self,
        title: str,
        categories: list[dict],
        model: str,
        description: str | None = None,
    ) -> JSONResponse:
        """使用 AI 分析话题内容，生成合适的分类名称（两级分类）

        Args:
            title: 问题标题
            categories: 可用分类列表（此参数保留用于日志记录，AI 不再使用）
            model: 指定模型（必填）
            description: 问题描述（可选）

        Returns:
            JSONResponse: 生成的分类名称 {"parent_category": "...", "child_category": "..."}
        """
        # 检查是否有可用的AI提供商
        if not self.config.ollama_enabled and not self.config.zhipu_enabled:
            return error("AI 功能未启用")

        # 确定使用的提供商
        provider = self._get_provider(model)

        # 验证提供商是否启用
        if provider == "zhipu" and not self.config.zhipu_enabled:
            return error("智谱AI未启用")
        if provider == "ollama" and not self.config.ollama_enabled:
            return error("Ollama未启用")

        logger.debug(f"[generate_category] 开始生成分类，标题: {title}")

        desc_part = f"\n{description}" if description else ""

        # 优化的 prompt：添加示例和更严格的约束
        prompt = f"""任务：为话题生成两级分类。

话题：{title}{desc_part}

输出示例：
输入：如何提高编程能力？
输出：{{"parent_category": "技术", "child_category": "编程学习"}}

输入：职场中如何处理人际关系？
输出：{{"parent_category": "职场", "child_category": "人际关系"}}

现在请输出：
{{"parent_category": "...", "child_category": "..."}}

严格要求：
- 只输出JSON，不要任何其他文字
- 不要解释、不要分析、不要输出思考过程
- 不要添加前缀、后缀、markdown标记"""

        try:
            if provider == "zhipu":
                # 调用智谱AI
                # 推理模型需要更多 token 用于推理过程
                max_tokens = 4000 if self._is_reasoning_model(model) else 500
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.3,  # 降低温度，获得更稳定的结果
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                response_text = data.get("data", {}).get("content", "").strip()
            else:
                # 调用 Ollama API
                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # 降低温度
                        "top_p": 0.9,
                        "num_predict": 2000,  # 保持 2000
                    },
                }

                logger.debug(f"[generate_category] Ollama API 请求 URL: {url}")
                logger.debug(f"[generate_category] Ollama API 请求参数: model={model}")

                async with httpx.AsyncClient(
                    timeout=self.config.ollama_timeout
                ) as client:
                    response = await client.post(url, json=payload)

                    logger.debug(
                        f"[generate_category] Ollama API 响应状态码: {response.status_code}"
                    )

                    if response.status_code != 200:
                        logger.error("[generate_category] Ollama API 调用失败")
                        logger.error(f"[generate_category] 响应内容: {response.text}")
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    logger.debug("[generate_category] Ollama API 调用成功")
                    response_text = self._clean_tags(result.get("response", "").strip())

            # ===== 调试日志：AI 响应 =====
            logger.debug(
                f"[generate_category] AI 原始响应长度: {len(response_text)} 字符"
            )
            logger.debug(f"[generate_category] AI 原始响应内容: {response_text}")

            # 解析响应
            if not response_text:
                logger.error("[generate_category] AI 响应为空！")
                return error("AI 生成内容为空")

            # 尝试解析 JSON
            import re

            # 查找 JSON 部分（可能被包裹在 ```json 中）
            json_match = re.search(
                r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL
            )
            if not json_match:
                json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)

            logger.debug(
                f"[generate_category] JSON 匹配结果: {'成功' if json_match else '失败'}"
            )
            if json_match:
                logger.debug(
                    f"[generate_category] 匹配到的 JSON 内容: {json_match.group(1)}"
                )

            if not json_match:
                logger.error(
                    f"[generate_category] AI 未能返回有效的 JSON！原始响应: {response_text}"
                )
                return error(f"AI 未能返回有效的 JSON: {response_text}")

            try:
                ai_response = json.loads(json_match.group(1))
                logger.debug(
                    f"[generate_category] 解析后的 JSON: {json.dumps(ai_response, ensure_ascii=False)}"
                )
            except json.JSONDecodeError as e:
                logger.error(
                    f"[generate_category] JSON 解析失败: {e}, 原始内容: {json_match.group(1)}"
                )
                return error(f"AI 返回的 JSON 格式错误: {json_match.group(1)}")

            # 获取分类名称
            parent_category = ai_response.get("parent_category")
            child_category = ai_response.get("child_category")

            if not parent_category or not child_category:
                logger.error(
                    f"[generate_category] AI 返回的分类名称不完整: {ai_response}"
                )
                return error(
                    "AI 返回的分类名称不完整，需要 parent_category 和 child_category"
                )

            logger.info(
                f"[generate_category] AI 生成的分类: {parent_category} > {child_category}"
            )

            # 直接返回分类名称，由 topic_service 处理后续逻辑
            return success(
                {
                    "parent_category": parent_category,
                    "child_category": child_category,
                    "model": model,
                }
            )

        except httpx.ConnectError:
            return error(f"无法连接到 {provider} 服务，请确认服务已启动")
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            logger.error(f"[generate_category] 异常: {str(e)}")
            return error(f"AI 生成失败: {str(e)}")

    async def generate_article(
        self,
        topic_id: int,
        mode: str,
        title: str,
        model: str,
        description: str | None = None,
        variant_index: int = 0,
        question_url: str | None = None,
    ) -> JSONResponse:
        """使用 AI 生成文章（一次性生成：标题 + 内容 + 摘要 + 标签）

        Args:
            topic_id: 话题ID
            mode: 生成模式 (title/description/full) - 用于确定字数要求
            title: 问题标题
            description: 问题描述（可选）
            model: 指定模型（必填）
            variant_index: 变体索引（用于生成不同版本的文章）
            question_url: 问答链接（可选，用于支持联网的AI模型获取更多参考内容）

        Returns:
            JSONResponse: 生成的文章标题、内容、摘要和标签
        """
        logger.info(
            f"[generate_article] 开始生成文章（一次性生成模式），model={model}, mode={mode}, topic_id={topic_id}, variant_index={variant_index}, question_url={question_url}"
        )

        # 检查是否有可用的AI提供商
        if not self.config.ollama_enabled and not self.config.zhipu_enabled:
            logger.error("[generate_article] AI 功能未启用")
            return error("AI 功能未启用")

        # 确定使用的提供商
        provider = self._get_provider(model)
        logger.info(f"[generate_article] 判断的提供商: {provider}")

        # 验证提供商是否启用
        if provider == "zhipu" and not self.config.zhipu_enabled:
            logger.error("[generate_article] 智谱AI未启用")
            return error("智谱AI未启用")
        if provider == "ollama" and not self.config.ollama_enabled:
            logger.error("[generate_article] Ollama未启用")
            return error("Ollama未启用")

        # 使用一次性生成方法
        result = await self._generate_article_all_in_one(
            topic_id=topic_id,
            mode=mode,
            title=title,
            model=model,
            description=description,
            variant_index=variant_index,
            question_url=question_url,
        )

        return result

    async def _generate_article_all_in_one(
        self,
        topic_id: int,
        mode: str,
        title: str,
        model: str,
        description: str | None = None,
        variant_index: int = 0,
        question_url: str | None = None,
    ) -> JSONResponse:
        """一次性生成文章的所有组件（标题、内容、摘要、标签）

        Args:
            topic_id: 话题ID
            mode: 生成模式 (title/description/full) - 用于确定字数要求
            title: 问题标题
            description: 问题描述（可选）
            model: 指定模型（必填）
            variant_index: 变体索引（用于生成不同版本的文章）
            question_url: 问答链接（可选，用于支持联网的AI模型获取更多参考内容）

        Returns:
            JSONResponse: 生成的文章标题、内容、摘要和标签
        """
        # 根据模式确定字数要求
        word_count_map = {
            "title": "800-1500",
            "description": "1000-2000",
            "full": "1500-3000",
        }
        word_count = word_count_map.get(mode, "800-1500")
        logger.debug(f"[_generate_article_all_in_one] 字数要求: {word_count}")

        # 根据变体索引添加不同的风格引导
        title_style_guidance = self._get_title_style_guidance(variant_index)
        variant_guidance = self._get_variant_guidance(variant_index)

        # 构建提示词的各部分
        desc_part = f"\n问题描述：{description}" if description else ""
        word_count_req = word_count

        # 处理参考内容（知乎内容等）- 统一使用 zhihu_content 字段
        reference_content = ""
        if question_url and "zhihu.com" in question_url:
            # 优先从数据库读取已抓取的知乎内容
            zhihu_content_from_db = None
            if topic_id:
                try:
                    from sqlmodel import select

                    from Modules.common.libs.database.sql.session import (
                        get_async_session,
                    )
                    from Modules.content.models.content_topic import (
                        ContentTopic,
                    )

                    async with get_async_session() as session:
                        result = await session.execute(
                            select(ContentTopic.zhihu_content).where(
                                ContentTopic.id == topic_id
                            )
                        )
                        zhihu_content_json = result.scalar_one_or_none()

                        if zhihu_content_json:
                            zhihu_data = json.loads(zhihu_content_json)
                            # 构建 ZhihuQuestionContent 对象
                            from Modules.content.services.zhihu_fetcher import (
                                ZhihuQuestionContent,
                            )

                            zhihu_content_from_db = ZhihuQuestionContent(
                                title=zhihu_data.get("title", ""),
                                description=zhihu_data.get("description", ""),
                                url=zhihu_data.get("url", ""),
                                answers=zhihu_data.get("answers", []),
                            )
                            logger.info(
                                f"[_generate_article_all_in_one] ✓ 从数据库读取知乎内容: 标题={zhihu_content_from_db.title}, 回答数={len(zhihu_content_from_db.answers)}"
                            )
                except Exception as e:
                    logger.warning(
                        f"[_generate_article_all_in_one] 从数据库读取知乎内容失败: {str(e)}"
                    )

            # 如果数据库中有内容，直接使用
            if zhihu_content_from_db:
                reference_content = f"\n## 网友真实经历分享\n{zhihu_content_from_db.to_prompt_context()}\n"
                logger.info(
                    f"[_generate_article_all_in_one] ✓ 使用数据库中的知乎内容: 标题={zhihu_content_from_db.title}, 回答数={len(zhihu_content_from_db.answers)}"
                )
            else:
                # 数据库中没有，尝试实时抓取
                logger.info(
                    f"[_generate_article_all_in_one] 数据库无知乎内容，尝试抓取: {question_url}"
                )
                try:
                    from Modules.content.services.zhihu_fetcher import (
                        ZhihuFetcher,
                    )

                    fetcher = ZhihuFetcher()
                    zhihu_content = await fetcher.fetch_question(question_url)

                    if zhihu_content:
                        # 使用抓取到的真实内容
                        reference_content = f"\n## 网友真实经历分享\n{zhihu_content.to_prompt_context()}\n"
                        logger.info(
                            f"[_generate_article_all_in_one] ✓ 成功抓取知乎内容: 标题={zhihu_content.title}, 回答数={len(zhihu_content.answers)}"
                        )
                    else:
                        # 抓取失败，不添加参考内容
                        logger.warning(
                            "[_generate_article_all_in_one] 抓取知乎内容失败，不使用参考内容"
                        )

                except Exception as e:
                    # 异常降级处理
                    logger.warning(
                        f"[_generate_article_all_in_one] 抓取知乎内容异常: {str(e)}，不使用参考内容"
                    )

        # 构建一次性生成的提示词
        prompt = f"""你是一位善于通过他人故事来分享见解的博主，擅长从朋友的经历中提炼观点。请根据以下话题，一次性生成文章的标题、内容、摘要和标签。

话题：{title}{desc_part}{reference_content}

请严格按照以下 JSON 格式输出，不要输出任何其他内容：

```json
{{
  "title": "文章标题（15-30字，简洁明了，吸引读者点击，不要使用问号、感叹号结尾，不要包含如何、怎么等口语化表达）",
  "content": "<p>HTML格式的文章内容，以朋友视角引入故事，讲述朋友经历，延伸分析普遍现象，最后总结提炼建议。使用<h2>、<h3>、<p>、<ul>、<ol>、<li>、<strong>、<em>等HTML标签。严禁提及知乎、小红书、今日头条等平台名称，统一使用网上、有网友、某平台等通用表述。字数{word_count_req}字。",
  "summary": "文章摘要（100-150字，概括文章核心内容和要点，不要包含任何标签、分类、话题等元数据信息）",
  "tags": ["标签1", "标签2", "标签3"]
}}
```

文章写作要求：
1. **朋友视角**：以"我有个朋友"或"前两天和朋友聊天"的方式引入故事
2. **故事化展开**：讲述朋友的故事、经历或遇到的问题，让读者有代入感
3. **延伸分析**：从朋友的情况延伸到普遍现象，让读者产生共鸣
4. **总结提炼**：最后给出建议或观点，重点是"从他身上我们学到什么"
5. **结构自然流畅**：
   - 开头：引入朋友和场景（不要说"本文将..."）
   - 中间：讲述朋友的故事 + 分析现象
   - 结尾：总结从朋友身上学到的教训或建议
6. **如果有参考回答**：
   - 提到"网上有位网友分享了他的经历..."
   - 或"我朋友也遇到了类似的问题..."
   - 引用具体细节和故事，不要泛泛而谈
7. **严禁编造**：不要编造名人名言、数据或案例，要真实可信
8. **HTML 格式要求**：
   - 章节用 <h2>、<h3>（严禁 <h1>）
   - 段落用 <p>
   - 列表用 <ul>、<ol>、<li>
   - 强调用 <strong>、<em>
9. **严禁提及平台名称**：
   - 不要出现"知乎"、"小红书"、"今日头条"等平台名称
   - 统一使用"网上"、"有网友"、"某平台"等通用表述
10. **标签要求**：
    - 生成 3-5 个标签
    - 每个标签 2-4 个字
    - 标签应该简洁、准确
{variant_guidance}
{title_style_guidance}

请严格按照上述 JSON 格式输出，不要添加任何其他内容、解释或说明。"""

        try:
            if self._get_provider(model) == "zhipu":
                # 调用智谱AI
                # 推理模型需要大量 token：推理过程 + 完整文章
                max_tokens = 24000 if self._is_reasoning_model(model) else None
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.7,
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                response_text = data.get("data", {}).get("content", "").strip()
            else:
                # 调用 Ollama API
                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 8000,  # 增加输出长度限制
                    },
                }

                logger.debug(
                    f"[generate_article_all_in_one] Ollama API 请求 URL: {url}"
                )

                async with httpx.AsyncClient(
                    timeout=self.config.ollama_timeout
                ) as client:
                    response = await client.post(url, json=payload)

                    if response.status_code != 200:
                        logger.error(
                            "[_generate_article_all_in_one] Ollama API 调用失败"
                        )
                        logger.error(
                            f"[_generate_article_all_in_one] 响应内容: {response.text}"
                        )
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    response_text = result.get("response", "").strip()

            logger.debug(
                f"[_generate_article_all_in_one] AI 原始响应长度: {len(response_text)}"
            )

            if not response_text:
                logger.error("[_generate_article_all_in_one] AI 响应为空")
                return error("AI 生成响应为空")

            # 解析 JSON 响应
            article_data = self._parse_article_json_response(response_text)
            if article_data is None:
                logger.error(
                    "[_generate_article_all_in_one] 无法解析 AI 响应为有效的 JSON 格式"
                )
                return error("AI 未能返回有效的 JSON 格式")

            # 验证并提取各字段
            article_title = article_data.get("title", "").strip()
            content = article_data.get("content", "").strip()
            summary = article_data.get("summary", "").strip()
            tag_names = article_data.get("tags", [])

            # 验证必填字段
            if not article_title:
                logger.warning(
                    "[_generate_article_all_in_one] 生成的标题为空，使用问题标题作为降级方案"
                )
                article_title = title

            if not content:
                logger.error("[_generate_article_all_in_one] 生成的文章内容为空")
                return error("AI 生成的文章内容为空")

            if not summary:
                logger.warning("[_generate_article_all_in_one] 生成的摘要为空")

            if not tag_names:
                logger.warning("[_generate_article_all_in_one] 生成的标签为空")

            # 清理各字段的多余内容
            article_title = self._clean_tags(article_title)
            summary = self._clean_tags(summary)
            content = self._clean_tags(content)

            # 处理标签：创建不存在的标签，返回标签ID列表和完整标签对象数组
            tag_ids = []
            tags = []
            if tag_names:
                logger.info(
                    f"[_generate_article_all_in_one] AI 生成的标签名称: {tag_names}, 数量: {len(tag_names)}"
                )
                tag_ids, tags = await self._process_tag_names_to_ids(tag_names)
                logger.info(
                    f"[_generate_article_all_in_one] 文章标签处理完成, ID列表: {tag_ids}"
                )

            logger.info(
                f"[_generate_article_all_in_one] 文章生成成功 - 标题: {article_title[:50]}..., 内容长度: {len(content)}, 摘要长度: {len(summary)}, 标签数: {len(tag_ids)}"
            )

            return success(
                {
                    "topic_id": topic_id,
                    "mode": mode,
                    "title": article_title,
                    "content": content,
                    "summary": summary,
                    "tag_ids": tag_ids,
                    "tags": tags,
                    "model": model,
                }
            )

        except httpx.ConnectError:
            return error(
                f"无法连接到 {self._get_provider(model)} 服务，请确认服务已启动"
            )
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            logger.error(f"[_generate_article_all_in_one] 异常: {str(e)}")
            logger.exception("[_generate_article_all_in_one] 异常堆栈")
            return error(f"AI 生成失败: {str(e)}")

    def _parse_article_json_response(self, response_text: str) -> dict | None:
        """解析 AI 返回的 JSON 格式文章数据

        Args:
            response_text: AI 原始响应文本

        Returns:
            dict | None: 解析后的文章数据，解析失败返回 None
        """
        import re

        # 尝试多种方式提取 JSON
        json_match = None

        # 1. 尝试匹配 ```json ... ``` 格式
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if json_match:
            logger.debug("[_parse_article_json_response] 匹配到 ```json ... ``` 格式")
        else:
            # 2. 尝试匹配 ``` ... ``` 格式（无 json 标记）
            json_match = re.search(r"```\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            if json_match:
                logger.debug("[_parse_article_json_response] 匹配到 ``` ... ``` 格式")

        if not json_match:
            # 3. 尝试直接匹配 JSON 对象
            json_match = re.search(
                r"\{[^{}]*\"title\"[^{}]*\"content\"[^{}]*\"summary\"[^{}]*\"tags\"[^{}]*\}",
                response_text,
                re.DOTALL,
            )
            if json_match:
                logger.debug("[_parse_article_json_response] 匹配到直接 JSON 对象格式")

        # 用于存储直接提取的 JSON 字符串（非正则匹配方式）
        direct_json_str: str | None = None

        if not json_match:
            # 4. 最后尝试：查找第一个 { 和最后一个 } 之间的内容
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                direct_json_str = response_text[first_brace : last_brace + 1]
                logger.debug("[_parse_article_json_response] 使用 { } 提取方式")

        if not json_match and not direct_json_str:
            logger.error(
                f"[_parse_article_json_response] 无法从响应中提取 JSON: {response_text[:500]}..."
            )
            return None

        try:
            # 优先使用直接提取的字符串，否则使用正则匹配结果
            json_str: str
            if direct_json_str:
                json_str = direct_json_str
            elif json_match:
                json_str = json_match.group(1)
            else:
                return None

            article_data = json.loads(json_str)
            logger.info("[_parse_article_json_response] JSON 解析成功")
            return article_data
        except json.JSONDecodeError as e:
            logger.error(f"[_parse_article_json_response] JSON 解析失败: {e}")
            logger.error(
                f"[_parse_article_json_response] 匹配到的 JSON 字符串: {json_str[:500] if json_str else 'empty'}..."
            )
            return None

    async def _generate_article_tags(
        self,
        article_title: str,
        summary: str,
        model: str,
    ) -> JSONResponse:
        """使用 AI 生成文章标签

        Args:
            article_title: 文章标题
            summary: 文章摘要
            model: 指定模型

        Returns:
            JSONResponse: 生成的标签列表 ["标签1", "标签2", ...]
        """
        logger.info("[_generate_article_tags] ===== 开始生成文章标签 =====")
        logger.debug(f"[_generate_article_tags] 输入参数 - 标题: {article_title}")
        logger.debug(
            f"[_generate_article_tags] 输入参数 - 摘要: {summary[:100] if summary else 'empty'}..."
        )
        logger.debug(f"[_generate_article_tags] 输入参数 - 模型: {model}")
        logger.debug(f"[_generate_article_tags] 提供商: {self._get_provider(model)}")

        prompt = f"""你是一个标签生成助手。基于以下文章，生成 3-5 个标签。

文章标题：{article_title}
文章摘要：{summary}

要求：
1. 标签应该简洁、准确
2. 每个标签 2-4 个字
3. 直接返回 JSON 数组，不要包含任何其他文字、解释或推理过程

返回格式（仅输出此格式，不要输出其他内容）：
["标签1", "标签2", "标签3"]

请严格按照要求，直接输出 JSON 数组，不要添加任何前缀、后缀或解释性文字。"""

        try:
            if self._get_provider(model) == "zhipu":
                # 推理模型需要更多 token 用于推理过程
                max_tokens = 3000 if self._is_reasoning_model(model) else 500
                result = await self._generate_with_zhipu(
                    prompt=prompt,
                    model=model,
                    temperature=0.3,
                    max_tokens=max_tokens,
                )
                if result.status_code != 200:
                    return result

                data = json.loads(bytes(result.body).decode())
                response_text = data.get("data", {}).get("content", "").strip()
            else:
                import httpx

                url = f"{self.config.ollama_base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 500,
                    },
                }

                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, json=payload)

                    if response.status_code != 200:
                        logger.error(
                            f"[_generate_article_tags] Ollama API 调用失败: {response.status_code}"
                        )
                        return error(f"Ollama API 调用失败: {response.status_code}")

                    result = response.json()
                    response_text = self._clean_tags(result.get("response", "").strip())

            logger.debug(f"[_generate_article_tags] AI 原始响应: {response_text}")

            if not response_text:
                logger.error("[_generate_article_tags] AI 响应为空")
                return error("AI 生成标签为空")

            # 解析 JSON 数组
            import re

            json_match = re.search(
                r"```json\s*(\[.*?\])\s*```", response_text, re.DOTALL
            )
            if not json_match:
                json_match = re.search(r"(\[.*\])", response_text, re.DOTALL)

            if not json_match:
                logger.error(
                    f"[_generate_article_tags] AI 未能返回有效的 JSON: {response_text}"
                )
                return error(f"AI 未能返回有效的 JSON: {response_text}")

            try:
                tags = json.loads(json_match.group(1))
                logger.info(f"[_generate_article_tags] AI 生成的标签: {tags}")
                logger.info("[_generate_article_tags] ===== 标签生成完成 =====")
                return success({"tags": tags, "model": model})
            except json.JSONDecodeError as e:
                logger.error(f"[_generate_article_tags] JSON 解析失败: {e}")
                logger.error(
                    f"[_generate_article_tags] 匹配到的内容: {json_match.group(1)[:200]}"
                )
                return error("AI 返回的 JSON 格式错误")

        except Exception as e:
            logger.error(f"[_generate_article_tags] 异常: {str(e)}")
            logger.exception("[_generate_article_tags] 异常堆栈")
            return error(f"AI 生成标签失败: {str(e)}")

    async def _process_and_link_tags(
        self,
        article_id: int,
        tag_names: list[str],
    ) -> list[dict]:
        """处理标签：去重、创建、关联到文章

        Args:
            article_id: 文章ID
            tag_names: 标签名称列表

        Returns:
            list[dict]: 处理后的标签列表 [{"id": 1, "name": "标签1"}, ...]
        """
        from Modules.common.libs.time.utils import now
        from Modules.content.models.content_article_tag import ContentArticleTag
        from Modules.content.models.content_tag import ContentTag

        processed_tags = []

        async with get_async_session() as session:
            for tag_name in tag_names:
                # 去重：检查标签是否已处理过
                if any(t["name"] == tag_name for t in processed_tags):
                    continue

                # 检查标签是否存在
                existing_tag = await session.execute(
                    select(ContentTag).where(ContentTag.name == tag_name)
                )
                tag = existing_tag.scalar_one_or_none()

                if not tag:
                    # 创建新标签
                    tag = ContentTag(
                        name=tag_name,
                        slug=tag_name,  # 与分类相同，直接用 name
                        status=1,
                        sort=999,
                        created_at=now(),
                        updated_at=now(),
                    )
                    session.add(tag)
                    await session.commit()
                    await session.refresh(tag)
                    logger.info(
                        f"[_process_and_link_tags] 创建新标签: {tag_name} (ID: {tag.id})"
                    )
                else:
                    logger.info(
                        f"[_process_and_link_tags] 使用现有标签: {tag_name} (ID: {tag.id})"
                    )

                # 创建文章-标签关联
                article_tag = ContentArticleTag(article_id=article_id, tag_id=tag.id)  # type: ignore
                session.add(article_tag)

                processed_tags.append({"id": tag.id, "name": tag.name})

            await session.commit()

        return processed_tags

    async def _process_tag_names_to_ids(
        self,
        tag_names: list[str],
    ) -> tuple[list[int], list[dict]]:
        """处理标签名称列表，返回标签ID列表和完整标签对象数组（不存在则创建）

        Args:
            tag_names: 标签名称列表

        Returns:
            tuple[list[int], list[dict]]: (标签ID列表, 完整标签对象数组)
        """
        from Modules.common.libs.time.utils import now
        from Modules.content.models.content_tag import ContentTag

        tag_ids = []
        tag_objects = []

        async with get_async_session() as session:
            for tag_name in tag_names:
                # 去重：检查标签是否已处理过
                if any(
                    existing_tag_name == tag_name
                    for existing_tag_name in tag_names[: tag_names.index(tag_name)]
                ):
                    continue

                # 检查标签是否存在
                existing_tag = await session.execute(
                    select(ContentTag).where(ContentTag.name == tag_name)
                )
                tag = existing_tag.scalar_one_or_none()

                if not tag:
                    # 创建新标签
                    tag = ContentTag(
                        name=tag_name,
                        slug=tag_name,  # 直接使用 name 作为 slug
                        status=1,
                        sort=999,
                        created_at=now(),
                        updated_at=now(),
                    )
                    session.add(tag)
                    await session.commit()
                    await session.refresh(tag)
                    logger.info(
                        f"[_process_tag_names_to_ids] 创建新标签: {tag_name} (ID: {tag.id})"
                    )
                else:
                    logger.debug(
                        f"[_process_tag_names_to_ids] 使用现有标签: {tag_name} (ID: {tag.id})"
                    )

                tag_ids.append(tag.id)
                # 同时保存完整标签对象
                tag_objects.append({"id": tag.id, "name": tag.name, "color": tag.color})

        return tag_ids, tag_objects
