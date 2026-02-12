"""
Content 分类管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.content.controllers.v1.category_controller import CategoryController

# 创建路由器
router = APIRouter(prefix="/category", tags=["分类管理"])
# 创建控制器实例
controller = CategoryController()


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取分类列表",
)(controller.index)


router.get(
    "/tree",
    response_model=dict[str, Any],
    summary="获取分类树形结构",
)(controller.tree)


router.post(
    "/add",
    response_model=dict[str, Any],
    summary="分类添加",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="分类编辑页面数据",
)(controller.edit)


router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="分类编辑",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="分类状态",
)(controller.set_status)


router.put(
    "/set_sort/{id}",
    response_model=dict[str, Any],
    summary="分类排序",
)(controller.set_sort)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="分类删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除",
)(controller.destroy_all)
