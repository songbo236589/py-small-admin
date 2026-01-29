# Common 模块详解

本文档详细介绍 Common 公共模块的功能和实现。

## 概述

Common 模块包含所有模块共用的基础组件，包括配置管理、数据库连接、基础服务、工具函数等。

## 模块结构

```
Modules/common/
├── libs/                    # 公共库
│   ├── config/              # 配置管理
│   │   ├── __init__.py
│   │   └── config.py
│   ├── database/            # 数据库相关
│   │   ├── __init__.py
│   │   ├── redis/
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   └── sql/
│   │       ├── __init__.py
│   │       ├── engine.py
│   │       └── session.py
│   ├── password/            # 密码加密
│   │   ├── __init__.py
│   │   └── password.py
│   ├── captcha/             # 验证码
│   │   ├── __init__.py
│   │   ├── captcha_service.py
│   │   ├── image_generator.py
│   │   └── utils.py
│   ├── validation/          # 验证
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── exceptions.py
│   │   └── pagination_validator.py
│   ├── responses/           # 响应
│   │   ├── __init__.py
│   │   └── response.py
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── decimal.py
│       └── url_helper.py
├── services/                # 基础服务
│   ├── __init__.py
│   └── base_service.py
└── models/                  # 基础模型
    ├── __init__.py
    └── base_model.py
```

## 核心组件

### 1. 配置管理

#### Config

配置管理类，使用 Pydantic 进行配置管理。

```python
class Config:
    """配置管理类"""

    @classmethod
    def load(cls):
        """加载配置"""

    @classmethod
    def get(cls, key: str, default=None):
        """获取配置值"""
```

#### 使用方式

```python
from Modules.common.libs.config.config import Config

# 获取配置
app_name = Config.get("app.name")
debug = Config.get("app.debug")
```

#### 配置文件

配置文件位于 `config/` 目录：

- `app.py`: 应用配置
- `database.py`: 数据库配置
- `cache.py`: 缓存配置
- `jwt.py`: JWT 配置
- `log.py`: 日志配置
- `password.py`: 密码配置
- `upload.py`: 上传配置
- `celery.py`: Celery 配置
- `captcha.py`: 验证码配置

### 2. 数据库连接

#### MySQL 连接

```python
from Modules.common.libs.database.sql.session import get_async_session

async def get_admin(id: int):
    async with get_async_session() as session:
        result = await session.execute(
            select(AdminAdmin).where(AdminAdmin.id == id)
        )
        return result.scalar_one_or_none()
```

#### Redis 连接

```python
from Modules.common.libs.database.redis.client import get_redis_client

async def get_cache(key: str):
    redis = await get_redis_client("default")
    value = await redis.get(key)
    return json.loads(value) if value else None

async def set_cache(key: str, value: any, expire: int = 3600):
    redis = await get_redis_client("default")
    await redis.setex(key, expire, json.dumps(value))
```

### 3. 密码加密

#### PasswordService

密码服务，提供密码加密和验证功能。

```python
class PasswordService:
    """密码服务"""

    def hash_password(self, password: str) -> str:
        """加密密码"""

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
```

#### 使用方式

```python
from Modules.common.libs.password.password import PasswordService

password_service = PasswordService()

# 加密密码
hashed_password = password_service.hash_password("123456")

# 验证密码
is_valid = password_service.verify_password("123456", hashed_password)
```

### 4. 验证码

#### CaptchaService

验证码服务，提供验证码生成和验证功能。

```python
class CaptchaService:
    """验证码服务"""

    async def generate_captcha(self) -> dict:
        """生成验证码"""

    async def verify_captcha(self, captcha_id: str, captcha_code: str) -> bool:
        """验证验证码"""
```

#### 使用方式

```python
from Modules.common.libs.captcha.captcha_service import CaptchaService

captcha_service = CaptchaService()

# 生成验证码
result = await captcha_service.generate_captcha()
captcha_id = result["id"]
captcha_image = result["image"]

# 验证验证码
is_valid = await captcha_service.verify_captcha(captcha_id, "1234")
```

### 5. 响应处理

#### success

成功响应函数。

```python
def success(data=None, message="success", code=200):
    """成功响应"""
    return JSONResponse({
        "code": code,
        "message": message,
        "data": data
    })
```

#### error

错误响应函数。

```python
def error(message="error", code=400, data=None):
    """错误响应"""
    return JSONResponse({
        "code": code,
        "message": message,
        "data": data
    })
```

#### 使用方式

```python
from Modules.common.libs.responses.response import success, error

# 成功响应
return success({"id": 1}, message="添加成功")

# 错误响应
return error("用户名已存在")
```

