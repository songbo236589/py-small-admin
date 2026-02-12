"""
Admin 模块路由包
"""

from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader, HTTPBearer

# 导入权限中间件
from Modules.admin.middleware import require_authentication

from .admin import router as router_admin
from .common import router as router_common
from .email import router as router_email
from .group import router as router_group
from .rule import router as router_rule
from .sys_config import router as router_sys_config
from .upload import router as router_upload

# 创建主路由器
main_router = APIRouter(prefix="/admin")
bearer_security = HTTPBearer()
api_key_security = APIKeyHeader(name="X-API-Key")


# 验证码路由 - 不需要认证
main_router.include_router(
    router_common,
    dependencies=[Depends(api_key_security), Depends(require_authentication())],
)

# 管理员管理路由 - 需要用户管理权限
main_router.include_router(
    router_admin,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 角色管理路由 - 需要用户管理权限
main_router.include_router(
    router_group,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 菜单管理路由 - 需要用户管理权限
main_router.include_router(
    router_rule,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
# 系统配置路由 - 需要用户管理权限
main_router.include_router(
    router_sys_config,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
# 系统文件路由 - 需要用户管理权限
main_router.include_router(
    router_upload,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 邮件管理路由 - 需要用户管理权限
main_router.include_router(
    router_email,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
__all__ = ["main_router"]
