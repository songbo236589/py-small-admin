"""
Quant模块路由包
"""

from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader, HTTPBearer

# 导入权限中间件
from Modules.admin.middleware import require_authentication

from .quant_concept import router as router_quant_concept
from .quant_concept_log import router as router_quant_concept_log
from .quant_industry import router as router_quant_industry
from .quant_industry_log import router as router_quant_industry_log
from .quant_stock import router as router_quant_stock
from .quant_stock_kline import router as router_quant_stock_kline

# 创建主路由器
main_router = APIRouter(prefix="/quant")
bearer_security = HTTPBearer()
api_key_security = APIKeyHeader(name="X-API-Key")

# 概念数据路由 - 需要用户管理权限
main_router.include_router(
    router_quant_concept,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
# 概念数据路由 - 需要用户管理权限
main_router.include_router(
    router_quant_industry,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
# 股票数据路由 - 需要用户管理权限
main_router.include_router(
    router_quant_stock,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
# 概念日志路由 - 需要用户管理权限
main_router.include_router(
    router_quant_concept_log,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
# 行业日志路由 - 需要用户管理权限
main_router.include_router(
    router_quant_industry_log,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)

# K线数据路由 - 需要用户管理权限
main_router.include_router(
    router_quant_stock_kline,
    dependencies=[
        Depends(bearer_security),
        Depends(api_key_security),
        Depends(require_authentication()),
    ],
)
