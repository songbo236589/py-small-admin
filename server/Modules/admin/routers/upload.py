"""
Admin 文件管理路由 - 只负责接口定义
"""

from typing import Any

from fastapi import APIRouter

from Modules.admin.controllers.v1.upload_controller import UploadController

# 创建路由器
router = APIRouter(prefix="/upload", tags=["文件管理"])
# 创建控制器实例
controller = UploadController()


router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取角色列表或搜索角色（统一接口）",
)(controller.index)

router.delete(
    "/destroy/{id}",
    response_model=dict[str, Any],
    summary="角色删除",
)(controller.destroy)


router.delete(
    "/destroy_all",
    response_model=dict[str, Any],
    summary="角色批量删除",
)(controller.destroy_all)


router.post(
    "/file",
    response_model=dict[str, Any],
    summary="上传文件接口",
)(controller.file)
