# 最佳实践

本文档介绍 Py Small Admin 开发中的最佳实践。

## 概述

遵循最佳实践可以编写更高质量、更易维护、更易扩展的代码。

## 代码规范

### 1. 命名规范

#### 文件命名

使用 kebab-case（小写字母 + 连字符）：

```python
# ✅ 正确
admin_controller.py
admin_service.py
article_model.py

# ❌ 错误
adminController.py
admin_service.py
ArticleModel.py
```

#### 类命名

使用 PascalCase（大驼峰命名）：

```python
# ✅ 正确
class AdminController:
    pass

class AdminService:
    pass

class ArticleModel:
    pass

# ❌ 错误
class adminController:
    pass

class admin_service:
    pass
```

#### 函数/方法命名

使用 snake_case（小写字母 + 下划线）：

```python
# ✅ 正确
def add_admin():
    pass

def get_user_list():
    pass

def validate_password():
    pass

# ❌ 错误
def AddAdmin():
    pass

def getUserList():
    pass
```

#### 变量命名

使用 snake_case：

```python
# ✅ 正确
user_id = 1
admin_name = "张三"
is_active = True

# ❌ 错误
userId = 1
adminName = "张三"
isActive = True
```

#### 常量命名

使用 UPPER_CASE（全大写 + 下划线）：

```python
# ✅ 正确
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
API_TIMEOUT = 30

# ❌ 错误
max_retry_count = 3
defaultPageSize = 20
api_timeout = 30
```

### 2. 代码格式化

#### 使用 Black

```bash
# 安装 Black
pip install black

# 格式化代码
black .

# 检查格式
black --check .
```

#### 使用 isort

```bash
# 安装 isort
pip install isort

# 排序导入
isort .

# 检查导入顺序
isort --check-only .
```

### 3. 类型提示

使用类型提示提高代码可读性和类型安全：

```python
# ✅ 正确
from typing import Any

async def add_admin(data: dict[str, Any]) -> JSONResponse:
    pass

# ❌ 错误
async def add_admin(data):
    pass
```

### 4. 文档字符串

为所有函数和类添加文档字符串：

```python
# ✅ 正确
class AdminService:
    """管理员服务 - 负责管理员相关的业务逻辑"""

    async def add(self, data: dict[str, Any]) -> JSONResponse:
        """添加管理员

        Args:
            data: 管理员数据

        Returns:
            JSONResponse: 操作结果
        """
        pass

# ❌ 错误
class AdminService:
    async def add(self, data):
        pass
```

## 架构设计

### 1. 遵循分层架构

严格按照分层架构开发：

```python
# ✅ 正确 - 遵循分层
# Routes
router.post("/add")(controller.add)

# Controllers
async def add(self, data):
    return await self.admin_service.add(data)

# Services
async def add(self, data):
    return await self.common_add(data, AdminAdmin)

# ❌ 错误 - 跨层调用
# Controllers 直接操作数据库
async def add(self, data):
    session.add(AdminAdmin(**data))
    await session.commit()
```

### 2. 单一职责

每个类和函数只负责一件事：

```python
# ✅ 正确
class AdminService:
    """只负责管理员业务逻辑"""
    pass

class PasswordService:
    """只负责密码处理"""
    pass

class EmailService:
    """只负责邮件发送"""
    pass

# ❌ 错误
class AdminService:
    """职责太多"""
    def add_admin(self): pass
    def hash_password(self): pass
    def send_email(self): pass
```

### 3. 依赖注入

使用依赖注入降低耦合：

```python
# ✅ 正确
class AdminController:
    def __init__(self, admin_service: AdminService):
        self.admin_service = admin_service

# ❌ 错误
class AdminController:
    def __init__(self):
        self.admin_service = AdminService()
```

## 数据库操作

### 1. 使用异步操作

使用异步数据库操作提高性能：

```python
# ✅ 正确
async def add(self, data: dict):
    async with get_async_session() as session:
        instance = AdminAdmin(**data)
        session.add(instance)
        await session.commit()

# ❌ 错误
def add(self, data: dict):
    with get_session() as session:
        instance = AdminAdmin(**data)
        session.add(instance)
        session.commit()
```

### 2. 使用事务

使用事务确保数据一致性：

