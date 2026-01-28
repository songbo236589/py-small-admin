# Responses 模块使用文档

## 概述

`libs/responses` 模块是一个强大的响应处理库，提供了标准化的 API 响应格式，集成 FastAPI 框架。该模块支持成功响应、错误响应等常见场景，并提供统一的响应格式、日志记录和配置管理功能。

该模块主要包含以下文件：

- `response.py`: 响应服务类和便捷函数
- `status_codes.py`: HTTP 状态码常量定义和响应消息

## 主要功能

- 统一响应格式
- 集成日志记录
- 支持配置化
- 类型安全
- 标准化 HTTP 状态码
- 预定义响应消息
- 调试模式支持

## 安装与导入

```python
from Modules.common.libs.responses import (
    # 响应服务类
    ResponseService,
    
    # 便捷函数
    success,
    error,
    
    # 状态码常量
    StatusCodes,
    StatusMessage,
    
    # 响应数据模型
    ResponseData,
)
```

## 响应服务类

### ResponseService 类

`ResponseService` 是核心的响应服务类，提供标准化的 API 响应格式。

#### 成功响应

```python
from Modules.common.libs.responses import ResponseService, StatusCodes

# 基本成功响应
response = ResponseService.success()
# 返回: {"code": 200, "message": "操作成功", "data": null, "timestamp": "2023-12-25 10:30:00"}

# 带数据的成功响应
user_data = {"id": 1, "name": "张三", "email": "zhangsan@example.com"}
response = ResponseService.success(data=user_data)
# 返回: {"code": 200, "message": "操作成功", "data": {"id": 1, "name": "张三"}, "timestamp": "..."}

# 自定义消息和状态码
response = ResponseService.success(
    data={"id": 1},
    message="用户创建成功",
    code=StatusCodes.CREATED
)
# 返回: {"code": 201, "message": "用户创建成功", "data": {"id": 1}, "timestamp": "..."}

# 添加额外字段
response = ResponseService.success(
    data={"id": 1},
    message="查询成功",
    extra_field="额外信息"
)
# 返回: {"code": 200, "message": "查询成功", "data": {"id": 1}, "timestamp": "...", "extra_field": "额外信息"}
```

#### 错误响应

```python
from Modules.common.libs.responses import ResponseService, StatusCodes

# 基本错误响应
response = ResponseService.error()
# 返回: {"code": 400, "message": "操作失败", "data": null, "timestamp": "2023-12-25 10:30:00"}

# 自定义消息和状态码
response = ResponseService.error(
    message="用户不存在",
    code=StatusCodes.NOT_FOUND
)
# 返回: {"code": 404, "message": "用户不存在", "data": null, "timestamp": "..."}

# 带详细信息的错误响应（仅在调试模式下显示）
response = ResponseService.error(
    message="参数验证失败",
    code=StatusCodes.BAD_REQUEST,
    details={"field": "email", "error": "邮箱格式不正确"}
)
# 调试模式返回: {"code": 400, "message": "参数验证失败", "data": null, "timestamp": "...", "details": {...}}
# 生产模式返回: {"code": 400, "message": "参数验证失败", "data": null, "timestamp": "..."}

# 添加额外字段
response = ResponseService.error(
    message="权限不足",
    code=StatusCodes.FORBIDDEN,
    required_permission="admin"
)
# 返回: {"code": 403, "message": "权限不足", "data": null, "timestamp": "...", "required_permission": "admin"}
```

## 状态码常量

### StatusCodes 类

`StatusCodes` 类提供了标准化的 HTTP 状态码常量，避免在代码中使用魔法数字。

#### 成功状态码 (2xx)

```python
from Modules.common.libs.responses import StatusCodes

# 常用成功状态码
print(StatusCodes.OK)              # 200 - 请求成功
print(StatusCodes.CREATED)          # 201 - 资源创建成功
print(StatusCodes.ACCEPTED)         # 202 - 请求已接受，但尚未处理
print(StatusCodes.NO_CONTENT)       # 204 - 请求成功，无返回内容
print(StatusCodes.PARTIAL_CONTENT)  # 206 - 部分内容
```

#### 重定向状态码 (3xx)

```python
# 重定向状态码
print(StatusCodes.MOVED_PERMANENTLY)  # 301 - 永久重定向
print(StatusCodes.FOUND)              # 302 - 临时重定向
print(StatusCodes.NOT_MODIFIED)       # 304 - 资源未修改
```

#### 客户端错误状态码 (4xx)

