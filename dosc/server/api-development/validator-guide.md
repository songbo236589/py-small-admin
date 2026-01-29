# 验证器开发指南

本文档详细介绍如何开发验证器层。

## 概述

验证器层负责定义请求和响应的数据模型，使用 Pydantic 实现。

## 验证器结构

### 基本结构

```python
from pydantic import BaseModel, Field

class AdminAddRequest(BaseModel):
    """管理员添加请求"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    status: int = Field(default=1, ge=0, le=1)
```

### 使用验证器

```python
from Modules.admin.validators.admin_validator import AdminAddRequest

@validate_request_data(AdminAddRequest)
async def add(self, username: str, password: str):
    # 参数已验证
    pass
```

## 字段验证

### 必填字段

```python
username: str = Field(..., description="用户名")
```

### 可选字段

```python
phone: str | None = Field(None, description="手机号")
```

### 字符串长度

```python
username: str = Field(
    ...,
    min_length=3,
    max_length=50,
    description="用户名"
)
```

### 数值范围

```python
status: int = Field(
    default=1,
    ge=0,  # 大于等于
    le=1,  # 小于等于
    description="状态"
)
```

### 正则表达式

```python
from pydantic import field_validator

class AdminAddRequest(BaseModel):
    """管理员添加请求"""

    username: str = Field(..., description="用户名")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
```

### 邮箱验证

```python
from pydantic import EmailStr

class UserAddRequest(BaseModel):
    """用户添加请求"""

    email: EmailStr = Field(..., description="邮箱")
```

### URL 验证

```python
from pydantic import HttpUrl

class WebsiteAddRequest(BaseModel):
    """网站添加请求"""

    url: HttpUrl = Field(..., description="网站地址")
```

## 常用验证器

### 分页请求

```python
class PaginationRequest(BaseModel):
    """分页请求"""

    page: int = Field(default=1, ge=1, description="页码")
    limit: int = Field(default=20, ge=1, le=100, description="每页数量")
```

### ID 请求

```python
class IdRequest(BaseModel):
    """ID 请求"""

    id: int = Field(..., ge=1, description="ID")
```

### ID 数组请求

```python
class IdArrayRequest(BaseModel):
    """ID 数组请求"""

    id_array: list[int] = Field(..., min_length=1, description="ID 数组")
```

### 状态请求

```python
class ListStatusRequest(BaseModel):
    """状态请求"""

    status: int = Field(..., ge=0, le=1, description="状态")
```

## 自定义验证

### 自定义验证器

```python
from pydantic import field_validator, model_validator

class AdminAddRequest(BaseModel):
    """管理员添加请求"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., description="确认密码")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @model_validator(mode='after')
    @classmethod
    def validate_model(cls, data):
        # 模型级别的验证
        return data
```

### 条件验证

```python
from pydantic import field_validator

class UserAddRequest(BaseModel):
    """用户添加请求"""

    email: str = Field(..., description="邮箱")
    phone: str | None = Field(None, description="手机号")

    @model_validator(mode='after')
    @classmethod
    def validate_contact(cls, data):
        if not data.email and not data.phone:
            raise ValueError('邮箱和手机号至少填写一个')
        return data
```

## 响应模型

### 成功响应

```python
class SuccessResponse(BaseModel):
    """成功响应"""

    code: int = 200
    message: str = "success"
    data: Any = None
```

### 错误响应

```python
class ErrorResponse(BaseModel):
    """错误响应"""

    code: int = 400
    message: str = "error"
    data: Any = None
```

## 最佳实践

### 1. 添加字段描述

为所有字段添加描述：

```python
# ✅ 正确
username: str = Field(
    ...,
    min_length=3,
    max_length=50,
    description="用户名，3-50个字符"
)

# ❌ 错误
username: str = Field(..., min_length=3, max_length=50)
```

### 2. 使用类型提示

使用类型提示提高代码可读性：

```python
# ✅ 正确
username: str = Field(..., description="用户名")
status: int = Field(default=1, description="状态")

# ❌ 错误
username = Field(..., description="用户名")
status = Field(default=1, description="状态")
```

### 3. 提供友好的错误提示

提供清晰的错误提示：

```python
# ✅ 正确
@field_validator('username')
@classmethod
def validate_username(cls, v):
    if len(v) < 3:
        raise ValueError('用户名长度不能少于3个字符')
    return v

# ❌ 错误
@field_validator('username')
@classmethod
def validate_username(cls, v):
    if len(v) < 3:
        raise ValueError('invalid')
    return v
```

## 常见问题

### 1. 如何验证可选字段？

```python
phone: str | None = Field(None, description="手机号")
```

### 2. 如何设置默认值？

```python
status: int = Field(default=1, description="状态")
```

### 3. 如何验证多个字段？

```python
@model_validator(mode='after')
@classmethod
def validate_model(cls, data):
    if not data.email and not data.phone:
        raise ValueError('邮箱和手机号至少填写一个')
    return data
```

## 相关链接

- [控制器开发指南](./controller-guide.md)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [第一个接口开发](../first-api.md)

---

通过遵循验证器开发指南，您可以定义清晰、规范的请求和响应模型。