```python
# ✅ 正确
async def transfer_money(self, from_id: int, to_id: int, amount: int):
    async with get_async_session() as session:
        try:
            # 扣款
            from_account = await session.get(Account, from_id)
            from_account.balance -= amount

            # 加款
            to_account = await session.get(Account, to_id)
            to_account.balance += amount

            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

# ❌ 错误 - 没有事务
async def transfer_money(self, from_id: int, to_id: int, amount: int):
    # 扣款
    from_account = await session.get(Account, from_id)
    from_account.balance -= amount

    # 加款
    to_account = await session.get(Account, to_id)
    to_account.balance += amount
```

### 3. 避免 N+1 问题

使用预加载避免 N+1 查询问题：

```python
# ✅ 正确 - 使用 selectinload
query = select(AdminAdmin).options(
    selectinload(AdminAdmin.group)
)

# ❌ 错误 - N+1 问题
admins = await session.exec(select(AdminAdmin))
for admin in admins:
    # 每次循环都会查询数据库
    group = admin.group
```

### 4. 使用索引

为常用查询字段添加索引：

```python
# ✅ 正确
class AdminAdmin(BaseTableModel, table=True):
    username: str = Field(default="", index=True)
    status: int = Field(default=1, index=True)
    created_at: datetime = Field(default=None, index=True)

# ❌ 错误 - 没有索引
class AdminAdmin(BaseTableModel, table=True):
    username: str = Field(default="")
    status: int = Field(default=1)
    created_at: datetime = Field(default=None)
```

## 错误处理

### 1. 统一错误处理

使用统一的错误处理机制：

```python
# ✅ 正确
from Modules.common.libs.responses.response import error

async def add(self, data: dict):
    try:
        # 业务逻辑
        return success(None, message="添加成功")
    except ValueError as e:
        return error(str(e))
    except Exception as e:
        return error("系统错误")

# ❌ 错误 - 错误处理不一致
async def add(self, data: dict):
    try:
        # 业务逻辑
        return {"code": 200, "message": "添加成功"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"status": "error", "msg": "系统错误"}
```

### 2. 记录错误日志

记录错误日志便于调试：

```python
# ✅ 正确
import logging

logger = logging.getLogger(__name__)

async def add(self, data: dict):
    try:
        # 业务逻辑
        pass
    except Exception as e:
        logger.error(f"添加管理员失败: {e}", exc_info=True)
        return error("添加失败")

# ❌ 错误 - 没有日志
async def add(self, data: dict):
    try:
        # 业务逻辑
        pass
    except Exception as e:
        return error("添加失败")
```

### 3. 友好的错误提示

提供友好的错误提示：

```python
# ✅ 正确
async def add(self, data: dict):
    if await self.check_username_exists(data["username"]):
        return error("用户名已存在，请使用其他用户名")

# ❌ 错误 - 错误提示不友好
async def add(self, data: dict):
    if await self.check_username_exists(data["username"]):
        return error("username exists")
```

## 安全实践

### 1. 密码加密

使用强加密算法加密密码：

```python
# ✅ 正确
from Modules.common.libs.password.password import PasswordService

password_service = PasswordService()
hashed_password = password_service.hash_password("123456")

# ❌ 错误 - 不加密
password = "123456"
```

### 2. 参数验证

严格验证所有输入参数：

```python
# ✅ 正确
from pydantic import BaseModel, Field

class AdminAddRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

# ❌ 错误 - 没有验证
async def add(self, username: str, password: str):
    pass
```

### 3. SQL 注入防护

使用 ORM 防止 SQL 注入：

```python
# ✅ 正确 - 使用 ORM
query = select(AdminAdmin).where(AdminAdmin.username == username)

# ❌ 错误 - SQL 注入风险
query = f"SELECT * FROM admin_admins WHERE username = '{username}'"
```

### 4. 敏感信息保护

不要在日志中记录敏感信息：

```python
# ✅ 正确
logger.info(f"用户登录: username={username}")

# ❌ 错误 - 记录密码
logger.info(f"用户登录: username={username}, password={password}")
```

## 性能优化

### 1. 使用缓存

使用 Redis 缓存常用数据：

```python
# ✅ 正确
from Modules.common.libs.database.redis.client import get_redis_client

async def get_config(self, key: str):
    redis = await get_redis_client("cache")
    # 先从缓存获取
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)

    # 缓存不存在，从数据库获取
    config = await self._get_from_db(key)
    # 写入缓存
    await redis.setex(key, 3600, json.dumps(config))
    return config

# ❌ 错误 - 每次都查询数据库
async def get_config(self, key: str):
    return await self._get_from_db(key)
```

### 2. 分页查询

使用分页避免一次性加载大量数据：

