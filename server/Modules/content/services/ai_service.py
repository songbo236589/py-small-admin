"""
Content AI 服务 - 负责 AI 生成文章的业务逻辑
"""

import httpx
from fastapi.responses import JSONResponse

from config.content import ContentConfig
from Modules.common.libs.responses.response import error, success


class AIService:
    """Content AI 服务 - 负责 AI 生成文章的业务逻辑"""

    def __init__(self):
        """初始化 AI 服务"""
        self.config = ContentConfig()

    async def get_models(self) -> JSONResponse:
        """获取 Ollama 可用模型列表

        Returns:
            JSONResponse: 模型列表
        """
        if not self.config.ollama_enabled:
            return error("AI 功能未启用")

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.config.ollama_base_url}/api/tags")

                if response.status_code != 200:
                    return error(f"Ollama API 调用失败: {response.status_code}")

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

                return success({"models": model_list})

        except httpx.ConnectError:
            return error("无法连接到 Ollama 服务，请确认服务已启动")
        except Exception as e:
            return error(f"获取模型列表失败: {str(e)}")

    async def generate_article(
        self,
        topic_id: int,
        mode: str,
        title: str,
        description: str | None = None,
        model: str | None = None,
    ) -> JSONResponse:
        """使用 AI 生成文章

        Args:
            topic_id: 话题ID
            mode: 生成模式 (title/description/full)
            title: 问题标题
            description: 问题描述（可选）
            model: 指定模型（可选，不指定则使用配置文件中的默认模型）

        Returns:
            JSONResponse: 生成的文章内容
        """
        if not self.config.ollama_enabled:
            return error("AI 功能未启用")

        # 使用指定的模型或默认模型
        use_model = model or self.config.ollama_model

        # 验证描述模式需要提供问题描述
        if mode == "description" and not description:
            return error("描述模式需要提供问题描述")

        # 构建提示词
        try:
            prompt = self._build_prompt(mode, title, description)
        except ValueError as e:
            return error(str(e))

        try:
            # 调用 Ollama API
            async with httpx.AsyncClient(timeout=self.config.ollama_timeout) as client:
                response = await client.post(
                    f"{self.config.ollama_base_url}/api/generate",
                    json={
                        "model": use_model,
                        "prompt": prompt,
                        "stream": False,  # 非流式模式
                        "options": {
                            "temperature": 0.7,  # 创造性
                            "top_p": 0.9,
                            "num_predict": 2000,  # 最大生成长度
                        },
                    },
                )

                if response.status_code != 200:
                    return error(f"Ollama API 调用失败: {response.status_code}")

                result = response.json()
                generated_content = result.get("response", "")

                if not generated_content:
                    return error("AI 生成内容为空")

                # 解析摘要和正文
                summary, content = self._parse_generated_content(generated_content)

                return success(
                    {
                        "topic_id": topic_id,
                        "mode": mode,
                        "title": title,  # 返回标题
                        "content": content,
                        "summary": summary,
                        "model": use_model,
                    }
                )

        except httpx.ConnectError:
            return error("无法连接到 Ollama 服务，请确认服务已启动")
        except httpx.TimeoutException:
            return error("AI 生成超时，请稍后重试")
        except Exception as e:
            return error(f"AI 生成失败: {str(e)}")

    def _build_prompt(self, mode: str, title: str, description: str | None = None) -> str:
        """构建 AI 提示词

        Args:
            mode: 生成模式
            title: 问题标题
            description: 问题描述

        Returns:
            str: 构建的提示词
        """
        output_format = """请严格按照以下格式输出：

[摘要]
在这里写一段100-150字的文章摘要，概括文章核心内容

[正文]
在这里写完整的文章内容，使用 HTML 格式。
要求：
- 段落使用 <p> 标签
- 标题使用 <h1>、<h2>、<h3> 等标签
- 列表使用 <ul>、<ol>、<li> 标签
- 强调使用 <strong>、<em> 标签
- 代码使用 <code> 或 <pre> 标签
- 不要输出 <!DOCTYPE>、<html>、<body> 等外层标签，只输出内容部分"""

        if mode == "title":
            return f"""请根据以下问题标题，生成一篇专业的技术文章：

问题标题：{title}

要求：
1. 文章结构清晰，包含引言、主体内容、总结
2. 内容专业且有深度，适合技术博客发布
3. 使用 HTML 格式输出
4. 字数控制在 800-1500 字
5. 不要包含问题标题本身

{output_format}"""

        elif mode == "description":
            return f"""请根据以下问题标题和描述，生成一篇专业的技术文章：

问题标题：{title}

问题描述：{description}

要求：
1. 文章结构清晰，包含引言、主体内容、总结
2. 内容专业且有深度，针对问题描述进行展开
3. 使用 HTML 格式输出
4. 字数控制在 1000-2000 字
5. 不要包含问题标题和描述本身

{output_format}"""

        elif mode == "full":
            desc_part = f"\n问题描述：{description}" if description else ""

            return f"""请根据以下完整问题信息，生成一篇深度技术文章：

问题标题：{title}{desc_part}

要求：
1. 文章结构完整，包含引言、详细分析、案例说明、总结建议
2. 内容深度分析，适合专业技术社区
3. 使用 HTML 格式输出，可包含代码示例
4. 字数控制在 1500-3000 字
5. 不要包含原始问题信息

{output_format}"""

        else:
            return f"请根据问题「{title}」生成一篇技术文章。"

    def _parse_generated_content(self, content: str) -> tuple[str, str]:
        """解析 AI 生成的内容，提取摘要和正文

        Args:
            content: AI 生成的原始内容

        Returns:
            tuple[str, str]: (摘要, 正文)
        """
        import re

        summary = ""
        body = content

        # 尝试匹配 [摘要] 和 [正文] 格式
        summary_match = re.search(r"\[摘要\](.*?)(?=\[正文\]|$)", content, re.DOTALL)
        body_match = re.search(r"\[正文\](.*)", content, re.DOTALL)

        if summary_match and body_match:
            summary = summary_match.group(1).strip()
            body = body_match.group(1).strip()
        elif summary_match:
            # 只有摘要，没有正文标记
            summary = summary_match.group(1).strip()
            # 移除摘要部分，剩余的作为正文
            body = re.sub(r"\[摘要\].*?(?=\[正文\]|$)", "", content, flags=re.DOTALL).strip()
            if body_match:
                body = body_match.group(1).strip()
        else:
            # 如果没有按格式输出，尝试从正文提取摘要
            # 取前 200 个字符作为摘要
            clean_content = re.sub(r"[#*`\n]", " ", content)
            clean_content = re.sub(r"\s+", " ", clean_content).strip()
            if len(clean_content) > 200:
                summary = clean_content[:200] + "..."
            else:
                summary = clean_content

        return summary, body
