"""
Content 文章管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.article_controller import ArticleController

# 创建路由器
router = APIRouter(prefix="/article", tags=["文章管理"])
# 创建控制器实例
controller = ArticleController()


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取文章列表",
)(controller.index)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="文章添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="文章编辑页面数据",
)(controller.edit)


router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="文章编辑",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="文章状态",
)(controller.set_status)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="文章删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除",
)(controller.destroy_all)
