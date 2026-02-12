"""
验证装饰器

提供请求数据验证的装饰器实现。
"""

import functools
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .exceptions import ValidationError, ValidationErrorCode


def validate_request_data(request_model_class: type) -> Callable:
    """
    请求数据验证装饰器 - 自动从函数参数中提取对应字段进行验证

    Args:
        request_model_class: Pydantic模型类，用于定义验证规则

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 获取模型字段信息 - 使用 Pydantic v2 的新 API
            model_fields = request_model_class.model_fields

            # 构建数据字典
            data_dict = {}
            for field_name, field_info in model_fields.items():
                # 从kwargs中获取对应参数值
                field_value = kwargs.get(field_name)
                if field_value is not None:
                    data_dict[field_name] = field_value
                elif field_info.is_required():
                    raise ValidationError(
                        f"缺少必需参数: {field_name}",
                        ValidationErrorCode.MISSING_REQUIRED_FIELD,
                    )

            # 使用Pydantic模型验证数据
            try:
                validated_instance = request_model_class(**data_dict)
                # 用验证后的数据更新 kwargs
                for field_name in model_fields:
                    if field_name in validated_instance.model_fields_set or field_name in data_dict:
                        kwargs[field_name] = getattr(validated_instance, field_name)
            except PydanticValidationError as e:
                # 处理SQLModel验证错误，提取用户友好的错误信息
                error_messages = []
                for error in e.errors():
                    # 获取字段名和错误消息
                    field = ".".join(str(x) for x in error["loc"])
                    msg = error["msg"]
                    error_messages.append(f"{field}: {msg}" if field else msg)

                # 合并所有错误消息
                error_detail = "; ".join(error_messages)
                raise ValidationError(
                    f"参数验证失败: {error_detail}",
                    ValidationErrorCode.VALIDATION_FAILED,
                    {"errors": error_messages},
                ) from None

            # 验证通过，执行原函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_body_data(request_model_class: type) -> Callable:
    """
    Body 参数验证装饰器 - 专门处理 Pydantic 模型作为请求体的验证

    与 validate_request_data 不同，这个装饰器不试图从 kwargs 中提取字段，
    而是直接验证 kwargs 中的 Pydantic 模型实例。

    Args:
        request_model_class: Pydantic模型类，用于定义验证规则

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 查找 kwargs 中的 Pydantic 模型实例
            model_instance = None
            param_name = None

            for name, value in kwargs.items():
                # 检查是否是指定类型的实例
                if isinstance(value, request_model_class):
                    model_instance = value
                    param_name = name
                    break

            # 如果没有找到对应的模型实例
            if model_instance is None:
                raise ValidationError(
                    f"缺少必需的请求体参数: {request_model_class.__name__}",
                    ValidationErrorCode.MISSING_REQUIRED_FIELD,
                )

            # 使用 Pydantic 模型的 model_validate 方法进行验证
            # 这会触发模型的验证器（如 field_validator）
            try:
                # 将实例转换为字典再重新验证，确保所有验证器都被执行
                model_dict = model_instance.model_dump()
                validated_instance = request_model_class.model_validate(model_dict)

                # 更新 kwargs 中的实例为验证后的实例
                if param_name is not None:
                    kwargs[param_name] = validated_instance

            except PydanticValidationError as e:
                # 处理验证错误，提取用户友好的错误信息
                error_messages = []
                for error in e.errors():
                    # 获取字段名和错误消息
                    field = ".".join(str(x) for x in error["loc"])
                    msg = error["msg"]
                    error_messages.append(f"{field}: {msg}" if field else msg)

                # 合并所有错误消息
                error_detail = "; ".join(error_messages)
                raise ValidationError(
                    f"请求体验证失败: {error_detail}",
                    ValidationErrorCode.VALIDATION_FAILED,
                    {"errors": error_messages},
                ) from None

            # 验证通过，执行原函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator
