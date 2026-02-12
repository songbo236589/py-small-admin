"""
Content AI 路由 - 负责 AI 生成文章的接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.ai_controller import AIController

# 创建路由器
router = APIRouter(prefix="/ai", tags=["AI 生成"])
# 创建控制器实例
controller = AIController()


router.get(
    "/models",
    response_model=dict[str, Any],
    summary="获取可用 AI 模型列表",
)(controller.get_models)


router.post(
    "/generate_article",
    response_model=dict[str, Any],
    summary="AI 生成文章",
)(controller.generate_article)
