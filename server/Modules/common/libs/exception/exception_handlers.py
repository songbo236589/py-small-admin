"""
异常处理器模块

集中管理 FastAPI 应用的异常处理逻辑，提供统一的错误响应格式。
"""

import jwt
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from loguru import logger
from sqlalchemy.exc import DisconnectionError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..config import Config
from ..responses.response import error
from ..validation.exceptions import ValidationError


# 1. FastAPI 参数验证错误异常处理器
async def fastapi_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """处理 FastAPI 的 RequestValidationError（参数验证失败）"""
    logger.warning(f"FastAPI 参数验证失败: {exc.errors()}")

    # 提取错误信息
    error_messages = []
    for err in exc.errors():
        # 获取字段名和错误消息
        field = ".".join(str(x) for x in err["loc"])
        msg = err["msg"]
        error_messages.append(f"{field}: {msg}" if field else msg)

    # 合并所有错误消息
    error_detail = "; ".join(error_messages)

    return error(
        message=f"参数验证失败: {error_detail}",
        code=400,
        details=error_messages if Config.get("app.debug", False) else None,
    )


# 2. 自定义验证错误异常处理器
async def validation_exception_handler(request: Request, exc: ValidationError):
    """处理自定义验证错误异常"""
    return error(
        message=exc.message, code=400, details=exc.details if exc.details else None
    )


# 3. HTTP异常处理器
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTPException，使用自定义响应格式"""
    logger.info(f"HTTPException 处理器被调用: {exc.detail}, 状态码: {exc.status_code}")
    return error(message=exc.detail, code=exc.status_code)


# 4. 404路由未找到异常处理器
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """处理404路由未找到异常"""
    if exc.status_code == 404:
        logger.warning(f"404路由未找到: {request.url.path}")
        return error(
            message=f"请求的路径 '{request.url.path}' 不存在",
            code=404,
            details={"path": request.url.path}
            if Config.get("app.debug", False)
            else None,
        )
    # 如果不是404，让其他处理器处理
    raise exc


# 5. JWT异常处理器
async def jwt_exception_handler(request: Request, exc: jwt.InvalidTokenError):
    """处理JWT令牌相关异常"""
    logger.warning(f"JWT异常处理器被调用: {type(exc).__name__}: {exc}")
    return error(
        message="访问令牌无效或已过期",
        code=401,
        details=str(exc) if Config.get("app.debug", False) else None,
    )


# 6. 数据库异常处理器
async def database_exception_handler(request: Request, exc: DisconnectionError):
    """处理数据库连接异常"""
    logger.error(f"数据库连接异常: {exc}")
    return error(
        message="数据库连接失败，请稍后重试",
        code=503,
        details=str(exc) if Config.get("app.debug", False) else None,
    )


async def database_operational_exception_handler(
    request: Request, exc: OperationalError
):
    """处理数据库操作异常"""
    logger.error(f"数据库操作异常: {exc}")
    return error(
        message="数据库操作失败",
        code=500,
        details=str(exc) if Config.get("app.debug", False) else None,
    )


# 7. 值错误异常处理器
async def value_error_handler(request: Request, exc: ValueError):
    """处理值错误异常（主要用于参数验证）"""
    logger.warning(f"值错误异常: {exc}")
    return error(
        message=str(exc),
        code=400,
        details=str(exc) if Config.get("app.debug", False) else None,
    )


# 8. 通用异常处理器
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的通用异常"""
    import traceback

    logger.info(f"通用异常处理器被调用: {type(exc).__name__}: {exc}")

    # 记录详细信息并返回通用错误
    logger.error(f"未处理的异常: {type(exc).__name__}: {exc}")
    logger.error(f"异常堆栈: {traceback.format_exc()}")

    return error(
        message="服务器内部错误",
        code=500,
        details=str(exc) if Config.get("app.debug", False) else None,
    )


# 9. 注册异常处理器的函数
def register_exception_handlers(app):
    """
    注册所有异常处理器到 FastAPI 应用

    Args:
        app: FastAPI 应用实例
    """
    # FastAPI 参数验证错误（优先级最高）
    app.add_exception_handler(
        RequestValidationError, fastapi_validation_exception_handler
    )

    # 自定义验证异常
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # HTTP异常 - 注意：Starlette的HTTPException优先级更高
    app.add_exception_handler(StarletteHTTPException, not_found_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # JWT相关异常
    app.add_exception_handler(jwt.ExpiredSignatureError, jwt_exception_handler)
    app.add_exception_handler(jwt.DecodeError, jwt_exception_handler)
    app.add_exception_handler(jwt.InvalidTokenError, jwt_exception_handler)

    # 数据库相关异常
    app.add_exception_handler(DisconnectionError, database_exception_handler)
    app.add_exception_handler(OperationalError, database_operational_exception_handler)

    # 值错误异常
    app.add_exception_handler(ValueError, value_error_handler)

    # 通用异常（必须放在最后，作为兜底）
    app.add_exception_handler(Exception, general_exception_handler)
