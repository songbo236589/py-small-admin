"""
股票路由 - 定义股票相关的API路由
"""

from typing import Any

from fastapi import APIRouter

from Modules.quant.controllers.v1.quant_stock_controller import QuantStockController

# 创建路由器
router = APIRouter(prefix="/stock", tags=["股票管理"])

# 创建控制器实例
controller = QuantStockController()


# ==================== 股票列表和详情 ====================

router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取股票列表",
)(controller.index)

# ==================== CRUD 操作 ====================

router.post(
    "/add",
    response_model=dict[str, Any],
    summary="添加股票",
)(controller.add)
router.get(
    "/edit/{id}",
    response_model=dict[str, Any],
    summary="获取股票详情",
)(controller.edit)

router.put(
    "/update/{id}",
    response_model=dict[str, Any],
    summary="更新股票信息",
)(controller.update)


router.put(
    "/set_status/{id}",
    response_model=dict[str, Any],
    summary="更新股票状态",
)(controller.set_status)


router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="删除股票",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="批量删除股票",
)(controller.destroy_all)


# ==================== 数据同步接口 ====================

router.post(
    "/sync_stock_list",
    response_model=dict[str, Any],
    summary="手动同步股票列表",
)(controller.sync_stock_list)