```python
# 常用客户端错误状态码
print(StatusCodes.BAD_REQUEST)            # 400 - 请求参数错误
print(StatusCodes.UNAUTHORIZED)           # 401 - 未授权
print(StatusCodes.FORBIDDEN)              # 403 - 禁止访问
print(StatusCodes.NOT_FOUND)              # 404 - 资源不存在
print(StatusCodes.METHOD_NOT_ALLOWED)     # 405 - 方法不允许
print(StatusCodes.NOT_ACCEPTABLE)         # 406 - 不可接受
print(StatusCodes.REQUEST_TIMEOUT)         # 408 - 请求超时
print(StatusCodes.CONFLICT)                # 409 - 资源冲突
print(StatusCodes.GONE)                    # 410 - 资源已永久删除
print(StatusCodes.PAYLOAD_TOO_LARGE)      # 413 - 请求体过大
print(StatusCodes.UNSUPPORTED_MEDIA_TYPE) # 415 - 不支持的媒体类型
print(StatusCodes.TOO_MANY_REQUESTS)       # 429 - 请求过多
```

#### 服务器错误状态码 (5xx)

```python
# 服务器错误状态码
print(StatusCodes.INTERNAL_SERVER_ERROR)    # 500 - 服务器内部错误
print(StatusCodes.NOT_IMPLEMENTED)          # 501 - 功能未实现
print(StatusCodes.BAD_GATEWAY)              # 502 - 网关错误
print(StatusCodes.SERVICE_UNAVAILABLE)      # 503 - 服务不可用
print(StatusCodes.GATEWAY_TIMEOUT)          # 504 - 网关超时
print(StatusCodes.HTTP_VERSION_NOT_SUPPORTED) # 505 - HTTP 版本不支持
```

#### 状态码判断方法

```python
# 判断状态码类型
print(StatusCodes.is_success(200))      # True
print(StatusCodes.is_success(201))      # True
print(StatusCodes.is_success(400))      # False

print(StatusCodes.is_client_error(400)) # True
print(StatusCodes.is_client_error(404)) # True
print(StatusCodes.is_client_error(500)) # False

print(StatusCodes.is_server_error(500)) # True
print(StatusCodes.is_server_error(503)) # True
print(StatusCodes.is_server_error(400)) # False

# 获取状态码分类
print(StatusCodes.get_category(200))    # "success"
print(StatusCodes.get_category(404))    # "client_error"
print(StatusCodes.get_category(500))    # "server_error"
print(StatusCodes.get_category(100))    # "other"
```

## 响应消息常量

### StatusMessage 类

`StatusMessage` 类提供了预定义的响应消息，用于存储增删改查的响应文案。

#### CRUD 操作消息

```python
from Modules.common.libs.responses import StatusMessage

# 创建操作消息
print(StatusMessage.CREATE_SUCCESS)  # "创建成功"
print(StatusMessage.CREATE_FAILED)    # "创建失败"
print(StatusMessage.CREATE_ERROR)     # "创建错误"

# 查询操作消息
print(StatusMessage.GET_SUCCESS)        # "获取成功"
print(StatusMessage.GET_FAILED)         # "获取失败"
print(StatusMessage.GET_LIST_SUCCESS)    # "获取列表成功"
print(StatusMessage.GET_LIST_FAILED)     # "获取列表失败"
print(StatusMessage.NOT_FOUND)           # "资源不存在"

# 更新操作消息
print(StatusMessage.UPDATE_SUCCESS)  # "更新成功"
print(StatusMessage.UPDATE_FAILED)    # "更新失败"
print(StatusMessage.UPDATE_ERROR)     # "更新错误"

# 删除操作消息
print(StatusMessage.DELETE_SUCCESS)         # "删除成功"
print(StatusMessage.DELETE_FAILED)         # "删除失败"
print(StatusMessage.BATCH_DELETE_SUCCESS)  # "批量删除成功"
print(StatusMessage.BATCH_DELETE_FAILED)   # "批量删除失败"
```

#### 通用操作消息

```python
# 通用操作消息
print(StatusMessage.OPERATION_SUCCESS)  # "操作成功"
print(StatusMessage.OPERATION_FAILED)    # "操作失败"
print(StatusMessage.OPERATION_ERROR)     # "操作错误"
print(StatusMessage.SAVE_SUCCESS)        # "保存成功"
print(StatusMessage.SAVE_FAILED)         # "保存失败"
```

#### 验证和权限消息

```python
# 验证相关消息
print(StatusMessage.VALIDATION_ERROR)      # "数据验证失败"
print(StatusMessage.PARAM_ERROR)           # "参数错误"
print(StatusMessage.MISSING_REQUIRED_PARAM) # "缺少必需参数"
print(StatusMessage.INVALID_FORMAT)        # "格式不正确"

# 权限相关消息
print(StatusMessage.UNAUTHORIZED)    # "未授权访问"
print(StatusMessage.FORBIDDEN)       # "禁止访问"
print(StatusMessage.TOKEN_EXPIRED)   # "令牌已过期"
print(StatusMessage.TOKEN_INVALID)   # "令牌无效"
```

#### 系统相关消息

```python
# 系统相关消息
print(StatusMessage.SERVER_ERROR)    # "服务器内部错误"
print(StatusMessage.SYSTEM_BUSY)     # "系统繁忙，请稍后再试"
print(StatusMessage.NETWORK_ERROR)   # "网络错误"
print(StatusMessage.TIMEOUT)         # "请求超时"
```

#### 动态消息获取方法

```python
# 根据操作结果获取消息
print(StatusMessage.get_create_message(True))   # "创建成功"
print(StatusMessage.get_create_message(False))  # "创建失败"

print(StatusMessage.get_get_message(True, False))    # "获取成功"
print(StatusMessage.get_get_message(True, True))     # "获取列表成功"
print(StatusMessage.get_get_message(False, False))   # "获取失败"

print(StatusMessage.get_update_message(True))   # "更新成功"
print(StatusMessage.get_update_message(False))  # "更新失败"

print(StatusMessage.get_delete_message(True, False))   # "删除成功"
print(StatusMessage.get_delete_message(True, True))    # "批量删除成功"
print(StatusMessage.get_delete_message(False, False))  # "删除失败"

print(StatusMessage.get_operation_message(True))   # "操作成功"
print(StatusMessage.get_operation_message(False))  # "操作失败"
```

## 便捷函数

模块提供了便捷函数，简化响应操作：

```python
from Modules.common.libs.responses import success, error, StatusCodes

# 便捷成功响应
response = success(data={"id": 1})
# 等同于 ResponseService.success(data={"id": 1})

# 便捷错误响应
response = error(message="参数错误", code=StatusCodes.BAD_REQUEST)
# 等同于 ResponseService.error(message="参数错误", code=StatusCodes.BAD_REQUEST)
```

## 实际应用场景

### 1. FastAPI 路由中的使用

```python
from fastapi import FastAPI, HTTPException, Depends
from Modules.common.libs.responses import success, error, StatusCodes, StatusMessage
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """创建用户"""
    try:
        # 模拟数据库操作
        if not user_data.name or not user_data.email:
            return error(
                message=StatusMessage.MISSING_REQUIRED_PARAM,
                code=StatusCodes.BAD_REQUEST
            )
        
        # 模拟创建用户
        new_user = {
            "id": 1,
            "name": user_data.name,
            "email": user_data.email
        }
        
        return success(
            data=new_user,
            message=StatusMessage.CREATE_SUCCESS,
            code=StatusCodes.CREATED
        )
    except Exception as e:
        return error(
            message=StatusMessage.CREATE_ERROR,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR
        )

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """获取用户信息"""
    try:
        # 模拟数据库查询
        if user_id == 999:  # 模拟用户不存在
            return error(
                message=StatusMessage.NOT_FOUND,
                code=StatusCodes.NOT_FOUND
            )
        
        # 模拟查询结果
        user = {
            "id": user_id,
            "name": "张三",
            "email": "zhangsan@example.com"
        }
        
        return success(
            data=user,
            message=StatusMessage.GET_SUCCESS
        )
    except Exception as e:
        return error(
            message=StatusMessage.GET_ERROR,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR
        )

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserCreate):
    """更新用户信息"""
    try:
        # 模拟数据库更新
        if user_id == 999:  # 模拟用户不存在
            return error(
                message=StatusMessage.NOT_FOUND,
                code=StatusCodes.NOT_FOUND
            )
        
        # 模拟更新结果
        updated_user = {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email
        }
        
        return success(
            data=updated_user,
            message=StatusMessage.UPDATE_SUCCESS
        )
    except Exception as e:
        return error(
            message=StatusMessage.UPDATE_ERROR,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR
        )

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """删除用户"""
    try:
        # 模拟数据库删除
        if user_id == 999:  # 模拟用户不存在
            return error(
                message=StatusMessage.NOT_FOUND,
                code=StatusCodes.NOT_FOUND
            )
        
        return success(
            message=StatusMessage.DELETE_SUCCESS,
            code=StatusCodes.NO_CONTENT
        )
    except Exception as e:
        return error(
            message=StatusMessage.DELETE_ERROR,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR
        )
```

