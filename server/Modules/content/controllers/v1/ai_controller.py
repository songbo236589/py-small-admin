"""
Content AI 控制器 - 负责 AI 生成文章的参数验证和业务逻辑协调
"""

import json

from fastapi import Form, Request
from fastapi.responses import JSONResponse
from sqlmodel import select

from Modules.common.libs.auth.auth_helper import AuthHelper
from Modules.common.libs.database.sql.session import get_async_session
from Modules.common.libs.responses.response import error, success
from Modules.common.libs.validation.decorators import validate_request_data
from Modules.content.models.content_topic import ContentTopic
from Modules.content.services.ai_service import AIService
from Modules.content.services.article_service import ArticleService
from Modules.content.validators.ai_validator import AIGenerateArticleRequest


class AIController:
    """Content AI 控制器 - 负责 AI 生成文章的参数验证和业务逻辑协调"""

    def __init__(self):
        """初始化 AI 控制器"""
        self.ai_service = AIService()

    async def get_models(self) -> JSONResponse:
        """获取可用 AI 模型列表

        Returns:
            JSONResponse: 模型列表
        """
        return await self.ai_service.get_models()

    @validate_request_data(AIGenerateArticleRequest)
    async def generate_article(
        self,
        request: Request,
        id: int = Form(..., description="话题ID"),
        mode: str = Form(..., description="生成模式: title/description/full"),
        model: str = Form(..., description="指定 AI 模型"),
        variant_index: int = Form(0, description="变体索引，用于生成不同版本的文章"),
    ) -> JSONResponse:
        """使用 AI 生成文章并自动保存

        Args:
            request: FastAPI 请求对象
            id: 话题ID
            mode: 生成模式
                - title: 仅根据标题生成
                - description: 根据标题和描述生成
                - full: 完整生成（包含标题和描述）
            model: 指定模型（必填）
            variant_index: 变体索引（可选，用于批量生成时让 AI 从不同角度撰写）

        Returns:
            JSONResponse: 保存后的文章信息
        """
        # 从数据库获取话题信息
        async with get_async_session() as session:
            result = await session.execute(
                select(ContentTopic).where(ContentTopic.id == id)
            )
            topic = result.scalar_one_or_none()

            if not topic:
                return error("话题不存在")

        # 调用 AI 服务生成文章
        ai_result = await self.ai_service.generate_article(
            topic_id=id,
            mode=mode,
            title=topic.title,
            model=model,
            description=topic.description,
            variant_index=variant_index,
            question_url=topic.url,
        )

        # 如果 AI 生成失败，直接返回错误
        if ai_result.status_code != 200:
            return ai_result

        # 解析 AI 生成的文章数据
        article_data = json.loads(bytes(ai_result.body).decode()).get("data", {})

        # 获取当前用户ID
        author_id = AuthHelper().get_current_user_id(request)

        # 保存文章到数据库
        article_service = ArticleService()
        save_result = await article_service.add({
            "topic_id": article_data.get("topic_id"),
            "title": article_data.get("title"),
            "content": article_data.get("content"),
            "summary": article_data.get("summary"),
            "tag_ids": article_data.get("tag_ids", []),
            "author_id": author_id,
            "category_id": topic.category_id,  # 继承话题的分类
            "status": 0,  # 默认为草稿状态
        })

        # 如果保存失败，返回错误
        if save_result.status_code != 200:
            return save_result

        # 返回保存后的文章信息（包含文章ID）
        saved_article = json.loads(bytes(save_result.body).decode()).get("data", {})
        return success({
            "article_id": saved_article.get("id"),
            "topic_id": article_data.get("topic_id"),
            "title": article_data.get("title"),
            "content": article_data.get("content"),
            "summary": article_data.get("summary"),
            "tags": article_data.get("tags"),
            "model": article_data.get("model"),
        }, message="文章生成并保存成功")
