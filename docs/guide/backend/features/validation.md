# 数据验证

本文档介绍了项目的数据验证功能。

## 简介

项目使用 Pydantic 进行数据验证，提供了强大的类型检查和验证功能。

## 基础验证

### 定义验证器

```python
from pydantic import BaseModel, Field, validator

class UserCreateValidator(BaseModel):
    """用户创建验证器"""
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    age: int = Field(..., ge=18, le=120)
    password: str = Field(..., min_length=6)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
```

### 使用验证器

```python
from fastapi import Body

@app.post("/api/user")
async def create_user(data: UserCreateValidator = Body(...)):
    """创建用户"""
    # data 已经验证通过
    user = db.create_user(data.dict())
    return user
```

## 验证装饰器

### 请求体验证

```python
from Modules.common.libs.validation.decorators import validate_request_data

@app.post("/api/user")
@validate_request_data(UserCreateValidator)
async def create_user(data: UserCreateValidator):
    """创建用户"""
    return user_service.create(data.dict())
```

### 体验证装饰器

```python
from Modules.common.libs.validation.decorators import validate_body_data

@app.post("/api/user/batch")
@validate_body_data(UserListRequest)
async def create_users(request: UserListRequest):
    """批量创建用户"""
    return user_service.create_batch(request.users)
```

## 分页验证

### 分页请求验证

```python
from Modules.common.libs.validation.pagination_validator import PaginationRequest

@app.get("/api/user")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """获取用户列表"""
    # 验证分页参数
    pagination = PaginationRequest(page=page, limit=limit)
    return user_service.get_list(pagination)
```

### ID 验证

```python
from Modules.common.libs.validation.pagination_validator import IdRequest, IdArrayRequest

@app.get("/api/user/{id}")
async def get_user(id: int = Path(..., description="用户ID")):
    """获取用户详情"""
    request = IdRequest(id=id)
    return user_service.get_by_id(request.id)

@app.delete("/api/user/batch")
async def delete_users(ids: IdArrayRequest = Body(...)):
    """批量删除用户"""
    return user_service.delete_batch(ids.id_array)
```

## 自定义验证

### 字段验证

```python
from pydantic import BaseModel, field_validator

class ProductValidator(BaseModel):
    """商品验证器"""
    name: str
    price: float

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('价格必须大于零')
        return v

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('名称不能为空')
        return v.strip()
```

### 模型验证

```python
from pydantic import model_validator

class OrderValidator(BaseModel):
    """订单验证器"""
    items: list[ItemValidator]
    total_amount: float

    @model_validator(mode='after')
    def validate_total_amount(self) -> 'OrderValidator':
        """验证总金额"""
        calculated = sum(item.price * item.quantity for item in self.items)
        if abs(calculated - self.total_amount) > 0.01:
            raise ValueError('总金额与商品明细不符')
        return self
```

## 验证错误处理

### 获取验证错误

```python
from pydantic import ValidationError

try:
    user = UserCreateValidator(**data)
except ValidationError as e:
    # 获取错误信息
    errors = e.errors()
    for error in errors:
        print(f"字段: {error['loc']}")
        print(f"错误: {error['msg']}")
```

### 自定义错误消息

```python
class UserValidator(BaseModel):
    """用户验证器"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="用户名"
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "admin"
            }
        }

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        if v in ['admin', 'root']:
            raise ValueError('该用户名已被保留')
        return v
```

## 复杂验证

### 嵌套验证

```python
class AddressValidator(BaseModel):
    """地址验证器"""
    province: str
    city: str
    street: str
    zip_code: str = Field(..., regex=r"^\d{6}$")

class UserValidator(BaseModel):
    """用户验证器"""
    username: str
    address: AddressValidator  # 嵌套验证
```

### 列表验证

```python
class UserListValidator(BaseModel):
    """用户列表验证器"""
    users: list[UserCreateValidator]

    @field_validator('users')
    @classmethod
    def users_not_empty(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError('用户列表不能为空')
        if len(v) > 100:
            raise ValueError('最多一次创建 100 个用户')
        return v
```

### 可选字段验证

```python
from typing import Optional

class UserUpdateValidator(BaseModel):
    """用户更新验证器"""
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=120)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v
```

## 验证最佳实践

### 1. 分离验证器

```python
# validators/user_validator.py
class UserCreateValidator(BaseModel):
    """创建验证器"""

class UserUpdateValidator(BaseModel):
    """更新验证器"""

class UserSearchValidator(BaseModel):
    """搜索验证器"""
```

### 2. 使用 Field 描述

```python
class ProductValidator(BaseModel):
    """商品验证器"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="商品名称"
    )
    price: float = Field(
        ...,
        gt=0,
        le=999999,
        description="商品价格（单位：元）"
    )
```

### 3. 提供示例

```python
class UserValidator(BaseModel):
    """用户验证器"""
    username: str
    email: str

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "admin",
                    "email": "admin@example.com"
                }
            ]
        }
```

### 4. 验证性能优化

```python
# 使用 frozenset 提高查找性能
VALID_CATEGORIES = frozenset(['electronics', 'clothing', 'food'])

class ProductValidator(BaseModel):
    category: str

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f'类别必须是以下之一: {", ".join(VALID_CATEGORIES)}')
        return v
```

## 相关文档

- [异常处理](./exception.md)
- [API 文档](../api/admin-api.md)
