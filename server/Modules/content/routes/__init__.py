"""
Content模块路由包
"""

from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader, HTTPBearer

# 导入权限中间件
from Modules.admin.middleware import require_authentication

from .article import router as router_article
from .category import router as router_category
from .extension import extension_router
from .platform_account import router as router_platform_account
from .publish import router as router_publish
from .tag import router as router_tag

# 创建主路由器
main_router = APIRouter(prefix="/content")
bearer_security = HTTPBearer()
api_key_security = APIKeyHeader(name="X-API-Key")


# 文章管理路由 - 需要认证
main_router.include_router(
    router_article,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 分类管理路由 - 需要认证
main_router.include_router(
    router_category,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 标签管理路由 - 需要认证
main_router.include_router(
    router_tag,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 平台账号管理路由 - 需要认证
main_router.include_router(
    router_platform_account,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 发布管理路由 - 需要认证
main_router.include_router(
    router_publish,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# 浏览器扩展路由 - 公开接口（不需要认证）
main_router.include_router(extension_router)


__all__ = ["main_router"]
