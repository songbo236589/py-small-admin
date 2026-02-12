"""
Content AI 控制器 - 负责 AI 生成文章的参数验证和业务逻辑协调
"""

from fastapi import Form
from fastapi.responses import JSONResponse

from Modules.common.libs.validation.decorators import validate_request_data
from Modules.content.services.ai_service import AIService
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
        id: int = Form(..., description="话题ID"),
        mode: str = Form(..., description="生成模式: title/description/full"),
        title: str = Form(..., description="问题标题"),
        description: str | None = Form(None, description="问题描述"),
        model: str | None = Form(None, description="指定模型（可选）"),
    ) -> JSONResponse:
        """使用 AI 生成文章

        Args:
            id: 话题ID
            mode: 生成模式
                - title: 仅根据标题生成
                - description: 根据标题和描述生成
                - full: 完整生成（包含标题和描述）
            title: 问题标题
            description: 问题描述（可选）
            model: 指定模型（可选，不指定则使用配置文件中的默认模型）

        Returns:
            JSONResponse: 生成的文章内容
        """
        return await self.ai_service.generate_article(id, mode, title, description, model)
