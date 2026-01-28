"""
统一响应服务

提供标准化的 API 响应格式，集成 FastAPI 框架。
支持成功响应、错误响应等常见场景。
"""

from datetime import datetime
from typing import Any

from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from ..config import Config
from .status_codes import StatusCodes, StatusMessage


class ResponseData(BaseModel):
    """响应数据模型"""

    code: int
    message: str
    data: Any | None = None
    timestamp: str


class ResponseService:
    """
    统一响应服务类

    提供标准化的 API 响应格式，集成日志记录和配置管理。
    支持成功响应、错误响应等常见场景。

    主要功能：
    - 统一响应格式
    - 集成日志记录
    - 支持配置化
    - 类型安全
    """

    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        try:
            from ..time import format_datetime, now

            return format_datetime(now())
        except Exception as e:
            # 降级到原始方式
            logger.warning(f"使用时区功能失败，降级到原始方式: {e}")
            return datetime.now().isoformat()

    @staticmethod
    def _should_include_details() -> bool:
        """判断是否应该包含详细信息（调试模式）"""
        return Config.get("app.debug", False)

    @staticmethod
    def _log_response(code: int, message: str | None, data: Any = None):
        """记录响应日志"""
        log_level = "INFO" if StatusCodes.is_success(code) else "ERROR"
        logger.bind(
            response_code=code,
            response_message=message or "",
            data_type=type(data).__name__ if data else None,
        ).log(log_level, f"API响应: {code} - {message or ''}")

    @staticmethod
    def success(
        data: Any = None,
        message: str | None = None,
        code: int = StatusCodes.OK,
        **kwargs,
    ) -> JSONResponse:
        """
        成功响应

        Args:
            data: 响应数据
            message: 响应消息，默认从配置获取
            code: HTTP 状态码，默认 200
            **kwargs: 额外的响应字段

        Returns:
            JSONResponse: FastAPI JSON 响应对象

        Examples:
            >>> ResponseService.success(data={"id": 1})
            >>> ResponseService.success(message="创建成功", code=StatusCodes.CREATED)
        """
        if message is None:
            message = StatusMessage.OPERATION_SUCCESS

        response_data = {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": ResponseService._get_timestamp(),
            **kwargs,
        }

        ResponseService._log_response(code, message, data)

        return JSONResponse(status_code=code, content=response_data)

    @staticmethod
    def error(
        message: str | None = None,
        code: int = StatusCodes.BAD_REQUEST,
        details: Any = None,
        **kwargs,
    ) -> JSONResponse:
        """
        错误响应

        Args:
            message: 错误消息，默认从配置获取
            code: HTTP 状态码，默认 400
            details: 错误详细信息，仅在调试模式下包含
            **kwargs: 额外的响应字段

        Returns:
            JSONResponse: FastAPI JSON 响应对象

        Examples:
            >>> ResponseService.error(message="参数错误", code=StatusCodes.BAD_REQUEST)
            >>> ResponseService.error(message="用户不存在", code=StatusCodes.NOT_FOUND)
        """
        if message is None:
            message = StatusMessage.OPERATION_FAILED

        response_data = {
            "code": code,
            "message": message,
            "data": None,
            "timestamp": ResponseService._get_timestamp(),
            **kwargs,
        }

        # 仅在调试模式下包含详细信息
        if details is not None and ResponseService._should_include_details():
            response_data["details"] = details

        ResponseService._log_response(code, message, details)

        return JSONResponse(status_code=code, content=response_data)


# 便捷函数导出
def success(
    data: Any = None,
    message: str | None = None,
    code: int = StatusCodes.OK,
    **kwargs,
) -> JSONResponse:
    """便捷函数：成功响应"""
    return ResponseService.success(data, message, code, **kwargs)


def error(
    message: str | None = None,
    code: int = StatusCodes.BAD_REQUEST,
    details: Any = None,
    **kwargs,
) -> JSONResponse:
    """便捷函数：错误响应"""
    return ResponseService.error(message, code, details, **kwargs)
