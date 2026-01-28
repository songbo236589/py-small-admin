"""
行业路由 - 定义行业相关的API路由
"""

from typing import Any

from fastapi import APIRouter

from Modules.quant.controllers.v1.quant_industry_controller import (
    QuantIndustryController,
)

# 创建路由器
router = APIRouter(prefix="/industry", tags=["行业管理"])

# 创建控制器实例
controller = QuantIndustryController()


# ==================== 行业列表和详情 ====================

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取行业列表",
)(controller.index)


router.get(
    "/simple",
    response_model=dict[str, Any],
    summary="获取行业简单列表（不分页，只返回 id 和 name）",
)(controller.simple_list)


# ==================== CRUD 操作 ====================

router.post(
    "/add",
    response_model=dict[str, Any],
    summary="添加行业",
)(controller.add)


router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="行业编辑页面数据",
)(controller.edit)


router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="更新行业信息",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="更新行业状态",
)(controller.set_status)

router.put(
    "/set_sort/{id}",
    response_model=dict[str, Any],
    summary="行业排序",
)(controller.set_sort)

router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="删除行业",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除行业",
)(controller.destroy_all)


# ==================== 数据同步接口 ====================

router.post(
    "/sync_list",
    response_model=dict[str, Any],
    summary="手动同步行业列表",
)(controller.sync_list)


router.post(
    "/sync_relation",
    response_model=dict[str, Any],
    summary="手动同步行业-股票关联关系",
)(controller.sync_relation)
