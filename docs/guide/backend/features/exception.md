# 异常处理

本文档介绍了项目的异常处理机制。

## 简介

项目使用 FastAPI 的异常处理机制，提供了统一的异常处理和错误响应。

## 异常类型

### 基础异常

```python
from fastapi import HTTPException

# 基本 HTTP 异常
raise HTTPException(status_code=404, detail="用户不存在")

# 带头部的异常
raise HTTPException(
    status_code=401,
    detail="未授权",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### 自定义业务异常

```python
from Modules.common.libs.exception.exceptions import (
    BusinessException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
)

# 资源不存在
raise NotFoundException("用户不存在")

# 验证失败
raise ValidationException("用户名格式不正确")

# 未授权
raise UnauthorizedException("没有权限访问")

# 业务异常
raise BusinessException("操作失败，请稍后重试")
```

## 全局异常处理

### 异常处理器

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from Modules.common.libs.exception.exceptions import BusinessException

app = FastAPI()

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
        },
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """资源不存在异常处理"""
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": exc.message,
            "data": None,
        },
    )
```

### 通用异常处理器

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误" if not debug else str(exc),
            "data": None,
        },
    )
```

## 自定义异常

### 定义异常类

```python
from typing import Any, Optional

class BaseException(Exception):
    """基础异常类"""

    def __init__(self, message: str, code: int = 400, data: Any = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)

class UserNotFoundException(BaseException):
    """用户不存在异常"""

    def __init__(self, user_id: int = None):
        message = f"用户 {user_id} 不存在" if user_id else "用户不存在"
        super().__init__(message, code=404)

class ValidationFailedException(BaseException):
    """验证失败异常"""

    def __init__(self, field: str, reason: str):
        message = f"{field} {reason}"
        super().__init__(message, code=422)
```

### 使用自定义异常

```python
def get_user(user_id: int):
    user = db.query_user(user_id)
    if user is None:
        raise UserNotFoundException(user_id)
    return user
```

## 异常日志

### 记录异常

```python
from loguru import logger

try:
    # 可能出错的代码
    result = risky_operation()
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
    raise BusinessException("操作失败")
```

### 结构化日志

```python
import structlog

logger = structlog.get_logger()

try:
    result = risky_operation()
except Exception as e:
    logger.error(
        "operation_failed",
        operation="risky_operation",
        error=str(e),
        error_type=type(e).__name__,
    )
    raise
```

## 异常响应格式

### 统一响应格式

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null,
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/api/user/123"
}
```

### 详细错误信息（开发环境）

```json
{
  "code": 500,
  "message": "数据库连接失败",
  "data": {
    "error_type": "ConnectionError",
    "error_detail": "Can't connect to database server",
    "stack_trace": "..."
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 异常处理最佳实践

### 1. 明确异常类型

```python
# 好
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValidationException("除数不能为零")
    return a / b

# 不好
def divide(a: int, b: int) -> float:
    return a / b  # 可能抛出 ZeroDivisionError
```

### 2. 提供有用的错误信息

```python
# 好
raise ValidationException("邮箱格式不正确，请输入有效的邮箱地址")

# 不好
raise ValidationException("错误")
```

### 3. 适当记录日志

```python
try:
    process_payment(order)
except PaymentException as e:
    # 业务异常，记录警告
    logger.warning(f"支付失败: {e}")
    raise
except Exception as e:
    # 系统异常，记录错误
    logger.error(f"支付处理异常: {e}", exc_info=True)
    raise BusinessException("支付处理失败")
```

### 4. 使用上下文管理器

```python
from contextlib import contextmanager

@contextmanager
def transaction():
    """事务管理"""
    try:
        yield
    except Exception:
        # 回滚事务
        db.rollback()
        raise
    else:
        # 提交事务
        db.commit()

# 使用
with transaction():
    create_order()
    process_payment()
```

### 5. 异常链

```python
try:
    result = external_api_call()
except ExternalAPIError as e:
    # 保留原始异常
    raise BusinessException("外部服务调用失败") from e
```

## 常见错误码

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 400 | 请求参数错误 | 400 |
| 401 | 未授权 | 401 |
| 403 | 禁止访问 | 403 |
| 404 | 资源不存在 | 404 |
| 422 | 数据验证失败 | 422 |
| 500 | 服务器内部错误 | 500 |
| 503 | 服务暂时不可用 | 503 |

## 相关文档

- [数据验证](./validation.md)
- [日志管理](./log.md)