### 2. 中间件中的使用

```python
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from Modules.common.libs.responses import error, StatusCodes, StatusMessage
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录请求日志
        logger.info(f"请求完成: {request.method} {request.url} - "
                   f"状态码: {response.status_code} - 处理时间: {process_time:.4f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        
        # 记录错误日志
        logger.error(f"请求失败: {request.method} {request.url} - "
                    f"处理时间: {process_time:.4f}s - 错误: {str(e)}")
        
        # 返回统一错误响应
        return error(
            message=StatusMessage.SERVER_ERROR,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR,
            process_time=process_time
        )

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """认证中间件"""
    # 跳过不需要认证的路径
    if request.url.path in ["/docs", "/openapi.json", "/health"]:
        return await call_next(request)
    
    # 检查认证头
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return error(
            message=StatusMessage.UNAUTHORIZED,
            code=StatusCodes.UNAUTHORIZED
        )
    
    # 验证令牌（简化示例）
    try:
        token = auth_header.split(" ")[1]
        if not validate_token(token):
            return error(
                message=StatusMessage.TOKEN_INVALID,
                code=StatusCodes.UNAUTHORIZED
            )
    except Exception:
        return error(
            message=StatusMessage.TOKEN_INVALID,
            code=StatusCodes.UNAUTHORIZED
        )
    
    return await call_next(request)

def validate_token(token: str) -> bool:
    """验证令牌（简化示例）"""
    # 实际项目中应该实现真正的令牌验证逻辑
    return token == "valid_token"
```