```python
# ✅ 正确
async def index(self, page: int = 1, size: int = 20):
    query = select(AdminAdmin)
    page_data = await paginate(session, query, CustomParams(page=page, size=size))
    return page_data

# ❌ 错误 - 一次性加载所有数据
async def index(self):
    query = select(AdminAdmin)
    result = await session.exec(query)
    return result.all()
```

### 3. 延迟加载

使用延迟加载减少不必要的查询：

```python
# ✅ 正确
async def get_admin(self, id: int):
    admin = await session.get(AdminAdmin, id)
    # 只在需要时加载关联数据
    if admin.group:
        return admin.group.name
    return None

# ❌ 错误 - 总是加载关联数据
async def get_admin(self, id: int):
    admin = await session.exec(
        select(AdminAdmin).options(selectinload(AdminAdmin.group))
    ).where(AdminAdmin.id == id)
    return admin.first()
```

## 测试

### 1. 编写单元测试

为关键功能编写单元测试：

```python
# ✅ 正确
import pytest
from Modules.admin.services.admin_service import AdminService

@pytest.mark.asyncio
async def test_add_admin():
    service = AdminService()
    result = await service.add({
        "username": "test",
        "password": "123456",
    })
    assert result.status_code == 200

# ❌ 错误 - 没有测试
async def add(self, data: dict):
    # 业务逻辑
    pass
```

### 2. 使用测试数据

使用测试数据隔离测试环境：

```python
# ✅ 正确
@pytest.fixture
async def test_db():
    # 创建测试数据库
    async with get_async_session() as session:
        yield session
        # 清理测试数据
        await session.rollback()

# ❌ 错误 - 使用生产数据
async def test_add_admin():
    # 直接使用生产数据库
    pass
```

## 文档

### 1. 编写 API 文档

为所有 API 编写文档：

```python
# ✅ 正确
@router.get(
    "/index",
    response_model=dict[str, Any],
    summary="获取管理员列表",
    description="分页获取管理员列表，支持搜索和排序",
)
async def index(
    page: int = Query(1, description="页码"),
    limit: int = Query(20, description="每页数量"),
):
    pass

# ❌ 错误 - 没有文档
@router.get("/index")
async def index(page: int, limit: int):
    pass
```

### 2. 编写代码注释

为复杂逻辑添加注释：

```python
# ✅ 正确
# 检查用户名是否已存在
# 如果存在，返回错误
existing_admin = await session.exec(
    select(AdminAdmin).where(AdminAdmin.username == username)
)
if existing_admin.first():
    return error("用户名已存在")

# ❌ 错误 - 没有注释
existing_admin = await session.exec(
    select(AdminAdmin).where(AdminAdmin.username == username)
)
if existing_admin.first():
    return error("用户名已存在")
```

## 常见错误

### 1. 忘记提交事务

```python
# ❌ 错误
async def add(self, data: dict):
    instance = AdminAdmin(**data)
    session.add(instance)
    # 忘记提交

# ✅ 正确
async def add(self, data: dict):
    instance = AdminAdmin(**data)
    session.add(instance)
    await session.commit()
```

### 2. 忘记关闭会话

```python
# ❌ 错误
async def add(self, data: dict):
    session = get_async_session()
    instance = AdminAdmin(**data)
    session.add(instance)
    await session.commit()
    # 忘记关闭会话

# ✅ 正确
async def add(self, data: dict):
    async with get_async_session() as session:
        instance = AdminAdmin(**data)
        session.add(instance)
        await session.commit()
```

### 3. 捕获所有异常

```python
# ❌ 错误
try:
    # 业务逻辑
    pass
except Exception:
    pass  # 吞掉所有异常

# ✅ 正确
try:
    # 业务逻辑
    pass
except ValueError as e:
    # 处理特定异常
    logger.error(f"ValueError: {e}")
    raise
except Exception as e:
    # 记录未知异常
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

## 工具推荐

### 代码格式化

- **Black**: 代码格式化
- **isort**: 导入排序
- **autoflake**: 删除未使用的导入

### 代码检查

- **Pylint**: 代码质量检查
- **Flake8**: 代码风格检查
- **Mypy**: 类型检查

### 测试工具

- **Pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 测试覆盖率

## 相关链接

- [架构概览](./architecture-overview.md)
- [分层架构说明](./layered-architecture.md)
- [设计模式应用](./design-patterns.md)
- [快速开始](../server/getting-started.md)

---

遵循最佳实践，编写高质量的代码！