### 6. 参数验证

#### validate_request_data

请求参数验证装饰器。

```python
def validate_request_data(request_model):
    """请求参数验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 验证逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

#### 使用方式

```python
from Modules.common.libs.validation.decorators import validate_request_data
from Modules.admin.validators.admin_validator import AdminAddRequest

@validate_request_data(AdminAddRequest)
async def add(self, username: str, password: str):
    # 参数已验证
    pass
```

### 7. 分页验证

#### PaginationRequest

分页请求模型。

```python
class PaginationRequest(BaseModel):
    """分页请求"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
```

#### CustomParams

自定义分页参数。

```python
class CustomParams(BaseModel):
    """自定义分页参数"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
```

#### 使用方式

```python
from Modules.common.libs.validation.pagination_validator import PaginationRequest

@validate_request_data(PaginationRequest)
async def index(self, page: int, limit: int):
    # page 和 limit 已验证
    pass
```

### 8. 基础服务

#### BaseService

基础服务类，提供通用的 CRUD 方法。

```python
class BaseService:
    """基础服务类"""

    async def common_add(self, data, model_class, ...):
        """通用添加方法"""

    async def common_update(self, id, data, model_class, ...):
        """通用更新方法"""

    async def common_destroy(self, id, model_class, ...):
        """通用删除方法"""

    async def common_destroy_all(self, id_array, model_class, ...):
        """通用批量删除方法"""

    async def apply_search_filters(self, query, model_class, search_params):
        """应用搜索过滤器"""

    async def apply_sorting(self, query, model_class, sort_param):
        """应用排序"""
```

#### 使用方式

```python
from Modules.common.services.base_service import BaseService

class ArticleService(BaseService):
    async def add(self, data: dict):
        return await self.common_add(
            data=data,
            model_class=Article,
        )

    async def update(self, id: int, data: dict):
        return await self.common_update(
            id=id,
            data=data,
            model_class=Article,
        )

    async def destroy(self, id: int):
        return await self.common_destroy(
            id=id,
            model_class=Article,
        )
```

### 9. 基础模型

#### BaseModel

基础模型类，所有模型的基类（不建表）。

```python
class BaseModel(SQLModel):
    """所有模型的基类"""
    # 统一 Pydantic / SQLModel 配置
```

#### BaseTableModel

基础表模型类，所有数据库表模型的基类。

```python
class BaseTableModel(BaseModel):
    """所有数据库表模型的基类"""

    # 提供：
    # - id 主键
    # - created_at / updated_at 自动维护
    # - 表注释支持
    # - 自动表名生成
    # - 表前缀支持
```

#### 使用方式

```python
from Modules.common.models.base_model import BaseTableModel

class Article(BaseTableModel, table=True):
    """文章模型"""
    __table_comment__ = "文章表"

    title: str = Field(default="")
    content: str = Field(default="")
```

### 10. 工具函数

#### decimal

小数处理工具。

```python
def round_decimal(value: float, digits: int = 2) -> float:
    """四舍五入"""

def format_decimal(value: float, digits: int = 2) -> str:
    """格式化小数"""
```

#### url_helper

URL 处理工具。

```python
def get_base_url(request: Request) -> str:
    """获取基础 URL"""

def build_url(base_url: str, path: str) -> str:
    """构建完整 URL"""
```

#### time

时间处理工具。

```python
def now() -> datetime:
    """获取当前时间"""

def format_datetime(dt: datetime) -> str:
    """格式化时间"""
```

## 最佳实践

### 1. 使用基础服务

继承 BaseService 获得通用功能，避免重复代码。

### 2. 使用配置管理

使用 Config 类管理配置，避免硬编码。

### 3. 使用响应函数

使用 success 和 error 函数返回统一格式的响应。

### 4. 使用验证装饰器

使用验证装饰器进行参数验证，提高代码可读性。

### 5. 使用异步操作

使用异步数据库和 Redis 操作，提高性能。

## 常见问题

### 1. 如何添加新的配置？

在 `config/` 目录中创建新的配置文件，然后在 `config/__init__.py` 中导入。

### 2. 如何添加新的工具函数？

在 `Modules/common/libs/utils/` 目录中创建新的工具文件。

### 3. 如何扩展基础服务？

创建新的服务类继承 BaseService，然后添加自定义方法。

## 相关链接

- [项目结构说明](./project-structure.md)
- [模块开发指南](./module-development.md)
- [Admin 模块详解](./admin-module.md)
- [Quant 模块详解](./quant-module.md)

---

Common 模块提供所有模块共用的基础组件，是项目的基础设施。