### 3. 异常处理器中的使用

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from Modules.common.libs.responses import error, StatusCodes, StatusMessage

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return error(
        message=exc.detail,
        code=exc.status_code
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """值错误处理器"""
    return error(
        message=str(exc),
        code=StatusCodes.BAD_REQUEST,
        details={"exception_type": "ValueError"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    return error(
        message=StatusMessage.SERVER_ERROR,
        code=StatusCodes.INTERNAL_SERVER_ERROR,
        details={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
    )
```

### 4. 数据验证中的使用

```python
from pydantic import BaseModel, validator
from typing import Optional
from Modules.common.libs.responses import error, StatusCodes, StatusMessage

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("姓名至少需要2个字符")
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError("邮箱格式不正确")
        return v.lower()
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError("年龄必须在0-150之间")
        return v

@app.post("/users")
async def create_user(user_data: dict):
    """创建用户（手动验证）"""
    try:
        # 手动验证数据
        if not user_data.get('name'):
            return error(
                message=StatusMessage.MISSING_REQUIRED_PARAM,
                details={"field": "name", "error": "姓名为必填项"},
                code=StatusCodes.BAD_REQUEST
            )
        
        if not user_data.get('email'):
            return error(
                message=StatusMessage.MISSING_REQUIRED_PARAM,
                details={"field": "email", "error": "邮箱为必填项"},
                code=StatusCodes.BAD_REQUEST
            )
        
        # 验证邮箱格式
        email = user_data['email']
        if '@' not in email:
            return error(
                message=StatusMessage.INVALID_FORMAT,
                details={"field": "email", "error": "邮箱格式不正确"},
                code=StatusCodes.BAD_REQUEST
            )
        
        # 创建用户逻辑...
        
        return success(
            data={"id": 1, **user_data},
            message=StatusMessage.CREATE_SUCCESS,
            code=StatusCodes.CREATED
        )
    except Exception as e:
        return error(
            message=StatusMessage.CREATE_ERROR,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR
        )
```

## 高级用法

### 1. 自定义响应格式

```python
from fastapi import FastAPI
from Modules.common.libs.responses import ResponseService, StatusCodes

class CustomResponseService(ResponseService):
    """自定义响应服务类"""
    
    @staticmethod
    def success(data=None, message=None, code=StatusCodes.OK, **kwargs):
        """自定义成功响应格式"""
        if message is None:
            message = StatusMessage.OPERATION_SUCCESS
        
        response_data = {
            "status": "success",
            "code": code,
            "message": message,
            "result": data,
            "timestamp": ResponseService._get_timestamp(),
            "version": "v1.0",
            **kwargs
        }
        
        ResponseService._log_response(code, message, data)
        
        return JSONResponse(status_code=code, content=response_data)
    
    @staticmethod
    def error(message=None, code=StatusCodes.BAD_REQUEST, details=None, **kwargs):
        """自定义错误响应格式"""
        if message is None:
            message = StatusMessage.OPERATION_FAILED
        
        response_data = {
            "status": "error",
            "code": code,
            "message": message,
            "error": {
                "type": "api_error",
                "details": details if ResponseService._should_include_details() else None
            },
            "timestamp": ResponseService._get_timestamp(),
            "version": "v1.0",
            **kwargs
        }
        
        ResponseService._log_response(code, message, details)
        
        return JSONResponse(status_code=code, content=response_data)

# 使用自定义响应服务
@app.get("/custom-success")
async def custom_success():
    return CustomResponseService.success(data={"custom": "data"})

@app.get("/custom-error")
async def custom_error():
    return CustomResponseService.error(
        message="自定义错误",
        details={"custom_detail": "详细信息"}
    )
```

### 2. 响应拦截器

```python
from functools import wraps
from Modules.common.libs.responses import success, error, StatusCodes

def api_response(func):
    """API响应装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            
            # 如果已经是响应对象，直接返回
            if isinstance(result, JSONResponse):
                return result
            
            # 包装为成功响应
            return success(data=result)
        except ValueError as e:
            # 处理值错误
            return error(
                message=str(e),
                code=StatusCodes.BAD_REQUEST
            )
        except PermissionError as e:
            # 处理权限错误
            return error(
                message=str(e),
                code=StatusCodes.FORBIDDEN
            )
        except FileNotFoundError as e:
            # 处理资源不存在错误
            return error(
                message=str(e),
                code=StatusCodes.NOT_FOUND
            )
        except Exception as e:
            # 处理其他异常
            return error(
                message="服务器内部错误",
                details=str(e),
                code=StatusCodes.INTERNAL_SERVER_ERROR
            )
    
    return wrapper

# 使用装饰器
@api_response
async def get_user_data(user_id: int):
    """获取用户数据"""
    if user_id <= 0:
        raise ValueError("用户ID必须大于0")
    
    if user_id == 999:
        raise FileNotFoundError("用户不存在")
    
    # 模拟数据查询
    return {"id": user_id, "name": f"用户{user_id}"}
```

### 3. 分页响应

```python
from typing import List, Any, Dict
from Modules.common.libs.responses import success, StatusMessage

class PaginatedResponse:
    """分页响应工具类"""
    
    @staticmethod
    def create(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = None
    ):
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        
        data = {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return success(
            data=data,
            message=message or StatusMessage.GET_LIST_SUCCESS
        )

@app.get("/users")
async def get_users(page: int = 1, page_size: int = 10):
    """获取用户列表（分页）"""
    try:
        # 模拟数据库查询
        total = 100  # 总记录数
        start = (page - 1) * page_size
        end = start + page_size
        
        # 模拟分页数据
        users = [
            {"id": i, "name": f"用户{i}"}
            for i in range(start + 1, min(end, total) + 1)
        ]
        
        return PaginatedResponse.create(
            items=users,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        return error(
            message=StatusMessage.GET_LIST_FAILED,
            details=str(e),
            code=StatusCodes.INTERNAL_SERVER_ERROR
        )
```

## 最佳实践

### 1. 统一响应格式

在整个项目中使用统一的响应格式，保持一致性：

```python
# 好的做法
return success(data=result, message="操作成功")

# 避免的做法
return {"success": True, "data": result}
return {"code": 200, "result": result, "msg": "success"}
```

### 2. 合理使用状态码

根据 HTTP 标准合理使用状态码：

```python
# 成功操作
return success(data=user, code=StatusCodes.OK)           # 获取资源
return success(data=user, code=StatusCodes.CREATED)       # 创建资源
return success(message="操作成功", code=StatusCodes.NO_CONTENT)  # 删除资源

# 错误情况
return error(message="参数错误", code=StatusCodes.BAD_REQUEST)     # 客户端错误
return error(message="服务器错误", code=StatusCodes.INTERNAL_SERVER_ERROR)  # 服务器错误
```

### 3. 调试模式下的详细信息

在生产环境中避免暴露敏感信息：

```python
# 配置文件中设置
DEBUG = False  # 生产环境设为 False

# 代码中使用
return error(
    message="操作失败",
    details=error_details,  # 仅在调试模式下显示
    code=StatusCodes.INTERNAL_SERVER_ERROR
)
```

### 4. 日志记录

利用内置的日志记录功能：

```python
# 响应会自动记录日志，无需额外操作
# 成功响应记录为 INFO 级别
# 错误响应记录为 ERROR 级别
```

## 常见问题

### Q: 如何添加自定义字段到响应中？

A: 可以通过 `**kwargs` 参数添加自定义字段：

```python
return success(
    data={"id": 1},
    custom_field="自定义值",
    another_field={"nested": "data"}
)
```

### Q: 如何在响应中包含请求ID？

A: 可以使用中间件添加请求ID：

```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    # 如果是JSONResponse且是我们的格式，添加request_id
    if isinstance(response, JSONResponse):
        content = response.body.decode()
        if '"code"' in content:  # 简单判断是否为我们的响应格式
            data = json.loads(content)
            data["request_id"] = request_id
            response.body = json.dumps(data).encode()
    
    return response
```

### Q: 如何处理国际化响应消息？

A: 可以创建多语言消息类：

```python
class I18nStatusMessage:
    """国际化响应消息"""
    
    @staticmethod
    def get_message(key: str, language: str = "zh") -> str:
        messages = {
            "zh": {
                "create_success": "创建成功",
                "create_failed": "创建失败",
                # ... 其他中文消息
            },
            "en": {
                "create_success": "Created successfully",
                "create_failed": "Creation failed",
                # ... 其他英文消息
            }
        }
        return messages.get(language, {}).get(key, "Unknown message")

# 使用
language = request.headers.get("Accept-Language", "zh")
message = I18nStatusMessage.get_message("create_success", language)
return success(message=message)
```

## API 参考

### ResponseService 类方法

| 方法 | 描述 | 参数 |
|------|------|------|
| `success(data, message, code, **kwargs)` | 创建成功响应 | `data`: 响应数据<br>`message`: 响应消息<br>`code`: HTTP状态码<br>`**kwargs`: 额外字段 |
| `error(message, code, details, **kwargs)` | 创建错误响应 | `message`: 错误消息<br>`code`: HTTP状态码<br>`details`: 错误详情<br>`**kwargs`: 额外字段 |

### StatusCodes 类常量

| 类别 | 常量 | 值 | 描述 |
|------|------|-----|------|
| 成功 | `OK` | 200 | 请求成功 |
| 成功 | `CREATED` | 201 | 资源创建成功 |
| 成功 | `ACCEPTED` | 202 | 请求已接受 |
| 成功 | `NO_CONTENT` | 204 | 请求成功，无内容 |
| 客户端错误 | `BAD_REQUEST` | 400 | 请求参数错误 |
| 客户端错误 | `UNAUTHORIZED` | 401 | 未授权 |
| 客户端错误 | `FORBIDDEN` | 403 | 禁止访问 |
| 客户端错误 | `NOT_FOUND` | 404 | 资源不存在 |
| 服务器错误 | `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |
| 服务器错误 | `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |

### StatusMessage 类常量

| 类别 | 常量 | 值 |
|------|------|-----|
| 创建 | `CREATE_SUCCESS` | "创建成功" |
| 创建 | `CREATE_FAILED` | "创建失败" |
| 查询 | `GET_SUCCESS` | "获取成功" |
| 查询 | `GET_LIST_SUCCESS` | "获取列表成功" |
| 查询 | `NOT_FOUND` | "资源不存在" |
| 更新 | `UPDATE_SUCCESS` | "更新成功" |
| 更新 | `UPDATE_FAILED` | "更新失败" |
| 删除 | `DELETE_SUCCESS` | "删除成功" |
| 删除 | `BATCH_DELETE_SUCCESS` | "批量删除成功" |
| 通用 | `OPERATION_SUCCESS` | "操作成功" |
| 通用 | `OPERATION_FAILED` | "操作失败" |
| 验证 | `VALIDATION_ERROR` | "数据验证失败" |
| 验证 | `PARAM_ERROR` | "参数错误" |
| 权限 | `UNAUTHORIZED` | "未授权访问" |
| 权限 | `FORBIDDEN` | "禁止访问" |
| 系统 | `SERVER_ERROR` | "服务器内部错误" |
| 系统 | `SYSTEM_BUSY` | "系统繁忙，请稍后再试" |

## 版本历史

- v1.0.0: 初始版本，提供基本的响应服务功能
- v1.1.0: 添加状态码常量和响应消息常量
- v1.2.0: 增强日志记录和调试模式支持
- v1.3.0: 优化响应格式和错误处理