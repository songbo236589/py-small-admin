"""
公共路由 - 验证码、登录相关接口定义
"""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader, HTTPBearer

from Modules.admin.controllers.v1 import CommonController

# 创建路由器
router = APIRouter(prefix="/common", tags=["公共路由"])

bearer_security = HTTPBearer()

api_key_security = APIKeyHeader(name="X-API-Key")

# 创建控制器实例
controller = CommonController()

router.post(
    "/generate_captcha",
    response_model=dict[str, Any],
    summary="生成验证码",
)(controller.generate_captcha)

router.post(
    "/verify_captcha",
    response_model=dict[str, Any],
    summary="验证验证码",
)(controller.verify_captcha)

router.get(
    "/get_system_config",
    response_model=dict[str, Any],
    summary="获取项目配置信息",
)(controller.get_system_config)

router.post(
    "/login",
    response_model=dict[str, Any],
    summary="用户登录",
)(controller.login)

router.post(
    "/logout",
    response_model=dict[str, Any],
    summary="用户登出",
    dependencies=[Depends(bearer_security)],
)(controller.logout)


router.post(
    "/refresh",
    response_model=dict[str, Any],
    summary="刷新令牌",
)(controller.refresh_token)


router.get(
    "/current",
    response_model=dict[str, Any],
    summary="获取当前用户信息",
    dependencies=[Depends(bearer_security)],
)(controller.get_current_user_info)

router.post(
    "/change_password",
    response_model=dict[str, Any],
    summary="修改密码",
    dependencies=[Depends(bearer_security)],
)(controller.change_password)

router.get(
    "/get_menu_tree",
    response_model=dict[str, Any],
    summary="获取菜单树",
    dependencies=[Depends(bearer_security)],
)(controller.get_menu_tree)
